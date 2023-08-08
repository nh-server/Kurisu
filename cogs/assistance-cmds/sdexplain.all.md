---
title: Kinds of SD cards
help-desc: Explains what type of SD cards are out there
---

There are two different **physical** SD card standards and three different **electrical** SD card standards that you may see.

SD cards, physically, are either (full-size) SD or microSD cards. SD and microSD cards are identical, and you can use a microSD card in **any** device that expects a full-sized SD card, with a simple adapter.

Electrically, there are three common SD standards: SD, SDHC and SDXC.

SD covers SD cards up to 2GB in size. Certain older devices can only use standard SD cards, which means that any SD card over 2GB will not work in them. In the world of Nintendo hacking, this only matters for the Wii - It received a firmware update to add support for higher-capacity cards, but not all games (ex. Super Smash Bros Brawl) support it.

SDHC covers cards between 4GB and 32GB. This is officially the specification that the 3DS and Wii U follow. The SDHC specification requires that all SD cards are formatted to FAT32, so these devices can only read FAT32 formatted SD cards.

The SDXC specification is for cards between 64GB and 2TB. It is **identical** to SDHC, with the exception that it requires that the SD card be formatted to exFAT. This means that most devices that expect an SDHC card (3DS, Wii U, etc) will work with an SDXC card, but you will need to manually format it in a computer beforehand.

Windows will, by default, not let you format SD cards over 32GB to FAT32. This is due to purely historic reasons, but it does mean that an external program is required to format these cards. Type `.sdformat` in <#261581918653513729> to see a guide you can follow to format cards to FAT32.
