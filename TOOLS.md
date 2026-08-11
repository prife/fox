# Tool provenance and upgrade procedure

This file makes binary upgrades reproducible and reviewable.

## Current pins

| Artifact | Source | Version / revision | SHA-256 |
| --- | --- | --- | --- |
| `extras/jadx-1.5.6/` | `skylot/jadx` release `v1.5.6` | released 2026-07-09 | ZIP: `545ea2be9c242511bc145755cf4bda2485ade42966e096f8b4d3da2a230e8974`; bundled `jadx-1.5.6-all.jar`: `fe3e12c45acf75f92369685fd02d1d7a7323385dc725680a9b98a0dac0ea554b` |
| `extras/apktool_3.0.3.jar` | `iBotPeaches/Apktool` release `v3.0.3` | released 2026-07-19 | `dbf930b076c6b9be08d57c449cacefc3bdd6b71ebd59b3066fc0e1f5b14f9423` |
| `extras/smali-3.0.9-android16.jar` | `google/smali` | `b353f17d9a66810a6d534fb3469cd4345855e845` | `ba1072804702157d6c159bccee7b8eb50ce310c9c754709002d767c4d33e823d` |
| `extras/baksmali-3.0.9-android16.jar` | `google/smali` | `b353f17d9a66810a6d534fb3469cd4345855e845` | `875efea1b8c32a4966c2b9405b6e7af9665e1497e18536920a41e448fc19e32f` |

The stated release/commit status was checked on **August 11, 2026**.

## Why the smali jars are built from a commit

Upstream's newest tag is `3.0.9` (December 19, 2024), but post-release commits
include Android 12–15 ODEX fixes and modern OAT parsing:

- `8be50d70`: ODEX deodex/disassembly fixes for Android 12–15.
- `b353f17`: correct modern OAT header key/value parsing.
- Current code accepts OAT versions through `254`, the Android 16-era ART
  format path.

Until upstream publishes a newer release, this project prefers the pinned
official-source build over retaining 2016-era smali/baksmali binaries.

## Rebuild / verify

### JADX

```sh
curl -fL -o jadx-1.5.6.zip \
  https://github.com/skylot/jadx/releases/download/v1.5.6/jadx-1.5.6.zip
shasum -a 256 jadx-1.5.6.zip
unzip -q jadx-1.5.6.zip -d extras/jadx-1.5.6
extras/jadx-1.5.6/bin/jadx --version
```

### Apktool

```sh
curl -fL -o extras/apktool_3.0.3.jar \
  https://github.com/iBotPeaches/Apktool/releases/download/v3.0.3/apktool_3.0.3.jar
shasum -a 256 extras/apktool_3.0.3.jar
java -jar extras/apktool_3.0.3.jar --version
```

### smali / baksmali

```sh
git clone https://github.com/google/smali.git /tmp/smali
cd /tmp/smali
git checkout b353f17d9a66810a6d534fb3469cd4345855e845
./gradlew --no-daemon :smali:fatJar :baksmali:fatJar

cp smali/build/libs/smali.jar \
  /path/to/fox/extras/smali-3.0.9-android16.jar
cp baksmali/build/libs/baksmali.jar \
  /path/to/fox/extras/baksmali-3.0.9-android16.jar
shasum -a 256 /path/to/fox/extras/{smali,baksmali}-3.0.9-android16.jar
```

Run `fox doctor`, a small smali→DEX→baksmali round trip, and decompile an APK
and an Android 15/16 OAT sample before committing a tool upgrade.
