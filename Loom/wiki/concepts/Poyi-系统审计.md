---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 67e28a0cadea4c0368daeffdef023791_4f37de4e788e11f1b3d35254007bceed
    ReservedCode1: LS1Cd0jYSGDjpXk6tlJ/1jqNgP6T0jqi+93URGZkWKa2fgXdMODvOZocd56N0FY6QS7Mxutjl0FPlr2Yd3nqRT36BBNCT1p4x0CLN60iA+9yQt3zdlu2tumrAm/IwUIsl2DmbNCvmWkl+qZwzhFlWjAgQ88Y7ICpKnyelwpdLaY9K3fZfShzDWTc9i4=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 67e28a0cadea4c0368daeffdef023791_4f37de4e788e11f1b3d35254007bceed
    ReservedCode2: LS1Cd0jYSGDjpXk6tlJ/1jqNgP6T0jqi+93URGZkWKa2fgXdMODvOZocd56N0FY6QS7Mxutjl0FPlr2Yd3nqRT36BBNCT1p4x0CLN60iA+9yQt3zdlu2tumrAm/IwUIsl2DmbNCvmWkl+qZwzhFlWjAgQ88Y7ICpKnyelwpdLaY9K3fZfShzDWTc9i4=
---

---
title: Poyi-系统审计
created: 2026-07-06 00:25:55
tags: [poyi, 审计, 对抗性测试, 文件系统]
---

# Poyi-系统审计

## 概述

全量对抗性审计完成：1096文件（Vault 195 + Loom 869 + 根32）vs AGENTS.md声明逐条核验

## 关键事实

- P0发现：SOUL.md仍存在（上次审计的修复未生效）；chatlog下声称的4目录(marvis/chatgpt/openai/windsurf)物理不存在
- P1发现：srtp项目缺plan.md；propagation-map中raw/2026-06-30(~600文件)实际路径为chatlog/raw/2026-06-30/
- P2发现：Wiki几乎为空（12文件，各domain/concept/entity/source均显示'暂无条目'）
- 23个技能目录物理存在，与INDEX.md一致
- Loom存在损坏文件（截断的.json扩展名）

## 关联

[[Loom-消化管线]] [[Courses-模块化管理]] [[私域内容运营]] [[Agent-数字分身]] [[小满]]
*（内容由AI生成，仅供参考）*
