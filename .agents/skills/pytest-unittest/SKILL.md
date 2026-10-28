---
name: pytest-unittest
description: Write focused, fast, deterministic unit tests for Python code with pytest. Covers choosing behaviours to test, file layout, fixtures, parametrization, mocking at boundaries, and running and fixing the suite. Use when the user asks to "add tests", "write unit tests", "test this function/module", raise coverage, or after implementing a behaviour change in Python.
---

# Unit tests with pytest

Tool-agnostic. You only need to read and edit files and run shell commands.

## 0. Prerequisites

- Check that pytest is available: `python -m pytest --version`. If it is missing,
  add `pytest` (and optionally `pytest-cov`) to the project's dev dependencies
  (`requirements-dev.txt`, `pyproject.toml` extras, Poetry/uv group), whichever
  the project already uses, and install it. Don't add a second dependency system.
- Read existing tests and `conftest.py` first, then match their style, fixtures and helpers.
- Read the pytest config (`pyproject.toml [tool.pytest.ini_options]`,
  `pytest.ini`, `setup.cfg`) for `testpaths`, `pythonpath`, markers.

## 1. Decide what to test

Read the code under test and list its **behaviours** (not its lines):

1. **Happy path:** typical inputs → expected output/side effect.
2. **Edge cases:** empty, zero, one, many, boundaries (`max`, `max+1`), unicode,
   `None`, duplicates, ordering.
3. **Error paths:** invalid input raises the documented exception and message;
   failures in dependencies are handled.
4. **Contracts:** return types, idempotency, no mutation of inputs, the side
   effects that callers depend on.

Test the public interface. Don't assert on private helpers or implementation
details that could change in a refactor without changing behaviour.

## 2. Layout and naming

- Mirror the source tree: `src/pkg/billing.py` → `tests/test_billing.py`
  (or `tests/pkg/test_billing.py` if the project nests).
- Test function names describe behaviour:
  `test_<unit>_<condition>_<expected>`, e.g. `test_parse_date_with_empty_string_raises_value_error`.
- Group related tests with plain functions; use a `class TestX:` only when it
  aids reading (no `unittest.TestCase` unless the project already uses it).
- Shared fixtures go in the nearest `conftest.py`. One-off setup stays in the test.

## 3. Write each test: Arrange, Act, Assert

```python
def test_apply_discount_caps_at_order_total():
    # Arrange
    order = Order(total=Decimal("20.00"))
    # Act
    result = apply_discount(order, Decimal("50.00"))
    # Assert
    assert result.total == Decimal("0.00")
```

Rules:
- **One behaviour per test.** Several asserts are fine if they describe the same outcome.
- Use plain `assert`. pytest rewrites it to show helpful diffs.
- Exceptions: `with pytest.raises(ValueError, match="must be positive"):`.
- Floats: `assert x == pytest.approx(0.3)`.
- Collapse near-duplicate tests with parametrization:

```python
@pytest.mark.parametrize(
    ("raw", "expected"),
    [("1", 1), (" 42 ", 42), ("-7", -7)],
    ids=["simple", "whitespace", "negative"],
)
def test_parse_int_valid_inputs(raw, expected):
    assert parse_int(raw) == expected
```

## 4. Isolation: keep tests deterministic

| Need | Use |
|------|-----|
| Files / dirs | built-in `tmp_path` fixture. Never write into the repo. |
| Env vars, attributes, `sys.path` | `monkeypatch.setenv`, `monkeypatch.setattr` |
| Time | inject a clock/`now` parameter, or monkeypatch the module's `datetime` |
| Randomness | seed it, or inject the RNG |
| Network, DB, subprocess, third-party APIs | mock **at the boundary you own** (`monkeypatch.setattr(module, "fetch", fake)` or `unittest.mock`) |
| Output | `capsys` / `caplog` |

- Patch where the name is **looked up**, not where it is defined
  (`mocker.patch("app.service.requests.get")`, not `"requests.get"`).
- Prefer simple fakes over deep `MagicMock` chains. If a test needs heavy mocking,
  tell the user the design could improve (e.g. dependency injection) instead of
  hiding it.
- No test may depend on another test's state or on execution order.
- No `time.sleep`. No real network.

## 5. Fixtures

```python
@pytest.fixture
def repo(tmp_path):
    """A throwaway repository with one committed file."""
    ...
    yield path          # teardown after yield, if needed
```

- Keep fixtures small and composable. Use the default function scope unless setup is
  genuinely expensive and immutable.
- Use factory fixtures (`make_user(**overrides)`) instead of many near-identical fixtures.
- See `templates/conftest.py` and `templates/test_example.py` in this skill.

## 6. Run, fix, repeat

```bash
python -m pytest -q                       # whole suite
python -m pytest tests/test_billing.py -q # one file
python -m pytest -k "discount and not slow" -q
python -m pytest --cov=<package> --cov-report=term-missing   # if pytest-cov is installed
```

- A new test should **fail first** when written against a bug or before the
  implementation exists. If it can't fail, it isn't testing anything.
- When a test fails, decide: is the **code** wrong or the **test** wrong? Never
  weaken an assertion just to get green. Report real bugs to the user.
- Coverage is a hint, not a goal. Uncovered branches with real logic deserve tests.
  Trivial getters don't.

## 7. Done checklist

- [ ] Happy path, edge cases and error paths covered for each changed behaviour
- [ ] Tests are isolated (tmp_path/monkeypatch/mocks), fast (< ~100 ms each), deterministic
- [ ] Names read as specifications
- [ ] Full suite passes locally. Paste the summary line in your report
- [ ] Commit as `test: ...` (or with the feature it covers)
