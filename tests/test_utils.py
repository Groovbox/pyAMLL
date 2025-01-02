import unittest
from pyttml.utils import convert_seconds_to_format

class TestConvertSecondsToFormat(unittest.TestCase):
    
    def test_zero_seconds(self):
        self.assertEqual(convert_seconds_to_format(0), "00:00:00")
    
    def test_whole_seconds(self):
        self.assertEqual(convert_seconds_to_format(75), "01:15:00")
    
    def test_seconds_with_milliseconds(self):
        self.assertEqual(convert_seconds_to_format(75.123), "01:15:12")
    
    def test_less_than_a_minute(self):
        self.assertEqual(convert_seconds_to_format(45.678), "00:45:67")
    
    def test_exact_minute(self):
        self.assertEqual(convert_seconds_to_format(60), "01:00:00")
    
    def test_more_than_an_hour(self):
        self.assertEqual(convert_seconds_to_format(3661.789), "61:01:78")

if __name__ == '__main__':
    unittest.main()