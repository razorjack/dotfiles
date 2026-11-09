# Agent instructions: yabridge VST3 `getState`/`beginEdit` hang

Goal: build yabridge with the patch in this folder and give the user a build to test. Background is in [README.md](README.md).

## Rules

- Do not run `git push` or post to yabridge's issue tracker unless the user asks. Draft only.
- Do not switch the active bridge while a DAW is running. Check for the DAW's processes first, and ask the user to close it.
- Do not read plugin licence or session files.
- Do not run `winedbg --command "bt all"` on prefixes with 32-bit processes. `gdb -batch -p <pid>` was safe.

## Steps

1. Confirm the symptom: a VST3 plugin hangs the host, and a capture matches the table in README.md. A different stack is a different bug, so stop and investigate.
2. Check that `git` and `podman` exist. Run `./build-yabridge`. It fails if any line of the unit test fails.
3. Follow "Build and install" in README.md. Keep the previous build installed.
4. Run `vstbridge doctor`.
5. Ask the user to repeat the action that hung. Record the result in the evidence ledger of `../../README.md`.

## If the hang persists

Capture all threads of both processes while hung, and compare them with the table in README.md. `YABRIDGE_DEBUG_LEVEL=2` in the DAW's environment logs each request, which names the request that is stuck. Debug logging changes timing and may hide the race.

## Checks for changes to this folder

Change the C++ in the clone under `~/.cache/vstbridge-yabridge-fix/src`, then regenerate `yabridge-gui-call-recursion.patch` with `git format-patch -1 --stdout --no-signature`, using identity `vstbridge <vstbridge@invalid>` and a fixed date. The build id in README.md depends on the patch, so update it from `git describe --always`. The `--old` mode of `recursion_test.cpp` must keep reporting a stuck request, because that proves the test can detect the hang.
