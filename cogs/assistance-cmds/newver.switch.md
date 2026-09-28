---
title: Is the new Switch update safe?
help-desc: Quick advice for new versions
---

Currently, the latest Switch system firmware is {nx_firmware}.

Atmosphere {ams_ver} and Hekate {hekate_ver} currently support {nx_firmware}.

As of September 28th, 2026, Nintendo have added a dns.mitm bypass that allows the console to connect to game content and management servers. While this is likely not a problem, it is strongly recommended to enable 90DNS (see `.90dns`) which appears to fix the bypass. [Source](https://discord.com/channels/196618637950451712/314856589716750346/1553958263135928463)

As of January 26th, 2026, the primary maintainer of Atmosphère, SciresM, has announced that they are retiring from the public hacking scene. Since they have retired, Atmosphère updates will likely take longer to release with future firmware updates. What this means is that, currently, firmware version 21.2.0 is the latest (officially) supported firmware, without any potential uncertainty.

Users should be cautious updating past firmware versions 21.2.0, as Atmosphère may not work on newer firmware versions if Nintendo has implemented any major changes.

Because of this, there is a large likelihood of (potentially dangerous) Atmosphère forks coming into existence. Users are advised not to use these forks, and should wait for proper Atmosphère updates from developers who know what they're doing.
*Last edited: {last_revision}*
