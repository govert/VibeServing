import unittest
from unittest import mock
import threading
from http.client import HTTPConnection

from vibestudio import studio

class _ServerThread(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.server = studio.HTTPServer(("localhost", 8002), studio.ProxyHandler)

    def run(self):
        self.server.serve_forever()

    def stop(self):
        self.server.shutdown()
        self.server.server_close()


class ProxyHandlerTest(unittest.TestCase):
    def setUp(self):
        self.patcher = mock.patch.object(
            studio.ProxyHandler,
            "call_llm",
            lambda self, messages: (
                "   {{{ meta }}}\n"
                "  HTTP/1.1 200 OK\n"
                "  Content-Type: text/html\n"
                "\n"
                "<html>REPLY</html>"
            ),
        )
        self.patcher.start()
        studio.LOGS = []
        studio.META_LOGS = []
        studio.CONVERSATION = []
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
        self.assertEqual(resp.getheader("Content-Type"), "text/html")
        self.assertTrue(studio.LOGS)
        self.assertEqual(studio.LOGS[-1]["request"], path)
        self.assertEqual(studio.LOGS[-1]["status"], 200)
        self.assertTrue(studio.META_LOGS)  # meta prompt logged


class ProxyHandlerErrorTest(unittest.TestCase):
    def setUp(self):
        self.patcher = mock.patch.object(
            studio.ProxyHandler,
            "call_llm",
            side_effect=RuntimeError("missing key"),
        )
        self.patcher.start()
        studio.LOGS = []
        studio.META_LOGS = []
        studio.CONVERSATION = []
        self.thread = _ServerThread()
        self.thread.start()

    def tearDown(self):
        self.thread.stop()
        self.thread.join()
        self.patcher.stop()

    def test_error_logging(self):
        conn = HTTPConnection("localhost", 8002)
        path = "/fail"
        conn.request("GET", path)
        resp = conn.getresponse()
        body = resp.read().decode()
        self.assertEqual(resp.status, 500)
        self.assertIn("missing key", body)
        self.assertTrue(studio.LOGS)
        self.assertTrue(studio.LOGS[-1]["error"])


class ProxyHandlerPostTest(unittest.TestCase):
    def setUp(self):
        self.captured = {}
        outer = self

        def fake_call(self, messages):
            outer.captured["messages"] = list(messages)
            return (
                "{{{ meta }}}\n"
                "HTTP/1.1 200 OK\n"
                "Content-Type: text/plain\n"
                "\n"
                "ok"
            )

        self.patcher = mock.patch.object(studio.ProxyHandler, "call_llm", fake_call)
        self.patcher.start()
        studio.LOGS = []
        studio.META_LOGS = []
        studio.CONVERSATION = []
        self.thread = _ServerThread()
        self.thread.start()

    def tearDown(self):
        self.thread.stop()
        self.thread.join()
        self.patcher.stop()

    def test_post_body_forwarded(self):
        conn = HTTPConnection("localhost", 8002)
        body = "name=Bob"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        conn.request("POST", "/submit", body=body, headers=headers)
        resp = conn.getresponse()
        resp.read()
        self.assertEqual(resp.status, 200)
        sent = self.captured["messages"][-1]["content"]
        self.assertIn("POST /submit", sent)
        self.assertIn(body, sent)


if __name__ == "__main__":
    unittest.main()
