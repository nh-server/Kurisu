---
title: exFAT on Switch: Why you shouldn't use it
help-desc:exFAT on Switch:  why not to use it
---

The recommended filesystem format for the Switch is FAT32.

While the Switch supports exFAT through an additional update from Nintendo, here are reasons not to use it:

* CFW may fail to boot due to a missing exFAT update in Horizon
* This filesystem is prone to corruption.
* Nintendo doesn't use files larger than 4GB, even with large games and exFAT.

Here are some links to common FAT32 formatting tools:
• [GUIFormat](http://ridgecrop.co.uk/index.htm?guiformat.htm) (Windows)
• [gparted](https://gparted.org/download.php) + [dosfstools](https://github.com/dosfstools/dosfstools) (Linux)
• [Disk Utility](https://support.apple.com/guide/disk-utility/format-a-disk-for-windows-computers-dskutl1010) (MacOS)
MacOS: Always select "MS-DOS (FAT)", even if the card is larger than 32GB.
