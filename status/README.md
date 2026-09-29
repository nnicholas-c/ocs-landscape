# Published project status

Public page: https://liu0029yuxuan.github.io/ocs-landscape-presentation/status/

This is the existing status website from master, updated through b36d9ec. It presents the completed run 2, its remaining limitations, the pipeline walkthrough, and a repository file guide.

Rebuild from the repository root:

```sh
python3 status/build.py
```

Publish `status/index.html` to `status/index.html` in `liu0029yuxuan/ocs-landscape-presentation`, together with `graphs/tech_map.html`, `graphs/coauthor.html`, and `graphs/project_timeline.html` at the same paths. That repository uses GitHub Pages from `main`, `/`. Commit and push these files to deploy. Keep the graph paths alongside `status/` so the interactive map links work.

The older Chinese presentation at the publication repository root uses earlier snapshots; the status page is the complete run 2 view. Prose is maintained in `status/template.html`; the builder reads the matrix, author rankings, and project table from the repository.
