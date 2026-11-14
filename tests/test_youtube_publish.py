import unittest
from compadre_shorts.youtube_publish import safe_title


class YouTubeMetadataTests(unittest.TestCase):
    def test_title_contains_brand_and_shorts_marker(self):
        title = safe_title("GTA5_capture_2026-11-14.mp4", 3)
        self.assertIn("Compadre Gameplay", title)
        self.assertIn("Momento 03", title)
        self.assertIn("#Shorts", title)
        self.assertLessEqual(len(title), 100)

    def test_title_sanitizes_long_or_special_source_names(self):
        title = safe_title("### partida___con_muchos_nombres_y_simbolos_!!!!.mp4", 10)
        self.assertLessEqual(len(title), 100)
        self.assertIn("Momento 10", title)
        self.assertNotIn("!!!!", title)


if __name__ == "__main__":
    unittest.main()
