# 原论文图裁取流程

1. 运行 `prepare_paper.py`，查看 `report.json` 中图注候选和 `pages/page-XXX.png` 页预览。
2. 打开相应页面的原始 PDF 或高清渲染，人工判断 figure 最外侧边界；不要仅凭 caption 文本 bbox 估算整图。
3. 填写裁图区域 JSON：

```json
[
  {"id": "Fig1", "page": 3, "bbox": [44, 70, 553, 235], "filename": "Fig1.png"},
  {"id": "Fig2", "page": 6, "bbox": [43, 68, 555, 270], "filename": "Fig2.png"}
]
```

`bbox` 是 PDF 页面自身的**point**坐标，左上角为原点，单位是 pt。这里的数字只示范结构，绝不能未经检查直接用于任何真实论文。

4. `crop_figures.py` 使用 PyMuPDF 的渲染裁剪；默认 2.5 倍分辨率，可以调 `--scale 3.0`。`--preview` 可在页面预览中画出边框以便复核。
5. 如果 Fig. 5 包含多个子图，且只想用 Fig. 5a–d，应保证框住必要的坐标、图例及面板标识。不要裁成脱离图注难以理解的碎片。
6. `crop_figures.py` 会生成 `figure_manifest.json`，记录原 PDF 的 sha256、页码与裁图坐标，便于追溯。
7. 最终 Word 中为每张图添加中文图注和“原论文 Fig. N”。微信公众号可能涉及公开转载，出版商图片版权政策需另行确认。
