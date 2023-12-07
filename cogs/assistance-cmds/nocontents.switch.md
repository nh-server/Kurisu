---
title: If your Switch crashes on boot
help-desc: How to temporarily rename the Atmosphere contents folder
---

Sometimes sysmodules and other LayeredFS files can cause boot errors or crashes.

You can test if this is the case by removing the contents folder temporarily and booting without it.

Rename `/atmosphere/contents` to `/atmosphere/oldcontents`, and boot Atmosphere again. If the Switch boots successfully, one of the items in the contents folder was the culprit. 