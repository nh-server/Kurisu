---
title: Debugging TegraRCMGui
help-desc: Common troubleshooting steps for injecting payloads into RCM
---

If you're having TegraRCMGui errors, driver issues or your Switch is just straight up being weird when trying to inject a payload via RCM, get [Zadig](https://zadig.akeo.ie/) and:
1. Boot out of RCM and into stock (if already in RCM)
2. Connect Switch to pc
3. Let Windows install default drivers (if it hasn't already)
4. Disconnect from PC, power off Switch and boot into rcm
5. Load Zadig
6. Connect Switch to pc
7. In Zadig, find "APX" in device list
8. For driver type, select libusbK (3.0.7.0)
9. Install that driver
10. Close zadig
11. Open TegraRCMGui and inject the payload

If this still doesn't work, cycle out of and back into RCM and try again.
