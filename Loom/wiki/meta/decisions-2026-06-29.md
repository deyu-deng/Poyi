---
type: meta
title: "决策记录 - 2026-06-29"
created: 2026-06-29
tags:
  - decision
  - daily-digest
status: stable
---

# 决策记录 - 2026-06-29

## 决策 1: LLM Wiki 知识库改造

选定 D:\Projects\Poyi 作为新知识库根目录，拆分为 Loom（AI管理区）和 Vault（用户笔记区），从 Cloud 中提出来放 D 盘根目录。Git 仓库对应 Poyi。

**Context**: 基于 Karpathy LLM Wiki 理念和 claude-obsidian 项目参考，用户决定彻底重构知识库。原 Vault 在 D:\Cloud 下臃肿难用，决定拆成 AI 全权管理区（Loom）和用户自管笔记区（Vault），命名选定 Loom（织机），物理路径 D:\Projects\Poyi\。Mac 端选方案 A，也走 ~/Poyi 通过 Git 同步。

## 决策 2: Research 文献整理

文献表格采用交叉拆分：中文论文、英文论文、中文专利各一张表，共 3 张放入一个文档；选择方案 C 深度扩充字段（DOI/摘要/关键词/研究方法/核心结论/实验数据/关联度）。

**Context**: 用户要求整理 Cloud\Research 下的文献。先从一张总表开始，用户反馈后改为交叉拆分为三张 sheet，并删除类型和语言列（因已按 sheet 分类）。扩充阶段从三个方案中选定深度扩充（方案 C），读取 PDF 全文提取核心结论和实验数据。

## 决策 3: Research 与 Vault 定位划分

确认 Research（Cloud\Research）存放文档和表格等原始资料，Vault 存放 Obsidian 笔记，两个定位不同。

**Context**: 用户发现 Cloud 下有两个 Research 目录，要求确认。明确：Research 里是文献 PDF 和汇总表格，Vault\Research 里是 Obsidian 笔记。后续 Zotero 存储路径 C:\Users\xgbc\Zotero\storage 也被纳入文献管理范围。

## 决策 4: Agent 数字分身方案

暑假前搭建路线一方案：硬件模拟（Raspberry Pi Pico 2 + ClawTouch MCP）做 HID 层键鼠操作，配合 Interception 驱动，构建三层架构的数字分身小桌宠。

**Context**: 用户想在寝室常开 Windows 上部署能做真实键鼠操作的数字分身，调度 Agent 工作，遇到需拍板的事打电话通知。调研后确定：不用 Teensy，用 Pico 2 + ClawTouch MCP 开源方案；npm 全局包放 Development 而非 Software。

## 决策 5: Workflow 工作流文档

在 D:\Cloud\Vault 下创建 Workflow 文件夹，用于维护不同场景的工作流文档。

**Context**: 用户想在核心工作区沉淀行之有效的操作流程。在已有 Obsidian Vault 下新建 Workflow 目录，建议按场景命名 .md 文件（如文献管理.md、信息雷达.md）。

## 决策 6: Course 课程资料整理规范

课件按章节序号+内容描述命名；考试资料归档为一份 PDF（原题+答案解析），小测也算考试，归档后删除原始附件和 Exercise 文件夹。

**Context**: 以「2026春夏-微积分(甲)II」为例完善课程整理流程。用户发现 Agent 不读 PDF 内容判断重复、命名无规范、Exercise 文件夹混乱。决定：命名加序号反映章节、考试沉淀为单 PDF 后删除 Exercise 文件夹、整理流程做成可复用的 skill。

## 决策 7: Course 文件夹命名规则

文件夹命名偏好英文，仅 Events 和 Courses 根目录下具体项目/课程名用中文。

**Context**: 用户指出：「文件夹都是喜欢用英文命名的，除了 Events 和 Courses 根目录下按项目和课程分配的文件夹由于具体到某一课程和事件所以用中文。」

## 决策 8: Aura 软著申请

删除源码注释以降低 AI 生成痕迹，同时使用 humanizer skill 做代码风格自然化处理。

**Context**: 用户为 Aura 项目准备软著材料，发现大量代码是 AI 写的。担心 AI 生成率过高影响审核。决定：删除注释直接解决注释 AI 痕迹问题，用 humanizer skill 处理代码风格。

## 决策 9: E-commerce 软件安装位置

应用宝等软件安装到 D:\Software 下的专门文件夹，不装 C 盘。

**Context**: 用户在构建电商自动化方案时发现应用宝可能装在 C 盘，明确习惯是安装在 D 盘的 Software 里面专门的文件夹里。亲自卸载后重装到指定位置。
