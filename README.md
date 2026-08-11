# Fox

Fox is a portable command-line toolkit for Android static analysis and
ROM/framework reverse engineering. The original project was written in 2017;
this revision updates the bundled toolchain and workflow for Android 15
(API 35) and Android 16 (API 36).

## Bundled toolchain

| Tool | Bundled version | Role |
| --- | --- | --- |
| JADX | 1.5.6 | Decompile APK, DEX, AAB, APKS, XAPK, APKM, JAR, AAR, etc. |
| Apktool | 3.0.3 | Decode/rebuild application resources and manifests. |
| smali / baksmali | 3.0.9 plus post-release Android 16 ART/OAT fixes | Assemble/disassemble DEX and deodex ART OAT/ODEX. |
| Java | 11+ required by JADX; Java 17 is recommended | Runs the Java-based tools. |

The `smali` and `baksmali` jars are built from the official `google/smali`
repository at commit `b353f17d9a66810a6d534fb3469cd4345855e845`. That commit
contains post-3.0.9 fixes for Android 12–15 ODEX handling and modern ART/OAT
layouts. The upstream project has not issued a newer tagged release yet, so
the jars deliberately retain the upstream `3.0.9` version string.

## Install

Run directly from the repository:

```sh
./fox doctor
./fox install
```

`install` creates symlinks in `~/.local/bin` by default. Use an explicit
directory or `FOX_BIN_DIR` to choose another location:

```sh
./fox install ~/bin
FOX_BIN_DIR=~/bin ./fox install
```

Ensure that chosen directory is present in `PATH`.

## Main workflow

### 1. Normal APK/app bundle analysis

Use JADX first. It handles app containers directly and is a better default than
an APK → dex → Java conversion pipeline.

```sh
fox decrom apk app.apk out/app
fox decrom apk bundle.apks out/bundle
fox decrom apk app.xapk out/xapk
```

For resource-oriented work or rebuilding:

```sh
apktool decode app.apk -o out/apktool
apktool build out/apktool -o out/rebuilt.apk
```

### 2. ART OAT/ODEX / ROM framework analysis

The legacy `dextra` binary is removed from the workflow: it only understood
Android 8-era OAT layouts. Fox now asks maintained `baksmali` to enumerate
every DEX entry in an OAT/ODEX, deodexes each entry, assembles the DEX files,
and passes the directory to JADX.

```sh
# One OAT/ODEX file. framework-dir must contain boot.oat/framework files.
fox decrom oat system/framework/oat/arm64/services.odex \
  system/framework \
  out/services

# An installed app directory with APK plus oat/arm64/*.odex.
fox decrom app system/framework system/priv-app/Settings out/settings

# All containers and OAT/ODEX files below a framework/system root.
fox decrom all system/framework out/framework

# Print embedded DEX entries for diagnosis.
fox decrom check system/framework
```

Deodexing still depends on vendor-specific ART image layout and a matching
`boot.oat`; when absent, Fox continues with a clear warning. For an APK with
embedded `classes*.dex`, use `fox decrom apk` instead.

## Android framework literal maps

`fixsrc` replaces selected string and numeric literals in JADX Java output with
framework constant names. The maps are generated from Android 16 API 36
sources, rather than an obsolete hard-coded Android 7.1 source path.

```sh
# Install Android SDK sources first (recommended).
sdkmanager "sources;android-36"
fox dump "$ANDROID_HOME/sources/android-36"

# Or download the pinned AOSP Android 16 source files.
fox dump --download

# Preview/apply replacements in JADX Java output.
fox fixsrc --dry-run out/app/sources
fox fixsrc out/app/sources
```

## Design and safety notes

- Input and output paths are quoted, support spaces, and are converted to
  absolute paths before tools change directory.
- `fox doctor` validates Java and bundled artifacts before analysis.
- Tool versions are pinned in filenames, so an upgrade is deliberate and
  reviewable.
- `fox update` only performs `git pull --ff-only`; it no longer makes a merge
  commit unexpectedly.
- Decompiled Java is a reconstruction. Use the smali output and original DEX
  as the source of truth when reviewing security-sensitive behavior.

## Updating bundled tools

See [`TOOLS.md`](TOOLS.md) for exact sources, SHA-256 values, and the release
verification/build procedure.
