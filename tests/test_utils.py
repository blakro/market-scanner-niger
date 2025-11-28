from src.utils import clean_json_response

def test_clean_json_response_simple():
    text = '{"key": "value"}'
    assert clean_json_response(text) == '{"key": "value"}'

def test_clean_json_response_markdown():
    text = '```json\n{"key": "value"}\n```'
    assert clean_json_response(text) == '{"key": "value"}'

def test_clean_json_response_markdown_no_json_tag():
    text = '```\n{"key": "value"}\n```'
    assert clean_json_response(text) == '{"key": "value"}'

def test_clean_json_response_empty():
    assert clean_json_response("") == ""
    assert clean_json_response(None) == ""
