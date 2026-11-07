"""Record corruption and enrolment registry module for bari-link."""

from barilink.corrupt.corruption import CorruptionEvent, FieldCorruptor
from barilink.corrupt.registry import RegistryOrchestrator, export_registries
from barilink.corrupt.sampler import EnrolmentCandidate, EnrolmentSampler, RosterMemberRaw
from barilink.corrupt.transliteration import (
    ALL_RULES,
    GENERATOR_ONLY_RULES,
    SHARED_RULES,
    TransliterationRule,
    apply_transliteration_variant,
    get_rule_counts,
)

__all__ = [
    "ALL_RULES",
    "CorruptionEvent",
    "EnrolmentCandidate",
    "EnrolmentSampler",
    "FieldCorruptor",
    "GENERATOR_ONLY_RULES",
    "RegistryOrchestrator",
    "RosterMemberRaw",
    "SHARED_RULES",
    "TransliterationRule",
    "apply_transliteration_variant",
    "export_registries",
    "get_rule_counts",
]
