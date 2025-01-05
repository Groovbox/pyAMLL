import unittest
from pathlib import Path
from pyttml.ttml import Vocal, VocalElement, Line, Lyrics, parse_lyrics_to_swlrc

class TestParseLyricsToSwlrc(unittest.TestCase):

    def setUp(self):
        self.vocal_elements = [
            VocalElement(word_index=0, text="Hello", line_index=0, start_time=0.0, end_time=0.5),
            VocalElement(word_index=1, text="world", line_index=0, start_time=0.5, end_time=1.0)
        ]
        self.lines = [
            Line(index=0, elements=self.vocal_elements, vocal=Vocal.STANDARD, is_backing=False)
        ]
        self.lyrics = Lyrics(self.lines)

    def test_parse_lyrics_to_swlrc(self):
        expected_output = {
            "StartTime": 0.0,
            "EndTime": 1.0,
            "Type": "Syllable",
            "VocalGroups": [
                {
                    "Type": "Vocal",
                    "OppositeAligned": False,
                    "StartTime": 0.0,
                    "EndTime": 1.0,
                    "Lead": [
                        {
                            "Text": "Hello",
                            "IsPartOfWord": False,
                            "StartTime": 0.0,
                            "EndTime": 0.5
                        },
                        {
                            "Text": "world",
                            "IsPartOfWord": False,
                            "StartTime": 0.5,
                            "EndTime": 1.0
                        }
                    ]
                }
            ]
        }

        result = parse_lyrics_to_swlrc(self.lyrics)
        self.assertEqual(result, expected_output)

if __name__ == '__main__':
    unittest.main()