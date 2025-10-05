---
title: Payload failing to load fixes
help-desc: Potential fixes for when payload.elf fails to load on the Wii U
---

**Fixes for "Failed to load payload.elf"**

- Make sure your SD card is unlocked (Slider should be facing up).

- Make sure you have both `payload.elf` and `payload.rpx` in the `wiiu` folder on the SD card. Refer to the layout [here](https://wiiu.eiphax.tech/sdlayout).

- Make sure your SD card is properly formatted to FAT32. A guide on how to do so can be found [here](https://wiki.hacks.guide/wiki/Formatting_an_SD_card).

- Make sure the SD card slot is clean and free from obstructions. Apply some compressed air into the slot to clear out dust or debris.

- Try saving a Mii image to the SD card to ensure that it is being properly read, which can be done like [this](https://en-americas-support.nintendo.com/app/answers/detail/a_id/1722/~/how-to-save-a-mii-as-a-photo).

- Make sure your SD card is properly inserted into the SD cart slot. You should hear a click sound when it is inserted.

If none of the above works, you may have a faulty/worn SD card, MicroSD card, or MicroSD card adapter, and are advised to purchase a new SD card or adapter. Type `.sdreco wiiu` in <#261581918653513729> for SD card size recommendations.
