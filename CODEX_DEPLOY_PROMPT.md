# 交给 Codex 的部署指令

请把以下任务作为一个完整的软件工程交付执行。我已经提供 `wechat-paper-review-skill.zip`，其中包含 repo-ready 的 Codex Skill（注意压缩包内有 `.agents/` 隐藏目录）。

**任务目标**：将 `wechat-paper-review` Skill 安装到我的 GitHub 仓库，确保在 Codex 中可以按名字调用它，用于“学术 PDF → 中文微信公众号文献解析 → 论文原图截取 → Word/Markdown 输出”。

请按以下顺序执行：

1. 检查压缩包目录结构，保持仓库级 `.agents/skills/wechat-paper-review/SKILL.md`、`references/`、`scripts/`、`agents/openai.yaml`、`README.md`、`tests/` 等内容的正确路径。不要只上传 ZIP 作为一个单独附件；请把压缩包的内容展开并作为 Git 源文件提交。
2. 我若已经指定仓库就使用该仓库；若未指定则优先创建一个新的**私有** GitHub 仓库（建议名字 `wechat-paper-review-skill`），并沿用我已经认证的 GitHub 用户身份。若需要选择账号或授权，请让我确认，不要猜用户名。
3. 安装 `requirements.txt` 依赖并执行 `python -m unittest discover -s tests -v`。若测试失败，先修复再提交。
4. 校验 `SKILL.md` 的 YAML 头部包含合法 `name` 和 `description`；确认 Codex 在该仓库中可以发现这个 Skill。不要把它误部署为一个无关的在线 Web 服务。
5. 把 GitHub Actions CI 和仓库文档一起提交，写明 PDF 预处理、人工图框选取、证据检查、DOCX 导出、Markdown 导出的方法及命令。
6. **不要上传**我的论文 PDF、修改后的 `文献解析.docx`、来自论文的图像、输出文件、密钥或本机绝对路径。公开转载论文图片涉及版权，不代表 GitHub 代码仓库可以自动转授权。
7. 检查 `.gitignore`，确保实际论文、原图、生成 Word、工作目录不会被误提交。目标仓库若已有代码或工作流，先保留用户现有内容，不要强制覆盖。
8. 完成后返回：GitHub 仓库 URL、提交 hash、CI 测试状态、Skill 所在目录、如何在 Codex 中调用 Skill 的实际示例，以及任何无法自动验证的环节。

只有当创建仓库/提交推送的操作已经获得权限与明确授权时才执行；否则先准备好本地 Git commit 并说明下一步，而不要声称已部署。
