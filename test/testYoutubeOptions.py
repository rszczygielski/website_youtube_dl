import unittest
from website_youtube_dl.common.youtube_options import (
    YoutubeVideoOptions,
    YoutubeAudioOptions,
    YoutubeOptiones,
    VideoQuality,
    VideoExtension,
    PostProcessors
)

class TestYoutubeOptions(unittest.TestCase):
    def setUp(self):
        # Template Constants
        self.default_template = "%(title)s.%(ext)s"
        self.custom_template = "%(id)s.%(ext)s"
        
        # Audio Expectation Constants
        self.audio_key_expected = "FFmpegExtractAudio"
        self.audio_codec_expected = "mp3"
        self.audio_bitrate_expected = "192"
        
        # Test Data
        self.supported_resolutions = ["360", "480", "720", "1080", "2160"]
        self.target_quality_str = "720"
        self.invalid_quality_str = "invalid_quality"
        self.invalid_extension_str = "invalid_extension"
        self.flat_extraction_val = "in_playlist"

        # Instance Initialization
        self.video_options = YoutubeVideoOptions(self.default_template)
        self.audio_options = YoutubeAudioOptions(self.default_template)

    def test_video_format_generation(self):
        """Verify that video format strings are correctly constructed for all resolutions."""
        for resolution in self.supported_resolutions:
            self.video_options.set_format(
                video_quality=VideoQuality(resolution), 
                extension=VideoExtension.MP4
            )
            options_dict = self.video_options.to_dict()
            
            expected_format = f"best[height={resolution}][ext=mp4]+bestaudio/bestvideo+bestaudio"
            self.assertEqual(options_dict[YoutubeOptiones.FORMAT.value], expected_format)

    def test_audio_post_processor_config(self):
        """Ensure audio options contain the correct FFmpeg post-processing parameters."""
        options_dict = self.audio_options.to_dict()
        self.assertIn(YoutubeOptiones.POSTPROCESSORS.value, options_dict)
        
        # Extract the first post-processor configuration
        config = options_dict[YoutubeOptiones.POSTPROCESSORS.value][0]
        
        self.assertEqual(config[PostProcessors.KEY.value], self.audio_key_expected)
        self.assertEqual(config[PostProcessors.PREFERREDCODEC.value], self.audio_codec_expected)
        self.assertEqual(config[PostProcessors.PREFERREDQUALITY.value], self.audio_bitrate_expected)

    def test_output_template_assignment(self):
        """Verify that custom output templates are correctly assigned to both video and audio."""
        video_opt = YoutubeVideoOptions(self.custom_template)
        audio_opt = YoutubeAudioOptions(self.custom_template)
        
        self.assertEqual(video_opt.to_dict()[YoutubeOptiones.OUT_TEMPLATE.value], self.custom_template)
        self.assertEqual(audio_opt.to_dict()[YoutubeOptiones.OUT_TEMPLATE.value], self.custom_template)

    def test_invalid_input_conversions(self):
        """Check that invalid quality or extension strings trigger appropriate ValueErrors."""
        with self.assertRaises(ValueError) as context:
            self.video_options.convert_video_quality(self.invalid_quality_str)
        self.assertIn(self.invalid_quality_str, str(context.exception))

        with self.assertRaises(ValueError) as context:
            self.video_options.convert_video_extension(self.invalid_extension_str)
        self.assertIn(self.invalid_extension_str, str(context.exception))

    def test_option_overwriting_logic(self):
        """Test the ability to update existing options and prevent unauthorized overwrites."""
        # Valid overwrite
        self.video_options.overwrite_option(YoutubeOptiones.NO_OVERWITES, True)
        self.assertTrue(self.video_options.NO_OVERWITES.argument_value)

        # Attempting to overwrite a missing key should raise KeyError
        with self.assertRaises(KeyError) as context:
            self.video_options.overwrite_option(YoutubeOptiones.EXTRACT_FLAT, self.flat_extraction_val)
        self.assertIn("Option 'extract_flat' does not exist", str(context.exception))

    def test_dynamic_option_addition(self):
        """Verify adding new options and the 'overwrite' safety flag behavior."""
        # 1. Add new
        self.video_options.add_new_option(YoutubeOptiones.EXTRACT_FLAT, self.flat_extraction_val)
        actual_val = getattr(self.video_options, YoutubeOptiones.EXTRACT_FLAT.name).argument_value
        self.assertEqual(actual_val, self.flat_extraction_val)

        # 2. Prevent accidental duplicate addition
        with self.assertRaises(KeyError):
            self.video_options.add_new_option(YoutubeOptiones.EXTRACT_FLAT, "some_other_value")

        # 3. Explicit overwrite
        new_format_val = "bestvideo"
        self.video_options.add_new_option(YoutubeOptiones.FORMAT, new_format_val, overwrite=True)
        self.assertEqual(self.video_options.FORMAT.argument_value, new_format_val)


class TestExtensionConverter(unittest.TestCase):
    def setUp(self):
        self.options = YoutubeVideoOptions("%(title)s.%(ext)s")

    def test_valid_extension_mapping(self):
        """Ensure all defined VideoExtension enums convert back to themselves correctly."""
        for ext in VideoExtension:
            result = self.options.convert_video_extension(ext.value)
            self.assertEqual(result, ext)

    def test_quality_string_to_enum_conversion(self):
        """Verify that string resolutions (e.g., '720') map to the correct VideoQuality Enum."""
        result = self.options.convert_video_quality("720")
        self.assertEqual(result, VideoQuality.Q720)


if __name__ == "__main__":
    unittest.main()