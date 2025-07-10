---
title: A Tool to extract the Common Key of your Wii U's OTP
author.name: GaryOderNichts and Acer_51 (Arthur)
help-desc: A tool to extract the Common Key of a Wii U's OTP
aliases: .wiiuck, .wiiucommonkey, .ckextractor 
color: FA0909
---

# Tools available (and with Downloads)

**1.** [GaryOderNichts one (Windows only, x64 and x86)](https://github.com/GaryOderNichts/WiiUCommonKeyExtractor) We recommend this tool if you're more familiar with GUIs. <br>
**2.** [Acer_51's one (Windows, macOS and Linux [ARM and x64 builds])](https://github.com/acer51-doctom/commonkey_extractor) We recommend this tool if you're more familiar with Terminal User Interfaces. <br>
**3.** Manual way. <br>

# Usage.

**1.** Open the program -> click `Open` -> Select your `otp.bin` file

**2.** Double click the program. A Terminal or Command Prompt window will open. Type in the path to your OTP or simply drag and drop it from a Finder or File Explorer window.

**3.** To find it manually, in a Hex Editor, you must copy the first **16 bytes** of the offset <br> 0xE0 or 0E0. **WARNING!** If you didn't know already, one byte is 2 letters and spaces do not count.