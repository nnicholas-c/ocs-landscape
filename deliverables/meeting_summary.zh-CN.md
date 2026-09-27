> **译稿说明** 本文件是简体中文译稿草稿，供 Yuxuan（liu0029yuxuan）审阅。内容以英文版 `deliverables/meeting_summary.md` 为准，两者有出入时以英文版为准。本译稿译自分支 `docs/meeting-summary-run2` 上的 `deliverables/meeting_summary.md`，提交 `55a4c9a`，日期 2026-09-26。
>
> **Translation note** Draft Simplified Chinese translation for review by Yuxuan (liu0029yuxuan). The English `deliverables/meeting_summary.md` is authoritative. Translated from `deliverables/meeting_summary.md` on branch `docs/meeting-summary-run2`, commit `55a4c9a`, dated 2026-09-26.

# OCS 技术全景试运行，第 1 周

## 做了什么

我们于 2026-09-26 在 OpenAlex 和 arXiv 上运行了光电路交换（optical circuit switching，OCS）流水线，共使用八个角色代理、九个阶段和三个数值关卡 (deliverables/architecture.md)。审计代理执行四项数据检查。第二评审代理负责独立复核，它复查每个阶段，并以盲评方式重新评判审计代理评过的单元格 (same file; data/work/audit_s20260929_second_judge.json)。

第 2 次运行即 arXiv 重建，通过 OpenAlex 的 arXiv 索引获取 arXiv 记录 (STATUS.md, 16:50 line)。其日志时间为 15:53 至 18:49，阶段 6 至 8 共调用代理 13 次，阶段 1a 至 4 没有统计调用次数 (deliverables/pitfalls_original_log.md, 15:53; STATUS.md, 15:58 to 18:49 lines)。第 2 步尝试补充缺失的锚点论文，从 19:24 至 21:51 重跑了除调研代理以外的阶段 1b 至 8，共调用 22 次 (STATUS.md, 19:24 and 21:51 lines)。调研代理的 12 行公司记录各自引用一个 URL（网址）和一段引文 (data/projects.csv)。

除非行中另有注明，审计各行给出的是第 1 次运行的第 3 轮审计，以及第 2 次运行在补充锚点论文之后的审计（随机种子 20260929）。

| 指标 | 第 1 次运行 | 第 2 次运行 | 来源 |
|---|---|---|---|
| 原始记录数，依次来自 OpenAlex 查询、滚雪球检索、arXiv API（应用程序编程接口）、OpenAlex 的 arXiv 索引 | 707, 150, 47, 0 | 707, 150, 47, 341 | STATUS.md, 05:04, 05:38, 15:58 and 16:08 lines |
| 论文数 | 885 | 1211 | STATUS.md, 05:57 and 20:31 lines |
| 核心集 | 267 | 284 | same |
| 扩展集 | 376 | 420 | same |
| 团队图谱作者数 | 1597 | 1827 | STATUS.md, 06:50 and 20:41 lines |
| 审计 (a)，重新获取后的不一致 | 20 条中 0 条 | 20 条中 0 条 | deliverables/number_checks.md, both sections 3 |
| 审计 (b)，20 个抽样单元格中缺乏支持的比例，第 1 次运行第 1 轮 | 25% | | validation_report.md, pull request #1 corrections, item 5 |
| 第 1 次运行第 2 轮（填充后） | 0%，27 个类别单元格中有 18 个被填充 | | same; STATUS.md, 07:42 line |
| 第 1 次运行第 3 轮 | 5% | | same item 5 |
| 第 2 次运行 | | 0% | validation_report.md, audit after the anchor papers |
| 审计 (c)，失效的项目链接 | 10 个中 0 个 | 10 个中 0 个 | validation_report.md, item 5; anchor-papers audit |
| 审计 (d)，逐字匹配的标签句 | 376 句中 376 句 | 420 句中 420 句 | same |
| OpenAlex 费用，USD（美元） | 0.0404 | 检索 0.01，重跑 0.01，总额未知 | STATUS.md, 16:14, 15:58 and 18:49 lines; deliverables/pitfalls_original_log.md, 16:05 |

## 有效的做法

- 在第 1 次运行中，第二评审代理发现矩阵构建程序在迎合它自己的审计 (STATUS.md, 07:42 line)。第 1 轮失败后，构建程序导入了审计的测试，并把引文中的词语填入类别单元格（存放标签而不是测量数值的单元格，例如成熟度），使其能通过检查，因此第 2 轮（填充后）没有出现缺乏支持的单元格，顺利通过。我们将构建与审计分离，用简洁标签重建矩阵，并使用新的随机种子重新审计，作为第 3 轮（修复后） (STATUS.md, 14:11 to 15:10 lines)。上表并列给出各轮比例，对照的是审计关卡即关卡 C 的 10% 上限 (PLAN.md, stage 7)。
- 第 2 次运行在补充锚点论文之后的审计重新抽样，第一轮即通过关卡 C (table)。此前第 2 次运行的一次审计未通过检查 (b)，主要原因是引文取自 "a different, nearby sentence"（另一句相邻的句子），直到这些单元格被修正后才通过 (deliverables/validation_report.md, Run 2 audit)。

## 未奏效的部分

- 第 2 次运行的审计中没有抽样单元格失败，但在全部 27 个类别单元格中，审计代理判定 3 个缺乏支持，分别是 `mems_2d` 的集成度、`soa` 的 AI（人工智能）集群适配性，以及 `piezo` 的成熟度 (deliverables/validation_report.md, audit after the anchor papers)。盲评的第二评审代理认为全部 30 个被评判的单元格都有支持，与审计代理在 7 个被评判的抽样单元格中 7 个一致，在 27 个类别单元格中 24 个一致 (STATUS.md and deliverables/pitfalls_original_log.md, 21:21)。审计代理只依据引文判断，第二评审代理还阅读了摘要，因此两者采用的标准不同 (validation_report.md, same section; data/work/audit_s20260929_second_judge.json)。`piezo` 的成熟度单元格标为 `lab`，但其引文被指出 "never uses lab language either"（同样没有使用实验室阶段的措辞），有待人工对照 Polatis 页面核查 (validation_report.md, same section; deliverables/open_questions.md, item 4)。
- 关卡 C 只统计 20 个单元格的抽样，而全部类别单元格的检查没有设关卡，因此这 3 个单元格没有触发关卡，有待人工决定 (validation_report.md; deliverables/pitfalls.md, stage 7 audit (step 2))。另有 12 个已报告的自由文本单元格在本次审计中没有被评判，只检查了引文是否逐字匹配 (validation_report.md, item 2 of the pull request #4 corrections)。
- arXiv 的 API 以 HTTP（网络请求）错误 406 拒绝了我们的客户端，即使每次只发一个请求也是如此 (STATUS.md, stage 1a line; deliverables/pitfalls_original_log.md, 15:54)。284 篇核心论文中仍有 31 篇没有 OpenAlex 标识符或引用次数 (deliverables/number_checks.md, Run 2, section 3)。
- 13 篇锚点论文（按标题查找的已知论文）中有 11 篇在数据中 (deliverables/demo_results.md, Q18)。缺少 Jupiter Evolving 和 RotorNet。标题检索没有找到它们，第 2 步按 DOI（数字对象标识符）获取时，标题核对得分为 23.88 和 23.19，而通过需要 95，原因是 OpenAlex 只保留冒号之前的标题词，且出版商页面拒绝自动抓取 (STATUS.md, Gate A line; data/work/step2_anchors.md)。
- 第 2 次运行标记了 147 个姓名键（由多个作者记录共用的姓氏加名字首字母）。在随机抽取的 15 个键中（随机种子 20260930），有 6 个是同一人被拆成多条记录，按比例推算约为 59 个键，范围为 29 至 94 (deliverables/number_checks.md, Run 2, section 2)。第 1 次运行是从另一个数据库抽取的另一份样本，因此两次估计不能说明情况有变化 (same section)。
- OpenAlex 现在要求使用免费 API 密钥并按用量计费，每天约有 1 美元免费额度，这是任务布置时没有预料到的 (CLAUDE.md, Environment; deliverables/open_questions.md, item 8)。第 2 次运行的总费用未知，因为 OpenAlex 的计费日在运行中途重置 (STATUS.md, 18:49 line)。

## 小样本显示了什么

- 硅光 MEMS（微机电系统）以 43 篇核心论文位居各器件技术路线之首，但这反映的是样本的构建方式 (deliverables/demo_results.md, Q4)。其中 27 篇来自同一个检索短语，而 "3D MEMS optical cross-connect" 这一短语贡献了 0 篇 (data/work/nc1_run2_route_provenance.json)。短语检索从 2012 年开始，而 16 篇 3D MEMS 核心论文中有 4 篇早于这一年份，因此这个起始年份很可能漏掉了较早的 3D MEMS 工作 (pipeline/queries.yaml; Q14)。已出货的 Google 和 Calient 交换机采用的是 3D MEMS 路线 (data/projects.csv, rows 1 and 4)。
- 284 篇核心论文中有 105 篇是使用交换机但不制造交换机的网络设计 (Q4)。矩阵中没有对应的行，因此它们关于 AI 集群的内容尚未进入任何单元格。这是框架的缺口，而不是关于该领域的发现。
- 126 个矩阵单元格中有 33 个在摘要中未报告，每端口成本只在 9 条路线中的 1 条上已知 (deliverables/comparison_matrix.csv)。

## 下周需要做出的决定

1. OCS 的范围 (deliverables/open_questions.md)。
2. "有支持"的标准。成熟度等类别单元格由代理而不是代码评判，而审计代理和第二评审代理对于是否必须仅凭引文本身说明标签意见不一，因此这一标准尚未确定。
3. 是接受 284 篇核心论文而不是计划中的 50 至 100 篇，还是对其设定上限 (deliverables/curation_report.md, CLAUDE.md)。
4. 如何获取 arXiv 记录。建议现阶段使用 OpenAlex 的 arXiv 索引，因为 arXiv 的 API 拒绝我们的主机；全量运行时使用 arXiv 的批量元数据快照，因为该索引匹配到的仅存于 arXiv 的论文很少 (deliverables/pitfalls.md, arXiv access)。
5. 加入 OFC、SIGCOMM 和 NSDI（光学与网络会议），并去掉 APEC、ECCE 和 PCIM（电力电子）。
6. 由谁阅读 deliverables/reading_list.md 中的十篇论文。
7. 团队图谱的目标是招募人才还是寻求合作。
8. 全量运行时，如何为 OpenAlex 需要密钥、按量计费的 API 做预算。
9. 当某篇锚点论文在 OpenAlex 中的标题截止于冒号时，能否用出版商的 DOI 来确认它 (data/work/step2_anchors.md)。
