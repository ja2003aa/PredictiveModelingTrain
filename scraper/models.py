from enum import Enum


class UserTicketPreference(Enum):
    CHEAPEST = 1
    EARLIEST = 2


class UserTicketType(Enum):
    SINGLE = 1
    RETURN = 2
    
class UserTimePreferenceType(Enum):
    ARRIVING = "arriving"
    DEPARTING = "departing"
