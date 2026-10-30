# COD-BOZ-Remastered

A fan remaster of **Call of Duty: Black Ops Zombies (mobile, Android)**, focused on bringing the maps closer to Black Ops 1 / World at War on PC.

Developed and Remastered by **cool715 (Discord) / Toughman591**.

> This is a fan project. It is not affiliated with or endorsed by Activision or Treyarch. This repository has **no game files**: no APK, no game data (`.dz`), no game code (`boz.s3e`) and no extracted assets. It only has the mod's own source: patch scripts, assembly and build tools.

## What's in the mod

The latest release on GitHub is **v5.11**. Items marked *(after v5.11)* are finished in newer builds and will come with the next release.

- **Kino der Toten**: BO1 PC textures, BO1-style loading screen and loading clip, theater flag, 115 song, Call of the Dead intro video. Call of the Dead cast and voices *(after v5.11)*.
- **Nacht der Untoten**: a playable map with windows, zombies, doors, box, wall weapons, radio easter egg, WaW couches/help door and fog.
- **Verrückt**: WaW doors, perk machines, chalk wall buys and Speed Cola. A Speed Cola buy fix *(after v5.11)*.
- **Shi No Numa**: WaW doors, roofs, fences, water, zipline, traps and the Wunderwaffe. The flogger as an electric trap *(after v5.11)*.
- **Co-op**: Nacht in online and local Wi-Fi co-op. Shi No Numa co-op *(after v5.11)*.
- **Ray Gun Mark II** in the mystery box.
- **Mule Kick (test builds, solo Kino only)** *(after v5.11)*: a 3-gun perk machine in Kino's Atrium. It has its own HUD icon and name, refills on Max Ammo, is kept in saved games and lights up green when the power is on.
- **Mali / all GPUs build**: textures converted so the game runs on every phone GPU, not just old Snapdragon phones.

The full history, including the builds after v5.11, is in [CHANGELOG.txt](CHANGELOG.txt).

## Download and install

1. Go to [Releases](../../releases) and download every part of the version you want (`.zip.001`, `.zip.002`, …).
2. Join the parts. Open [`tools/joiner.html`](tools/joiner.html) in Chrome on your phone, pick all the parts and save the APK. Or join them on a PC with any zip tool that handles split archives.
3. Install the APK. On the first launch it unpacks the game data once (a % screen), then starts the game.

Use the **Mali** build on any phone GPU. Since v5.8 you can install a new version over an old one and keep your progress.

## Repository layout

| Folder | What it is |
| --- | --- |
| `src/code-patches/` | Changes to the game code (`boz.s3e`), one folder per version: Python patchers and Thumb-2 assembly (`*.s` + linker scripts), applied in order. `mule3/` is the current Mule Kick code. |
| `src/data/` | Builders for the game data: level entities, perk machines, HUD icon, text in all languages, the front-end menu (co-op cards) and the `.dz` archive. |
| `src/lib/` | Shared Python helpers: resource groups, entities, textures (ATC/Mali), models, `.dz` read/write, navmesh. |
| `src/android/` | The APK's first-launch unpacker (smali). |
| `src/pack/` | Scripts that put the APK together, sign it with a debug key and split it into 30 MB parts. |
| `tools/joiner.html` | A page that joins the parts on a phone. |

## Building

The scripts are the real sources used for the releases. They won't run as-is on another machine:

- They need **your own copy** of the original game (APK + `blackops_atitc.dz`). None of it is here.
- They use the absolute paths of the machine they were built on (`/root/work/...`). Adjust these to your setup.
- Tools used: Python 3 (numpy, Pillow), LLVM (`llvm-mc`, `ld.lld`) for the Thumb-2 code, `xz`, apktool and an APK signer.

The code image is patched in place: new code goes into unused parts of the binary ("caves"), and the original instructions branch to it. Every patcher checks the original bytes before writing, so it refuses to run on a different game build.

## Credits

- **cool715 / Toughman591**: the remaster, testing and assets.
- **[BOZ Redux SDK](https://github.com/ZappaVinny/boz-redux-sdk)** by ZappaVinny: its MIT-licensed game definition (named functions, data layouts, events) and Ghidra scripts were used to reverse-engineer the perk, HUD, Max Ammo and save code for Mule Kick.
- [Ghidra](https://github.com/NationalSecurityAgency/ghidra) for decompiling.
- Call of Duty, Black Ops and all related content belong to Activision.
