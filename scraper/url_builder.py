# url builder national rail
from scraper.models import UserTimePreferenceType


def generate_url_national_rail_single(
    start_loc_crs,
    end_loc_crs,
    month,
    day,
    hour,
    min,
    year,
    leaving_type,
    num_of_adult_passengers: str,
    num_of_child_passengers: str,
    railcard: bool,
) -> str:
    """
    Args:
        num_of_adult_passengers: str as str is needed in URL
        num_of_adult_passengers: str as str is needed in URL
    """
    ticket_type = "single"

    num_of_adult_passengers_int: int = int(num_of_adult_passengers)
    num_of_child_passengers_int: int = int(num_of_child_passengers)
    leaving_type: str = leaving_type.value

    if num_of_adult_passengers_int > 0 and num_of_child_passengers_int < 1:
        if railcard == True:
            national_rail_url = f"https://www.nationalrail.co.uk/journey-planner/?type={ticket_type}&origin={start_loc_crs}&destination={end_loc_crs}&leavingType={leaving_type}&leavingDate={day}{month}{year}&leavingHour={hour}&leavingMin={min}&adults={num_of_adult_passengers}&railcards=YNG|1"
        else:
            national_rail_url = f"https://www.nationalrail.co.uk/journey-planner/?type={ticket_type}&origin={start_loc_crs}&destination={end_loc_crs}&leavingType={leaving_type}&leavingDate={day}{month}{year}&leavingHour={hour}&leavingMin={min}&adults={num_of_adult_passengers}"
    elif num_of_child_passengers_int > 0:
        national_rail_url = f"https://www.nationalrail.co.uk/journey-planner/?type={ticket_type}&origin={start_loc_crs}&destination={end_loc_crs}&leavingType={leaving_type}&leavingDate={day}{month}{year}&leavingHour={hour}&leavingMin={min}&adults={num_of_adult_passengers}&children={num_of_child_passengers}"
    return national_rail_url


# url builder national rail
def generate_url_national_rail_return(
    start_loc_crs,
    end_loc_crs,
    month,
    day,
    hour,
    min,
    year,
    leaving_type,
    return_hour,
    return_min,
    return_day,
    return_month,
    return_year,
    return_type,
    num_of_adult_passengers: str,
    num_of_child_passengers: str,
    railcard: bool,
) -> str:
    """
    Args:
        num_of_adult_passengers: str as str is needed in URL
        num_of_adult_passengers: str as str is needed in URL
    """
    ticket_type = "return"

    num_of_adult_passengers_int: int = int(num_of_adult_passengers)
    num_of_child_passengers_int: int = int(num_of_child_passengers)
    leaving_type: str = leaving_type.value
    return_type: str = return_type.value

    if num_of_adult_passengers_int > 0 and num_of_child_passengers_int < 1:
        if railcard == True:
            national_rail_url = f"https://www.nationalrail.co.uk/journey-planner/?type={ticket_type}&origin={start_loc_crs}&destination={end_loc_crs}&leavingType={leaving_type}&leavingDate={day}{month}{year}&leavingHour={hour}&leavingMin={min}&returnType={return_type}&returnDate={return_day}{return_month}{return_year}&returnHour={return_hour}&returnMin={return_min}&adults={num_of_adult_passengers}&railcards=YNG|1"
        else:
            national_rail_url = f"https://www.nationalrail.co.uk/journey-planner/?type={ticket_type}&origin={start_loc_crs}&destination={end_loc_crs}&leavingType={leaving_type}&leavingDate={day}{month}{year}&leavingHour={hour}&leavingMin={min}&returnType={return_type}&returnDate={return_day}{return_month}{return_year}&returnHour={return_hour}&returnMin={return_min}&adults={num_of_adult_passengers}"
    elif num_of_child_passengers_int > 0:
        national_rail_url = f"https://www.nationalrail.co.uk/journey-planner/?type={ticket_type}&origin={start_loc_crs}&destination={end_loc_crs}&leavingType={leaving_type}&leavingDate={day}{month}{year}&leavingHour={hour}&leavingMin={min}&returnType={return_type}&returnDate={return_day}{return_month}{return_year}&returnHour={return_hour}&returnMin={return_min}&adults={num_of_adult_passengers}&children={num_of_child_passengers}"
    return national_rail_url
