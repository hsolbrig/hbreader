import unittest
from urllib.error import URLError

from hbreader import hbopen

HTTP_TEST_PORT = 8100
HTTPS_TEST_PORT = 8543


class SSLSecurityTestCase(unittest.TestCase):
    def test_secure_access(self):
        # Make sure the server is running
        try:
            hbopen(f'http://localhost:{HTTP_TEST_PORT}/schema.context.jsonld')
        except URLError:
            print(f"=====> Unit test not run on https server -- unable to access port {HTTP_TEST_PORT}")
            return

        with hbopen(f'https://localhost:{HTTPS_TEST_PORT}/schema.context.jsonld') as f:
            self.assertEqual(b'{\n', next(f))


if __name__ == '__main__':
    unittest.main()
