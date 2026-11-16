"""Layer: interface · TDD · TOPAK source: ADR-0031 §1. The schema as a pydantic model with
`extra="forbid"`, and tests that the set is closed and that round-trips are exact (the
`serde` round-trip the reference tests, in Python)."""
import json
from typing import Literal

import pytest
from pydantic import BaseModel, ConfigDict, Field, ValidationError

Digest = str
ActionKind = Literal["Read", "Draft", "Invoke", "Emit", "Submit", "Vote", "Consult", "Actuate", "Report"]


class Confinement(BaseModel):
    model_config = ConfigDict(extra="forbid")
    digest: Digest = Field(pattern=r"^[0-9a-f]{64}$")
    rung: int = Field(ge=0, le=3)


class Lease(BaseModel):
    """ADR-0031 §1: twelve fields, closed."""
    model_config = ConfigDict(extra="forbid", frozen=True)
    principal: str
    seat: str
    persona: Digest = Field(pattern=r"^[0-9a-f]{64}$")
    epoch: int = Field(ge=0)
    fence: int = Field(ge=1)
    rulesEpoch: int = Field(ge=0)
    bundle: Digest = Field(pattern=r"^[0-9a-f]{64}$")
    confinement: Confinement
    alphabet: frozenset[ActionKind]
    round: int = Field(ge=0)
    role: Literal["author", "voter"]
    ttl_ms: int = Field(ge=0)


D = "0" * 64
GOOD = dict(principal="a1", seat="a1", persona=D, epoch=3, fence=41, rulesEpoch=5, bundle=D,
            confinement=dict(digest=D, rung=0), alphabet=["Read", "Emit"], round=7, role="author", ttl_ms=1000)


def test_twelve_fields():
    assert len(Lease.model_fields) == 12


def test_a_thirteenth_field_is_refused():
    with pytest.raises(ValidationError) as e:
        Lease(**GOOD, scope="everything")
    assert "scope" in str(e.value)


@pytest.mark.parametrize("missing", list(GOOD))
def test_every_field_is_required(missing):
    with pytest.raises(ValidationError):
        Lease(**{k: v for k, v in GOOD.items() if k != missing})


def test_rung_is_bounded():
    with pytest.raises(ValidationError):
        Confinement(digest=D, rung=4)


def test_round_trip_is_exact():
    l = Lease(**GOOD)
    assert Lease.model_validate_json(l.model_dump_json()) == l
    assert json.loads(l.model_dump_json())["alphabet"] and set(json.loads(l.model_dump_json())) == set(GOOD)
