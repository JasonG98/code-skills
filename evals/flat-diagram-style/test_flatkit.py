"""Regressions for observed portability and rendering failures; uses Pillow."""
from pathlib import Path
import sys
import tempfile
import unittest

from PIL import Image, ImageChops, ImageColor

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'skills/flat-diagram-style/scripts'))
import flatkit as f


class FlatkitTests(unittest.TestCase):
    def tearDown(self):
        f.configure_fonts()
        f.WARN.clear()

    def test_local_font_discovery(self):
        regular = f.font(24)
        self.assertGreater(regular.getlength('中文 English'), 0)
        # Coverage is also checked visually; width alone cannot detect missing glyphs.

    def test_explicit_font_and_cache_reset(self):
        path = f._find_font('Regular')
        old = f.font(24)
        f.configure_fonts(regular=path)
        self.assertIsNot(old, f.font(24))
        self.assertEqual(f.font(24).path, path)
        self.assertEqual(f.font(24, 'Bold').path, path)
        with self.assertRaises(FileNotFoundError):
            f.configure_fonts(regular='/not-a-real-font/absent.ttf')

    def test_custom_light_fill_has_dark_legible_text(self):
        c = f.Canvas(400, 200)
        c.box(30, 30, 340, 140, '#FFFF99', 'Readable')
        region = c.img.crop((80, 80, 720, 320))
        colors = [color for count, color in region.getcolors(region.width * region.height)]
        self.assertIn(ImageColor.getrgb(f.INK), colors)
        self.assertNotIn(ImageColor.getrgb(f.WHITE), colors)

    def test_full_width_components_respect_canvas_margins(self):
        c = f.Canvas(1200, 700)
        c.strip(100, 'Summary')
        c.kpi_row(300, 160, [('3', 'Steps', f.NAVY), ('2', 'Groups', f.TEAL)])
        for y in [138, 380]:
            self.assertEqual(c.img.getpixel((1170 * f.S, y * f.S)), (255, 255, 255))
            self.assertNotEqual(c.img.getpixel((1140 * f.S, y * f.S)), (255, 255, 255))

    def test_fixed_dimensions_and_colored_background_trimming(self):
        c = f.Canvas(640, 480, background='#F0EAFE', margin=30)
        c.rect(30, 40, 200, 100, f.NAVY)
        with tempfile.TemporaryDirectory() as temp:
            full = Path(temp) / 'full.png'
            crop = Path(temp) / 'crop.png'
            c.save(full, trim=False)
            c.save(crop)
            with Image.open(full) as im:
                self.assertEqual(im.size, (640, 480))
                self.assertEqual(im.getpixel((600, 450)), (240, 234, 254))
            with Image.open(crop) as im:
                self.assertEqual(im.size, (640, 170))

    def test_zero_bars_do_not_encode_positive_values(self):
        c = f.Canvas(600, 300)
        c.hbars([('', 0, f.NAVY, '', None)], 50)
        c.vbar(20, 200, 50, 0, 10, f.TEAL)
        self.assertIsNone(ImageChops.difference(c.img, Image.new('RGB', c.img.size, f.WHITE)).getbbox())

    def test_negative_bars_are_rejected(self):
        c = f.Canvas()
        with self.assertRaises(ValueError):
            c.hbars([('Negative', -5, f.NAVY, '-5', None)], 50)
        with self.assertRaises(ValueError):
            c.vbar(20, 200, 50, -5, 10, f.TEAL)

    def test_small_bars_keep_their_scale(self):
        c = f.Canvas(600, 300)
        c.hbars([('', 0.2, f.NAVY, '', None)], 50, scale=10)
        bbox = ImageChops.difference(c.img, Image.new('RGB', c.img.size, f.WHITE)).getbbox()
        self.assertEqual(bbox[2] - bbox[0], 2 * f.S + 1)
        c = f.Canvas(600, 300)
        c.vbar(20, 200, 50, 0.2, 10, f.TEAL)
        bbox = ImageChops.difference(c.img, Image.new('RGB', c.img.size, f.WHITE)).getbbox()
        self.assertEqual(bbox[3] - bbox[1], 2 * f.S + 1)


if __name__ == '__main__':
    unittest.main()
