import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_each_test_case_creates_assert(client, monkeypatch):

    fake_llm_response = {
        "candidates": [{
            "content": {
                "parts": [{
                    "text": (
                        "import unittest\n\n"
                        "class TestGen(unittest.TestCase):\n"
                        "    def test_1(self):\n"
                        "        assert True\n\n"
                        "    def test_2(self):\n"
                        "        assert True\n"
                    )
                }]
            }
        }]
    }

    class FakeResponse:
        status_code = 200
        def raise_for_status(self): pass
        def json(self): return fake_llm_response

    monkeypatch.setattr(
        "uygulamaKısmı.views.requests.post",
        lambda *a, **k: FakeResponse()
    )

    cases = "input,expected\n1,1\n2,4"

    response = client.post(
        reverse("llm_testcode"),
        data={"cases": cases}
    )

    result = response.context["result"]

    assert result.count("assert") >= 2
