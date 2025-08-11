---
title: To clear PlayTime Management (PTM) data
help-desc: Quick guide to clear PTM data to avoid crashes
---

1. open GodMode9 by holding start prior to and during 3ds power on
2. go to `SYSNAND CTRNAND`
3. go to `data`
4. go to `<ID0>` (ID0 is a random looking 32 letter/number folder)
5. go to `sysdata`
6. press R+A on `00010022` and hit `Copy to 0:/gm9/out`
7. once it copies, go into `00010022`
8. find `00000000` and press X to delete
    - this will remove all playtime management data for activity log
9. reboot
