---
help-desc: Quick troubleshooting guide for "boss" module crash
---

If you are having an issue where your 3DS crashes with the "boss" process, this is due to NetPass. You can disable game patching to avoid this by doing:

1. Hold SELECT while turning on the 3DS
2. At Luma3DS configuration, disable "Enable loading external FIRMs and modules"
3. Press START to save and exit
    - If this works, open /luma/sysmodules/ and delete 0004013000003402.ips and  0004013000002602.ips
