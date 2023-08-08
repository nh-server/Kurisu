---
title: What are trimmed cartridge dumps?
help-desc: Explain how ROM trimming works
---

All cartridges use memory chips which are in powers of 2 (as in 4, 8, 16, 32, 64, 128). If a game is 120MiB, it will be stored on a 128MiB chip and include 8MiB of 'padding' (garbage data) so the operating system does not think there is more content beyond the actual game and get confused.

Dumping the 'trimmed' game removes this padding data. However, some utilities (like patchers) use this 'padding' data to insert their own patch data, which means if you do not include the padding data, the patchers will be unable to insert their data.

If you intend to use the game for ROM hacks or `.xdelta` patches or something like that, get the untrimmed version.

If you just intend to use the game as its own game, get the trimmed version.
