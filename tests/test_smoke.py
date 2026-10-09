"""Phase 0 smoke test: the package installs and exposes its version."""

from skillguard import __version__


def test_version_is_a_string() -> None:
    assert isinstance(__version__, str)
    assert __version__
