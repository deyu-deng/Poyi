---
title: 硬件HID模拟-vs-软件模拟
tags: [comparison, HID, 数字分身]
---

# 硬件 HID 模拟 vs 软件模拟

> 路线取舍：数字分身要绕过现代人机验证，模拟方式决定成败。来源 [[Agent-数字分身]]。

## 对比

| 维度 | 软件模拟 | 硬件 HID 模拟 |
|---|---|---|
| 代表方案 | SendInput / pynput / playwright | Teensy 4.0 + Interception + ClawTouch MCP |
| 系统视角 | 应用层合成输入 | 真实 USB 设备（被识别为真键盘鼠标） |
| isTrusted | ❌ 假（属性可被检测） | ✅ 真 |
| 行为分布 | 统计特征异常，易识别 | 与真人一致 |
| 成本 | 0 | ~200 元（Teensy ~180 + USB 切换 ~30） |
| 多设备冲突 | 无 | 需 USB 切换开关 |

## 结论
现代人机验证（isTrusted + 行为分布统计）下，**纯软件模拟不可用**，必须硬件级 HID 模拟。暑假学生预算可覆盖。

## 关联
[[Agent-数字分身]] · [[Marvis]]（运行于本机）
