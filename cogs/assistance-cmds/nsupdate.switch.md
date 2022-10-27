---
title: What do I need to do before updating my system firmware when running CFW?
help-desc: What you should do before updating a Nintendo Switch
aliases: updateprep,nxupdate
---

**Make sure your version of Atmosphere is up-to-date and that it supports the latest firmware**

**Atmosphere {ams_ver} (latest release)**
Supports up to firmware {nx_firmware}.

*To find Atmosphere's version information, while booted into CFW, go into System Settings -> System, and look at   the text under the System Update button. If it says that a system update is ready instead of displaying the CFW version, type .pendingupdate in <#261581918653513729> to learn  how to delete it.*

**Make sure your version of Hekate is up-to-date and that it supports the latest firmware**

**Hekate {hekate_ver} (latest release)**
Supports up to firmware {nx_firmware}.

*To find Hekate's version information, once Hekate starts, look in the top left corner of the screen. If you use auto-boot, hold `volume -` to stop it.*

**If you use a custom theme (Atmosphere 0.10.0 and above)**
Delete or rename `/atmosphere/contents/0100000000001000` on your SD card prior to updating, as custom themes must be reinstalled for most firmware updates. **Note: On Atmosphere 0.9.4 or below, `contents` is called `titles`.**

