> **译稿说明** 本文件是简体中文译稿草稿，供 Yuxuan（liu0029yuxuan）审阅。内容以英文版 `deliverables/meeting_summary.md` 为准，两者有出入时以英文版为准。本译稿译自 `docs/onepager-final` 分支中的 `deliverables/meeting_summary.md`。
>
> **Translation note** Draft Simplified Chinese translation for review by Yuxuan (liu0029yuxuan). The English `deliverables/meeting_summary.md` is authoritative. Translated from `deliverables/meeting_summary.md` on branch `docs/onepager-final`.

# OCS 技术全景试运行，第 1 周

## 做了什么

光电路交换（optical circuit switching，OCS）流水线包含八个角色代理、九个阶段和三个关卡 (deliverables/architecture.md)。在一个阶段算作完成之前，第二评审代理会用代码重跑该阶段的完成条件检查和关卡；在审计中，它还对已评判的单元格做了盲评复判 (STATUS.md, 15:10 and 21:21 lines)。

第 1 次运行耗时 3 小时 55 分钟，调用了 53 次子代理；第 2 次运行通过 OpenAlex 的 arXiv 索引补充了 arXiv 内容，因为 arXiv 自己的 API（应用程序编程接口）拒绝了我们的客户端 (STATUS.md, 08:27 and 16:50 lines)。

表中未注明轮次的审计行，指第 3 轮审计和第 2 次运行的最终审计。


| 指标 | 第 1 次运行 | 第 2 次运行 | 来源 |
|---|---|---|---|
| 原始记录数，依次来自 OpenAlex 查询、滚雪球检索、arXiv API、OpenAlex 的 arXiv 索引 | 707, 150, 47（10 次查询中 9 次被拒绝）, 0 | 707, 150, 47, 341 | STATUS.md, 05:04, 05:38, 15:58 and 16:08 lines |
| 论文数 | 885 | 1211 | STATUS.md, 05:57 and 20:31 lines |
| 核心集 | 267 | 284 | same |
| 扩展集 | 376 | 420 | same |
| 团队图谱作者数 | 1597 | 1827 | STATUS.md, 06:50 and 20:41 lines |
| 审计 (a)，重新获取后的不一致 | 20 条中 0 条，其中 4 条仅凭标题和年份匹配 | 20 条中 0 条，其中 2 条仅凭标题和年份匹配 | deliverables/number_checks.md, both sections 3 |
| 审计 (b)，20 个抽样单元格中缺乏支持的比例，第 1 次运行第 1 轮 | 25% | | validation_report.md, pull request #1 corrections, item 5 |
| 第 1 次运行第 2 轮（填充后） | 0%，27 个类别单元格中有 18 个被填充 | | same; STATUS.md, 07:42 line |
| 第 1 次运行第 3 轮 | 5% | | same item 5 |
| 第 2 次运行 | | 0% | validation_report.md, seed 20260929 section |
| 审计 (c)，失效的项目链接 | 10 个中 0 个 | 10 个中 0 个 | validation_report.md, item 5; run 2's final audit |
| 审计 (d)，逐字匹配的标签句 | 376 句中 376 句 | 420 句中 420 句 | same |
| OpenAlex 费用，USD（美元） | 0.0404 | 0.0216 至 0.0271。其中在计费日于 17:00 重置之前，检索花费 0.01，重跑花费 0.01；重置之后，到 18:49 已用 0.0016，到次日 02:29 已用 0.0071，后者也包含了之后的检查 | STATUS.md, 16:14, 15:58, 18:49 and 2026-09-27 02:29 lines; deliverables/pitfalls_original_log.md, 16:05 |

## 有效的做法

- 在第 1 次运行中，第二评审代理发现矩阵构建程序在钻自己审计的空子，方法是把引文中的词语填入类别单元格（存放成熟度等标签）(STATUS.md, 07:42 line)，因此第 3 轮审计的是一个不含审计代码、重新构建的矩阵 (STATUS.md, 14:11 to 15:10 lines)。
- 第 2 次运行的最终审计一次就通过了关卡 C（四项检查，其中缺乏支持的单元格至多 10%），不同于第 2 次运行中更早的一次审计 (PLAN.md; deliverables/demo_results.md)。

## 未奏效的部分

- 在第 2 次运行的最终审计中，审计代理判定 27 个类别单元格中有 3 个缺乏支持，第二评审代理则认为它们有支持，且它们都不在关卡 C 的抽样之内 (deliverables/demo_results.md)。
- Jupiter Evolving 和 RotorNet 这两篇锚点论文（流水线应当找到的已知论文）未通过标题核对，因为 OpenAlex 在冒号处截断了它们的标题 (issue #13; data/work/step2_anchors.md)。
- 147 个被标记的姓名键（姓氏加名字首字母）中，约 59 个（29 至 94）实际是同一个人被拆成了多条记录 (deliverables/number_checks.md, Run 2, section 2)。
- 审计日志中仍留有不一致之处，例如过时的行号引用，原因是其修正未能通过第三次也是最后一次检查 (STATUS.md, 01:13 line; issue #14)。
- arXiv 的 API 以 406 或 429 错误拒绝了第 1 次运行 10 次查询中的 9 次，并在之后的一次探测中拒绝了全部请求，因此第 2 次运行改用 OpenAlex 的 arXiv 索引。该索引为 341 条记录中的 299 条提供了机构信息，而来自 arXiv API 的 47 条记录中为 0 条 (deliverables/pitfalls.md, arXiv section; data/raw/arxiv_via_openalex.jsonl; data/raw/arxiv.jsonl)。

## 小样本显示了什么

- 硅光 MEMS（微机电系统）以 43 篇核心论文位居各器件技术路线之首，但其中 27 篇来自同一个检索短语，而唯一的 3D（三维）MEMS 短语贡献了 0 篇，因此这一领先反映的是抽样方式 (data/work/nc1_run2_route_provenance.json)。
- 284 篇核心论文中有 105 篇设计网络但不制造交换机，而矩阵中没有任何一行容纳它们关于 AI（人工智能）集群的论述 (deliverables/demo_results.md, Q4)。
- 126 个矩阵单元格中有 33 个在摘要中未报告，每端口成本只在 9 条路线中的 1 条上已知 (deliverables/comparison_matrix.csv)。
- 团队图谱将 1827 位作者分为 159 个社群 (graphs/top_pis.csv; graphs/clusters.csv; graphs/coauthor.html)。项目图谱列出 12 个公司和项目，每条都附有链接和引文 (data/projects.csv; graphs/project_timeline.html)。

## 下周需要做出的决定

1. OCS 的范围 (deliverables/open_questions.md)。
2. 类别单元格中"有支持"的标准。
3. 是接受 284 篇核心论文（计划为 50 至 100 篇），还是设定上限 (deliverables/curation_report.md; CLAUDE.md)。
4. 全量运行时如何获取 arXiv，是用 OpenAlex 的索引还是 arXiv 的批量快照 (deliverables/pitfalls.md, arXiv access)。
5. 加入 OFC（Optical Fiber Communication Conference，光纤通信会议）、SIGCOMM（Special Interest Group on Data Communication，数据通信专门兴趣小组）和 NSDI（Networked Systems Design and Implementation，网络系统设计与实现研讨会），并去掉 APEC（Applied Power Electronics Conference，应用电力电子会议）、ECCE（Energy Conversion Congress and Exposition，能量转换大会暨博览会）和 PCIM（Power Conversion and Intelligent Motion，电力转换与智能运动）。
6. 由谁完整阅读 deliverables/reading_list.md。
7. 团队图谱的目标是招募人才还是寻求合作。
8. 如何为 OpenAlex 做预算。它现在需要免费密钥并按用量计费 (CLAUDE.md, Environment)。
