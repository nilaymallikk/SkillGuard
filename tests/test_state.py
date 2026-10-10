"""the scan state's shape and its reducer channels."""

from __future__ import annotations

import operator
from typing import get_type_hints

from skillguard.state import ScanState


def _reducer_of(channel: str) -> tuple[object, ...]:
    """Return the reducer metadata attached to a state channel, if any."""
    hints = get_type_hints(ScanState, include_extras=True)
    return getattr(hints[channel], "__metadata__", ())


def test_findings_channel_has_a_reducer() -> None:
    # Without this, parallel analyzers overwrite each other's findings.
    assert operator.add in _reducer_of("findings")


def test_errors_channel_has_a_reducer() -> None:
    assert operator.add in _reducer_of("errors")


def test_deduplicated_findings_has_no_reducer() -> None:
    # deduplicate is the single writer of this channel.
    assert _reducer_of("effective_findings") == ()


def test_state_accepts_partial_updates() -> None:
    assert ScanState(input_ref="./some-skill") == {"input_ref": "./some-skill"}
