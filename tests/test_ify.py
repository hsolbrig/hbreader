import os
import unittest
from urllib.error import HTTPError
from urllib.parse import quote, urlsplit, urlunsplit, urlparse

from hbreader import hbread, FileInfo, hbopen

github_url_base = "https://raw.githubusercontent.com/hsolbrig/hbreader/master/"

class Stringable:
    def __init__(self, v):
        self.v = v

    def __str__(self):
        return str(self.v)


class HBReaderTestCase(unittest.TestCase):
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

        self.assertEqual(s, hbread(s), "Read a simple string")
        self.assertEqual(s, hbread(bytes(s, encoding='utf-8')), "Read bytes")
        self.assertEqual(s, hbread(bytearray(s, encoding='utf-8')), "Read a bytearray")
        self.assertEqual(s, hbread(Stringable(s)), "Read a stringable object")
        with self.assertRaises(FileNotFoundError, msg="Redirect to file open") as e:
            hbread('/a/nonexistent/location/file.txt')
        self.assertEqual('/a/nonexistent/location/file.txt', hbread('/a/nonexistent/location/file.txt',
                                                                       is_actual_data=lambda s: True),
                         msg="override string file test")
        with self.assertRaises(HTTPError) as e:
            hbread('http://example.org/test.txt')
            self.assertIn('HTTP Error 404: http://example.org/test.txt', str(e.exception),
                          msg = "Redirect to URL GET")
        self.assertEqual('http://example.org/test.txt', hbread('http://example.org/test.txt',
                                                                  is_actual_data=lambda s: True),
                         msg="override string URL test")

    def test_wrapped_string(self):
        """ Test starting with a string going in """
        s = "   A string w/ \nsome other stuff\r\t."

        metadata = FileInfo()
        with hbopen(s, metadata) as f:
            self.assertEqual(s, f.read())
        self.assertEqual(35, metadata.source_file_size)
        metadata.clear()
        self.assertEqual(s, hbread(s, metadata))
        self.assertEqual(35, metadata.source_file_size)

    def test_file_name(self):
        """ Test file open path of hbopen and read"""
        metadata = FileInfo()
        self.assertEqual(self.expected, hbread(self.data_file, metadata))
        self.assertTrue(metadata.source_file.endswith('/tests/data/test data 1.txt'), "file read works")
        self.assertTrue(metadata.base_path.endswith('/tests/data'))
        self.assertEqual(28, metadata.source_file_size)
        self.assertIsNotNone(metadata.source_file_date)

        metadata.clear()
        self.assertIsNone(metadata.base_path)
        self.assertIsNone(metadata.source_file)
        self.assertIsNone(metadata.source_file_date)
        self.assertIsNone(metadata.source_file_size)

        with hbopen(self.data_file, metadata) as f:
            text = f.read()
        self.assertEqual(self.expected, text)
        metadata2 = FileInfo()
        with hbopen('test data 1.txt', base_path=metadata.base_path, open_info=metadata2) as f:
            self.assertEqual(self.expected, f.read())
            self.assertEqual(metadata, metadata2)

        metadata.clear()
        with open(os.path.join(self.data_dir, 'test_8859.txt'), encoding='latin-1') as f:
            self.assertEqual('Some Text	With weird  ÒtextÓ	And single ÔquotesÕ', hbread(f), metadata)
        with open(os.path.join(self.data_dir, 'test_8859.txt'), encoding='latin-1') as f:
            with hbopen(f) as of:
                self.assertEqual('Some Text	With weird  ÒtextÓ	And single ÔquotesÕ', hbread(of), metadata)

    @unittest.skip("Won't work until we get the non-with idiom working")
    def test_non_with(self):
        """ Test the non-with branches of the process """
        metadata = FileInfo()
        self.assertEqual("I'm some friendly test data", hbopen('data/test data 1.txt', metadata).strip())

    def test_url(self):
        """ Test the URL branches of the process """
        metadata = FileInfo()
        file_url = github_url_base + 'tests/data/test data 1.txt'
        with hbopen(file_url, metadata) as f:
            self.assertEqual(self.expected, f.read())
        with hbopen('test data 1.txt', base_path=metadata.base_path, open_info=metadata.clear()) as f:
            self.assertEqual(self.expected, f.read())
        with hbopen('test_8859.txt', base_path=metadata.base_path, read_codec='latin-1') as f:
            print(f.read())

    def test_metadata_lock(self):
        """ Quick test to make sure that typos whilst writing the metadata file are intercepted """
        metadata = FileInfo()
        metadata.source_file_size = 10
        with self.assertRaises(AttributeError) as e:
            metadata.source_file_sizee = 10

    def test_metadata_relpath(self):
        try:
            FileInfo.rel_offset = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            metadata = FileInfo()
            with hbopen(self.data_file, metadata) as f:
                ...
            self.assertEqual('hbreader/tests/data', metadata.base_path)
            self.assertEqual('hbreader/tests/data/test data 1.txt', metadata.source_file)
        finally:
            FileInfo.rel_offset = None

    # TODO: Make sure the FileInfo is filled out the way we want it
    @unittest.skip("Test needs to be completed")
    def test_metadata_values(self):
        self.assertTrue(False, "File info filled from file")
        self.assertTrue(False, "URL info comes from header")
        self.assertTrue(False, "Text info has boilerplate + current date")
        self.assertTrue(False, "IO comes from file descriptor")

    # TODO: Make sure that HBReader always returns TextIO


if __name__ == '__main__':
    unittest.main()
