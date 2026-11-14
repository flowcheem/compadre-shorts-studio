import unittest

from compadre_shorts.cli import build_segments, build_video_filters


class RenderPlanningTests(unittest.TestCase):
    def test_safe_framing_uses_full_frame_composition(self):
        simple, graph = build_video_filters("viral", "safe")
        self.assertIsNone(simple)
        self.assertIn("boxblur", graph)
        self.assertIn("force_original_aspect_ratio=decrease", graph)
        self.assertIn("overlay=(W-w)/2:(H-h)/2", graph)
        self.assertIn("unsharp", graph)

    def test_safe_clean_framing_has_no_viral_grade(self):
        _, graph = build_video_filters("clean", "safe")
        self.assertNotIn("eq=contrast", graph)
        self.assertNotIn("unsharp", graph)

    def test_center_framing_keeps_legacy_crop(self):
        simple, graph = build_video_filters("viral", "center")
        self.assertIsNone(graph)
        self.assertIn("crop=1080:1920", simple)
        self.assertIn("eq=contrast=1.10", simple)

    def test_segments_cover_full_minutes_and_drop_short_remainder(self):
        self.assertEqual(
            build_segments(180, 60, 15),
            [(0.0, 60), (60.0, 60), (120.0, 60)],
        )
        self.assertEqual(
            build_segments(130, 60, 15),
            [(0.0, 60), (60.0, 60)],
        )


if __name__ == "__main__":
    unittest.main()
