import unittest
from vulnerable import app

class TestVulnerableApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_hello_endpoint(self):
        response = self.app.get('/hello?name=Test')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Hello, Test!', response.data)

    def test_hello_without_name(self):
        response = self.app.get('/hello')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
