---
title: Wii USB drive layout
help-desc: A quick overview on the USB drive layout for Wii and GameCube games
---

The file structure of your USB drive should look like this:

```
💾 SD or USB HDD:
┣ 📂 wbfs
┃ ┣ 📂 GameName [gameID]
┃ ┃ ┗ 📜 gameid.wbfs
┃ ┣ 📂 GameName [gameID] -- This example is for split WBFS files. If your drive's file system is NTFS or your game is smaller than 4 GB, ignore it.
┃ ┃ ┣ 📜 gameid.wbfs
┃ ┃ ┗ 📜 gameid.wbf1
┣ 📂 games
┃ ┣ 📂 GameName [gameID]
┃ ┃ ┗ 📜game.iso -- This is not a placeholder, the file, with its file extension, should literally be named "game.iso".
┃ ┣ 📂 GameName [gameID] -- This example is for games with multiple discs.
┃ ┃ ┣ 📜game.iso
┃ ┃ ┗ 📜disc2.iso
```

You can also use [Wii Backup Manager](https://wii.hacks.guide/wii-backups#using-wii-backup-manager) and [GameCube Backup Manager](https://wii.hacks.guide/gc-backups) to manage your backups.

The `wbfs` folder is only for Wii games and the `games` folder is only for GameCube games.
You can find the game IDs [here](https://www.gametdb.com).
