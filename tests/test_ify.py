import os
import unittest
from urllib.error import HTTPError
from urllib.parse import quote, urlsplit, urlunsplit

from avidreader import avid_read, FileInfo, avid_open


class Stringable:
    def __init__(self, v):
        self.v = v

    def __str__(self):
        return str(self.v)


class AvidReaderTestCase(unittest.TestCase):
    data_dir = 'data'
    data_file = None
    expected = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.data_file = cls.data_file('test data 1.txt')
        with open(cls.data_file) as f:
            cls.expected = f.read()

    @classmethod
    def data_file(cls, fname: str) -> str:
        return os.path.join(cls.data_dir, fname)

    def test_vanilla_string(self):
        """ Test plain text options """
        s = "I'm just some plain text"

        self.assertEqual(s, avid_read(s), "Read a simple string")
        self.assertEqual(s, avid_read(bytes(s, encoding='utf-8')), "Read bytes")
        self.assertEqual(s, avid_read(bytearray(s, encoding='utf-8')), "Read a bytearray")
        self.assertEqual(s, avid_read(Stringable(s)), "Read a stringable object")
        with self.assertRaises(FileNotFoundError, msg="Redirect to file open") as e:
            avid_read('/a/nonexistent/location/file.txt')
        self.assertEqual('/a/nonexistent/location/file.txt', avid_read('/a/nonexistent/location/file.txt',
                                                                       is_actual_data=lambda s: True),
                         msg="override string file test")
        with self.assertRaises(HTTPError) as e:
            avid_read('http://example.org/test.txt')
            self.assertIn('HTTP Error 404: http://example.org/test.txt', str(e.exception),
                          msg = "Redirect to URL GET")
        self.assertEqual('http://example.org/test.txt', avid_read('http://example.org/test.txt',
                                                                  is_actual_data=lambda s: True),
                         msg="override string URL test")

    def test_wrapped_string(self):
        """ Test starting with a string going in """
        s = "   A string w/ \nsome other stuff\r\t."

        metadata = FileInfo()
        with avid_open(s, metadata) as f:
            self.assertEqual(s, f.read())
        self.assertEqual(35, metadata.source_file_size)
        metadata.clear()
        self.assertEqual(s, avid_read(s, metadata))
        self.assertEqual(35, metadata.source_file_size)

    def test_file_name(self):
        """ Test file open path of avid_open and read"""
        metadata = FileInfo()
        self.assertEqual(self.expected, avid_read(self.data_file, metadata))
        self.assertTrue(metadata.source_file.endswith('/tests/data/test data 1.txt'), "file read works")
        self.assertTrue(metadata.base_path.endswith('/tests/data'))
        self.assertEqual(28, metadata.source_file_size)
        self.assertIsNotNone(metadata.source_file_date)

        metadata.clear()
        self.assertIsNone(metadata.base_path)
        self.assertIsNone(metadata.source_file)
        self.assertIsNone(metadata.source_file_date)
        self.assertIsNone(metadata.source_file_size)

        with avid_open(self.data_file, metadata) as f:
            text = f.read()
        self.assertEqual(self.expected, text)
        metadata2 = FileInfo()
        with avid_open('test data 1.txt', base_path=metadata.base_path, open_info=metadata2) as f:
            self.assertEqual(self.expected, f.read())
            self.assertEqual(metadata, metadata2)

        metadata.clear()
        with open(os.path.join(self.data_dir, 'test_8859.txt'), encoding='latin-1') as f:
            self.assertEqual('Some Text	With weird  ÒtextÓ	And single ÔquotesÕ', avid_read(f), metadata)
        with open(os.path.join(self.data_dir, 'test_8859.txt'), encoding='latin-1') as f:
            with avid_open(f) as of:
                self.assertEqual('Some Text	With weird  ÒtextÓ	And single ÔquotesÕ', avid_read(of), metadata)

    @unittest.skip("Won't work until we get the non-with idiom working")
    def test_non_with(self):
        """ Test the non-with branches of the process """
        metadata = FileInfo()
        self.assertEqual("I'm some friendly test data", avid_open('data/test data 1.txt', metadata).strip())

    def test_url(self):
        """ Test the URL branches of the process """
        metadata = FileInfo()
        comps = urlsplit("https://raw.githubusercontent.com/hsolbrig/avid_reader/main/tests/data/test data 1.txt")
        # (scheme, netloc, url, query, fragment)
        text_url = urlunsplit( (comps.scheme, comps.netloc, quote(comps.path), comps.query, comps.fragment) )
        with avid_open(text_url) as f:
            self.assertEqual(self.expected, f.read())


if __name__ == '__main__':
    unittest.main()
