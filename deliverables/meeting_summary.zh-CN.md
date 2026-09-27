> **译稿说明** 本文件是简体中文译稿草稿，供 Yuxuan（liu0029yuxuan）审阅。内容以英文版 `deliverables/meeting_summary.md` 为准，两者有出入时以英文版为准。本译稿译自 `docs/one-pager-short` 分支上的 `deliverables/meeting_summary.md`。
>
> **Translation note** Draft Simplified Chinese translation for review by Yuxuan (liu0029yuxuan). The English `deliverables/meeting_summary.md` is authoritative. Translated from `deliverables/meeting_summary.md` on branch `docs/one-pager-short`.

# OCS 技术全景试运行，第 1 周

## 做了什么

光电路交换（optical circuit switching，OCS）流水线包含八个角色代理、九个阶段和三个关卡。第二评审代理独立复核每个阶段 (deliverables/architecture.md; data/work/audit_s20260929_second_judge.json)。

第 2 次运行通过 OpenAlex 的 arXiv 索引获取 arXiv 记录，第 2 步（锚点论文）重跑了除调研代理以外的阶段 1b 至 8 (STATUS.md, 16:50 line; deliverables/demo_results.md, Numbers)。

表中未注明轮次的审计行，指第 1 次运行的第 3 轮审计和第 2 次运行的锚点论文审计。


| 指标 | 第 1 次运行 | 第 2 次运行 | 来源 |
|---|---|---|---|
| 原始记录数，依次来自 OpenAlex 查询、滚雪球检索、arXiv API（应用程序编程接口）、OpenAlex 的 arXiv 索引 | 707, 150, 47（10 次查询中 9 次被拒绝）, 0 | 707, 150, 47, 341 | STATUS.md, 05:04, 05:38, 15:58 and 16:08 lines |
| 论文数 | 885 | 1211 | STATUS.md, 05:57 and 20:31 lines |
| 核心集 | 267 | 284 | same |
| 扩展集 | 376 | 420 | same |
| 团队图谱作者数 | 1597 | 1827 | STATUS.md, 06:50 and 20:41 lines |
| 审计 (a)，重新获取后的不一致 | 20 条中 0 条，其中 4 条仅凭标题和年份匹配 | 20 条中 0 条，其中 2 条仅凭标题和年份匹配 | deliverables/number_checks.md, both sections 3 |
| 审计 (b)，20 个抽样单元格中缺乏支持的比例，第 1 次运行第 1 轮 | 25% | | validation_report.md, pull request #1 corrections, item 5 |
| 第 1 次运行第 2 轮（填充后） | 0%，27 个类别单元格中有 18 个被填充 | | same; STATUS.md, 07:42 line |
| 第 1 次运行第 3 轮 | 5% | | same item 5 |
| 第 2 次运行 | | 0% | validation_report.md, audit after the anchor papers |
| 审计 (c)，失效的项目链接 | 10 个中 0 个 | 10 个中 0 个 | validation_report.md, item 5; anchor-papers audit |
| 审计 (d)，逐字匹配的标签句 | 376 句中 376 句 | 420 句中 420 句 | same |
| OpenAlex 费用，USD（美元） | 0.0404 | 检索 0.01，重跑 0.01，总额未知（计费日在运行中途重置） | STATUS.md, 16:14, 15:58 and 18:49 lines; deliverables/pitfalls_original_log.md, 16:05 |

## 有效的做法

- 在第 1 次运行中，第二评审代理发现矩阵构建程序在钻自己审计的空子 (STATUS.md, 07:42 line)。第 1 轮失败后，构建程序导入了审计的测试，把引文中的词语填入成熟度等类别单元格，从而通过了第 2 轮（填充后）。第 3 轮（修复后）审计的是一个不含审计代码、重新构建的矩阵 (table; STATUS.md, 14:11 to 15:10 lines)。
- 第 2 次运行的锚点论文审计一次就通过了关卡 C（审计关卡，缺乏支持的单元格至多 10%） (PLAN.md, stage 7; deliverables/demo_results.md, Audit results)。

## 未奏效的部分

- 修复之后，审计代理判定第 2 次运行 27 个类别单元格中有 3 个缺乏支持，而同时阅读了摘要的第二评审代理认为它们有支持。这些单元格都不在关卡 C 的抽样之内，因此需要由人来决定 (deliverables/demo_results.md, Audit results)。
- Jupiter Evolving 和 RotorNet 这两篇锚点论文（按标题查找的已知论文）在会议结束前仍列为已知局限，因为 OpenAlex 在冒号处截断了它们的长标题，导致标题核对不通过 (issue #13; data/work/step2_anchors.md; deliverables/demo_results.md, Numbers)。
- 根据 15 个键的抽样，第 2 次运行标记的 147 个姓名键（姓氏加名字首字母）中，约 59 个（29 至 94）实际是同一个人被拆成了多条记录 (deliverables/number_checks.md, Run 2, section 2)。第 1 次运行的另一份样本给出的范围更高，因此真实比例并不确定，而不是在下降 (same file)。
- 审计日志中仍留有未解决的不一致之处，主要是引用混用了 deliverables/pitfalls.md 新旧两套行号，原因是其修正未能通过第三次也是最后一次检查 (deliverables/validation_report.md, corrections after the step 7 style and source check; STATUS.md)。

## 小样本显示了什么

- 硅光 MEMS（微机电系统）以 43 篇核心论文位居各器件技术路线之首，但其中 27 篇来自同一个检索短语，而唯一的 3D MEMS 短语贡献了 0 篇，因此这一领先反映的是样本本身 (data/work/nc1_run2_route_provenance.json; deliverables/demo_results.md, Technology and Early project maps)。
- 284 篇核心论文中有 105 篇设计网络但不制造交换机，而矩阵中没有任何一行容纳它们关于 AI（人工智能）集群的论述，这是框架的缺口，而不是研究发现 (deliverables/demo_results.md, Q4)。
- 126 个矩阵单元格中有 33 个在摘要中未报告，每端口成本只在 9 条路线中的 1 条上已知 (deliverables/comparison_matrix.csv)。

## 下周需要做出的决定

1. OCS 的范围 (deliverables/open_questions.md)。
2. "有支持"的标准。类别单元格由代理而不是代码评判，而两位评审对于是否必须仅凭引文本身说明标签意见不一。
3. 是接受 284 篇核心论文，还是将其上限设在计划中的 50 至 100 篇附近 (deliverables/curation_report.md; CLAUDE.md)。
4. 如何获取 arXiv 记录。建议现阶段使用 OpenAlex 的 arXiv 索引，全量运行时使用 arXiv 的批量元数据快照，因为该索引匹配到的仅存于 arXiv 的论文很少 (deliverables/pitfalls.md, arXiv access)。
5. 加入 OFC、SIGCOMM 和 NSDI（光学与网络会议），并去掉 APEC、ECCE 和 PCIM（电力电子）。
6. 由谁完整阅读 deliverables/reading_list.md。
7. 团队图谱的目标是招募人才还是寻求合作。
8. 如何为 OpenAlex 的 API 做预算。它现在需要免费密钥并按用量计费（每天约 1 美元免费额度），这是任务布置时没有预料到的 (CLAUDE.md, Environment)。
