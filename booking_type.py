from enum import Enum

class BookingType(Enum):
    SUS = 1
    DEPT = 2
    SCI = 3
    UBC = 4
    EXT = 5

getBookingType = {
    'SUS Internal Group': BookingType.SUS,
    'Science Departmental Club': BookingType.DEPT,
    'UBC Organization (Science Affiliated)': BookingType.SCI,
    'UBC Organization (Non-Science Affiliated)': BookingType.UBC,
    'External Organization': BookingType.EXT
}