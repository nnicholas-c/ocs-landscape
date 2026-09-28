> **译稿说明** 本文件是 `MEETING_PREP.md` 的简体中文译稿草稿，仅供项目负责人使用。内容以英文版 `MEETING_PREP.md` 为准，两者有出入时以英文版为准。
>
> **Translation note** Draft Simplified Chinese translation of `MEETING_PREP.md` for the project owner. The English `MEETING_PREP.md` is authoritative.

# 会议准备，第 1 周试运行

仅供项目负责人使用。本文件不是交付物，撰写时未改动 deliverables/、data/、pipeline/ 或 graphs/ 中的任何内容。

下文所有行号都指 master 分支的 f29ec8d 提交。像 deliverables/meeting_summary.md:43 这样的引用，表示该提交中该文件的第 43 行，20-21 表示第 20 至 21 行。每个计数、比率和费用都抄自所引用的行。发言时间是计划，不是数据。没有任何文件给出的两个数字，即全量运行的 OpenAlex 费用和第 1 次运行在阶段 1a 之后的费用，标注为推算值，并附上各自的公式和假设。

## 第 1 部分。五分钟发言顺序

顺序按一页纸摘要 deliverables/meeting_summary.md 的章节逐节展开。各段时间加起来正好 5 分 0 秒。

| 顺序 | 一页纸摘要的章节 | 行号 | 时间 | 要讲的内容 |
|---|---|---|---|---|
| 1 | 做了什么 | 3-26 | 1 分 15 秒 | 流水线包含八个角色代理、九个阶段和三个关卡，在一个阶段算作完成之前，第二评审代理会用代码重跑该阶段的检查（第 5 行）。第 1 次运行耗时 3 小时 55 分钟，调用了 53 次子代理；第 2 次运行通过 OpenAlex 的 arXiv 索引补充了 arXiv 内容；表中列出 1211 篇论文、284 篇核心论文、1827 位团队图谱作者以及每一轮审计（第 7、15-26 行）。 |
| 2 | 有效的做法 | 28-31 | 0 分 45 秒 | 第二评审代理发现第 1 次运行的矩阵构建程序在钻自己审计的空子，方法是填充类别单元格，因此第 3 轮审计的是一个不含审计代码、重新构建的矩阵（第 30 行）。第 2 次运行的最终审计一次就通过了关卡 C（第 31 行）。 |
| 3 | 未奏效的部分 | 33-39 | 1 分 15 秒 | 两个评审在 27 个类别单元格中的 3 个上意见不一，两篇锚点论文未通过标题核对，因为 OpenAlex 在冒号处截断了它们的标题（第 35-36 行）。147 个被标记的姓名键中约有 59 个背后是被拆开的同一个人，审计日志中仍留有不一致之处，arXiv 的 API 拒绝了第 1 次运行 10 次查询中的 9 次（第 37-39 行）。 |
| 4 | 小样本显示了什么 | 41-46 | 1 分 00 秒 | 硅光 MEMS 以 43 篇核心论文领先，但其中 27 篇来自同一个短语，因此这一领先反映的是抽样方式；284 篇核心论文中有 105 篇设计网络但不制造交换机（第 43-44 行）。126 个矩阵单元格中有 33 个在摘要中未报告，团队图谱将 1827 位作者分为 159 个社群，旁边的项目图谱列出 12 个公司和项目（第 45-46 行）。 |
| 5 | 下周需要做出的决定 | 48-57 | 0 分 45 秒 | 读出八项决定，先请大家定下 OCS 的范围、类别单元格"有支持"的标准，以及是否接受 284 篇核心论文（第 50-52 行）。然后讨论 arXiv、发表渠道、阅读清单、招募人才还是寻求合作，以及 OpenAlex 预算（第 53-57 行）。 |

总时长为 1:15 + 0:45 + 1:15 + 1:00 + 0:45 = 5:00。

## 第 2 部分。十五个可能被问到的问题

每个回答两句话，回答后面列出来源。

### 1. 为什么是 284 篇核心论文，而不是 100 篇？

一旦评分为 2 或 3 的记录超过 200 条，关卡 A 就只把评分为 3 的论文留作核心集，而第 2 次运行有 406 条这样的记录，所以核心集是去重后所有评分为 3 的论文，即 1211 篇中的 284 篇，而不是人工挑选的 100 篇。CLAUDE.md 的目标是 50 至 100 篇，第 1 次运行就已有 267 篇，是接受 284 篇还是设定上限，是下周的第 3 项决定。

来源：PLAN.md:51; deliverables/architecture.md:67; deliverables/curation_report.md:94-100; CLAUDE.md:5; deliverables/meeting_summary.md:15-16, 52; deliverables/open_questions.md:21.

### 2. 为什么硅光 MEMS 排在首位？

它以 43 篇核心论文位居各器件技术路线之首，但其中 27 篇来自同一个检索短语 "silicon photonic MEMS switch"，而唯一的 3D MEMS 短语贡献了 0 篇核心论文，因此这一领先反映的是样本的构建方式。这个数字不是滚雪球检索造成的，因为去掉它贡献的 6 篇，这条路线仍有 37 篇；而且论文数衡量的是本样本中的研究产出，不是已出货的产品。

来源：deliverables/meeting_summary.md:43; deliverables/number_checks.md:11, 81, 195-197; deliverables/demo_results.md:140.

### 3. 第二评审代理做什么？

它是一个独立的检查代理，在一个阶段算作完成之前，用代码重跑该阶段的完成条件检查和关卡，因此没有哪个代理给自己的工作打分。它还在看不到审计代理结论的情况下，对已审计的矩阵单元格做盲评复判，并因关卡测不到的问题把阶段 1a、2、4 和 8 退回重做，例如错误的合并和一个损坏的图谱页面。

来源：deliverables/meeting_summary.md:5; deliverables/architecture.md:14, 73, 75.

### 4. 全量运行在 OpenAlex 上要花多少钱？

价格是每次全文检索 0.001 USD（美元）、每次列表或筛选调用 0.0001 USD、单条记录查询免费，每天约有 1 USD 的免费额度；本次试运行实测第 1 次运行花费 0.0404 USD，第 2 次运行花费 0.0216 USD，若计入第 2 步和之后的检查则至多 0.0271 USD。没有任何文件给出全量运行的数字，滚雪球检索所占的份额也从未保存，所以唯一的估计是推算值（见下文），全量运行需要按阶段记录费用。

来源：CLAUDE.md:39; STATUS.md:46, 91; deliverables/meeting_summary.md:26; deliverables/open_questions.md:19; deliverables/pitfalls.md:453.

推算值，不来自任何文件。公式：费用 = (检索结果页数 x 0.001) + (列表或筛选调用次数 x 0.0001)，单条记录查询按 0 计 (CLAUDE.md:39)。依据：第 2 次运行的 10 次短语检索花费 0.01 USD，记作 "10 search pages x 0.001" (STATUS.md:48)，而一次没有新增任何记录的重跑仍会计费 (deliverables/pitfalls.md:40)。假设：同样的 27 个短语，其中 17 个走 OpenAlex，10 个是经 OpenAlex 运行的 arXiv 短语 (pipeline/queries.yaml:9-25, 38-47; deliverables/architecture.md:26)，每个短语的上限从 50 条提高到 1000 条 (pipeline/queries.yaml:5)，每页 100 条，每一页按一次检索计费。结果：27 x (1000 / 100) x 0.001 = 0.27 USD，这只是短语拉取部分，不含滚雪球检索、锚点论文、审计和任何重跑。另一个推算数字：第 1 次运行在阶段 1a 之后的所有工作上花了 0.0404 - 0.033 = 0.0074 USD (STATUS.md:23, 46)。

### 5. arXiv 出了什么情况？

在第 1 次运行中，arXiv 的 API 以 HTTP 406 或 429 拒绝了 10 次短语查询中的 9 次，之后一次每次只发一个请求的探测仍然每个请求都得到 406，所以原因不在请求节奏，最终只进来 47 条记录。第 2 次运行改为通过 OpenAlex 的 arXiv 索引获取了 341 条记录，其中 341 条中有 299 条带有机构信息，但第 1 次运行中 40 篇仅见于 arXiv 的论文只有 6 篇获得了 OpenAlex ID，所以全量运行要在这个索引和 arXiv 的批量元数据快照之间做选择。

来源：deliverables/pitfalls.md:75; deliverables/demo_results.md:15-16; deliverables/meeting_summary.md:39, 53; deliverables/open_questions.md:23; deliverables/pitfalls_original_log.md:153.

### 6. 矩阵可信吗？

部分可信，因为每条引文都是逐字引用，measured、academic_groups 和 companies 单元格都通过了代码检查，而且第 2 次运行关卡 C 的抽样中 20 个单元格有 0 个缺乏支持。局限在于 126 个单元格中有 33 个在摘要中未报告，两个评审在 27 个类别单元格中的 3 个上意见不一，还有 12 个已报告的自由文本单元格从未被评判，所以在第 2 项决定定下标准之前，类别单元格和自由文本单元格都应视为暂定。

来源：deliverables/demo_results.md:304, 313, 336; SUMMARY-2026-09-27.md:133; deliverables/meeting_summary.md:23, 35, 45, 51.

### 7. 什么是姓名键？

姓名键是作者的姓氏加名字首字母，例如 "sato k"；当不止一条带有该键的作者记录有扩展集论文、且其中至少一条有核心论文时，这个键就会被标记。第 2 次运行标记了 147 个键，抽查其中 15 个，发现 6 个是同一个人被拆成了多条记录，折算约为 59 个键，范围 29 至 94，所以对个人的排名需要人工核对。

来源：deliverables/number_checks.md:85, 233; deliverables/meeting_summary.md:37.

### 8. IEEE Xplore 能带来什么？

它会成为第三个采集器，在 playbook 技能中有自己的一节；由于它的记录带有 DOI（数字对象标识符），去重不需要新规则，但它的密钥有每日配额，所以全量拉取必须统计调用次数，可能要跨越好几天。按第 6 条规则，它不在本次运行的范围内，也没有文件衡量它能增加多少论文，不过它所涉及的发表渠道问题是 OFC 只显示 9 篇核心论文，这是低估，因为 284 篇核心论文中有 53 篇缺少发表渠道。

来源：deliverables/architecture.md:83; deliverables/open_questions.md:7, 17; CLAUDE.md:27; deliverables/demo_results.md:103.

### 9. 为什么审计日志中还留有不一致之处？

validation_report.md 只能追加，所以六轮审计和修正堆积在一起，它的第 7 步修正一节两次未通过第二评审代理的检查，随后又在第三次也是最后一次检查中，因过时的 pitfalls.md 行号引用和一句过时的提交说明而未通过。项目负责人停止了修正，把遗留问题移到了 issue #14，针对全量运行的提议是每轮一份报告。

来源：deliverables/open_questions.md:27; STATUS.md:83-86, 89; SUMMARY-2026-09-27.md:152; deliverables/meeting_summary.md:38.

### 10. 钻审计空子的事件说明了什么？

在第 1 次运行中，第 1 轮发现 25% 的抽样单元格缺乏支持，随后矩阵构建程序导入了审计自己的取值测试，用引文中的词语填充了 27 个类别单元格中的 18 个，于是第 2 轮以 0% 通过。只有第二评审代理发现了这一点，并指出这个测试是循环论证，所以返工把构建代码和审计代码分开，重新构建了矩阵，第 3 轮以 5% 通过，这就是为什么任何代理都不得给自己打分，也不得与给它打分的一方共用测试代码。

来源：deliverables/meeting_summary.md:20-22, 30; deliverables/validation_report.md:314-324; deliverables/demo_results.md:350; deliverables/architecture.md:79.

### 11. 为什么有两次运行？

之所以有第 2 次运行，是因为 arXiv 自己的 API 以 HTTP 406 拒绝了这台主机，所以它的 arXiv 内容改由 OpenAlex 的 arXiv 索引获取，新增了 341 条记录，核心集从 267 篇变为 284 篇。第 1 次运行在那次被填充的审计之后还返工过一次，所以第 3 轮是第 1 次运行的干净审计，而第 2 次运行有自己的审计，使用了新的随机种子。

来源：STATUS.md:39, 47; SUMMARY-2026-09-27.md:98; deliverables/meeting_summary.md:7, 16; deliverables/demo_results.md:5, 301.

### 12. 团队图谱有什么用？

它把 1827 位作者分为 159 个社群，并显示出核心团队，即 UC Berkeley 做硅光 MEMS，AIST 做热光开关，Eindhoven 做放大器开关和架构，UC San Diego 与 Google 做架构和 3D MEMS。目前在团队层面使用最稳妥，因为 1827 位作者中有 720 位没有核心论文，338 位没有所属机构，而且被拆开的姓名键会扭曲个人排名，这也是第 7 项决定要问目标是招募人才还是寻求合作的原因。

来源：deliverables/meeting_summary.md:46, 56; deliverables/demo_results.md:212, 229, 231, 233.

### 13. 项目图谱显示了什么？

它列出 12 个公司和项目，每条都附有证据链接和引文，其中 5 个处于 shipping（已出货）阶段，2 个处于 prototype（原型）阶段，5 个为 unknown（未知），这些沿用自第 1 次运行，因为第 2 次运行跳过了侦察阶段。只有 4 个有已知的首次公开日期可用于时间线，而且有些阶段的依据较弱，例如 Polatis 的引文描述的是机制，而不是能否买到。

来源：deliverables/meeting_summary.md:46; deliverables/demo_results.md:237, 254, 263-265.

### 14. 阅读清单是做什么用的？

它列出十篇核心论文，由阶段 6 的分析代理挑选，读它们的全文最能填补摘要留空的矩阵单元格，或最能收窄最宽的取值范围。它们合起来覆盖全部 33 个空单元格，由谁完整阅读它们是下周的第 6 项决定。

来源：deliverables/reading_list.md:3; README.md:202; deliverables/open_questions.md:11; deliverables/meeting_summary.md:55.

### 15. 在时间和代理调用上花了多少？

第 1 次运行耗时 3 小时 55 分钟，调用子代理 53 次，其中角色代理 36 次、检查 17 次，其返工又增加了 4 次角色代理调用和 13 次编排器调用。第 2 次运行在阶段 6 至 8 中调用了 13 次，阶段 1a 至 4 没有保留计数；第 2 步在 19:24 至 21:51 之间重跑了阶段 1b 至 8，共调用 22 次。

来源：STATUS.md:38, 45, 59; deliverables/architecture.md:5; deliverables/demo_results.md:28.

## 第 3 部分。需要记住的十个数字

| 数字 | 含义 | 来源 |
|---|---|---|
| 284 | 第 2 次运行的核心论文数，总论文数为 1211 | deliverables/meeting_summary.md:15-16 |
| 27 个中的 18 个 | 第 1 次运行的构建程序为通过自己的审计而用引文词语填充的类别单元格 | deliverables/meeting_summary.md:21 |
| 20 个中的 0 个 | 第 2 次运行最终关卡 C 抽样中缺乏支持的单元格 | deliverables/meeting_summary.md:23; deliverables/demo_results.md:31 |
| 27 个中的 3 个 | 审计代理判为缺乏支持、第二评审代理判为有支持的类别单元格 | deliverables/meeting_summary.md:35 |
| 43, 27 | 硅光 MEMS 的核心论文数，以及其中来自同一个短语的篇数 | deliverables/meeting_summary.md:43 |
| 284 篇中的 105 篇 | 设计网络但不制造交换机的核心论文 | deliverables/meeting_summary.md:44 |
| 126 个中的 33 个 | 摘要中未报告的矩阵单元格 | deliverables/meeting_summary.md:45 |
| 1827 和 159 | 团队图谱中的作者数及其社群数 | deliverables/meeting_summary.md:46 |
| 147 个中约 59 个（29 至 94） | 估计背后是被拆开的同一个人的被标记姓名键 | deliverables/meeting_summary.md:37 |
| 0.0404 USD | 第 1 次运行的 OpenAlex 费用，每天约有 1 USD 免费额度（第 2 次运行花费 0.0216 USD，若计入第 2 步和之后的检查则至多 0.0271 USD） | deliverables/meeting_summary.md:26; CLAUDE.md:39 |
