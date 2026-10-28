"""Reference test module showing the conventions from SKILL.md.

The unit under test is defined inline so this file runs on its own:
    python -m pytest .agents/skills/pytest-unittest/templates/test_example.py -q
"""
import pytest


def parse_price(raw: str) -> float:
    """Example unit under test: '€1,234.50' -> 1234.5."""
    if not raw or not raw.strip():
        raise ValueError("price must not be empty")
    cleaned = raw.strip().lstrip("€$").replace(",", "")
    value = float(cleaned)
    if value < 0:
        raise ValueError("price must be positive")
    return value


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("10", 10.0), ("€1,234.50", 1234.5), ("  $3.10 ", 3.1)],
    ids=["plain", "euro-thousands", "dollar-whitespace"],
)
def test_parse_price_valid_inputs_return_float(raw, expected):
    assert parse_price(raw) == pytest.approx(expected)


@pytest.mark.parametrize("raw", ["", "   "])
def test_parse_price_blank_input_raises_value_error(raw):
    with pytest.raises(ValueError, match="must not be empty"):
        parse_price(raw)


def test_parse_price_negative_raises_value_error():
    with pytest.raises(ValueError, match="must be positive"):
        parse_price("-1")


def test_parse_price_garbage_raises_value_error():
    with pytest.raises(ValueError):
        parse_price("abc")
