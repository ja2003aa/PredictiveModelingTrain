from typing import Optional
from scraper.firefox_driver import initialize_browser
from scraper.crs_converter import crs_converter
from scraper.models import UserTicketPreference, UserTicketType, UserTimePreferenceType
from scraper.national_rail import (
    calculate_total_journey_time,
    get_route_national_rail_single,
    get_route_national_rail_return,
)
from scraper.url_builder import (
    generate_url_national_rail_single,
    generate_url_national_rail_return,
)


def get_scraped_train_details(
    user_ticket_preference: UserTicketPreference,
    user_ticket_type: UserTicketType,
    start_loc: str,
    end_loc: str,
    month: str,
    day: str,
    hour: str,
    min: str,
    year: str,
    leaving_type: UserTimePreferenceType,
    return_hour: Optional[str],
    return_min: Optional[str],
    return_day: Optional[str],
    return_month: Optional[str],
    return_year: Optional[str],
    return_type: Optional[UserTimePreferenceType],
    num_of_adult_passengers: str,
    num_of_child_passengers: str,
    railcard: bool,
):
    print(day)
    print(month)
    print(return_day)
    print(return_month)
    try:
        start_loc_crs, end_loc_crs = crs_converter(start_loc, end_loc)
    except BaseException as e:
        return {
            "status": "unsuccessful",
            "error": e
        }
    driver = initialize_browser()

    if user_ticket_type == UserTicketType.SINGLE:
        national_rail_url = generate_url_national_rail_single(
            start_loc_crs,
            end_loc_crs,
            month,
            day,
            hour,
            min,
            year,
            leaving_type,
            num_of_adult_passengers,
            num_of_child_passengers,
            railcard=True,
        )

        print("scraper: get_route_national_rail_single")
        try:    
            journeys_outbound, price = get_route_national_rail_single(
                driver, national_rail_url, user_ticket_preference
            )
        except BaseException as e:
            return {
                "status": "unsuccessful",
                "error": e
            }

        driver.close()
        driver.quit()

        return {
            "start_location": journeys_outbound[0]["start_loc"],
            "end_location": journeys_outbound[-1]["end_loc"],
            "user_ticket_preference": user_ticket_preference,
            "user_ticket_type": user_ticket_type,
            "ticket_price": price,
            "ticket_purchase_link": national_rail_url,
            "journeys_outbound": {
                "journeys": journeys_outbound,
                "time": calculate_total_journey_time(journeys_outbound),
            },
            "journeys_return": None,
        }

    elif user_ticket_type == UserTicketType.RETURN:

        if not return_hour:
            raise TypeError("return_hour must be str")

        national_rail_url = generate_url_national_rail_return(
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
            num_of_adult_passengers,
            num_of_child_passengers,
            railcard=railcard,
        )
        
        print("scraper: get_route_national_rail_return")
        try:
            journeys_outbound, journeys_return, price = get_route_national_rail_return(
                driver, national_rail_url, user_ticket_preference
            )
        except BaseException as e:
            print(e)
            return {
                "status": "unsuccessful",
                "error": e
            }

        driver.close()
        driver.quit()

        return {
            "start_location": journeys_outbound[0]["start_loc"],
            "end_location": journeys_outbound[-1]["end_loc"],
            "user_ticket_preference": user_ticket_preference,
            "user_ticket_type": user_ticket_type,
            "ticket_price": price,
            "ticket_purchase_link": national_rail_url,
            "journeys_outbound": {
                "journeys": journeys_outbound,
                "time": calculate_total_journey_time(journeys_outbound),
            },
            "journeys_return": {
                "journeys": journeys_return,
                "time": calculate_total_journey_time(journeys_return),
            },
        }
