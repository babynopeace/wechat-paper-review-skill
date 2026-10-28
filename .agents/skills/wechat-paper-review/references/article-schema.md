# article.json 格式

相对路径中的 `image` 以 `article.json` 文件所在目录为起点。

```json
{
  "metadata": {
    "original_title": "Published English paper title",
    "wechat_title": "【论文解析】期刊 年份：学术陈述式中文标题",
    "authors": "Full authors",
    "journal": "Journal name",
    "publication_date": "2026-09-22",
    "doi": "10.xxxx/xxxxx",
    "journal_metrics": "可选；经年份和来源核对的IF/JCR/分区"
  },
  "lead": ["研究背景、方法和核心贡献的1段简短概述。"],
  "sections": [
    {
      "title": "研究背景",
      "blocks": [],
      "subsections": [
        {
          "title": "研究问题及现有局限",
          "blocks": [
            {
              "type": "paragraph",
              "text": "经过证据核验的准确解读。",
              "source_pages": [1, 2],
              "evidence": ["来自论文的短原文片段，尽可能可直接文本检索"]
            },
            {
              "type": "figure",
              "image": "figures/Fig1.png",
              "caption": "研究模型结构。原论文Fig. 1。",
              "source_page": 3,
              "original_figure": "Fig. 1"
            }
          ]
        }
      ]
    }
  ]
}
```

- `sections` 至少1项；每节可直接包含 `blocks`，也可包含 `subsections`，或两者。
- `lead` 为一段/多段文字数组。
- `blocks[].type` 为 `paragraph` 或 `figure`。
- 图像应是真实裁图，不能把原图说明文字替代图片。
- `source_pages` / `evidence` 属于内部核验数据，在最终公众号Word正文中不展示。
- 核查原文确实没有某字段时用 `未明确报告`；不编造。
- 结果段落应尽可能配来源页码；数字多时必须复核原文比较方向和指标。
