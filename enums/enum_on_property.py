from enum import Enum

class EnumOnProperty(Enum):
    """Enum for properties on which restrictions can be applied."""
    VZTAZNY_PRVEK = "https://slovník.gov.cz/základní/pojem/má-vztažený-prvek"
    VZTAZNY_PRVEK_1 = "https://slovník.gov.cz/základní/pojem/má-vztažený-prvek-1"
    VZTAZNY_PRVEK_2 = "https://slovník.gov.cz/základní/pojem/má-vztažený-prvek-2"
    JE_VLASTNOSTI = "https://slovník.gov.cz/základní/pojem/je-vlastností"
    

    @classmethod
    def to_list(cls):
        """Returns a list of all enum values as strings."""
        return [member.value for member in cls]