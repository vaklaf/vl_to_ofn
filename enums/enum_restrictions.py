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
    
    
class EnumRestrictionsLong(Enum):
    SOME_VALUES_FROM = "http://www.w3.org/2002/07/owl#someValuesFrom"
    ALL_VALUES_FROM = "http://www.w3.org/2002/07/owl#allValuesFrom"
    MIN_QUALIFIED_CARDINALITY = "http://www.w3.org/2002/07/owl#minQualifiedCardinality"
    MAX_QUALIFIED_CARDINALITY = "http://www.w3.org/2002/07/owl#maxQualifiedCardinality"

    @classmethod
    def to_list(cls):
        """Returns a list of all enum values as strings."""
        return [member.value for member in cls]