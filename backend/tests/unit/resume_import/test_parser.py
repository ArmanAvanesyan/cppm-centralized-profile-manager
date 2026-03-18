"""Unit tests for app.modules.resume_import.parser."""

from app.modules.resume_import.parser import extract_text_from_file, parse_resume_text


def test_extract_text_from_file():
    text = extract_text_from_file("/tmp/fake.pdf")
    assert text == "Stub extracted text"


def test_parse_resume_text():
    exp, skills = parse_resume_text("some text")
    assert exp == []
    assert skills == []
