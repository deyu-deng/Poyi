---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 67e28a0cadea4c0368daeffdef023791_4dbce437788e11f1a8895254002afed2
    ReservedCode1: /twXvLE7ymhUivwv/u9G57++YnyVdhkVyOQmladoznWbC5vMg0GdIwBwA56Imtx2Ry/FoyroetO0x8NCwrtwzD+AYa0Ci1xZ4c7A4P6GQ3xY7pJw840+GvkvYYuor9tk13x6Z4ROFl0TwzSku09+AsPI0nknvaGyrNKQQW2LaWZO6ZYsOG3aMKrFCTQ=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 67e28a0cadea4c0368daeffdef023791_4dbce437788e11f1a8895254002afed2
    ReservedCode2: /twXvLE7ymhUivwv/u9G57++YnyVdhkVyOQmladoznWbC5vMg0GdIwBwA56Imtx2Ry/FoyroetO0x8NCwrtwzD+AYa0Ci1xZ4c7A4P6GQ3xY7pJw840+GvkvYYuor9tk13x6Z4ROFl0TwzSku09+AsPI0nknvaGyrNKQQW2LaWZO6ZYsOG3aMKrFCTQ=
---

---
title: Agent-数字分身
created: 2026-07-06 00:25:55
tags: [agent, 数字分身, HID, 硬件]
---

# Agent-数字分身

## 概述

硬件级HID模拟方案调研：Teensy 4.0 + Interception驱动 + ClawTouch MCP → 绕过isTrusted/驱动栈指纹 → 目标：构建可键鼠操作的桌宠数字分身

## 关键事实

- ClawTouch MCP：Python MCP Server，通过Raspberry Pi Pico 2暴露真实USB HID作为MCP工具
- pyinterception：Windows Interception驱动的Python封装，内核级输入模拟
- Teensy 4.0 ~180元，USB HID键盘鼠标模拟，被Windows识别为真设备
- USB切换开关 ~30元，解决真键盘与数字分身共用一台电脑的冲突
- 总硬件成本200出头，暑假学生预算可覆盖
- 纯软件模拟（SendInput/pynput/playwright）无法通过现代人机验证——isTrusted属性、行为分布统计特征检测

## 关联

[[Loom-消化管线]] [[定时任务生态]] [[Marvis]]
*（内容由AI生成，仅供参考）*
