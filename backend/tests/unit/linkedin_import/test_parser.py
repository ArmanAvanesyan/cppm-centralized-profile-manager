"""Unit tests for app.modules.linkedin_import.parser."""
from app.modules.linkedin_import.parser import parse_linkedin_file


def test_parse_linkedin_file():
    exp, edu, skills = parse_linkedin_file("/tmp/fake.pdf")
    assert exp == []
    assert edu == []
    assert skills == []
