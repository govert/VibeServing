import unittest
from unittest import mock
import threading
from http.client import HTTPConnection
import os
import sys

sys.path.append(os.path.dirname(__file__))
from simple_server import Handler, HTTPServer


class _ServerThread(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.server = HTTPServer(("localhost", 8001), Handler)

    def run(self):
        self.server.serve_forever()

    def stop(self):
        self.server.shutdown()
        self.server.server_close()


class SimpleServerTest(unittest.TestCase):
    def setUp(self):
        def fake_call(self, path):
            return f"Echo {path}"

        self.patcher = mock.patch.object(Handler, "call_llm", fake_call)
        self.patcher.start()

        self.thread = _ServerThread()
        self.thread.start()

    def tearDown(self):
        self.thread.stop()
        self.thread.join()
        self.patcher.stop()

    def test_echo_path(self):
        path = "/hello?world=1"
        conn = HTTPConnection("localhost", 8001)
        conn.request("GET", path)
        resp = conn.getresponse()
        body = resp.read().decode()
        self.assertIn(path, body)


if __name__ == "__main__":
    unittest.main()
