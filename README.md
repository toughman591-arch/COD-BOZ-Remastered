# COD-BOZ-Remastered

A fan remaster of **Call of Duty: Black Ops Zombies (mobile, Android)**, focused on bringing the maps closer to Black Ops 1 / World at War on PC.

Developed and Remastered by **cool715 (Discord) / Toughman591**.

> This is a fan project. It is not affiliated with or endorsed by Activision or Treyarch.

## What's in the mod

The latest release is **v5.32**. Items marked *(after v5.11)* were added after v5.11 and are in v5.32.

- **Kino der Toten**: BO1 PC textures, BO1-style loading screen and loading clip, theater flag, 115 song, Call of the Dead intro video. Call of the Dead cast and voices *(after v5.11)*.
- **Nacht der Untoten**: a playable map with windows, zombies, doors, box, wall weapons, radio easter egg, WaW couches/help door and fog.
- **Verrückt**: WaW doors, perk machines, chalk wall buys and Speed Cola. A Speed Cola buy need fixing, electric trap *(after v5.11)*.
- **Shi No Numa**: WaW doors, roofs, fences, water, zipline, traps and the Wunderwaffe. The flogger as an electric trap *(after v5.11)*.
- **Der Riese**: WaW doors, perk machines, chalk wall buys, bridge animation (needs some fixing), power on (needs some fixing), and electric traps *(after v5.11)*
- **Co-op**: Nacht in online and local Wi-Fi co-op. Shi No Numa co-op *(after v5.11)*.
- **Ray Gun Mark II** in the mystery box only on Nacht, Shi no Numa, Verruckt and Der Riese.
- **Mule Kick (test builds, solo Kino only)** *(after v5.11)*: a 3-gun perk machine in Kino's Atrium. It has its own HUD icon and name, refills on Max Ammo, is kept in saved games and lights up green when the power is on.
- **Co-op map select: REZURRECTION page** *(after v5.11, test builds)*: the co-op map select keeps the 4 Black Ops maps; tap the REZURRECTION arrow for Nacht, Verrückt, Shi No Numa and Der Riese. The lobby vote stays the original 4 maps.
- **Five** *(after v5.11, test builds)*: new loading screen and a skippable story intro video (single player).
- **Full screen** *(after v5.11, test builds)*: the status and navigation bars are hidden and the game draws into the camera notch.
- **Der Riese** *(after v5.11, test builds)*: fix attempts for the Pack-a-Punch door crash; Call of the Dead's name shortened to fit the cards.
- **HD zombie heads** *(v5.32)*: the 4 shared zombie head and hand textures at twice the resolution, on every map. Only the pictures change, so crossplay is unaffected.
- **Mali / all GPUs build**: textures converted so the game runs on every phone GPU, not just old Snapdragon phones.

The full history, including the builds after v5.11, is in [CHANGELOG.txt](CHANGELOG.txt).

## Map progress

Rough estimate of how close each map is to its PC version (Black Ops 1 / World at War), as of v5.32.

| Map | Progress | Status |
| --- | :---: | --- |
| Kino der Toten | 90% | BO1 PC textures, loading screen and clip, 115 song, intro video, Call of the Dead cast option. Still missing: BO1 character and weapon textures. |
| Nacht der Untoten | 85% | Fully playable in solo, online and local co-op: windows, doors, box, wall buys, radio easter egg, fog. |
| Verrückt | 80% | WaW doors, perks, chalk wall buys, electric trap. Speed Cola buy still needs fixing. |
| Shi No Numa | 80% | WaW doors, roofs, water, zipline, traps, Wunderwaffe, co-op. |
| Der Riese | 60% | WaW doors, perks, wall buys, electric traps, co-op. Bridge and power need more fixing; Pack-a-Punch door fix not confirmed yet; no jump-down spots yet. |
| Shangri-La | 55% | BO1 port: jungle, geysers, water slide, 2 power switches, loading screen. Minecart on hold. |
| Five | 50% | BO1 port: new loading screen and skippable story intro. Still being fixed. |
| Call of the Dead | 35% | Original mobile map plus intro video, loading screen and the cast's voices and pictures. No own hands or player models (the game has none). |
| Ascension | 20% | Original mobile map, with the HD zombie heads. |
| Dead Ops Arcade | 10% | Original mobile mode. Solo loading crash reported on Mali (likely memory). |
| Moon | 0% | Planned after Shangri-La and Five. |

Shared by all maps: HD zombie heads (v5.32), full screen, Mali / all-GPU textures. The co-op map select has a REZURRECTION page for the 4 World at War maps; the lobby vote keeps the original 4 maps.

## Download and install

1. Go to [Releases](../../releases) and download the latest APK.
2. Older releases come in parts: open [`tools/joiner.html`](tools/joiner.html) in Chrome on your phone, pick all the parts and save the APK (or join them on a PC with any zip tool that handles split archives). v5.29 and later are a single APK.
3. Install the APK. On the first launch it unpacks the game data once (a % screen), then starts the game.

Use the **Mali** build on any phone GPU. Since v5.8 you can install a new version over an old one and keep your progress.

## Repository layout

| Folder | What it is |
| --- | --- |
| `src/code-patches/` | Changes to the game code (`boz.s3e`), one folder per version: Python patchers and Thumb-2 assembly (`*.s` + linker scripts), applied in order. `mule3/` is the current Mule Kick code. |
| `src/data/` | Builders for the game data: level entities, perk machines, HUD icon, text in all languages, the front-end menu (co-op cards) and the `.dz` archive. |
| `src/lib/` | Shared Python helpers: resource groups, entities, textures (ATC/Mali), models, `.dz` read/write, navmesh. |
| `src/android/` | The APK's first-launch unpacker, the full-screen patch and the map intro player (smali). |
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

- Call of Duty, Black Ops and all related content belong to Activision.
