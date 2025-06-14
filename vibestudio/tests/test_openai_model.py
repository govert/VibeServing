import os
import types
import unittest
from unittest import mock

from vibestudio import studio

class OpenAIModelEnvTest(unittest.TestCase):
    def test_model_variable_used(self):
        fake_response = types.SimpleNamespace()
        fake_response.choices = [types.SimpleNamespace(message=types.SimpleNamespace(content="ok"))]
        fake_openai = types.SimpleNamespace()
        fake_openai.responses = types.SimpleNamespace(create=mock.Mock(return_value=fake_response))
        fake_openai.chat = types.SimpleNamespace()
        fake_openai.chat.completions = types.SimpleNamespace(create=mock.Mock(return_value=fake_response))
        fake_openai.ChatCompletion = types.SimpleNamespace(create=mock.Mock(return_value=fake_response))
        with mock.patch.dict(studio.__dict__, {"openai": fake_openai}):
            with mock.patch.dict(os.environ, {"OPENAI_API_KEY": "x"}):
                studio.MODEL = "test-model"
                messages = [{"role": "user", "content": "prompt"}]
                studio.ProxyHandler.call_llm(studio.ProxyHandler, messages)
                fake_openai.responses.create.assert_called_with(
                    model="test-model",
                    messages=messages,
                    previous_response_id=None,
                )

if __name__ == "__main__":
    unittest.main()
