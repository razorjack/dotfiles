# yabridge: VST3 plugin hangs when `getState` meets `beginEdit`

A Windows VST3 plugin running through yabridge can hang the host when the host asks for the plugin's state while the plugin's GUI thread is busy and about to start a parameter edit. This folder holds a yabridge patch, a test for it, and a script that builds yabridge with the patch.

It was developed for **Kilohearts Phase Plant** in **Bitwig Studio 6.1.4**, where quickly switching presets freezes the plugin until Bitwig offers to kill the sandbox. If you are an agent, follow [AGENTS.md](AGENTS.md).

Status: the unit test reproduces the hang on the old code path and passes with the patch. With the patched build, quick preset switching in Phase Plant no longer hung Bitwig (reported by the user, 2026-11-09). The race is timing-dependent, so one good session does not prove it is gone, and other plugins and hosts have not been tested.

Search terms: yabridge, VST3, deadlock, hang, freeze, Bitwig, "plugin not responding", Phase Plant, Kilohearts, `getState`, `beginEdit`, `IComponentHandler`, `do_mutual_recursion_on_gui_thread`, `MutualRecursionHelper`, yabridge issue 504, PR 505.

## Symptom

The plugin works, then freezes during rapid GUI activity such as switching presets. CPU use is idle. Four threads wait on each other:

| Process and thread | Waiting for |
|---|---|
| Bitwig main thread, in yabridge's `fork()`, holding Bitwig's plugin mutex | The answer to a request sent to the Wine side |
| Bitwig `host-callbacks` thread | That mutex, before it can answer `beginEdit` |
| Wine GUI thread, inside the plugin's `beginEdit` call | The answer to `beginEdit`, running only the temporary IO context in `fork()` |
| Wine `worker` thread | A `std::future` for the request, which is queued on the main IO context |

To check for this hang, look at `/proc/<pid>/task/*/wchan` and `ss -xpn` for the Bitwig plugin host and `yabridge-host.exe`, or attach `gdb -batch -p <pid> -ex 'thread apply all bt'`. Do not use `winedbg --command "bt all"` on a prefix with 32-bit processes, because it crashed a process here.

## Cause

[yabridge #505](https://github.com/robbert-vdh/yabridge/pull/505) fixed the order in which `beginEdit` starts first: `beginEdit` now creates a mutual recursion context on the GUI thread, and a state request that arrives afterwards runs in that context.

The opposite order remains in `5.1.1-72-g7529c2d6`:

1. The Wine GUI thread is busy, for example loading a preset.
2. `IComponent::getState` arrives on a socket thread. `do_mutual_recursion_on_gui_thread()` finds no recursion context, so it queues the call on the main IO context and waits.
3. The busy GUI thread calls `beginEdit`, which enters `fork()` and runs only the new temporary IO context.
4. The queued `getState` stays on the main IO context, which the GUI thread cannot reach until `beginEdit` returns.
5. Bitwig holds its mutex until `getState` returns, so it cannot answer `beginEdit`. All of them wait forever.

The first capture on `5.1.1-72` matches this state. Step 2 happened before step 3 by inference from that state, because a capture cannot show arrival order. The Bitwig call site is vtable slot 13 (offset `0x68`), which is `IComponent::getState`. Bitwig has no symbols, so the name comes from the offset.

## What the patch does

`MutualRecursionHelper` gets `handle_or_schedule()` and a list of calls that have not finished. `fork()` adds every waiting call to its new IO context. A call can then sit in the main IO context and in one or more recursion contexts, and an atomic flag lets the first queue that reaches it run it. The others do nothing.

`Vst3Bridge::do_mutual_recursion_on_gui_thread()` uses the new function. Every VST3 plugin goes through it, for `setState`, `getState`, `setChannelContextInfos`, `setActive` and a few `IPlugView` calls. The patch runs such a call nested inside the plugin's `beginEdit`, the same nesting that #505 introduced for a request that arrives after `beginEdit`. The Linux-side library is unchanged.

CLAP has the same pattern in `src/wine-host/bridges/clap.h`, and the patch does not change it, because no CLAP hang has been observed. VST2 uses a different path.

## Build and install

Needs `git` and `podman`. The script does not need root or any host packages, because it builds in upstream's CI image `robbert/docker-yabridge:focal`, pinned by digest. A build takes a few minutes.

```sh
./build-yabridge
```

The script clones yabridge into `~/.cache/vstbridge-yabridge-fix`, applies the patch to commit `7529c2d6` with a fixed identity and date, builds with the flags from upstream's CI, runs `recursion_test.cpp` normally and under ThreadSanitizer, and writes `yabridge-5.1.1-73-g18fcc9f7.tar.gz` to `out/`. It leaves `yabridgectl` out, so use the upstream `yabridgectl` archive of the same commit.

```sh
vstbridge bridge install ~/.cache/vstbridge-yabridge-fix/out/yabridge-5.1.1-73-g18fcc9f7.tar.gz \
  <yabridgectl-5.1.1-72-g7529c2d6 archive> \
  --accept-unpinned --origin 'upstream 7529c2d6 with fixes/yabridge-vst3-state-deadlock'
vstbridge bridge use 5.1.1-73-g18fcc9f7
```

Then set `pin = 5.1.1-73-g18fcc9f7` in `~/.config/vstbridge/vstbridge.conf`, so that `doctor` accepts the build. Close the DAW before `bridge use`, because a running host mixes old libraries with new `yabridge-host.exe` processes.

## Removing it

```sh
vstbridge bridge use 5.1.1-72-g7529c2d6
```

Set `pin` back as well. Installed builds stay in `~/.local/share/vstbridge/bridges/`.

## Moving to a newer yabridge

Drop this patch when upstream fixes the race. Otherwise update `commit` in `build-yabridge`, regenerate the patch if it does not apply, and rebuild. The version in the commands above changes with the base commit. The patch touches only `src/common/mutual-recursion.h` and `do_mutual_recursion_on_gui_thread()` in `src/wine-host/bridges/vst3.h`.

## Licence and provenance

The patch modifies yabridge and is GPL-3.0-or-later, like yabridge. It was written with LLM assistance, so check yabridge's contribution rules and disclose this before submitting it upstream. This folder has no affiliation with yabridge, Bitwig or Kilohearts.
