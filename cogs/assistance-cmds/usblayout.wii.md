---
title: Wii USB drive layout
help-desc: A quick overview on the USB drive layout for Wii and GameCube games
---

The file structure of your USB or SD should look like this:

For Wii Games:
```
💾 USB/SD Root
⠀⠀> wbfs
⠀⠀⠀⠀> Game 1 Name [GAMEID]
⠀⠀⠀⠀⠀⠀> GAMEID.wbfs
⠀⠀⠀⠀> Game 2 Name [GAMEID]
⠀⠀⠀⠀⠀⠀> GAMEID.wbfs
```
A "wbf1" file may also be present for larger games like Smash Bros, just name it the same as the wbfs.

For GameCube Games:
```
💾 USB/SD Root
⠀⠀> games
⠀⠀⠀⠀> Game 1 Name [GAMEID]
⠀⠀⠀⠀⠀⠀> game.iso (Yes, this is literally "game.iso".)
⠀⠀⠀⠀> Game 2 Name [GAMEID]
⠀⠀⠀⠀⠀⠀> game.iso
```
For games that have multiple discs, just name the other disc "disc2.iso".

You can also use [Wii Backup Manager](https://wii.hacks.guide/wii-backups#using-wii-backup-manager) and [GameCube Backup Manager](https://wii.hacks.guide/gc-backups) to manage your backups.

If you do not know your games ID, you can find it by searching the name [here](https://www.gametdb.com). Remember to differentiate region ID letters!
