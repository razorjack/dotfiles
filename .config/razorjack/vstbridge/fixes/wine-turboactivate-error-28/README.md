# TurboActivate "Error 28" under Wine: adding MSFT_NetAdapter to wbemprox

Plugins and programs that license through TurboActivate (wyDay, LimeLM) fail to activate under Wine with **Error 28, `TA_E_ENABLE_NETWORK_ADAPTERS`**, because Wine's `wbemprox` has no `MSFT_NetAdapter` class. This folder holds a Wine patch that adds the class, and a script that builds and installs only the patched `wbemprox.dll` into a Wine runner.

It was developed for **Bogren Digital MLC S_Zero 93** and **MLC S_Zero 100** running through **yabridge** on Fedora. It should apply to anything that reaches the same query. If you are an agent, follow [AGENTS.md](AGENTS.md).

Status: with this DLL on giang17 Wine 11.21-101.fc44, a valid serial activated MLC S_Zero 100 (reported by the user, 2026-11-08). Activation after a cold restart, MLC S_Zero 93, other runners and other machines have not been tested.

Search terms: Error 28, `TA_E_ENABLE_NETWORK_ADAPTERS`, "Enable network adapters", "There are network adapters on the system that are disabled", TurboActivate, LimeLM, `MSFT_NetAdapter`, `root\StandardCimv2`, wbemprox, Bogren Digital, Wine, Proton, yabridge.

## Symptom

A valid serial is rejected with error 28, which TurboActivate documents as disabled network adapters. A mistyped serial gives error 1, which is a local format check. Every adapter on the Linux host can be up and working. Bogren's advice (enable adapters in Device Manager, update drivers) does not apply, because Wine has no such state to change.

## Evidence

`WINEDEBUG=+wbemprox` during a failed activation shows exactly two WMI queries in `root\StandardCimv2`, and no other WMI activity:

```
SELECT DeviceID, PermanentAddress, PNPDeviceID, WdmInterface FROM MSFT_NetAdapter WHERE (Virtual = FALSE AND NOT PNPDeviceID LIKE "XEN%\\%" AND NOT PNPDeviceID LIKE "VMBUS\\%") AND (InterfaceType = 6 OR InterfaceType = 71) AND NOT NdisPhysicalMedium = 10 AND NOT PNPDeviceID LIKE "ROOT\\%"
SELECT DeviceID, PermanentAddress, PNPDeviceID, WdmInterface FROM MSFT_NetAdapter WHERE (InterfaceType = 6 OR InterfaceType = 71) AND NOT NdisPhysicalMedium = 10 AND NOT PNPDeviceID LIKE "ROOT\\%"
```

To check whether you have this problem, run with `WINEDEBUG=+wbemprox` and search the output for `MSFT_NetAdapter`. `netadapter-fix verify` (below) runs both queries directly and needs no plugin.

## Cause

`root\StandardCimv2` has existed in Wine's `wbemprox` since November 2023 ([MR 4453](https://gitlab.winehq.org/wine/wine/-/merge_requests/4453), for a Unity licensing client that wants the same class), but no classes are registered in it. In a known namespace, an unknown class is not an error: `create_view` leaves the view with no tables, `exec_select_view` returns `S_OK`, and the caller gets an empty enumerator. TurboActivate sees no adapters and returns error 28.

Wine bug [50256](https://bugs.winehq.org/show_bug.cgi?id=50256) is an older report of the same error, through `Win32_NetworkAdapter`. The strings in the MLC S_Zero binary suggest that TurboActivate also carries a path for older Windows, which uses `Win32_NetworkAdapter` and the `MSNdis_*` classes in `root\wmi`. Wine has no `MSNdis_*` classes. On a default Windows 10 prefix, the trace shows only the `MSFT_NetAdapter` path.

## What the patch does

The patch adds one table, `MSFT_NetAdapter`, to `root\StandardCimv2`, with the seven columns that the queries use. Each adapter that is not a loopback interface gets a row. Reported values come from the Linux host:

| Column | Value |
|---|---|
| `DeviceID` | The adapter GUID with braces, the same GUID as `AdapterName` from `GetAdaptersInfo` |
| `InterfaceType` | Wine's `IfType` (6 Ethernet, 71 Wi-Fi) |
| `NdisPhysicalMedium` | 14 for Ethernet, 9 for Wi-Fi, otherwise 0 |
| `PermanentAddress` | 12 upper-case hex digits. Wi-Fi uses the burned-in address from `/sys/class/net/<if>/phy80211/macaddress`. Other adapters use the current address |
| `PNPDeviceID` | `PCI\VEN_xxxx&DEV_xxxx&SUBSYS_xxxxxxxx\<if>`, `USB\VID_xxxx&PID_xxxx\<if>` or `SD\...` from the real IDs in `/sys/class/net/<if>/device/uevent`. Adapters with no sysfs device (bridges, veth, tunnels) get `ROOT\NET\<if>` |
| `Virtual` | True for adapters with no sysfs device |
| `WdmInterface` | True for USB adapters |

The patch reports real adapters and real addresses. It does not change any licence check and does not fake values. The DLL reads sysfs through Wine's `\\?\unix\` path prefix, because Wine's API does not expose the bus or the burned-in Wi-Fi address.

The filters in TurboActivate's queries then drop `ROOT\` entries, so Docker bridges and similar devices do not reach the fingerprint.

## Install

Needs `git`, `gcc`, `make`, `flex`, `bison` and the x86_64 mingw compiler (`mingw64-gcc` on Fedora, `gcc-mingw-w64-x86-64` on Debian or Ubuntu). `--runner` is the runner's root directory or its `wine` binary, and the script finds `x86_64-windows/wbemprox.dll` under `usr/lib64/wine`, `usr/lib/wine`, `lib64/wine` or `lib/wine`. Runners in `/usr` need a user who can write there.

```sh
./netadapter-fix install --runner <runner> [--repo <git URL>] [--ref <tag|branch|commit>] [--extra-patch <file|URL>]
./netadapter-fix verify  --runner <runner> --prefix <prefix>
./netadapter-fix status  --runner <runner>
```

The default source is the `wine-11.21` tag from `gitlab.winehq.org`. Use a source that matches your runner. The script fetches it into `~/.cache/wine-msft-netadapter`, applies the patch, configures with `--enable-archs=x86_64`, builds only `wbemprox.dll` and the tools it needs, backs up the original DLL by its hash, and replaces the DLL atomically. It is safe to rerun. Backups are named after their hash and are never overwritten. The script keeps its state in `<wine lib dir>/wbemprox-msft-netadapter/`.

Start a new Wine process after installing. Running processes keep the old DLL mapped. You do not need to touch the prefix, because Wine loads the builtin from the runner and ignores the prefix's `system32/wbem/wbemprox.dll` copy.

`verify` compiles a small client (`netadapter_query.c`), runs the two queries in your prefix and prints the rows with the addresses masked. Pass `--full` to print full addresses, and do not publish that output.

For the `patrickl/wine-staging-dev` COPR build `wine-11.21-101` (giang17's fork plus wine-staging), this command reproduces that build's `wbemprox`:

```sh
./netadapter-fix install --runner ~/.local/share/vstbridge/runners/giang17 \
  --repo https://github.com/giang17/wine.git \
  --ref 2f932280e034f018d118dc0303ff98df5f148701 \
  --extra-patch https://raw.githubusercontent.com/wine-staging/wine-staging/v11.21/patches/wbemdisp-ISWbemObject-Invoke/0003-wbemprox-Support-VT_BYREF-in-to_longlong.patch
```

## Limits and warnings

**Activation is tied to the values this DLL reports.** TurboActivate fingerprints the machine from them. Deactivate under Menu > License Info (or the product's own deactivation) before you change Wine, the runner, the network hardware, or remove this DLL, because a changed fingerprint can count as a different computer and use up another of your activations.

- The class has only the seven columns above. A program that asks for other `MSFT_NetAdapter` properties gets `WBEM_E_NOT_FOUND`, and a WHERE clause on a missing column fails the query.
- Wine's adapter GUID is derived from the kernel interface index. If interface indexes change between boots, `DeviceID` changes too. That normally needs a hardware or driver-order change.
- A burned-in address is read only for Wi-Fi. If you override the address of a wired adapter, `PermanentAddress` is that override, not the hardware's. `ip -d link` shows `permaddr` when the two differ.
- `PNPDeviceID` holds the real vendor and device IDs but no Windows instance suffix. It ends with the Linux interface name, so renaming an interface changes it.
- The patch reads Linux sysfs, so it is Linux-only. Without sysfs every adapter becomes virtual and the queries return no rows.
- Only the 64-bit DLL is built. A 32-bit program in a WoW64 runner still loads the unpatched `i386-windows` DLL.
- Other MSFT and MSNdis classes are still missing. A program might fail at a later step for a different reason, so check for the next error with `WINEDEBUG=+wbemprox`.

## Removing it

Deactivate the licence first, then:

```sh
./netadapter-fix restore --runner <runner>
```

The original DLL returns to its place. The backup stays in `wbemprox-msft-netadapter/`, which you can delete. `restore` refuses when the DLL has changed since the install, unless you pass `--force`. Updating a runner package replaces the DLL. Run `install` again afterwards, because TurboActivate needs the class to read the fingerprint.

## Applying to another Wine or version

The patch applies at the time of writing to `wine-11.21`, to giang17's `d2d1-dcomp-11.21` fork at the commit above and to WineHQ `master` (78e52205d9, November 2026), and the resulting DLLs passed `verify`.

- Use `--ref` with the tag that matches your runner, or `--repo`/`--ref` for a fork. Use `--extra-patch` for any patch your runner's `wbemprox` also carries.
- If the patch does not apply, the changes are small and self-contained: the column array and record struct near `col_networkadapter`, the `fill_msft_netadapter` function and its helpers after `fill_networkadapter`, the `standard_cimv2_builtin_classes` array before `#undef C`, and the `StandardCimv2` line in `builtin_namespaces`. Older Wine needs `heap_alloc`/`heap_strdupW` in place of `malloc`/`wcsdup` and `aa->u.s.IfIndex` in place of `aa->IfIndex`.
- A runner that places DLLs somewhere else needs the DLL copied to its `x86_64-windows` directory by hand. A DLL built without Wine's `--wine-builtin` signature is ignored by the loader.

## Licence and provenance

The patch is derived from Wine and is LGPL-2.1-or-later, like the file it modifies. Publish it with its base (the commit named in its header) if you distribute a built DLL.

**The patch was written with LLM assistance.** WineHQ excludes that code: its [Clean-Room Guidelines](https://gitlab.winehq.org/wine/wine/-/wikis/Clean-Room-Guidelines) say "Don't use an LLM tool to generate code. There's no guarantee that the training material of that LLM respects our Clean Room Guidelines, or that its output is compatible with the LGPL." Do not submit it to WineHQ. An implementation for upstream has to be written separately under those guidelines.

This folder has no affiliation with wyDay, Bogren Digital or WineHQ.
