# WeChat Paper Review · Codex Skill

将一篇完整学术论文 PDF 转为**中文微信公众号学术文献解析**：学术化标题、研究主线、关键方法与结果、证据边界、两段个人思考，直接截取原论文图表，最终导出 `.docx` + `.md`。

> 这是 **Codex Agent Skill + 辅助脚本**，不是一个脱离模型就能自动撰写科学文章的独立网页服务。Codex 负责阅读、写作和证据判断；脚本负责 PDF 预处理、按坐标裁原图、基础检查和排版。仓库不包含用户私有论文、原始 Word 文稿或版权图像。

## 设计来源

按用户人工编辑后的公众号文章范式定制：英文原题 + 作者/期刊/日期；按研究特色调整“背景、方法、结果、贡献、局限”；一级/二级标题为学术陈述句；原论文图表居中、中文图注；“个人思考与研究展望”只保留两段，不机械罗列“首先、其次、最后”。

## 目录

```text
wechat-paper-review-skill/
├── .agents/skills/wechat-paper-review/
│   ├── SKILL.md                    # Codex 调用入口（必需）
│   ├── agents/openai.yaml          # 显示名称与默认调用语
│   ├── references/                 # 写作风格、JSON结构、截图说明
│   └── scripts/
│       ├── prepare_paper.py        # PDF逐页文本、图注候选、页面预览
│       ├── crop_figures.py         # 截取原PDF图，并保留裁剪来源
│       ├── validate_article.py     # 基础数字出处/图片/风格检查
│       └── build_article.py        # DOCX+Markdown生成
├── AGENTS.md                       # 仓库行为规则
├── requirements.txt
├── examples/article.sample.json
├── tests/
├── .github/workflows/validate.yml
└── CODEX_DEPLOY_PROMPT.md
```

## 安装与使用

Python 3.10+，推荐 Python 3.11：

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS / Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

在 Codex 中打开这个仓库，使用：

> 使用 `$wechat-paper-review` 解析 `D:\\Papers\\example.pdf`，保持我修订过的Word文献解析风格，采用论文原始截图，正文约2000字，末尾个人思考两段，导出可编辑Word和Markdown。

Codex 会按 `.agents/skills/wechat-paper-review/SKILL.md` 中的步骤调用配套脚本。

若当前聊天尚未显示该 Skill，请在仓库根目录新开一个 Codex 聊天再调用。仓库模式无需复制到全局技能目录。

### 手动脚本命令（便于排错）

```bash
python .agents/skills/wechat-paper-review/scripts/prepare_paper.py \
  --paper "paper.pdf" --out "work/paper"

# 浏览 work/paper/pages/*.png 后人工给出原图坐标
python .agents/skills/wechat-paper-review/scripts/crop_figures.py \
  --paper "paper.pdf" --regions "work/figure_regions.json" \
  --out "work/figures" --preview

python .agents/skills/wechat-paper-review/scripts/validate_article.py \
  --article "work/article.json" --paper "paper.pdf"

python .agents/skills/wechat-paper-review/scripts/build_article.py \
  --article "work/article.json" --out "work/review.docx" \
  --markdown "work/review.md"
```

> 如果使用 Windows PowerShell，请将示例多行命令改写为单行，或用 PowerShell 续行符（反引号），不要原样使用上面的 Bash 反斜杠。

Markdown 图片路径相对于 `--markdown` 的输出目录生成；移动 Markdown 时需同时保留对应图片目录及相对位置。

### 验证范围

`python -m unittest discover -s tests -v` 使用临时生成的合成 PDF，验证页面提取、原图裁剪、图片路径边界、Word 图片嵌入，以及同目录和跨目录的 Markdown 图片链接。测试不读取用户论文，也不验证模型撰写的科学结论。`SKILL.md` 另通过 Codex Skill 格式校验，本地 Codex 的 `skills/list` 已确认其为启用的仓库级 Skill，未出现加载错误。完整论文的模型写作与逐页版式审阅仍需在实际文献任务中完成。

### 全局安装（可选）

将 `.agents/skills/wechat-paper-review/` 整个文件夹复制至 `${CODEX_HOME:-~/.codex}/skills/wechat-paper-review/`。也可直接在仓库内使用（推荐，可用 Git 更新）。

## GitHub 部署

把本压缩包解压成仓库根目录。让已登录 GitHub 的 Codex 读取 [CODEX_DEPLOY_PROMPT.md](CODEX_DEPLOY_PROMPT.md)，由它在指定仓库创建提交并推送。未指定仓库时建议**新建私有仓库**，确认后再开放。

Skill 上传GitHub仅保存代码与规则；并不自动上线一个可以打开的网址。若未来需要网页上传论文和一键生成文章，需要另外开发前后端/API服务。

## 质量与隐私

- 所有图像来自论文原 PDF，不用生成图替代原图；公开发布前确认出版社版权。
- 不将用户上传的论文 PDF、Word 参考文稿、私人数据或生成图直接提交至 GitHub。
- 基础核验脚本只做静态检查，不能替代对论文方法与统计结论的人工/模型研读。
- 缺少独立验证时，不得声称泛化到外部队列；缺少临床验证时，不得写成可用于临床诊断。
- 没有核实来源的影响因子和分区不能编造。
