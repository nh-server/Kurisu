---
title: A Tool to extract the Common Key of your Wii U's OTP
author.name: GaryOderNichts and Acer_51 (Arthur)
help-desc: A tool to extract the Common Key of a Wii U's OTP
aliases: .wiiuck, .wiiucommonkey, .ckextractor 
color: FA0909
---

# Tools available (and with Downloads)

**1.** [GaryOderNichts one (Windows)](https://github.com/GaryOderNichts/WiiUCommonKeyExtractor) <br>
**2.** [Acer_51's one (macOS and Linux)](https://github.com/acer51-doctom/commonkey_extractor) <br>
**3.** Manual way. <br>

# Usage.

**1.** Open the program -> click `Open` -> Select your `otp.bin` file

**2.** You must execute it in your Terminal while being in the same folder as the executable: <br> `chmod +x commonkey_extractor && ./commonkey_extractor <path/to/your/otp.bin>`

**3.** To find it manually, in a Hex Editor, you must copy the first **16 bytes** of the offset <br> 0xE0 or 0E0. **WARNING!** If you didn't know already, one byte is 2 letters and spaces do not count.