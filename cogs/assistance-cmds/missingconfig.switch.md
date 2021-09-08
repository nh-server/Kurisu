---
title: Getting the "No main boot entries found" error in hekate?
help-desc: No main boot entries found solution
aliases: missingco
---

You forgot to copy the "hekate_ipl.ini" file to the bootloader folder on your sd card, or forgot to insert your sd card before booting hekate.

Note that if hekate can't find a config, it'll create one. So likely you now have a hekate_ipl.ini in your bootloader folder, replace it with the one from [the guide](https://nh-server.github.io/switch-guide/user_guide/emummc/sd_preparation/)
