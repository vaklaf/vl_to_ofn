from enum import Enum


class EnumRestrictions(Enum):
    SOME_VALUES_FROM = "owl:someValuesFrom"
    ALL_VALUES_FROM = "owl:allValuesFrom"
    MIN_QUALIFIED_CARDINALITY = "owl:minQualifiedCardinality"
    MAX_QUALIFIED_CARDINALITY = "owl:maxQualifiedCardinality"

    @classmethod
    def to_list(cls):
        """Returns a list of all enum values as strings."""
        return [member.value for member in cls]