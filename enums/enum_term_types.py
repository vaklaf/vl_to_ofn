from enum import Enum

class EnumTermTypes(Enum):
    VLASTNOST = "<https://slovník.gov.cz/základní/pojem/typ-vlastnosti>"
    VZTAH = "<https://slovník.gov.cz/základní/pojem/typ-vztahu>"
    OBJEKT = "<https://slovník.gov.cz/základní/pojem/typ-objektu>"
    
    @classmethod
    def to_list(cls):
        """Returns a list of all enum values as strings."""
        return [member.value for member in cls]
    
    @classmethod
    def from_value(cls, value):
        """Returns the enum member name capitalized according to the value."""
        if value is None:
            return None
        
        for member in cls:
            if member.value == "<"+value+">": 
                name = "Třída" if member == cls.OBJEKT else member.name.capitalize()
                return (member,name)
        return None