import unittest
from unittest import mock
import threading
from http.client import HTTPConnection

from vibestudio import studio

class _ServerThread(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.server = studio.HTTPServer(("localhost", 8002), studio.ExampleHandler)

    def run(self):
        self.server.serve_forever()

    def stop(self):
        self.server.shutdown()
        self.server.server_close()


class ExampleHandlerTest(unittest.TestCase):
    def setUp(self):
        self.patcher = mock.patch.object(
            studio.ExampleHandler,
            "call_llm",
            lambda self, text: f"REPLY:{text}",
        )
        self.patcher.start()
        studio.LOGS = []
        self.thread = _ServerThread()
        self.thread.start()

    def tearDown(self):
        self.thread.stop()
        self.thread.join()
        self.patcher.stop()

    def test_logs_and_response(self):
        conn = HTTPConnection("localhost", 8002)
        path = "/test"
        conn.request("GET", path)
        resp = conn.getresponse()
        body = resp.read().decode()
        self.assertIn("REPLY", body)
        self.assertTrue(studio.LOGS)
        self.assertEqual(studio.LOGS[-1]["request"], path)


if __name__ == "__main__":
    unittest.main()
