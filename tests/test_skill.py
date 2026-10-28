"""Smoke tests for the actual bundled PDF/figure/DOCX workflow."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
import fitz
from PIL import Image
from docx import Document

ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=ROOT/'.agents'/'skills'/'wechat-paper-review'/'scripts'

def module(name):
    spec=importlib.util.spec_from_file_location(name,SCRIPTS/(name+'.py'))
    obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj)
    return obj

class SkillTests(unittest.TestCase):
    def test_frontmatter(self):
        t=(SCRIPTS.parent/'SKILL.md').read_text(encoding='utf-8')
        self.assertTrue(t.startswith('---\n'))
        head=t.split('---',2)[1]
        self.assertIn('name: wechat-paper-review',head)
        self.assertIn('description:',head)

    def test_end_to_end(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)
            paper=p/'demo.pdf'
            with fitz.open() as doc:
                pg=doc.new_page(width=600,height=700)
                pg.insert_text((55,60),'Fig. 1 | Demo Figure',fontsize=13)
                pg.draw_rect(fitz.Rect(55,80,500,300),color=(0,0,0),fill=(0.95,0.95,0.95))
                doc.save(paper)
            rep=module('prepare_paper').run(paper,p/'work',max_pages=1)
            self.assertEqual(rep['processed_pages'],1)
            self.assertTrue((p/'work'/'pages'/'page-001.png').exists())
            regions=[{'id':'Fig1','page':1,'bbox':[50,50,510,310],'filename':'fig1.png'}]
            (p/'figure_regions.json').write_text(json.dumps(regions),encoding='utf-8')
            module('crop_figures').crop(paper,p/'figure_regions.json',p/'figures',scale=2,preview=True)
            with Image.open(p/'figures'/'fig1.png') as img:
                self.assertGreater(img.width,600)
            sample=json.loads((ROOT/'examples'/'article.sample.json').read_text(encoding='utf-8'))
            sample['sections'][0]['subsections'][0]['blocks'].append({'type':'figure','image':'figures/fig1.png','caption':'示意原图。原论文Fig. 1。','source_page':1,'original_figure':'Fig. 1'})
            art=p/'article.json'
            art.write_text(json.dumps(sample,ensure_ascii=False),encoding='utf-8')
            errs,warns=module('validate_article').audit(art,paper)
            self.assertEqual(errs,[])
            out=module('build_article').export(sample,p,p/'review.docx',p/'review.md')
            self.assertEqual(out['figures'],1)
            document=Document(p/'review.docx')
            self.assertTrue(any('个人思考' in x.text for x in document.paragraphs))
            self.assertEqual(len(document.inline_shapes),1)
            self.assertIn('![图1:',(p/'review.md').read_text(encoding='utf-8'))
            nested_md=p/'exports'/'review.md'
            module('build_article').export(sample,p,p/'exports'/'review.docx',nested_md)
            self.assertIn('](../figures/fig1.png)',nested_md.read_text(encoding='utf-8'))

    def test_figure_path_escape(self):
        audit=module('validate_article').audit
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)
            data=json.loads((ROOT/'examples'/'article.sample.json').read_text(encoding='utf-8'))
            data['sections'][0]['blocks']=[{'type':'figure','image':'../secret.png','caption':'图','original_figure':'Fig. 1'}]
            art=p/'article.json'
            art.write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
            errors,_=audit(art)
            self.assertTrue(any('escapes' in e for e in errors))

if __name__=='__main__':
    unittest.main()
