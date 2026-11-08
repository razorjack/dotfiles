# vstbridge

`vstbridge` runs Windows plugins in native Linux Bitwig Studio, REAPER and Renoise through Wine and yabridge on Fedora KDE. Each vendor gets its own Wine prefix. Each prefix is bound to a runner profile: a Wine binary, its matching `wineserver`, a graphics policy and extra environment. A generated `WINELOADER` dispatcher gives every bridged plugin the runner that its prefix was set up with, so installers, `winecfg`, winetricks, diagnostics and the DAW all use the same Wine.

On Linux, yadm links `~/.local/bin/vstbridge` to the tracked alternate `~/.local/bin/vstbridge##os.Linux`, which is a relative symlink to this script, so `vstbridge` is on `PATH`. On macOS the plain name does not exist.

Research baseline: 2026-11-05. The evidence ledger at the end records what each default rests on.

## Commands to run next

```sh
vstbridge setup --plan                  # review; nothing changes
vstbridge config init                   # then edit ~/.config/vstbridge/vstbridge.conf
vstbridge setup                         # missing packages, new prefixes, dispatcher
# download the two CI artifacts of yabridge master f1fc21e6 (see "Bridge")
vstbridge bridge install <yabridge archive> <yabridgectl archive> --origin 'upstream CI, master f1fc21e6'
vstbridge bridge use 5.1.1-59-gf1fc21e6
vstbridge desktop install               # optional menu entries "Bitwig Studio (vstbridge)" etc.
vstbridge doctor
```

Then install plugins with `vstbridge install <prefix> <installer.exe>` or `vstbridge run <prefix> <manager.exe>`, and start the DAW with `vstbridge launch bitwig` (or the menu entry). In KDE System Settings > Display Configuration, keep the 150% scale and set "Legacy applications (X11)" to "Apply scaling themselves".

Machines that ran the previous vstbridge: follow "Migrating from the previous vstbridge" first.

## Installing products

This section records the steps that a fresh Linux install needs. Run one installer at a time.

Bitwig Studio comes from `~/.config/razorjack/install_bitwig`, which repackages Bitwig's `.deb` as an RPM. Start it with `vstbridge launch bitwig`. New plugins can be hard to find in its browser: most FabFilter plugins are effects, so they appear on an audio effect slot, and they are indexed without the vendor name (`Pro-Q 3`). Search by product name.

| Prefix | Download | Install | Notes |
|---|---|---|---|
| `fabfilter` | fabfilter.com/download; earlier major versions are under Additional Downloads | `vstbridge install fabfilter <installer>` | Install only the versions your license covers. Skip Pro Tools. Skip VST2 unless existing projects use it. Leave the VST3 and CLAP folders at their defaults |
| `kilohearts` | kilohearts.com/download | `vstbridge run kilohearts <Kilohearts Installer.exe>`, then **iLok License Support** into the same prefix, then `vstbridge sync` | Without License Support, Phase Plant loads and its interface works, but it makes no sound |
| `arturia` | Software Center from arturia.com/support/downloads-manuals | `vstbridge run arturia <installer>`, then start the Software Center (below) and install Pigments | Run `vstbridge sync` after the products finish installing |
| `xln` | xlnaudio.com/install | Unpack the giang17 runner and enable its profile (below), run `vstbridge setup`, then `vstbridge run xln <XLN Online Installer.exe>` and install XO from it | Needs the `giang17` profile: on Fedora Wine 11.20, version 5.0.2 never shows a window (see the evidence ledger). Run `vstbridge sync` after the products finish installing |
| `neuraldsp` | neuraldsp.com/downloads; iLok License Support from ilok.com | `vstbridge install neuraldsp <License Support>`, then the plugin installer | Activate through iLok License Manager |
| `minimalaudio` | Products & Downloads in your Minimal Audio account | Unpack the giang17 runner and enable its profile (below), run `vstbridge setup`, then `vstbridge install minimalaudio <installer> /COMPONENTS=vst3_64` | No public installer link. The installer reports success and installs only presets when no plugin component is selected, and `/COMPONENTS` selects the VST3 one. Uses the `giang17` profile because its PATCHES.md lists Minimal Hub and Minimal Audio's JUCE 8.0.13 plugins as needing that build's fixes |
| `bogren` | Your Bogren Digital account | Unpack the giang17 runner and enable its profile (below), run `fixes/wine-turboactivate-error-28/netadapter-fix install`, run `vstbridge setup`, then `vstbridge install bogren <installer>` | No public installer link. Needs the `giang17` profile and the patched `wbemprox.dll`; see the vendor notes |
| `ni` | Native Access through the ni-wine helper | `vstbridge ni setup`, `vstbridge ni native-access` | Set the content location to a Linux folder through `Z:` before installing libraries |

- **Run `vstbridge sync` after every installer that downloads products.** The Kilohearts Installer exits and relaunches itself from `C:\ProgramData\Kilohearts`, so the sync that `vstbridge run` performs happens before any plugin exists. The Arturia and XLN managers also install products after the program starts.
- **Starting an installed manager later.** Pass the program to `vstbridge run`. For the Arturia Software Center:

  ```sh
  vstbridge run arturia ~/.vstbridge/prefixes/arturia/drive_c/"Program Files (x86)"/Arturia/"Arturia Software Center"/"Arturia Software Center.exe"
  ```

  The Kilohearts Installer is at `drive_c/ProgramData/Kilohearts/Kilohearts Installer.exe` in its prefix. Wine creates no Linux menu entries for these programs, because winemenubuilder is disabled.
- **iLok License Support runs as a service in its prefix** (`LDSvc.exe`). It keeps that prefix's wineserver alive, so vstbridge's bounded waits in `kilohearts` and `neuraldsp` can report that Wine is still running. That report is expected.
- **Sample libraries for XO.** Every prefix maps `Z:` to `/`, so add Linux folders as `Z:\home\<user>\...`. Keep NI libraries outside `~/.wine-ni`: Wine's file dialogs hide dot folders, and the libraries then survive a prefix rebuild.
- **Realtime limits.** Apply the fix that `doctor` prints, then reboot.
- **giang17 runner.** The `xln` prefix uses Wine from COPR `patrickl/wine-staging-dev`, unpacked into its own directory so that Fedora's `/usr/bin/wine` and every other prefix stay unchanged. No sudo is needed, and no RPM scriptlet runs. The symlinks reuse Fedora's Mono and Gecko packages, which avoids a download prompt during `wineboot -i`, so check that their versions still match when you update the runner:

  ```sh
  T=~/.local/share/vstbridge/runners/giang17 D=$(mktemp -d)
  C=https://download.copr.fedorainfracloud.org/results/patrickl/wine-staging-dev
  dnf download --repofrompath=giang,$C/fedora-$(rpm -E %fedora)-x86_64/ --repo=giang --destdir=$D \
    wine-core wine-common wine-filesystem wine-pulseaudio wine-alsa wine-cms wine-ldap 'wine-*winefonts'
  curl -fsSL -o $D/key.gpg $C/pubkey.gpg
  mkdir $D/db && rpm --dbpath $D/db --initdb && rpm --dbpath $D/db --import $D/key.gpg
  rpm --dbpath $D/db -K $D/*.rpm
  mkdir -p $T && cd $T && for f in $D/*.rpm; do rpm2cpio $f | cpio -idm --quiet; done
  for a in mono gecko; do rmdir $T/usr/share/wine/$a; ln -s /usr/share/wine/$a $T/usr/share/wine/$a; done
  ```

  Then add `[profile giang17]` from the commented template in `vstbridge.conf`, set `evidence`, and set `profile = giang17` under `[prefix xln]`. A prefix that was created with another profile is refused, so point `path` at a new directory or use `vstbridge migrate`. Updating this runner replaces the patched `wbemprox.dll` that Bogren activation needs, so run `fixes/wine-turboactivate-error-28/netadapter-fix install` again afterwards.

## Architecture

- **Runner profiles.** `baseline` is Fedora's `wine` package, which Fedora builds with the wine-staging patchset and new WoW64. `ni-modern` uses the same binary for the prefix that the ni-wine helper owns. Optional fallbacks (`giang17`, `legacy`, `dxvk`) are commented out in the default configuration. A fallback profile must record `evidence`, and `config check` rejects it otherwise.
- **Prefix identity.** `vstbridge` initializes only prefixes that do not exist and writes `.vstbridge-prefix` (profile, runner, runner version) into the prefix. Commands refuse a prefix whose marker disagrees with the configuration. A prefix created elsewhere, or by the previous vstbridge, is adopted only with `vstbridge migrate <prefix>`.
- **Dispatcher.** `~/.local/share/vstbridge/wineloader` is regenerated from `vstbridge.conf` by every command except `doctor`. yabridge resolves each plugin's prefix, sets `WINEPREFIX`, and runs the dispatcher as `WINELOADER`. The dispatcher looks up the prefix, exports `WINESERVER` for the paired `wineserver`, applies the prefix's esync policy and profile environment, removes `WAYLAND_DISPLAY`, requires `DISPLAY`, and replaces itself with the runner. Wine therefore always uses its X11 driver through XWayland. An unlisted prefix follows `unknown_prefix`: `system` runs the plain `wine` from `PATH` without the managed environment, and `fail` refuses with exit status 127. `--version` without a managed prefix reports the default profile's runner, because yabridge and yabridgectl probe the Wine version that way.
- **Launch.** `vstbridge launch <bitwig|reaper|renoise> [-- args...]` resolves the native executable (Flatpak exports are skipped), syncs appearance, removes any `WINEPREFIX` from the environment, exports `WINELOADER`, and replaces itself with the DAW. Arguments pass through unchanged. Nothing else in the desktop session gets `WINELOADER`, so unrelated Wine programs are unaffected. `vstbridge desktop install` writes `~/.local/share/applications/vstbridge-<daw>.desktop`. It never touches system desktop files, and it never overwrites a file that lacks `X-Vstbridge-Managed=true`.
- **Bridge.** yabridge's native libraries, `yabridge-host.exe` and `yabridgectl` are installed together into `~/.local/share/vstbridge/bridges/<id>/` with an `ORIGIN` file. `~/.local/share/yabridge` is a symlink to the active build. Only one build is active at a time, because a prefix does not isolate yabridge versions. `bridge use` switches the symlink, keeps the old build, and runs `yabridgectl sync` so the chainloaders in `~/.vst*/yabridge` and `~/.clap/yabridge` match the new build.
- **Exit status.** `install`, `run` and `iso` return the program's status. They return 130 when cancelled, and 3 when the program succeeded but finalization failed. Finalization always runs: a bounded `wineserver -w`, font repair if needed, and `yabridgectl sync`. Each finalization failure is reported separately. A wait that times out names the prefix and operation and leaves the processes running. NTKDaemon, PACE services and a running DAW are expected causes. vstbridge never kills Wine processes.

## Configuration

`~/.config/vstbridge/vstbridge.conf` (or `$XDG_CONFIG_HOME/vstbridge/vstbridge.conf`). Without the file, the built-in defaults apply. `vstbridge config show` prints them, `config init` writes them, and `config check [file]` validates a file. Comments are whole lines starting with `#`. Keys marked "list" may repeat.

| Section | Key | Meaning |
|---|---|---|
| `[general]` | `unknown_prefix` | `system` (default) or `fail`: dispatcher behaviour for unlisted prefixes |
| | `new_prefix_dpi` | DPI written into prefixes that vstbridge creates; default 144 (96 × 1.5) |
| | `theme` | default theme policy: `auto`, `dark`, `light`, `keep` |
| | `vst2` (list) | VST2 directories relative to `drive_c`, registered only when they exist |
| `[bridge]` | `source` | `local` (built by `bridge install`) or `system` (a packaged yabridge in `/usr`) |
| | `pin` | expected build id, e.g. `5.1.1-59-gf1fc21e6` |
| `[profile NAME]` | `runner` | absolute path of the `wine` binary |
| | `wineserver` | defaults to `wineserver` next to the runner |
| | `graphics` | `wined3d`, `dxvk` or `giang17` |
| | `origin`, `evidence` | provenance; `evidence` is required for `dxvk`, `giang17` or a `bridge` requirement |
| | `bridge` | active bridge id prefix this profile needs, e.g. `5.1.1` |
| | `env` (list) | `NAME=value` exported for this runner (not `WINEPREFIX`, `WINELOADER`, `WINESERVER`) |
| | `font_helper`, `font_helper_sha256` | giang17 only: reviewed `wine-font-setup.sh` and its pinned hash |
| `[prefix NAME]` | `path`, `profile` | prefix location and runner profile |
| | `backend` | `vstbridge` (default) or `ni-wine` (the helper creates and maintains the prefix) |
| | `dpi` | absent: 144 at creation, never changed later; a number: enforced on apply; `keep`: never written |
| | `theme` | overrides `[general] theme` |
| | `esync` | `inherit` (default), `off` (exports `WINEESYNC=0`), `on` |
| | `vst2` (list) | extra VST2 directories for this prefix |
| | `settle` | seconds for the bounded `wineserver -w` |
| | `ni_scale` | ni-wine only: `NI_WINE_SCALE` |
| `[daw NAME]` | `exec` | executable for `bitwig`, `reaper` or `renoise` when the built-in search misses it |
| `[yabridge]` | `rule` (list) | `<vst2\|vst3\|clap> \| <glob> \| <option> = <value>` |
| `[validation]` | any | `<product>/<host> = pending \| reported <source> \| observed <date> <note>`; copied into `manifest` |

### yabridge.toml

`sync` writes `yabridge.toml` in `~/.vst/yabridge`, `~/.vst3/yabridge` and `~/.clap/yabridge`. vstbridge owns only the block between its markers, which it generates from `[yabridge]` rules, and the rest of the file is preserved. yabridge matches section names as case-sensitive globs against the bridged file's path relative to the TOML file. `*` does not cross `/`, a pattern that matches a leading directory covers its contents, and only the first matching section applies. glibc `fnmatch` has no `{a,b}` alternation, and a TOML table header cannot be an array, so a section must name one pattern. The previous template's `["*Nameless*", "*Fortin*", ...]` example was invalid for both reasons. An unmodified previous template is replaced on `sync` and saved as `yabridge.toml.vstbridge-v1`. If you edited that template, `doctor` asks you to delete the old example. `editor_xembed` and `editor_coordinate_hack` were removed from yabridge's development builds, and `config check` rejects them.

No rule is active by default. `editor_disable_host_scaling` is a per-plugin remedy for an editor that is demonstrably double-scaled or cropped at 150%. `editor_force_dnd` applies to REAPER only.

## HiDPI, fonts and theme

- **Scaling layers.** KDE stays at 150%. XWayland clients scale themselves, and new prefixes start at 144 DPI. Bitwig's interface scale and each plugin's zoom are separate controls. Change one at a time and compare against the acceptance checks; do not multiply them. vstbridge sets no global `QT_SCALE_FACTOR`, `GDK_SCALE` or similar. A 200% desktop comparison is only a diagnostic.
- **Fonts.** Each prefix gets DejaVu Sans (regular, bold) and Noto Sans Symbols2 copied from Fedora packages into `C:\windows\Fonts`, registered under `...\CurrentVersion\Fonts`, and linked first in the `Tahoma` and `DejaVu Sans` FontLink chains. Existing chain entries stay after them. `Arial`, `Times New Roman` and `Courier New` are substituted with Liberation fonts only when the genuine font is absent and no substitute exists. Copying skips a destination that already is, or equals, the source. Wine rewrites `SystemLink` when the code page changes; the giang17 branch has carried the fallbacks in its own defaults since 2026-09-02, and ordinary Wine has not. vstbridge therefore checks the registry and files after each install or run and repairs only what is missing. `fix-fonts` does the same on demand, and with no prefixes it is a successful no-op. A missing host font fails with the package name and is never reported as complete.
- **Segoe UI** is never downloaded. `vstbridge fonts import-segoe <prefix> <dir>` copies only `segoeui*.ttf`/`segui*.ttf` from a Windows font directory you supply. `--ui-font` also sets six system UI fonts (`WindowMetrics`) to Segoe UI 9 pt at the prefix's DPI, after exporting the previous values to `drive_c/vstbridge/windowmetrics.reg`. `appearance restore` reverts both. Fonts embedded in plugins are never substituted. MS Core Fonts are proprietary downloads, so vstbridge does not fetch them. `vstbridge tricks <prefix> corefonts` is available if you choose to install them.
- **Theme.** With `theme = auto`, vstbridge reads `org.freedesktop.appearance color-scheme` from the desktop portal. It uses `ReadOne` when the Settings interface reports version 2 or later, and otherwise the deprecated `Read`, whose value has two variant layers. 1 is dark, and 2 is light. 0, unknown values, or no portal leave the prefix unchanged. Dark and light set `AppsUseLightTheme` and `SystemUsesLightTheme` in `HKCU\...\Themes\Personalize`. The original values are saved once in `<prefix>/.vstbridge-appearance` before the first change, and `appearance restore` puts them back. These flags do not recolor Win32 controls. Wine's visual style (Aero since Wine 11.3) and classic colors are left alone; an active style can overwrite `HKCU\Control Panel\Colors`. Plugins with their own skins (Pigments' Classic/Light, XO, Rift) keep their own theme setting. Changes apply at `appearance apply`, `launch`, `install`, `run` and `ni native-access`, and reach plugins only after the DAW restarts.

## Vendors

- **FabFilter.** Use VST3 for consistency across hosts. VST2 is a selectable fallback for a reproduced scaling problem. Keep each project on the format it was saved with, because a format change changes the plugin identity in the project. VST2 instances need a shared process for inter-instance features: `rule = vst2 | FabFilter* | group = "fabfilter"`. Do not group unrelated plugins.
- **Kilohearts.** The prefix has `esync = off`; yabridge documents file-descriptor leaks with esync. Fedora's Wine 11.x and current staging have no esync patchset, so the setting matters only for runners that implement it. The Kilohearts Installer stores content and licensing in `C:\ProgramData\Kilohearts`, so keep the whole prefix. Install iLok License Support into this prefix as well: without it, Phase Plant makes no sound. Formats are VST2/VST3, without CLAP.
- **Arturia.** Run Arturia Software Center (`vstbridge run arturia ...`) and install Pigments into the same prefix. Pigments resizes from 50 to 200% and has a manual Classic (dark) / Light theme.
- **Minimal Audio.** Rift and Morph EQ are validated separately. On the `giang17` profile at 144 DPI they work, but their windows open too large; about 80% in the plugin's own size setting looks normal (locally observed 2026-11-08). The 2025 report of both working used Wine 9.21 with yabridge 5.1.1. Do not install DXVK reflexively; Rift has its own OpenGL setting.
- **XLN Audio.** Validate the XLN Online Installer separately from XO. XO's 50-200% scaling and its OpenGL toggle need testing. XLN states that on Windows only the first open instance gets OpenGL acceleration.
- **Native Instruments (Komplete 14).** The `ni` prefix uses `backend = ni-wine`: install the helper (`sudo dnf copr enable selimbucher/ni-wine && sudo dnf install ni-wine`, after reviewing the COPR), then run `vstbridge ni setup` and `vstbridge ni native-access`. vstbridge passes `NI_WINE_PREFIX`, `WINE` (the profile's runner) and `WINESERVER`. It passes `NI_WINE_SCALE=1.5` only after confirming that the installed helper parses the value as a float; ni-wine 2.5.0 passes it to Native Access as `--force-device-scale-factor`. vstbridge refuses to start `Native Access.exe` directly and refuses an `NI_WINE_PREFIX` that differs from the configuration. Install the products you own; do not use "Update all". Keep Kontakt 7 with library versions that still load in Kontakt 7, because updated libraries can require Kontakt 8. NI's suggestion of the free Kontakt 8 Player is a separate decision. Ozone 10 Standard installs and activates through Native Access 2 (Library > Available), not iZotope Product Portal. Plugin Alliance extras use their own redemption. `ni-postinstall` is deprecated: with ni-wine it runs `ni doctor`, and NA 1.14.1 is only available as the commented `[prefix ni-legacy]` fallback. For an installer image, `vstbridge iso <prefix> <image>` lists the installers, and `--exe <path>` runs one. The image is attached read-only through udisks, with a UDF retry, and is detached afterwards, including on failure or Ctrl-C.
- **Neural DSP (Fortin Nameless Suite / Suite X).** iLok without a dongle. Install iLok License Manager into the `neuraldsp` prefix and activate the licence to this computer; the 14-day trial is added to the iLok account. Check installation, trial audio, and licensed audio after a cold restart separately. Copying a prefix does not reliably keep an activation identity. Deactivate before rebuilding. Newer PACE installer workarounds must be reviewed individually before use. The previous REAPER `disable_pipes`/`editor_force_dnd` workaround cited yabridge #432; that issue was fixed by downgrading Wine and does not name the product, so the workaround is removed.
- **Bogren Digital MLC S_Zero 93 / S_Zero 100.** Wine compatibility is unverified. Activate with the serial through the plugin's "Activate License"; Bogren allows three devices and deactivation under Menu > License Info. The plugins are JUCE with Direct2D and need the `giang17` profile: on Fedora Wine 11.20 the activation screen ignored clicks. They license through TurboActivate. On giang17 Wine 11.21 they make sound, but a valid serial returns error 28 (`TA_E_ENABLE_NETWORK_ADAPTERS`), and a mistyped serial returns error 1, which is a local format check. In a `WINEDEBUG=+wbemprox` run of a failed activation, the program queries `MSFT_NetAdapter` in `root\StandardCimv2` twice and makes no other WMI query. Wine's `wbemprox` has no such class and returns an empty result without an error. A patched `wbemprox.dll` that implements that class in the giang17 runner made activation succeed for S_Zero 100 (locally observed 2026-11-08). The patch, build script and instructions are in `fixes/wine-turboactivate-error-28/` next to this file. Activation is tied to the adapter values that DLL reports, so deactivate under Menu > License Info before changing Wine, the runner or the DLL.
- **bx_crispytuner (K14 editions that include it).** If DXVK is needed, use a separate prefix with a `dxvk` profile and DXVK 3.1 or later. The 3.0 crash was confirmed fixed in 3.1 (dxvk#5739). Never install DXVK into a `giang17` prefix.

## Fallback profiles

Select a fallback only for a documented or reproduced problem, and put the link or reproduction in `evidence`.

- **giang17** (`graphics = giang17`). This is Wine with wine-staging plus the giang17 DirectComposition, Direct2D, DirectWrite and winex11 patches, from COPR `patrickl/wine-staging-dev` (the successor of the discontinued `wine-11.8-vstgui-juce8`, which has only a Fedora 44 chroot). Use it for a reproduced JUCE 8, VSTGUI or installer problem, such as the Native Access 3 or Minimal Hub installer routes described in its PATCHES.md. Before enabling it, query the COPR's repository metadata and review what it ships. Enabling that COPR replaces Fedora's `/usr/bin/wine` for every profile. An unpacked copy in its own directory avoids that (see "giang17 runner" under Installing products). Never install Fedora 44 packages on Fedora 45. A version string containing `11.` does not prove the patchset is present. Its display fixes target winex11, which the dispatcher always selects. DXVK must stay out (`tricks` refuses it, and `doctor` fails on native D3D/DXGI DLLs or overrides). The pinned font helper, with `font_helper_sha256`, runs only for this profile with `--no-mscore`.
- **legacy.** Wine 9.21 with official yabridge 5.1.1 is a recovery pair. yabridge is global, so this also needs `vstbridge bridge use 5.1.1`, which affects every prefix. `doctor` fails when a profile in use needs a different bridge than the active one.
- **dxvk.** DXVK in dedicated prefixes only, and `tricks <prefix> dxvk` works only in those. Fedora's `wine` Recommends `wine-dxvk`, whose scriptlet switches the system's 64-bit `d3d8`, `d3d9`, `d3d10core`, `d3d11` and `dxgi` to DXVK through `alternatives`, so every prefix gets DXVK. `setup` installs `wine` with `--exclude=wine-dxvk*`. On a machine that already has it, remove it with `sudo dnf remove 'wine-dxvk*'`, then run `vstbridge run <prefix> wineboot -u` for each prefix and check again with `doctor`. `doctor` identifies Wine's own DLLs by their `Wine builtin DLL`/`Wine placeholder DLL` signature, and Fedora builds DXVK with that same signature, so `doctor` also checks each DLL for a `DXVK` string and asks `alternatives` which implementation the system selects. It also reports native overrides, including per-application ones. Its repair instructions rename DLLs and remove overrides, and they never delete prefixes.

## Bridge

Fedora 45 has no `yabridge` package. Official release 5.1.1 (2024-11-04) does not work with Wine 9.22 or later. The pin is upstream master `f1fc21e668e18a324915010912700727c8626619` (2026-11-01). Its CI artifacts are named `yabridge-5.1.1-59-gf1fc21e6` and `yabridgectl-5.1.1-59-gf1fc21e6`. GitHub artifacts expire, so keep the archives. `bridge install` reads the build id from `libyabridge-vst3.so`. It refuses an unpinned build unless you pass `--accept-unpinned` with `--origin`, and it never overwrites an installed build. The community `5.1.2-alpha2` (Schroedingers-Cat fork) is not an upstream release. Use it only as an unpinned, recorded choice. `[bridge] source = system` uses a packaged build (for example from a COPR) instead.

`doctor` fails when more than one installation is visible (local, `/usr`, `/usr/local`, or `yabridge-host.exe` elsewhere on `PATH`), because the chainloader prefers `PATH`. It also counts generated wrappers whose chainloader differs from the active build.

`yabridgectl sync` verifies the build by starting `yabridge-host.exe` in `$WINEPREFIX`. Without `WINEPREFIX`, Wine would create a default prefix in `~/.wine`. vstbridge therefore runs the verification in the first ready managed prefix, and passes `--no-verify` when no managed prefix is ready yet.

Two limitations of the pinned build were observed locally:

- **Non-ASCII prefix paths.** VST3 plugins from a prefix whose path contains a non-ASCII character (for example `ü`) fail to load: the Wine host reports `wstring_convert::from_bytes`, and yabridge's log prints the path in Latin-1. CLAP plugins from the same prefix load and process audio. `setup` warns when it creates such a prefix, and `doctor` warns for each one. Keep prefix paths ASCII.
- **One wrapper per relative path.** yabridgectl names each wrapper after the plugin's path relative to its registered directory. When two prefixes contain the same relative path, yabridgectl bridges only the copy from the directory listed first in `yabridgectl list`, and it reports nothing. `doctor` warns about each such plugin and names both prefixes. Install a plugin into one prefix only.

## Diagnostics

- `doctor` is read-only and prints pass, warn, FAIL or unknown for each check. Its exit status is 1 on any failure. It checks the session (`DISPLAY`, KDE's `XwaylandClientsScale`, a stray `WINEPREFIX`), each runner's `--version` and paired `wineserver --version`, and RPM origin. It checks bridge completeness, the pin, shadowing copies, `yabridgectl status` and wrapper freshness, as well as whether the dispatcher is current. Per prefix, it checks the marker and profile, architecture, Windows version, Wine graphics driver, DPI, theme flags, D3D/DXGI DLLs and overrides, fonts, and the effective esync value (`WINEESYNC=0` is disabled). It also validates each `yabridge.toml` and resolves the DAW executables. A Flatpak DAW is reported, never failed. `doctor` does not show that activation or audio works.
- **Realtime limits.** yabridge locks its shared audio buffers into memory and gives its audio threads realtime priority. Fedora's `25-pw-rlimits.conf` grants limits only to the `pipewire` group, and its 4 MiB memlock is too low, so without changes yabridge prints "Low memory locking limit detected" for every plugin. `doctor` warns, and `setup` lists the fix as a manual step: `/etc/security/limits.d/95-audio.conf` with `@audio - memlock unlimited` and `@audio - rtprio 95`, plus membership in the `audio` group. The limits apply after a reboot, because the systemd user manager reads them only when it starts. Fedora's `realtime-setup` package is an alternative, but it pulls in tuned and RT-kernel tuning.
- **Logs.** `install`, `run`, `iso`, `migrate`, `winecfg`, `tricks` and prefix creation write Wine's output to `~/.local/state/vstbridge/logs/<prefix>-<operation>-<time>-<pid>.log`. The terminal shows the log path, and on failure the last 15 lines. Wine's `fixme:` lines and Mesa's EGL warnings on NVIDIA's proprietary driver are expected there. `VSTBRIDGE_VERBOSE=1` streams the output to the terminal instead.
- **Registry files.** wineserver writes `user.reg` and `system.reg` only when it exits, about 3 s after its last client. `doctor`, `manifest` and the theme and DPI logic read those files directly. Every command that started Wine in a prefix therefore waits for that prefix's wineserver before it returns, for at most the prefix's `settle` time (default 15 s), and says so if Wine is still running there.
- **`graphics reset <prefix...> [--plan]`** returns a prefix to Wine's own D3D/DXGI. It refuses while the system still selects DXVK through `alternatives`. It renames DXVK and other non-Wine `d3d*`/`dxgi` DLLs in `system32` and `syswow64` to `<name>.vstbridge-<timestamp>`, deletes native global overrides for those DLLs after saving them to `<prefix>/.vstbridge-graphics-overrides`, warns about per-application overrides, and runs `wineboot -u`. Fedora's `wine-core` ships no 64-bit `d3d8.dll`, so a `d3d8.dll` that `wine-dxvk` once placed in `system32` stays there after `wine-dxvk` is removed. `graphics reset` handles that case. To undo, rename the files back.
- `manifest [--write]` records the OS, session, color scheme, runners (path, version, package and vendor, `wineserver`, graphics, origin, evidence), the bridge `ORIGIN`, and each prefix's architecture, Windows build, DPI, theme, DLL overrides and marker. It also lists the VST3 bundles with their `moduleinfo.json` versions, the DAW executables, and the `[validation]` entries. It contains no registry dumps, serials or tokens.

## Migrating from the previous vstbridge

The previous version installed `wine` and `yabridge` from COPR `patrickl/wine-11.8-vstgui-juce8` and created unmarked prefixes under `~/.vstbridge/prefixes/`. Do these steps manually; vstbridge does not change packages or repositories on its own beyond installing missing Fedora packages.

1. `vstbridge doctor` and `vstbridge manifest --write` record the current state.
2. Decide on the runner. To return to Fedora's Wine: `sudo dnf copr disable patrickl/wine-11.8-vstgui-juce8`, then `sudo dnf remove yabridge` (otherwise `/usr/bin/yabridge-host.exe` shadows the local bridge), then `sudo dnf distro-sync wine`. To keep the giang17 build, move to `patrickl/wine-staging-dev` after reviewing it. Then enable the `giang17` profile with evidence, and point the affected prefixes at it.
3. `vstbridge config init` and review the file.
4. Install and activate the pinned bridge (see "Commands to run next").
5. For each existing prefix, run `vstbridge migrate <prefix> --plan`, then `vstbridge migrate <prefix>`. Migration backs up the prefix's `*.reg` files and marker to `<prefix>/.vstbridge-backup/<timestamp>/`, writes the marker, and runs `wineboot -u` with the configured runner. The prefix keeps its DPI. From the next `setup` or `launch` on, its theme flags follow the theme policy, and the originals are saved for `appearance restore`. Run `doctor` afterwards to check for DXVK left behind.
6. Native Instruments moves to `~/.wine-ni` under ni-wine. The old NA1 prefix `~/.vstbridge/prefixes/ni` stays untouched and unregistered. Install the products you own again through Native Access 2; do not copy activation data between prefixes. To keep NA1 as a fallback, uncomment `[prefix ni-legacy]` together with a `legacy` profile and its evidence.
7. `vstbridge sync`, then `vstbridge desktop install`.

Rollback:

- Script: `yadm log --follow -- .config/razorjack/vstbridge/vstbridge`, then `yadm checkout <commit> -- .config/razorjack/vstbridge/vstbridge`. Commits from before the script moved into this folder have it at `.config/razorjack/vstbridge`.
- Prefix: close all programs using it, run `cp -p <prefix>/.vstbridge-backup/<timestamp>/*.reg <prefix>/`, and restore the backed-up `.vstbridge-prefix` (or delete it for a prefix that had none).
- Bridge: `vstbridge bridge use <previous id>`. A pre-existing `~/.local/share/yabridge` was moved to `~/.local/share/vstbridge/bridges/preexisting-<timestamp>`; remove the symlink and move that directory back. Then run `yabridgectl sync`.
- Appearance: `vstbridge appearance restore [prefix...]`. Menu entries: `vstbridge desktop remove`.
- yabridge.toml: copy back `yabridge.toml.vstbridge-v1`.

## Evidence ledger (checked 2026-11-05)

"Upstream" means the vendor or project documents it. "Reported" means a third party reported it for that exact product. "Unverified" means no exact report was found. Nothing here was observed on this machine with real plugins.

| Claim | Basis |
|---|---|
| Fedora 45 ships `wine` 11.20-1.fc45 with the wine-staging patchset and new WoW64; `wine-core` owns `wine` and `wineserver`; Fedora has no `yabridge` package | Upstream: packages.fedoraproject.org, `wine.spec` (f45) |
| yabridge 5.1.1 (2024-11-04) does not work with Wine 9.22+; master fixes clicks with Wine 9.22 and later and removed `editor_xembed` and `editor_coordinate_hack` | Upstream: README, CHANGELOG `[Unreleased]` at f1fc21e6 |
| yabridge runs `$WINELOADER` when set; section globs are relative paths matched with `fnmatch`, first match wins | Upstream: README; `src/common/configuration.cpp` |
| Master builds work with Wine 11.11, 11.15 and 11.21 for some users and plugins | Reported: yabridge #409 (2026-06 to 2026-11); not product-specific to this set |
| `patrickl/wine-staging-dev` carries the giang17 patches, has a fedora-45-x86_64 chroot, and is the successor of `wine-11.8-vstgui-juce8` (Fedora 44 only, discontinued) | Upstream: COPR API |
| giang17: keep DXVK out; Wine stays on XWayland while `DISPLAY` is set; FontLink fallback defaults since 2026-09-02 (27d6d102) | Upstream: giang17/wine README, PATCHES.md |
| Kilohearts plugins leak file descriptors under esync | Upstream: yabridge README |
| ni-wine 2.5.0: `NI_WINE_PREFIX`, `WINE`, fractional `NI_WINE_SCALE`; Native Access 2; needs Wine 11 and yabridge development builds | Upstream: selimbucher/native-instruments at 24b6dad (2026-11-02) |
| Komplete's Ozone installs and activates through Native Access | Upstream: NI article 69000879277 |
| NA2 recommended for K14 because some products (Ozone 10) fail on NA1 | Upstream: NI staff, community comment 33534 (2022-09-28); comment 33646 is a user post |
| Updated libraries can require Kontakt 8 | Upstream: NI article 69000879710; NI staff 2026-01-01 |
| Minimal Audio Rift and Morph EQ worked with Wine 9.21 + yabridge 5.1.1 | Reported: yabridge #404 (2025-02-25); current Wine unverified |
| yabridge #432 concerns an unnamed Neural DSP plugin in REAPER, resolved by downgrading Wine | Reported: yabridge #432; not a Nameless test |
| Neural DSP: iLok computer activation without a dongle; 3 activations | Upstream: Neural DSP support pages; iLok Cloud not mentioned |
| Bogren: serial activation in the plugin, 3 devices | Upstream: Bogren help center (vendor-wide); MLC S_Zero under Wine unverified |
| bx_crispytuner crash with DXVK 3.0 fixed in 3.1 | Reported and confirmed: dxvk#5739 (2026-09-05) |
| REAPER's SWELL forces GDK's X11 backend; Bitwig 6.1 links xcb/X11 only; Renoise 3.5.4 requires X.org and lists no CLAP | Upstream WDL source; Bitwig observed locally with `ldd` on 2026-11-05; Renoise release notes |
| Fedora's `wine` Recommends `wine-dxvk` (2.7.1 on Fedora 44); its alternatives (priority 20) select DXVK for 64-bit D3D8-11/DXGI, and the DLLs carry Wine's builtin signature | Locally observed 2026-11-07 (`rpm -q --recommends wine`, `alternatives --display`) |
| Plasma 6.8 has no X11 session; `XwaylandClientsScale` in kdeglobals selects "Apply scaling themselves" | Upstream: KDE announcements, kscreen/KWin sources |
| Wine reads DPI from `HKCU\Control Panel\Desktop\LogPixels`; uxtheme reads `AppsUseLightTheme`/`SystemUsesLightTheme` | Upstream: Wine sources (winecfg, win32u, uxtheme) |
| Portal `ReadOne` since Settings version 2; `color-scheme` 0/1/2 | Upstream: xdg-desktop-portal documentation |
| Fedora's `wine-core` has no 64-bit `d3d8` alternative, and registers its 32-bit `d3d8` under the `wine-dxgi(x86-32)` group; after `wine-dxvk` is removed, `system32/d3d8.dll` in existing prefixes stays DXVK | Locally observed 2026-11-07 (`alternatives --display`, scriptlet warning, `doctor`) |
| `yabridgectl sync` without `--no-verify` starts `yabridge-host.exe` in `$WINEPREFIX`, which creates `~/.wine` when unset | Locally observed 2026-11-07 |
| yabridge 5.1.1-59-gf1fc21e6 with Fedora Wine 11.20: VST3 fails (`wstring_convert::from_bytes`) from a prefix path with `ü`; CLAP works from the same prefix; both work from an ASCII path | Locally observed 2026-11-07 with Airwindows Consolidated (`test_vstbridge_real.py`) |
| yabridgectl keeps one wrapper per relative plugin path across registered directories, without a warning | Locally observed 2026-11-07 |
| Airwindows Consolidated (JUCE 8.0.4, Direct2D) through the pinned bridge and Fedora Wine 11.20: the CLAP editor embeds and renders its first frame at the same size at 96 and 144 DPI; a click reaches Wine (`ButtonPress` in `+event`) but the editor never repaints; `clap_plugin_gui::destroy` never returns, because the plugin's main thread waits on one of its own threads while Wine's `dcomp` composition thread runs. Same result under Xvfb and under headless KWin with Xwayland. Other plugins and the giang17 runner untested | Locally observed 2026-11-07 (`test_vstbridge_real.py`, yabridge debug log, `winedbg` backtraces) |
| Phase Plant (Kilohearts Installer 2.4.6 content) in Bitwig through the pinned bridge: without iLok License Support the interface and parameters work, but there is no sound, and `kiloHearts.log` reports `iLok Error: -4 ... Unable to open pipe`. After installing License Support 5.10.5 into the prefix, it makes sound. Kilohearts effects pass audio with or without it. The test host's default-patch measurement stays at 0.0 either way, so it does not detect this | Locally observed 2026-11-08 |
| XLN Online Installer 5.0.2 (JUCE 8.0.13, Direct2D) on Fedora Wine 11.20: the launcher starts the inner program, whose window stays unmapped at 1x1 with no CPU use or network connections. Same result in a new prefix, on Xvfb, with a Wine virtual desktop, with Windows 7 or 8.1 selected, and with `d2d1`, `dcomp` or `windows.ui` disabled through `WINEDLLOVERRIDES` | Locally observed 2026-11-08 |
| The same installer on giang17 Wine 11.21-101.fc44, unpacked to a scratch directory, in a new prefix with a temporary HOME on the desktop session: the window appears and looks correct, at Wine's default 96 DPI. In the `xln` prefix on this runner, the installer put `XO.vst3` in place and XO worked through the pinned bridge | Locally observed 2026-11-08; XO reported by the user |
| Through vstbridge's dispatcher, the pinned bridge loads Airwindows Consolidated as CLAP (scan, activate, 10,240 frames of audio, finite output) and as VST3 (factory, classes) | Locally observed 2026-11-07 (`test_vstbridge_real.py`) |

## Acceptance matrix

Every cell is pending until you observe it. Record results in `[validation]` (for example `pigments/bitwig = observed 2026-11-12 C1-C12, buffer 128`) so `manifest` carries them.

Checks per product and host:

- C1: plugin scan finds the expected format(s) only once.
- C2: genuine activation survives a cold restart (log out, start the DAW again).
- C3: audio passes and sounds right.
- C4: editor geometry and text at 150%: no double scaling, cropping or blur.
- C5: mouse, keyboard, pointer coordinates, popups, menus and tooltips.
- C6: preset and project recall after reopening the project.
- C7: automation, and sidechain where applicable.
- C8: drag-and-drop and export (XO: sample browsing and audition, export, and drag into the DAW).
- C9: several instances, with several editors open.
- C10: CPU load with the editor open.
- C11: offline render matches realtime.
- C12: a sustained session at your chosen buffer size, without xruns or hangs.

| Product (prefix) | Bitwig Studio | REAPER | Renoise |
|---|---|---|---|
| FabFilter VST3 (fabfilter) | pending | pending | pending |
| FabFilter VST2 fallback, grouped (fabfilter) | pending | pending | pending |
| Kilohearts Phase Plant (kilohearts) | pending | pending | pending |
| Kilohearts effects (kilohearts) | pending | pending | pending |
| Arturia Pigments (arturia) | pending | pending | pending |
| Minimal Audio Rift (minimalaudio) | pending | pending | pending |
| Minimal Audio Morph EQ (minimalaudio) | pending | pending | pending |
| XLN Audio XO (xln) | pending | pending | pending |
| Kontakt 7 + owned K14 libraries (ni) | pending | pending | pending |
| Guitar Rig 6 Pro (ni) | pending | pending | pending |
| Ozone 10 Standard, if in the edition (ni) | pending | pending | pending |
| Other owned K14 instruments and effects, each (ni) | pending | pending | pending |
| Plugin Alliance K14 extras, if redeemed (own prefix) | pending | pending | pending |
| bx_crispytuner, if owned (dxvk profile) | pending | pending | pending |
| Neural DSP Fortin Nameless Suite (X) (neuraldsp) | pending | pending | pending |
| Bogren MLC S_Zero 93 (bogren) | pending | pending | pending |
| Bogren MLC S_Zero 100 (bogren) | pending | pending | pending |

Installers and managers, which are host-independent:

| Program (prefix) | Install | Sign-in / activation | Installs a product | Survives restart |
|---|---|---|---|---|
| Arturia Software Center (arturia) | pending | pending | pending | pending |
| Kilohearts Installer (kilohearts) | pending | pending | pending | pending |
| Minimal Audio installers (minimalaudio) | pending | pending | pending | pending |
| XLN Online Installer (xln) | pending | pending | pending | pending |
| Native Access 2 through ni-wine (ni) | pending | pending | pending | pending |
| iLok License Manager (neuraldsp) | pending | pending | pending | pending |
| Bogren installers and activation (bogren) | pending | pending | pending | pending |

## Tests

```sh
bash -n ~/.config/razorjack/vstbridge/vstbridge
shellcheck --shell=bash --severity=warning ~/.config/razorjack/vstbridge/vstbridge
PYTHONDONTWRITEBYTECODE=1 uvx pytest -q -p no:cacheprovider ~/.local/tests/test_vstbridge.py
```

The tests mock every external command (Wine with a small Wine-format registry, wineserver, yabridgectl, gdbus, rpm, sudo, dnf, udisksctl, ni-wine, a DAW) and use temporary directories whose paths contain spaces and non-ASCII characters. They never install plugins or touch real prefixes.

`test_vstbridge_real.py` runs vstbridge against Fedora's Wine, the pinned yabridge build and the free Airwindows Consolidated plugin (MIT), in a temporary `HOME`. It needs the two yabridge CI archives and the two Airwindows downloads in `~/.cache/vstbridge-tests` (or `VSTBRIDGE_REAL_INPUTS`), and checks them against pinned hashes; its docstring has the URLs. It takes about two minutes:

```sh
VSTBRIDGE_REAL=1 PYTHONDONTWRITEBYTECODE=1 uvx pytest -q -p no:cacheprovider ~/.local/tests/test_vstbridge_real.py
```

With `xvfb-run`, `xdotool` and ImageMagick's `import` installed (`sudo dnf install xorg-x11-server-Xvfb xdotool`; only the tests need them), it also opens the CLAP editor on a virtual X display, takes screenshots, clicks it and closes it, with a watchdog so a plugin that never closes cannot hang the run.

It covers bridge installation, prefix creation at 144 DPI, preserved DPI on a second `setup`, the dispatcher's runner pairing and `unknown_prefix = fail`, theme apply and restore, font repair, the Segoe UI `WindowMetrics` round trip, a real Inno Setup install, CLAP scanning and audio processing and VST3 scanning through the bridge (`vstbridge_host.py`, a minimal ctypes host), `doctor`, `manifest`, and the absence of `~/.wine`. Three known problems are strict expected failures, so each test fails once the problem is fixed and the docs need updating: the VST3 load from a non-ASCII prefix, and the Airwindows editor's missing repaint after a click and its hang on close (see the evidence ledger). Licensed products and their editors remain manual checks in the acceptance matrix.
