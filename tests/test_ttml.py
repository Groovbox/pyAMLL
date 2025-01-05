import unittest
from pyttml.ttml import process_lyrics, Line, VocalElement, Vocal, Lyrics

class TestProcessLyrics(unittest.TestCase):

    def test_empty_string(self):
        result = process_lyrics("")
        self.assertIsNone(result)

    def test_single_line(self):
        lyrics_str = "Hello world"
        result = process_lyrics(lyrics_str)
        self.assertIsInstance(result, Lyrics)
        self.assertEqual(len(result.init_list), 1)
        self.assertEqual(result.init_list[0].elements[0].text, "Hello")
        self.assertEqual(result.init_list[0].elements[1].text, "world")

    def test_multiple_lines(self):
        lyrics_str = "Hello world\nThis is a test"
        result = process_lyrics(lyrics_str)
        self.assertIsInstance(result, Lyrics)
        self.assertEqual(len(result.init_list), 2)
        self.assertEqual(result.init_list[0].elements[0].text, "Hello")
        self.assertEqual(result.init_list[0].elements[1].text, "world")
        self.assertEqual(result.init_list[1].elements[0].text, "This")
        self.assertEqual(result.init_list[1].elements[1].text, "is")
        self.assertEqual(result.init_list[1].elements[2].text, "a")
        self.assertEqual(result.init_list[1].elements[3].text, "test")

    def test_backing_line(self):
        lyrics_str = "(Hello world)"
        result = process_lyrics(lyrics_str)
        self.assertIsInstance(result, Lyrics)
        self.assertEqual(len(result.init_list), 1)
        self.assertTrue(result.init_list[0].is_backing)
        self.assertEqual(result.init_list[0].elements[0].text, "Hello")
        self.assertEqual(result.init_list[0].elements[1].text, "world")

    def test_syllables(self):
        lyrics_str = "Hel/lo wor/ld"
        result = process_lyrics(lyrics_str)
        self.assertIsInstance(result, Lyrics)
        self.assertEqual(len(result.init_list), 1)
        self.assertEqual(result.init_list[0].elements[0].text, "Hel")
        self.assertEqual(result.init_list[0].elements[1].text, "lo")
        self.assertEqual(result.init_list[0].elements[2].text, "wor")
        self.assertEqual(result.init_list[0].elements[3].text, "ld")

    def test_samples(self):
        from tests.samples.obj_levitating_dua_lipa import OBJ as SAMPLE1
        from tests.samples.obj_blinding_lights_the_weeknd import OBJ as SAMPLE2

        result = process_lyrics(open("tests/samples/lyrics_levitating_dua_lipa.txt").read())
        self.assertEqual(result, SAMPLE1)
        result = process_lyrics(open("tests/samples/lyrics_blinding_lights_the_weeknd.txt").read())
        self.assertEqual(result, SAMPLE2)

if __name__ == '__main__':
    unittest.main()