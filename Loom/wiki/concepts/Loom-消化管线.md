---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 67e28a0cadea4c0368daeffdef023791_504cf0bc788e11f1a7da5254006c9bbf
    ReservedCode1: MXIRPlm6vRySKDeBdKDFsHUqO2ltvl7Yw7sPAJ2mIv+6kxAIItYuv3ntV5BVi5JdmSu4IwrIdb4uDiHhcvH4iPQ0A3xCTN0MYrgwmOIlEAfwFsourpPpJfhrbJY8soNZX+zjdgIvUT5Yaf1tLu3VOOTQPk+WBVneDe1si8GoqOO8w7hHa9iaHHf9Y+A=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 67e28a0cadea4c0368daeffdef023791_504cf0bc788e11f1a7da5254006c9bbf
    ReservedCode2: MXIRPlm6vRySKDeBdKDFsHUqO2ltvl7Yw7sPAJ2mIv+6kxAIItYuv3ntV5BVi5JdmSu4IwrIdb4uDiHhcvH4iPQ0A3xCTN0MYrgwmOIlEAfwFsourpPpJfhrbJY8soNZX+zjdgIvUT5Yaf1tLu3VOOTQPk+WBVneDe1si8GoqOO8w7hHa9iaHHf9Y+A=
---

---
title: Loom-消化管线
created: 2026-07-06 00:25:55
tags: [loom, 消化, AI, 管线, aggregate]
---

# Loom-消化管线

## 概述

aggregate_win.py v3.0→v4.0升级完成：正则匹配Phase2删除，改为信号文件+Marvis AI消化管线

## 关键事实

- 新管线：cron导出raw JSON → aggregate_win.py Phase0+Phase1 → _pending_digestion.json信号文件 → Marvis定时任务(AI语义消化) → knowledge/preferences/decisions.json + 更新summary.md
- 两个新定时任务：09:15「Poyi AI日清消化（上午）」、23:45「Poyi AI日清消化（夜间）」
- 旧cron任务(09:00、23:30)仍在运行但执行v4脚本，产出summary.md统计+信号文件
- v4保留Phase0(raw JSON导出)和Phase1(summary.md统计)，仅删除Phase2正则逻辑
- raw/中06-12~06-24的7个日期从未被消化（原料被v3正则处理丢弃）
- digested/正确路径：<POYI_ROOT>/Loom/raw/chatlog/digested/（之前文档缺raw/层，已修正13文件19处）

## 关联

[[Poyi-系统审计]] [[Agent-数字分身]] [[定时任务生态]] [[Marvis]]
*（内容由AI生成，仅供参考）*
