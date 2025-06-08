import json
import threading
import unittest
from http.client import HTTPConnection
from unittest import mock

from vibestudio import studio


class _StudioThread(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.server = studio.HTTPServer(("localhost", 8502), studio.StudioHandler)

    def run(self):
        self.server.serve_forever()

    def stop(self):
        self.server.shutdown()
        self.server.server_close()


class StudioRestartTest(unittest.TestCase):
    def setUp(self):
        self.proxy_patch = mock.patch.object(studio, "_start_proxy_server")
        self.proxy_patch.start()
        studio.CONVERSATION = [{"role": "user", "content": "old"}]
        studio.LOGS = [{"type": "old"}]
        studio.META_LOGS = [{"direction": "out", "text": "old"}]
        self.thread = _StudioThread()
        self.thread.start()

    def tearDown(self):
        self.thread.stop()
        self.thread.join()
        self.proxy_patch.stop()

    def test_restart_resets_conversation(self):
        conn = HTTPConnection("localhost", 8502)
        body = json.dumps({"prompt": studio.PROMPT, "meta_prompt": studio.META_PROMPT})
        conn.request("POST", "/api/restart", body=body, headers={"Content-Type": "application/json"})
        resp = conn.getresponse()
        resp.read()
        self.assertEqual(resp.status, 200)
        with studio.STATE_LOCK:
            self.assertEqual(len(studio.CONVERSATION), 2)
            self.assertEqual(studio.CONVERSATION[0]["content"], f"{{{{{studio.META_PROMPT}}}}}")
            self.assertEqual(studio.CONVERSATION[1]["content"], f"{{{{{studio.PROMPT}}}}}")


if __name__ == "__main__":
    unittest.main()
