# OCS 中文展示网站

静态 HTML/CSS/JavaScript，无前端依赖，无 API 密钥。主页面是 `index.html`，可直接由 GitHub Pages 发布。

## 本地预览

源码位于 [原项目的 feat/chinese-project-pages 分支](https://github.com/nnicholas-c/ocs-landscape/tree/feat/chinese-project-pages)。以下构建命令针对该源码仓库。个人发布仓库只保存 site/ 的发布内容，不包含完整研究代码或数据生成器。

在源码仓库根目录运行：

```sh
python3 -m http.server 4173 --directory site
```

如果克隆的是个人发布仓库 `ocs-landscape-presentation`，应在它的根目录运行 `python3 -m http.server 4173`，不加 `--directory site`。

访问 http://localhost:4173 。页面包含中文正文、九阶段交互、两轮快照对比、126 格矩阵筛选、证据详情、项目表、图谱、八页汇报模式、打印和资料下载。

## 数据更新

```sh
python3 scripts/build_site_data.py --run1 <完整提交SHA> --run2 <完整提交SHA>
```

脚本从 Git 快照读取 SQLite 与 CSV，生成 `assets/data.js`、图谱与 CSV 下载、原始文档/代码 ZIP。运行环境仅需要 Python 标准库以及包含对应提交的 Git 仓库，不进行 API 请求，不读取 .env。

生成器只更新数据资产。更新之后还必须检查 `index.html`、`assets/app.js`、两份中文下载文档中的版本、研究状态、数字和讲稿。不应仅替换 JSON 就声称网站已经同步。新增字段或阶段变化也需人工核查。

第一轮固定 7901618，第二轮固定 3859702。第二轮的矩阵、审计、最终报告尚未完成；不要给第二轮套用第一轮的审计结果。此页不将全部既有研究归为个人完成。

## 发布

将 `site/` 的内容发布到个人仓库 `liu0029yuxuan/ocs-landscape-presentation` 的 `main` 分支根目录。GitHub Pages source 设为 `main`、`/`，访问 https://liu0029yuxuan.github.io/ocs-landscape-presentation/ 。源项目保留 `feat/chinese-project-pages` 贡献分支。部署使用普通分支构建，无 Actions 写入工作流权限需求。

## 发布前检查

- 运行数据构建脚本，对比基本计数与两轮报告。
- 检查资源路径、锚点、下载与来源链接。
- 桌面/手机无页面横向溢出；表格容器可横向滚动。
- 阶段切换、键盘切换、矩阵筛选/清空、证据弹窗关闭、汇报键盘操作可用。
- 图谱按需加载；不将旧产品网页状态说成当前事实。
- 检查打印版和两份下载文档的版本一致性。

源码维护位置：`site/index.html`、`site/assets/style.css`、`site/assets/app.js`；数据生成器：`scripts/build_site_data.py`。
