import unittest
from website_youtube_dl.common.youtubeOptions import (
    YoutubeVideoOptions,
    YoutubeAudioOptions,
    YoutubeOptiones,
    VideoQuality,
    VideoExtension,
    PostProcessors,
    RequestArgument,
)


class TestYoutubeOptions(unittest.TestCase):
    def setUp(self):
        self.default_out_template = "%(title)s.%(ext)s"
        self.custom_out_template = "%(id)s.%(ext)s"
        self.invalid_quality = "invalid_quality"
        self.invalid_extension = "invalid_extension"
        self.expected_audio_key = "FFmpegExtractAudio"
        self.expected_audio_codec = "mp3"
        self.expected_audio_quality = "192"
        self.list_of_formats = ["360", "480", "720", "1080", "2160"]
        self.valid_quality = "720"
        self.new_format = "bestvideo+bestaudio"
        self.new_option_value = "in_playlist"

        self.video_options = YoutubeVideoOptions(self.default_out_template)
        self.audio_options = YoutubeAudioOptions(self.default_out_template)

    def test_get_video_options(self):
        original_format = self.video_options.to_dict()[
            YoutubeOptiones.FORMAT.value]
        for format_type in self.list_of_formats:
            self.video_options.set_format(
                video_quality=VideoQuality(format_type), extension=VideoExtension.MP4
            )
            video_options_dict = self.video_options.to_dict()
            self.assertNotEqual(
                original_format, video_options_dict[YoutubeOptiones.FORMAT.value]
            )
            self.assertEqual(
                f"best[height={format_type}][ext=mp4]+bestaudio/bestvideo+bestaudio",
                video_options_dict[YoutubeOptiones.FORMAT.value],
            )

    def test_get_audio_options(self):
        audio_options_dict = self.audio_options.to_dict()
        self.assertIn(YoutubeOptiones.POSTPROCESSORS.value, audio_options_dict)
        postprocessors = audio_options_dict[YoutubeOptiones.POSTPROCESSORS.value][0]
        self.assertIn(PostProcessors.KEY.value, postprocessors)
        self.assertIn(PostProcessors.PREFERREDCODEC.value, postprocessors)
        self.assertIn(PostProcessors.PREFERREDQUALITY.value, postprocessors)
        self.assertEqual(
            postprocessors[PostProcessors.KEY.value], self.expected_audio_key)
        self.assertEqual(
            postprocessors[PostProcessors.PREFERREDCODEC.value], self.expected_audio_codec)
        self.assertEqual(
            postprocessors[PostProcessors.PREFERREDQUALITY.value], self.expected_audio_quality)

    def test_video_options_out_template(self):
        video_options = YoutubeVideoOptions(self.custom_out_template)
        video_options_dict = video_options.to_dict()
        self.assertEqual(
            video_options_dict[YoutubeOptiones.OUT_TEMPLATE.value], self.custom_out_template
        )

    def test_audio_options_out_template(self):
        audio_options = YoutubeAudioOptions(self.custom_out_template)
        audio_options_dict = audio_options.to_dict()
        self.assertEqual(
            audio_options_dict[YoutubeOptiones.OUT_TEMPLATE.value], self.custom_out_template
        )

    def test_invalid_video_quality(self):
        with self.assertRaises(ValueError) as context:
            self.video_options.convert_video_quality(self.invalid_quality)
        self.assertIn(self.invalid_quality, str(context.exception))

    def test_invalid_video_extension(self):
        with self.assertRaises(ValueError) as context:
            self.video_options.convert_video_extension(self.invalid_extension)
        self.assertIn(self.invalid_extension, str(context.exception))

    def test_overwrite_option(self):
        # Overwrite an existing option
        self.video_options.overwrite_option(
            YoutubeOptiones.FORMAT, self.new_format)
        self.assertEqual(
            self.video_options.FORMAT.argument_value, self.new_format
        )

        # Attempt to overwrite a non-existent option
        with self.assertRaises(KeyError) as context:
            self.video_options.overwrite_option(
                YoutubeOptiones.EXTRACT_FLAT, self.new_option_value)
        self.assertIn("Option 'extract_flat' does not exist",
                      str(context.exception))

    def test_add_new_option(self):
        # Add a new option
        self.video_options.add_new_option(
            YoutubeOptiones.EXTRACT_FLAT, self.new_option_value)
        self.assertEqual(
            getattr(self.video_options,
                    YoutubeOptiones.EXTRACT_FLAT.name).argument_value,
            self.new_option_value,
        )

        # Attempt to add an existing option without overwrite
        with self.assertRaises(KeyError) as context:
            self.video_options.add_new_option(
                YoutubeOptiones.FORMAT, self.new_format)
        self.assertIn("Option 'format' already exists", str(context.exception))

        # Add an existing option with overwrite
        overwrite_value = "new_format"
        self.video_options.add_new_option(
            YoutubeOptiones.FORMAT, overwrite_value, overwrite=True)
        self.assertEqual(
            self.video_options.FORMAT.argument_value, overwrite_value
        )

    def test_convert_video_quality(self):
        # Test valid video quality
        result = self.video_options.convert_video_quality(self.valid_quality)
        self.assertEqual(result, VideoQuality.Q720)

        # Test invalid video quality
        with self.assertRaises(ValueError) as context:
            self.video_options.convert_video_quality(self.invalid_quality)
        self.assertIn(
            self.invalid_quality,
            str(context.exception),
        )


class TestConvertVideoExtension(unittest.TestCase):

    def setUp(self):
        self.default_out_template = "%(title)s.%(ext)s"
        self.video_options = YoutubeVideoOptions(self.default_out_template)
        self.valid_quality = "720"
        self.invalid_quality = "invalid_quality"

    def test_valid_video_extension(self):
        for extension in VideoExtension:
            result = self.video_options.convert_video_extension(
                extension.value)
            self.assertEqual(result, extension)

    def test_invalid_video_extension(self):
        invalid_extension = "invalid_extension"
        with self.assertRaises(ValueError) as context:
            self.video_options.convert_video_extension(invalid_extension)
        self.assertIn(
            invalid_extension,
            str(context.exception),
        )

    def test_convert_video_quality(self):
        # Test valid video quality
        result = self.video_options.convert_video_quality(self.valid_quality)
        self.assertEqual(result, VideoQuality.Q720)

        # Test invalid video quality
        with self.assertRaises(ValueError) as context:
            self.video_options.convert_video_quality(self.invalid_quality)
        self.assertIn(
            self.invalid_quality,
            str(context.exception),
        )


if __name__ == "__main__":
    unittest.main()
