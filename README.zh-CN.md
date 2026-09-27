# OCS 技术全景

[English](README.md) | 简体中文

[中文项目汇报网站 · Chinese presentation](https://liu0029yuxuan.github.io/ocs-landscape-presentation/)

> 本文译自提交 `5a25410` 中的英文 README。进度、结果、配额和费用均沿用该版本的描述；“本周”等时间表述指原文的项目安排。个人贡献及后续更新见 [CONTRIBUTIONS.md](CONTRIBUTIONS.md)。

这是一个由代理驱动的流水线，利用开放文献数据源梳理面向 AI 数据中心的光电路交换（Optical Circuit Switching，OCS）。Python 脚本负责确定性步骤，各角色代理负责需要判断的工作。每项判断都保存证据，例如原文引述、论文 ID 或网址，以便核查。流水线构建三类图谱：

1. **技术图谱**：比较 3D MEMS、2D MEMS、硅光 MEMS、LCoS、压电、热光、电光、SOA 和机器人配线架等交换技术路线的切换时间、损耗、端口数、成熟度，以及对 AI 集群的适用性。
2. **团队图谱**：梳理研究 OCS 的团队，以及能力可以迁移到 OCS 的相邻领域团队，包括电信交叉连接、微镜、硅光子、LCoS 显示、自由空间封装和数据中心网络。
3. **项目图谱**：梳理初创公司、成熟供应商和超大规模云服务商的项目，每项均附公开网址和逐字引述。

本仓库保存第一周的小样本试运行，目的是验证流水线可以完整运行，且输出可核查，目前还不是最终的技术全景报告。

## 当前进度

| 里程碑 | 状态 | 位置 |
| --- | --- | --- |
| 第一次运行：完整执行阶段 0 至 8，经过三个检查关卡 | 已完成 | 标签 `run1` |
| 审计修复：将矩阵构建与审计分离，使用新随机种子重跑阶段 6 和 7 | 已完成 | 标签 `run1-fixed` |
| 核查三个受到质疑的数字 | 已完成 | `deliverables/number_checks.md` |
| 修订一页会议摘要，将审计轮次重命名为第 1 轮、第 2 轮（填充后）和第 3 轮（修复后） | 已完成 | `master` |
| 第二次运行：通过 OpenAlex 的 arXiv 索引采集 arXiv 论文，并执行阶段 1b 至 8 | 进行中 | 尚未推送，之后将出现在 `run2` 分支 |

在第二次运行提交之前，应展示 `master` 版本。一页摘要位于 `deliverables/meeting_summary.md`。

## 试运行范围

- **数据源**：仅使用 OpenAlex 和 arXiv，见 `CLAUDE.md` 第 6 条规则。明确不纳入 IEEE Xplore、PCIM、Crossref、专利和付费公司数据。加入 IEEE Xplore、PCIM、专利或公司数据需要哪些条件，记录在 `deliverables/architecture.md` 中。
- **规模**：原目标是 50 至 100 篇核心论文，见 `CLAUDE.md`。当相关记录超过 200 条时，关卡 A 保留全部相关性评分为 3 的记录，去重后得到 267 篇核心论文。是否接受这一规模仍需决定。
- **费用**：OpenAlex 要求使用免费 API 密钥，按用量计费，每天约有 1 美元免费额度。第一次运行花费 0.04 美元。

## 工作方式

流水线共有九个阶段。各阶段由 `PLAN.md` 指定的角色代理执行，并将输出写入磁盘，因此可以根据 `STATUS.md` 中断后继续。工作分为两类：

- **确定性工作**：由 `pipeline/` 中的普通 Python 脚本完成，包括 API 采集、去重、数据库加载、图谱构建、渲染和审计抽样。脚本可以安全地重复运行。
- **判断性工作**：由角色代理完成，包括相关性评分、打标签、矩阵单元格判断、网络调研和类别单元格评估。每个代理遵循 `.claude/agents/` 中的角色文件、共同规则 `CLAUDE.md`，以及角色文件指定的一至两项领域技能。代理通过文件交接工作，见“运行判断性阶段”。

| 阶段 | 角色 | 主要输出 |
| --- | --- | --- |
| 0 冒烟测试 | collector | 每个来源 5 条记录，验证记录结构 |
| 1 采集、相关性评分、滚雪球检索、关卡 A | collector、tagger | `data/raw/*.jsonl`、`data/raw/relevance.csv` |
| 2 整理与去重 | curator | `data/db/papers.sqlite`、`deliverables/curation_report.md` |
| 3 打标签、关卡 B | tagger | `tags` 表 |
| 4 合著者与机构图谱 | grapher | `graphs/` |
| 5 公司与项目调研 | scout | `data/projects.csv` |
| 6 比较矩阵 | analyst | `deliverables/comparison_matrix.csv` 和 `.md`、`deliverables/reading_list.md` |
| 7 审计、关卡 C | auditor | `deliverables/validation_report.md` |
| 8 撰写文档 | writer | 六份会议交付文档 |

**检查关卡**：首次失败时，返回生成相关数据的阶段重做一次；再次失败则停止运行。

- **关卡 A**：相关性评分为 2 或 3 的记录应有 60 至 200 条。超过 200 条时，仅将评分为 3 的论文作为核心集。
- **关卡 B**：所有核心论文都已打标签，且至少 90% 的证据句是对应摘要中的逐字子串。
- **关卡 C**：重新获取记录后的不一致比例不超过 10%，缺乏支持的矩阵单元格不超过 10%，项目证据失败比例不超过 20%，逐字证据通过率至少为 90%。

**第二评审代理**：在此前的运行中，编排层驱动各阶段，一个独立的第二评审代理用代码重新检查每个阶段，通过后才将其标为完成，从而避免阶段自行评定自己的工作。编排层和第二评审代理的指令尚未纳入仓库，因此仅依据 `CLAUDE.md` 和 `PLAN.md` 启动的运行没有第二评审代理。补充这些内容属于待办事项。

**所有代理遵循的规则**：

- 数字必须来自代码计算或引用的原文，不能凭记忆填写。
- 每项结论都附来源，例如论文 ID、CSV 行，或带日期的网址。
- 信息缺失时明确写出“摘要未报告”，不要猜测补全。
- 数据结构约定以 `pipeline/schema.sql` 为准。

## 领域技能

| 技能 | 内容 |
| --- | --- |
| `ocs-domain` | 技术路线分类、技术成熟度等级（TRL）区间、AI 适用性取值、相关性判定规则、相邻领域和调研初始实体 |
| `openalex-arxiv-playbook` | API 用法、原始记录结构、去重和合并规则，以及已知 API 故障模式 |
| `comparison-framework` | 矩阵维度、长格式 CSV 和单元格填写规则 |
| `report-format` | 交付文档模板、长度限制和文风规则 |

## 环境设置

需要 Python 3.11 或更新版本，原项目使用 3.14 测试。

1. 使用 `python -m venv .venv` 创建虚拟环境。
2. 使用 `.venv/bin/pip install -r requirements.txt` 安装依赖；Windows 使用 `.venv\Scripts\pip`。
3. 在 <https://openalex.org/settings/api> 获取免费 OpenAlex 密钥，执行 `cp .env.example .env`，填写 `OPENALEX_API_KEY`。该密钥是必需的，未设置时 `collect_openalex` 和 `audit` 会停止。arXiv 无需密钥。

Windows 的解释器路径为 `.venv\Scripts\python.exe`，控制台默认代码页在处理非 ASCII 标题时会导致程序出错。在 Git Bash 中，将下面内容写入 `.venv/bin/python`，然后运行 `chmod +x .venv/bin/python`。在 PowerShell 中，设置 `$env:PYTHONUTF8=1`，再调用 `.venv\Scripts\python -m pipeline.<module>`。

```sh
#!/bin/sh
PYTHONUTF8=1 exec "$(dirname "$0")/../Scripts/python.exe" "$@"
```

## 运行确定性步骤

在仓库根目录下，使用 `.venv/bin/python -m pipeline.<module>` 运行各模块。有命令行选项的模块可通过 `--help` 查看选项。其余模块不接受选项，会忽略 `--help`，因此添加它仍会实际运行模块。

| 模块 | 用途 |
| --- | --- |
| `collect_openalex` | 将 OpenAlex 记录采集到 `data/raw/`；使用 `--mode smoke`、`full` 或 `snowball`，且必须提供 `--out <file>.jsonl` |
| `collect_arxiv` | 采集 arXiv 记录；使用 `--mode smoke` 或 `full`，并提供 `--out` |
| `tag_export`、`tag_import` | 导出供标签代理处理的批次文件，并导入标签；使用 `--mode relevance` 或 `full`。`tag_export --mode full --only <file>` 用于对文件中每行一个的论文 ID 重新打标签 |
| `curate` | 依次按 DOI、arXiv ID 和模糊标题去重，并加载到 `papers.sqlite` |
| `graph` | 构建合著者与机构图谱、排名和 `coauthor.html` |
| `matrix_export`、`matrix_build`、`matrix_render` | 导出技术路线文件，根据分析代理记录的单元格判断构建矩阵 CSV，并渲染 Markdown |
| `audit` | 使用固定随机种子执行关卡 C 的检查 (a) 至 (d)，需要 OpenAlex 密钥和网络。`--merge` 将判断前的结果与审计代理的判断合并 |
| `check_route_provenance`、`check_name_keys`、`merge_name_keys` | 执行 `deliverables/number_checks.md` 所依据的数字核查 |
| `test_curate`、`test_tag_pipeline` | 回归检查 |

若要利用已提交的数据重建输出，请依次运行 `curate`、`graph`、`matrix_export`、`matrix_build` 和 `matrix_render`。数字核查和两个测试也可使用已提交的文件运行。

`matrix_build.py` 不从 `audit.py` 导入任何内容。在审计修复过程中，分析代理先重建矩阵，之后才重写 `audit.py`，因此分析代理没有看到新的测试。目前还没有规则强制保证这一点。

## 运行判断性阶段

这些阶段无法仅靠脚本运行。它们需要一个代理运行环境，能够将 `CLAUDE.md` 作为持续适用的指令，将 `.claude/agents/` 中的角色文件作为子代理启动，并加载 `.claude/skills/` 中的技能，同时为调研代理提供网页搜索和抓取能力。要启动或恢复运行，在仓库根目录打开会话，要求它按照 `PLAN.md`，从 `STATUS.md` 中第一个未勾选的阶段继续。

| 角色 | 交回的文件 | 读取方 |
| --- | --- | --- |
| tagger | `data/work/relevance_batch_NNN.out.json`、`data/work/tag_batch_NNN.out.json` | `tag_import --mode relevance`、`tag_import --mode full` |
| scout | `data/projects.csv` | `matrix_build`、`audit` |
| analyst | `data/work/matrix_cells.yaml` | `matrix_build` |
| auditor | `data/work/audit_run2_judgments.json` | `audit --merge` |
| writer | `deliverables/` 中的六个文件 | 读者 |

## 已有结果

以下数字来自原文所述的 `master` 版本。

| 指标 | 数值 | 来源 |
| --- | --- | --- |
| 原始记录到去重后论文 | 904 条到 885 篇 | `deliverables/curation_report.md` |
| 核心集与扩展集 | 267 篇和 376 篇 | `deliverables/curation_report.md` |
| 团队图谱中的作者 | 1597 人，分属 143 个社群 | `graphs/top_pis.csv`、`graphs/clusters.csv` |
| 公司与项目记录 | 12 条，每条均附网址和引述 | `data/projects.csv` |
| 矩阵单元格 | 126 个，其中 81 个有报告值、9 个为推导值、32 个未报告、4 个无来源 | `deliverables/comparison_matrix.csv` |
| 关卡 C，第 3 轮 | 不一致 0%，缺乏支持 5%，项目失败 0%，逐字证据 100% | `deliverables/validation_report.md` |

**命名说明**：`data/work/audit_run2_*.json`、`pipeline/audit.py` 的文档字符串，以及 `STATUS.md` 中 16:00 之前的日志，用“run 2”指代本文所称的第 3 轮审计。该审计与 arXiv 的第二次运行无关。

**使用数据前需要了解的问题**：

- **发现矩阵构建迎合审计的是第二评审代理，而不是审计本身。** 第 2 轮中，构建程序导入审计测试，并在 27 个类别单元格中的 18 个里填入引文词语以通过测试。该轮关卡 C 给出的缺乏支持比例为 0%，只有第二评审代理指出问题。修复时将构建与审计分离，用简洁标签重建矩阵，并使用新随机种子重新审计。缺乏支持的比例从第 1 轮的 25%，变为第 2 轮的 0%（不可信），再变为第 3 轮的 5%。
- **硅光 MEMS 以 43 篇核心论文领先各器件路线，与样本构建方式有关。** 其中 27 篇来自一个检索词组；3D MEMS 检索词组没有增加新的核心论文；词组检索从 2012 年开始，很可能遗漏了更早的 3D MEMS 研究。
- **同一作者被拆分成多条记录。** 149 个被标记的姓名键由“姓氏加名字首字母”组成，每个键对应多个作者记录，且至少一条记录关联核心论文。抽查 15 个键后，有 10 个符合作者被拆分的情况，据此估计 62 至 126 个键对应同一人被拆成两条或更多记录。用团队图谱招募个人之前，应先解决这一问题。
- **arXiv API 拒绝了 10 个词组查询中的 9 个**，主要返回 HTTP 406，部分返回 429，最终只有 47 条 arXiv 记录。后续逐个发送请求的探测仍全部返回 406，表明请求节奏并非原因。第二次运行改为通过 OpenAlex 的 arXiv 索引获取内容，并明确标注来源方式。

## 待完成事项

**本周**

- [ ] 完成第二次运行，推送至 `run2` 分支，并提供第一次与第二次运行的对比表。
- [ ] 通过 DOI 获取缺失的两篇种子论文 Jupiter Evolving 和 RotorNet，单条查询免费。真正的 c-Through 论文已经通过滚雪球检索进入核心集。
- [ ] 将整理代理的子集匹配保护规则应用于 `collect_openalex` 的种子论文匹配器；该匹配器此前将一篇无关的 1999 年论文误认作 c-Through。
- [ ] 提交编排层和第二评审角色，或将第二评审步骤写入 `PLAN.md`，使其成为仓库的一部分。
- [ ] 在 `.claude/agents/analyst.md` 和 `PLAN.md` 第 6 阶段中，禁止分析代理读取或导入 `pipeline/audit.py`。
- [ ] 在审计中独立重算矩阵的学术团队和公司单元格；当前审计复用了构建程序的对应函数。
- [ ] 按阶段记录 OpenAlex 费用；滚雪球检索的费用未保存。

**需要决定的事项，见 `deliverables/open_questions.md`**

- [ ] OCS 的范围，包括光分组交换机和超大规模云服务商博客是否纳入。
- [ ] 判断类别单元格“有证据支持”的标准。审计代理检查全部 27 个类别单元格后，认为其中 3 个缺乏支持，分别为 3D MEMS 和 2D MEMS 的集成单元格，以及压电路线的成熟度单元格。
- [ ] 接受 267 篇核心论文，还是增加数量上限。
- [ ] 团队图谱用于招募个人还是寻找合作伙伴；前者需先完成作者消歧。
- [ ] 是否重点覆盖 OFC、SIGCOMM 和 NSDI，目前分别有 9、0、0 篇核心论文；以及 APEC、ECCE 和 PCIM 等电力电子会议是否应纳入范围。

**完整规模运行**

- [ ] 使用 arXiv 批量元数据快照替代其 API。
- [ ] 将 IEEE Xplore 加入为第三个采集源，并在操作手册中增加 IEEE 章节，其需要密钥且有每日配额。若 PCIM 属于研究范围，可通过手动导出或类似调研代理的方式加入，因为它没有 API。为专利新增采集器和技能；通过提高调研代理的数量上限并使用真实浏览器获取公司数据，见 `deliverables/architecture.md`。
- [ ] 为 101 篇仅讨论架构的核心论文增加矩阵视图，目前它们关于 AI 集群的结论尚未进入任何单元格。
- [ ] 完整阅读 `deliverables/reading_list.md` 中的十篇论文，它们针对摘要未能填充的 32 个单元格中的 23 个。

## 仓库结构

```text
README.md               英文项目说明
README.zh-CN.md         中文项目说明
CONTRIBUTIONS.md        个人贡献记录及后续更新模板
PLAN.md                 九个阶段、对应输出和检查关卡
STATUS.md               检查点日志，每个阶段事件一行
CLAUDE.md               所有代理遵循的规则
.claude/agents/         八个角色定义
.claude/skills/         四份领域技能文档
pipeline/               阶段脚本、schema.sql、queries.yaml
data/raw/               API 采集的 JSONL 原始记录，以及 relevance.csv
data/db/papers.sqlite   整理后的数据库
data/work/              批次文件和审计输入，多数被 Git 忽略；交付文档或脚本需要的文件已提交
data/projects.csv       调研代理的公司与项目表
graphs/                 GraphML、排名、社群和 coauthor.html
deliverables/           会议文档、矩阵、审计和问题日志
```

原文说明：没有提交密钥等机密信息，`.env` 已被 Git 忽略，且仓库历史已扫描过 API 密钥。
