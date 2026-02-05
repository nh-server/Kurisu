---
title: Wii and GameCube game file layout
help-desc: A quick overview on the drive layout for Wii and GameCube games
---

The file layout of your drive should look like this:

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
┃ ┃ ┗ 📜game.iso -- This is not a placeholder. The file, with its file extension, should literally be named "game.iso".
┃ ┣ 📂 GameName [gameID] -- This example is for games with multiple discs.
┃ ┃ ┣ 📜game.iso
┃ ┃ ┗ 📜disc2.iso
```

The `wbfs` folder is only for Wii games and the `games` folder is only for GameCube games.
You can find the game IDs [here](https://www.gametdb.com).

Instead of manually managing this file structure, you could also use [TinyWiiBackupManager](https://wii.hacks.guide/backups) to manage your backups. It will set up the above file structure for you.
