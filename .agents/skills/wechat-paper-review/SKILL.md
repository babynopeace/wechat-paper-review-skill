---
name: wechat-paper-review
description: 将用户提供的学术论文 PDF 解析为面向科研读者的中文微信公众号文献解析，按用户修订过的学术Word风格提炼研究背景、方法、关键结果、证据边界与两段个人思考，截取并嵌入原论文图表，核对数值并导出可编辑 DOCX 和 Markdown。适用于“论文解读”“文献解析公众号”“图文并茂论文精读”“按已有Word风格分析新论文”等任务。
---

# 微信公众号学术文献解析（Paper → Chinese analysis + original figures + Word）

## 输入

- 必需：用户提供的完整论文 PDF（而非只有摘要）。
- 可选：用户修改后的参考 DOCX；期望字数；文章定位；图数；研究领域；需强调的研究问题。
- 不要假设存在固定的本地路径，也不要把上传文件复制进 Git 仓库。

## 核心交付

1. 可独立阅读的中文文献解析（不是逐段直译），保留学术标题及分级小标题。
2. 与正文对应的 **原论文实际图表截图**（不重新绘制、不用图库照片代替）。
3. 可编辑 `.docx`，另附 `.md` 方便复制到公众号；需要时另导出核对记录和裁图清单。
4. 在文末提供原文 DOI/作者/期刊/日期；不确定的 IF、JCR、中科院分区应标注待核验或省略。

## 固定写作风格（源自用户定稿习惯）

- 大标题学术陈述式，如“【论文解析】npj Digital Medicine 2026：基于……的……”。禁止标题采用疑问句、反问或营销式夸张表达。
- Word 起始区：英文原文标题居中；作者、发表期刊、发表日期各自单行；一段约 100–180 字中文导语；再进入正文。
- 章节与小节按研究逻辑组织，不机械套同一目录。常见框架：1 研究背景；2 研究方法/模型；3 核心结果；4 机制/下游应用；5 研究贡献与局限；6 个人思考与研究展望。复杂模型应详细拆核心模块；实验论文应讲清对照、评价及关键证据。
- 一级/二级标题均为客观、精确、学术陈述式，如“4.2 共同冲激响应与跨频率迁移证据”。避免“为什么会……？”“最强”“震撼”等。
- 约 1600–2400 中文字为默认目标（根据论文酌情增减）；段落紧凑、有观点，压缩空话。
- 最后一节“个人思考与研究展望”一般 **两段**，不再使用 6.1/6.2；不使用“首先、其次、最后”，从方法或生理机制的未解决问题提出可操作的下一步；区分论文原文结论与编辑个人推断。
- 不要把“准确率高”“分类效果好”当作唯一亮点，优先呈现论文真正的新研究问题与证据链。
- 参考 [style-guide.md](references/style-guide.md)。

## 工作顺序（不可跳过证据核对）

1. 阅读完整 PDF：提取摘要、Introduction、Methods、Results、Discussion、Limitations、Figure captions。不要只依赖第一页和摘要。
2. 使用 `scripts/prepare_paper.py` 导出逐页文本、图注候选和页缩略图（须安装 requirements.txt）。
3. 创建“证据表”：每项数据写明来自哪个原文表/图、PDF 页码、是否经调整、比较条件、统计显著性；对冲突数值或作者讨论中的推断作注记。保留准确率与敏感度、AUC、样本量等互补指标，不得挑漂亮指标误导。
4. 构思目录与每节主旨。研究方法、结果、边界保持足够比例；减少泛泛背景与无证据的生理推断。
5. 仅选择能支撑正文的 4–7 张原论文图，确定 PDF 页与矩形边界。用 `scripts/crop_figures.py` 按手工审定的 PDF 坐标裁图，检查所裁图片的内容、图注、分辨率、文字清晰度。禁止重新绘制原图，禁止裁掉必要的图例、坐标轴或显著性说明。若用户明确需要全图，保留全部子图。
6. 填写符合 [article-schema.md](references/article-schema.md) 的 article.json；每个关键数据段落标注 `source_pages` 和最短可核对的 `evidence`（作者原文片段）；确保不能把相关性写成因果性、不能将同一数据集交叉验证描述为独立外部验证。
7. 运行 `scripts/validate_article.py` 作基础规则检查、证据引文查找（非语义事实核验），修正所有 ERROR。再人工核对原论文图文，尤其数字、p 值、模型比较方向、数据划分、结论限定。
8. 运行 `scripts/build_article.py` 导出 DOCX+MD。DOCX 编排模拟用户的参考Word：A4，宋体中文/Times New Roman英文，一级标题14pt，二级标题12pt，正文12pt，图注居中小字，原论文标题居中。
9. 可用 LibreOffice / Word 渲染 DOCX，逐页检查断页、裁图清晰度、字体缺失和图注位置；必要时调整后重新导出。检查文本与所有图号、引用对应。
10. 交付文稿，说明所有图片均来自用户原 PDF；对于授权问题提醒用户公开转载时确认出版社版权许可。

## 常用命令（从仓库根目录运行）

```bash
python -m pip install -r requirements.txt
python .agents/skills/wechat-paper-review/scripts/prepare_paper.py --paper /path/to/paper.pdf --out work/paper
python .agents/skills/wechat-paper-review/scripts/crop_figures.py --paper /path/to/paper.pdf --regions work/figure_regions.json --out work/figures
python .agents/skills/wechat-paper-review/scripts/validate_article.py --article work/article.json --paper /path/to/paper.pdf
python .agents/skills/wechat-paper-review/scripts/build_article.py --article work/article.json --out work/review.docx --markdown work/review.md
python -m unittest discover -s tests -v
```

这些脚本处理文件与版式，**不调用模型 API，无法独立完成论文的科学理解和写作**；Codex 应完成证据理解、中文写作、图表选择与人工审核环节。裁图 JSON 的 bbox 使用 PDF 点坐标 `[x0, y0, x1, y1]`、页码从 1 开始。详见 [figure-workflow.md](references/figure-workflow.md)。

## 验收红线

- 不编造作者、发表日期、IF、分区、样本数、指标及其显著性。
- 对论文数字、实验范围或临床应用边界的不确定性不得隐瞒。
- 不能把论文图表当作自行创作图、不能宣称已获得图片转载授权。
- 未读完文献/只用摘要不得称为“完整文献解析”。
- 不要在用户没有明确要求时执行 Git 推送、创建远程仓库或上传论文附件。
