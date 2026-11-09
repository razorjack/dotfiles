// Checks MutualRecursionHelper::handle_or_schedule() without Wine or a plugin.
// `build-yabridge` compiles this against the patched header and runs it.
// With --old it runs the first scenario through maybe_handle(), the code path
// before the patch, and passes only if the request stays stuck.

#include <atomic>
#include <chrono>
#include <cstdio>
#include <cstring>
#include <future>
#include <thread>

#include <asio/executor_work_guard.hpp>

#include "common/mutual-recursion.h"

using namespace std::chrono_literals;

class JoiningThread {
   public:
    template <typename F>
    explicit JoiningThread(F&& fn) : thread_(std::forward<F>(fn)) {}
    ~JoiningThread() { thread_.join(); }

   private:
    std::thread thread_;
};

using Helper = MutualRecursionHelper<JoiningThread>;

static int failures = 0;

static void check(bool ok, const char* what) {
    std::printf("%s: %s\n", ok ? "ok  " : "FAIL", what);
    failures += !ok;
}

// The GUI thread is busy when the request arrives, and it enters fork() before
// it returns to the event loop. fork() waits for the request to finish, which
// is what Bitwig does when it holds up the answer to beginEdit().
static void request_before_fork() {
    Helper helper;
    asio::io_context main_context;
    std::atomic_int runs = 0;
    std::atomic<std::thread::id> ran_on{};
    std::promise<void> finished;
    auto finished_future = finished.get_future();
    std::promise<void> queued;

    std::thread requester([&]() {
        int result = helper.handle_or_schedule(
            [&]() {
                runs++;
                ran_on = std::this_thread::get_id();
                return 42;
            },
            [&](std::function<void()> call) {
                asio::post(main_context, std::move(call));
                queued.set_value();
            });
        check(result == 42, "the requester gets the result");
        finished.set_value();
    });

    queued.get_future().wait();
    const bool answered = helper.fork([&]() {
        return finished_future.wait_for(5s) == std::future_status::ready;
    });
    check(answered, "a request queued before fork() runs during fork()");
    check(ran_on.load() == std::this_thread::get_id(),
          "the request runs on the thread that called fork()");

    main_context.poll();
    requester.join();
    check(runs == 1, "the copy left in the main context does not run again");
}

// The same order of events through the code path before the patch.
static void request_before_fork_old() {
    Helper helper;
    asio::io_context main_context;
    std::promise<void> finished;
    auto finished_future = finished.get_future();
    std::promise<void> queued;

    std::thread requester([&]() {
        auto fn = [&]() { return 42; };
        if (!helper.maybe_handle(fn)) {
            std::packaged_task<int()> task(fn);
            auto result = task.get_future();
            asio::post(main_context, std::move(task));
            queued.set_value();
            result.get();
        }
        finished.set_value();
    });

    queued.get_future().wait();
    const bool answered = helper.fork([&]() {
        return finished_future.wait_for(2s) == std::future_status::ready;
    });
    check(!answered, "before the patch, the request is stuck during fork()");

    main_context.poll();
    requester.join();
}

// A request reaches the outer fork() while a handler on that fork() is about
// to start a nested fork() that depends on the request.
static void request_in_outer_fork() {
    Helper helper;
    std::promise<void> finished;
    auto finished_future = finished.get_future();
    std::promise<void> outer_handler_running;
    auto outer_handler_future = outer_handler_running.get_future();
    std::atomic_int runs = 0;
    bool nested_answered = false;

    std::thread requester([&]() {
        outer_handler_future.wait();
        helper.handle_or_schedule(
            [&]() {
                runs++;
                return 1;
            },
            [](std::function<void()> call) { call(); });
        finished.set_value();
    });

    helper.fork([&]() {
        return helper.handle_or_schedule(
            [&]() {
                outer_handler_running.set_value();
                std::this_thread::sleep_for(100ms);
                nested_answered = helper.fork([&]() {
                    return finished_future.wait_for(5s) ==
                           std::future_status::ready;
                });
                return 0;
            },
            [](std::function<void()> call) { call(); });
    });
    requester.join();

    check(nested_answered, "a nested fork() picks up the outer fork()'s request");
    check(runs == 1, "that request runs once");
}

// Requests race with the main context being drained and with fork().
static void race(int iterations) {
    Helper helper;
    asio::io_context main_context;
    auto guard = asio::make_work_guard(main_context);
    std::atomic_int runs = 0;
    std::atomic_bool stop = false;

    std::thread requester([&]() {
        for (int i = 0; i < iterations; i++) {
            helper.handle_or_schedule(
                [&]() {
                    runs++;
                    return 0;
                },
                [&](std::function<void()> call) {
                    asio::post(main_context, std::move(call));
                });
        }
        stop = true;
    });

    while (!stop) {
        main_context.poll();
        helper.fork([&]() { return main_context.stopped(); });
    }
    main_context.poll();
    requester.join();
    check(runs == iterations, "every racing request runs exactly once");
}

int main(int argc, char** argv) {
    if (argc > 1 && !std::strcmp(argv[1], "--old")) {
        request_before_fork_old();
    } else {
        request_before_fork();
        request_in_outer_fork();
        race(5000);
    }
    return failures ? 1 : 0;
}
