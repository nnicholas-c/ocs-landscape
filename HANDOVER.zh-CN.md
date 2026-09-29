# 交接说明（给 Yuxuan）

> 说明：本文件是 HANDOVER.md 的简体中文译稿，以英文版 HANDOVER.md 为准。

写给 Yuxuan（GitHub 账号 liu0029yuxuan），你对本仓库有写权限（`gh api repos/nnicholas-c/ocs-landscape/collaborators`，role_name 为 "write"）。文中每个数字都抄自其旁边注明的文件或命令。HANDOVER.zh-CN.md（即本译稿）是中文草稿，以英文原文为准。

## 1. 项目是什么，进展到哪里

这是一个由代理驱动的流水线，利用 OpenAlex 和 arXiv 梳理面向 AI 数据中心的光电路交换（OCS），产出技术、团队和项目三张图谱。它是第一周的小样本试运行，不是完整报告（README.md）。第 1 次和第 2 次运行都已完成，STATUS.md 中九个阶段全部打勾。第 2 次运行有 1211 篇论文，其中核心论文 284 篇（deliverables/curation_report.md，第 48 行和第 100 行）。撰写本文时，master 位于 b861015，即 #21 的合并提交（`git log -1 --format=%h origin/master`）。标签有 run1（8172417）、run1-fixed（874ee9c）、run2-early-wip（6ad1c6f）和 run2-final（提交 908917f）（`git ls-remote --tags origin`）。汇报时使用 deliverables/meeting_summary.md（一页纸摘要）、MEETING_PREP.md（发言顺序和可能的提问）以及 SUMMARY-2026-09-27.md（master 上有什么、哪些事需要人来做）。

## 2. 环境准备

1. `gh repo clone nnicholas-c/ocs-landscape`。
2. Python 3.11 或更新版本（README.md，Setup）。运行 `python -m venv .venv`，再运行 `.venv/bin/pip install -r requirements.txt`（Windows 上用 `.venv\Scripts\pip`）。
3. 在 https://openalex.org/settings/api 申请你自己的免费 OpenAlex 密钥，运行 `cp .env.example .env`，并设置 OPENALEX_API_KEY。项目负责人的密钥从不提交，因为 .env 已被 gitignore 忽略（.gitignore，第 4 行）。
4. 在 Windows 上，按 README.md 的 Setup 一节中的垫片（shim）说明操作。它让 .venv/bin/python 以 PYTHONUTF8=1 调用 .venv/Scripts/python.exe，这样非 ASCII 标题不会让控制台崩溃。
5. 确定性步骤见 README.md 的 "Running the deterministic steps" 一节，其中有从已提交数据重建输出的顺序。判断阶段见 README.md 的 "Running the judgement stages" 一节，需要一个能加载 CLAUDE.md、.claude/agents 和 .claude/skills、并让侦察代理（scout）能做网页搜索和抓取的代理环境（README.md，第 124 行）。
6. 恢复运行时，在仓库根目录打开一个代理会话，让它按 PLAN.md 从 STATUS.md 中第一个未打勾的阶段继续（README.md，同一节）。目前所有阶段都已打勾，所以下一次运行从一份 PLAN-run3.md 开始，这份文件还没有写（第 4 节说明其中要写什么）。

## 3. 本项目的工作方式

- 每项修改都放在一个分支上，然后开拉取请求（pull request）。
- 代码评审发布在拉取请求上（#1 和 #17 是常见格式）。
- 在分支上修复评审发现的问题，并在评论中说明修了什么。
- 用合并提交（merge commit）合并（`git log --merges origin/master`）。
- STATUS.md、deliverables/pitfalls_original_log.md 和 deliverables/validation_report.md 只能追加。旧行有误时，追加新行来更正，不要改旧行（STATUS.md，第 3 行；deliverables/pitfalls_original_log.md，第 5 行；deliverables/validation_report.md，第 1981 行）。
- 数字不能凭记忆写。数字只能来自脚本或带引文的原文句子，缺失的内容就写 "not reported"（CLAUDE.md，硬性规则 1 和 3）。
- 第二评审代理检查每个阶段。一个独立代理先用代码重跑该阶段的检查和关卡，阶段才算完成，并盲审审计单元格（deliverables/meeting_summary.md，第 5 行）。它的指令还不在仓库里（README.md，Second judge），所以第 3 次运行前要先把它写下来。

已合并的拉取请求（`gh pr list --state merged --json number,title`）：#1 通过 OpenAlex 的 arXiv 索引做第 2 次运行；#4 步骤 2，锚点论文；#6 步骤 3，技术图谱和时间线；#7 步骤 4，数字核查；#8 步骤 5，基于第 2 次运行的一页纸摘要；#9 步骤 6，README 和 CONTRIBUTIONS；#12 步骤 7，validation_report.md 更正；#15 步骤 7，一页纸精简；#17 步骤 7，项目负责人的 B 方案修改；#18 步骤 8，SUMMARY-2026-09-27.md；#19 会议准备稿；#21 运行后的代理检查。#1 到 #17 都有发布的评审，#18 和 #21 各有一条核查评论，#19 两者都没有（`gh pr list --state merged --json number,comments,reviews`）。

## 4. 待办工作（按顺序）

1. **先做 issue #13。** 用匹配方法 doi_publisher_confirmed 加入 Jupiter Evolving（DOI 10.1145/3544216.3544265）和 RotorNet（DOI 10.1145/3098822.3098838）。ACM Digital Library 的页面对脚本返回 HTTP 403，这个拦截不能绕过（issue #13，2026-09-27T08:51:29Z 的评论）。所以要由一个人在浏览器里（或通过其他在范围内的来源）确认标题、会议或期刊、年份和第一作者。这一步已经完成：2026-09-28 在浏览器中核对了两篇论文的 ACM 页面，两篇都与步骤 2 找到的 OpenAlex 记录一致（issue #13，2026-09-29T05:55:29Z 的评论）。然后脚本按 DOI 获取 OpenAlex 记录（免费的单条查询），当 OpenAlex 截断的标题是完整标题的前缀、且年份和第一作者一致时接受。这会用新的随机种子和盲审的第二评审代理重跑阶段 6 到 8（issue #13）。
2. **再做 issue #20。** 有 4 次模糊标题合并把不同的出版物合在了一起（deliverables/curation_report.md，第 69、70、71 和 80 行）。先定规则：每篇出版物各算一篇论文，还是会议版和期刊版算同一项工作。如果分开算，就在 pipeline/curate.py 中加一道保护，使 DOI 不同且都非空的两条记录永远不做模糊合并，然后从阶段 2 起重跑（issue #20）。这样一次阶段 2 到 8 的重跑也能把 #13 一起覆盖。
3. **其余未关闭的 issue**（`gh issue list --state open`）：
   - #14。validation_report.md 中遗留的不一致，按项目负责人的决定保留。
   - #10。"SIGCOMM 核心论文 0 篇" 主要反映的是缺失的会议信息，53 篇无会议信息的核心论文中有 15 篇带 ACM DOI（issue #10）。
   - #5。graphs/clusters.csv 中成员的顺序取决于 PYTHONHASHSEED。
   - #3。合并记录时，如果保留的记录没有 arXiv ID，curate 会丢掉被合并记录的 arXiv ID。
   - #2。用免费的 DOI 查询为只有 arXiv 的论文补齐 OpenAlex 记录。

会后，在任何新运行之前，把八项决定写进 PLAN-run3.md（deliverables/meeting_summary.md，第 50 到 57 行）。它们是：OCS 的范围；接受 284 篇核心论文还是设上限；类别单元格 "有支持" 的标准；arXiv 的获取途径；会议范围；谁来读阅读清单；团队图谱的目的是招募还是合作；OpenAlex 预算。

## 5. 专门给 Yuxuan 的事项

- 审阅 deliverables/meeting_summary.zh-CN.md 和 MEETING_PREP.zh-CN.md。两者都是草稿，以英文版为准（见各自开头的说明）。
- README.zh-CN.md 仍是按提交 5a25410 的 README.md 翻译的，（见其开头说明），那是第 2 次运行之前的状态（CONTRIBUTIONS.md，第 5 行；README.md，第 182 行），需要整体更新。它第 140 行仍用 "迎合"。根据拉取请求 #15 的评审意见，项目负责人更倾向用 "钻自己审计的空子"，与 deliverables/meeting_summary.zh-CN.md 第 34 行一致。
- CONTRIBUTIONS.md 是你的文件。项目负责人在第 5 行加了一条注明身份的说明，说 README.zh-CN.md 译自 5a25410、以 README.md 为准。更新 README.zh-CN.md 时，一并更新或删除这条说明。
- feat/chinese-project-pages 分支（最新提交 f3c1a29）没有拉取请求（`gh pr list --head feat/chinese-project-pages --state all` 返回为空）。它的第 2 次运行数据固定在提交 3859702，早于阶段 6 到 8（该分支的 site/README.md，第 29 行）。它显示 1213 篇论文（该分支的 site/assets/data.js，第 32 行），而 master 上是 1211 篇（deliverables/curation_report.md，第 48 行）。请用当前 master 重建它的数据，再开拉取请求。

## 6. 已知局限

- deliverables/open_questions.md 中的 13 个开放问题。
- Issue #14，deliverables/validation_report.md 中已接受的遗留问题。
- 两位评审在 27 个类别单元格中的 3 个上意见不一，另有 12 个自由文本单元格从未被评审（README.md，Findings to know before using the data）。
- 147 个被标记的姓名键中，估计约 59 个（29 到 94）是同一个人被拆成了多条记录，所以团队图谱宜按团队层面使用（deliverables/number_checks.md，Run 2，section 2）。
- 两个代理（不是人）检查了排名前 20 的作者（16 位是同一个人，4 位被拆分）和 13 次模糊标题合并（9 次是同一篇论文，4 次是不同论文，见 issue #20），已在 #21 中合并（deliverables/demo_results.md，Reviews after the run；data/work/agentcheck_final.md）。在把团队图谱用于招募之前，应由人来确认这 4 位被拆分的作者和 4 次错误合并（deliverables/open_questions.md，第 13 项）。

## 7. 不在仓库里的东西

- 项目负责人 .env 中的 OpenAlex 密钥。
- 本地虚拟环境 .venv。
- 运行期间使用的编排脚本、第二评审代理的指令和临时文件。README.md 的 Second judge 一节说明，第二评审代理的指令目前还不在仓库中。data/work/ 的大部分内容也被 gitignore 忽略（.gitignore，第 6 行）。
