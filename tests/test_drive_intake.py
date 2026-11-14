import unittest
from unittest.mock import MagicMock, patch

from compadre_shorts import drive_intake


class CleanupSafetyTests(unittest.TestCase):
    @patch("compadre_shorts.drive_intake.urlopen")
    @patch("compadre_shorts.drive_intake.patch_props")
    @patch("compadre_shorts.drive_intake.drive_file")
    @patch("compadre_shorts.drive_intake.request_json")
    def test_unprocessed_youtube_video_never_deletes_source(
        self, request_json, drive_file, patch_props, urlopen
    ):
        request_json.return_value = {"items": [{
            "id": "yt123",
            "status": {"uploadStatus": "uploaded"},
            "processingDetails": {"processingStatus": "processing"},
        }]}
        with self.assertRaises(drive_intake.ApiError):
            drive_intake.cleanup_after_publish("token", "drive123", "yt123")
        drive_file.assert_not_called()
        patch_props.assert_not_called()
        urlopen.assert_not_called()

    @patch("compadre_shorts.drive_intake.urlopen")
    @patch("compadre-shorts.drive_intake.patch_props")
    @patch("compadre-shorts.drive_intake.drive_file")
    @patch("compadre-shorts.drive_intake.request_json")
    def test_missing_youtube_video_never_deletes_source(
        self, request_json, drive_file, patch_props, urlopen
    ):
        request_json.return_value = {"items": []}
        with self.assertRaises(drive_intake.ApiError):
            drive_intake.cleanup_after_publish("token", "drive123", "yt-missing")
        drive_file.assert_not_called()
        patch_props.assert_not_called()
        urlopen.assert_not_called()

    @patch("compadre_shorts.drive_intake.urlopen")
    @patch("compadre_shorts.drive_intake.patch_props")
    @patch("compadre_shorts.drive_intake.drive_file")
    @patch("compadre_shorts.drive_intake.request_json")
    def test_processed_youtube_video_allows_source_deletion(
        self, request_json, drive_file, patch_props, urlopen
    ):
        request_json.return_value = {"items": [{
            "id": "yt123",
            "status": {"uploadStatus": "processed"},
            "processingDetails": {"processingStatus": "succeeded"},
        }]}
        drive_file.return_value = {"id": "drive123", "appProperties": {
            "compadreStatus": "rendered"
        }}
        response = MagicMock()
        response.__enter__.return_value = response
        urlopen.return_value = response

        drive_intake.cleanup_after_publish("token", "drive123", "yt123")

        patch_props.assert_called_once()
        req = urlopen.call_args.args[0]
        self.assertEqual(req.get_method(), "DELETE")
        self.assertIn("/files/drive123", req.full_url)

    @patch("compadre_shorts.drive_intake.urlopen")
    @patch("compadre_shorts.drive_intake.patch_props")
    @patch("compadre_shorts.drive_intake.drive_file")
    @patch("compadre_shorts.drive_intake.request_json")
    def test_ineligible_source_state_never_deletes(
        self, request_json, drive_file, patch_props, urlopen
    ):
        request_json.return_value = {"items": [{
            "id": "yt123",
            "status": {"uploadStatus": "processed"},
            "processingDetails": {"processingStatus": "succeeded"},
        }]}
        drive_file.return_value = {"id": "drive123", "appProperties": {
            "compadreStatus": "failed"
        }}
        with self.assertRaises(drive_intake.ApiError):
            drive_intake.cleanup_after_publish("token", "drive123", "yt123")
        patch_props.assert_not_called()
        urlopen.assert_not_called()


if __name__ == "__main__":
    unittest.main()
