# Agent instructions: TurboActivate error 28 on Wine

Goal: give a Wine runner a `wbemprox.dll` that implements `MSFT_NetAdapter`, so that a TurboActivate-licensed program can read the network adapters. It was developed for Bogren Digital MLC S_Zero 93 and MLC S_Zero 100. Background is in [README.md](README.md).

## Rules

- Do not read licence or activation files (`TurboActivate.dat`, `*.tad`, or anything the product stores for its licence).
- Do not run the licensed program and do not attempt activation. Give the user the commands, and the user runs them and enters the serial.
- Do not fake adapter values and do not change a licence check.
- Do not put MAC addresses, serials or hardware details in commits, reports or issues. `netadapter-fix verify` masks addresses by default, so do not pass `--full` unless the user asks.
- Warn the user before changing a runner on which a licence is already activated: activation is tied to the values this DLL reports. The user should deactivate in the product before any change that alters them.
- Do not submit this patch to WineHQ. It is LLM-assisted, and WineHQ excludes such code.

## Steps

1. Identify the runner. Ask the user for its root directory or `wine` binary and the prefix if you cannot find them. Confirm the runner's version with `<runner>/usr/bin/wine --version` (or `bin/wine`).
2. Confirm the symptom with the user: error 28 from a valid serial. Check that the prefix uses this runner.
3. Check the tools: `git`, `gcc`, `make`, `flex`, `bison`, `x86_64-w64-mingw32-gcc`. Install them only with the user's approval.
4. Pick the source that matches the runner, using `--repo` and `--ref`, plus `--extra-patch` for patches that the runner also carries in `dlls/wbemprox`. The default is the `wine-11.21` tag. README.md gives the exact command for the giang17 COPR runner.
5. Run `./netadapter-fix install --runner <runner> ...`. If a patch fails to apply, follow "Applying to another Wine or version" in README.md. Do not change the patch's values to make it apply.
6. Run `./netadapter-fix verify --runner <runner> --prefix <prefix>`.
7. Check the result. Expected: `strict: N rows, N with an address`, with N equal to the machine's real wired and Wi-Fi adapters. Count them by checking which entries in `/sys/class/net` have a `device` link and are Ethernet or Wi-Fi. Exit status 0 means success, 1 means no usable rows, 2 means a WMI call failed.
8. Tell the user to start the program fresh, and to activate with the serial. Remind them to deactivate before changing Wine later. Give them `WINEDEBUG=+wbemprox` for a failing run.

## If activation still fails

Ask the user for the new error number and a `WINEDEBUG=+wbemprox` log. Do not ask for the serial. Search the log for `wbem_services_ExecQuery` and `get_method`. The queries after the two `MSFT_NetAdapter` ones show what TurboActivate wanted next. Do not paste log contents with hardware values into anything public.

Likely next steps, none of them proven:

- `root\wmi` `MSNdis_*` classes, if TurboActivate falls back to the Windows 7 route.
- A property or method that `MSFT_NetAdapter` does not have yet.

Add only what the log shows is needed, with real values.

## Undo

`./netadapter-fix restore --runner <runner>` restores the backed-up DLL. Ask the user to deactivate first. `./netadapter-fix status --runner <runner>` shows what is installed.

## Checks for changes to this folder

After editing the script: `uvx ruff check --config ~/.config/ruff/ruff.toml netadapter-fix` and `uvx ruff format --check --config ~/.config/ruff/ruff.toml netadapter-fix`. To test without touching a real runner, copy the runner (`cp -a --reflink=auto`), create a temporary prefix with it, and pass the copy to `--runner`. An unpatched runner must make `verify` fail with 0 rows. A patched one must pass `verify` on a prefix that was created before the DLL was replaced, which proves that the loader uses the runner's copy and ignores the prefix's copy.
