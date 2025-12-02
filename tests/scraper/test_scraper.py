import pytest
from scraper import scraper
from scraper.models import UserTicketPreference, UserTicketType, UserTimePreferenceType

def test_scraper_success_single_cheapest():
    results = scraper.get_scraped_train_details(
        user_ticket_preference=UserTicketPreference.CHEAPEST,
        user_ticket_type=UserTicketType.SINGLE,
        start_loc="Norwich",
        end_loc="Liverpool Street London",
        hour="08",
        min="30",
        day="07",
        month="06",
        year="24",
        leaving_type=UserTimePreferenceType.DEPARTING,
        return_hour = None,
        return_min = None,
        return_day=None,
        return_month=None,
        return_year=None,
        return_type=None,
        num_of_adult_passengers="1",
        num_of_child_passengers="0",
        railcard=True,
    )
    
    
    print(results)
    assert results["user_ticket_preference"] is UserTicketPreference.CHEAPEST
    assert results["journeys_outbound"]["journeys"] is not None
    
def test_scraper_success_single_earliest():
    results = scraper.get_scraped_train_details(
        user_ticket_preference=UserTicketPreference.EARLIEST,
        user_ticket_type=UserTicketType.SINGLE,
        start_loc="Norwich",
        end_loc="Liverpool Street London",
        hour="08",
        min="30",
        day="07",
        month="06",
        year="24",
        leaving_type=UserTimePreferenceType.DEPARTING,
        return_hour = None,
        return_min = None,
        return_day=None,
        return_month=None,
        return_year=None,
        return_type=None,
        num_of_adult_passengers="1",
        num_of_child_passengers="0",
        railcard=True,
    )
    
    
    print(results)
    assert results["user_ticket_preference"] is UserTicketPreference.EARLIEST
    assert results["journeys_outbound"]["journeys"] is not None
    
def test_scraper_success_return_cheapest():
    results = scraper.get_scraped_train_details(
        user_ticket_preference=UserTicketPreference.CHEAPEST,
        user_ticket_type=UserTicketType.RETURN,
        start_loc="Norwich",
        end_loc="Liverpool Street London",
        hour="08",
        min="30",
        day="07",
        month="06",
        year="24",
        leaving_type=UserTimePreferenceType.DEPARTING,
        return_hour = "08",
        return_min = "30",
        return_day = "09",
        return_month = "06",
        return_year = "24",
        return_type=UserTimePreferenceType.ARRIVING,
        num_of_adult_passengers="1",
        num_of_child_passengers="0",
        railcard=False,
    )
    
    print(results)
    assert results["user_ticket_preference"] is UserTicketPreference.CHEAPEST
    assert results["journeys_outbound"]["journeys"] is not None
    
def test_scraper_success_return_earliest():
    results = scraper.get_scraped_train_details(
        user_ticket_preference=UserTicketPreference.EARLIEST,
        user_ticket_type=UserTicketType.RETURN,
        start_loc="Norwich",
        end_loc="Liverpool Street London",
        hour="08",
        min="30",
        day="07",
        month="06",
        year="24",
        leaving_type=UserTimePreferenceType.DEPARTING,
        return_hour = "08",
        return_min = "30",
        return_day = "09",
        return_month = "06",
        return_year = "24",
        return_type=UserTimePreferenceType.ARRIVING,
        num_of_adult_passengers="1",
        num_of_child_passengers="2",
        railcard=True,
    )
    
    print(results)
    assert results["user_ticket_preference"] is UserTicketPreference.EARLIEST
    assert results["journeys_outbound"]["journeys"] is not None
    
def test_scraper_no_adults_with_railcard():
    results = scraper.get_scraped_train_details(
        user_ticket_preference=UserTicketPreference.EARLIEST,
        user_ticket_type=UserTicketType.RETURN,
        start_loc="Norwich",
        end_loc="Liverpool Street London",
        hour="08",
        min="30",
        day="07",
        month="06",
        year="24",
        leaving_type=UserTimePreferenceType.DEPARTING,
        return_hour = "08",
        return_min = "30",
        return_day = "09",
        return_month = "06",
        return_year = "24",
        return_type=UserTimePreferenceType.ARRIVING,
        num_of_adult_passengers="0",
        num_of_child_passengers="2",
        railcard=True,
    )
    
    print(results)
    assert results["user_ticket_preference"] is UserTicketPreference.EARLIEST
    assert results["journeys_outbound"]["journeys"] is not None
    
def test_scraper_success_with_changeovers():
    results = scraper.get_scraped_train_details(
        user_ticket_preference=UserTicketPreference.EARLIEST,
        user_ticket_type=UserTicketType.RETURN,
        start_loc="Norwich",
        end_loc="Dundee",
        hour="08",
        min="30",
        day="07",
        month="06",
        year="24",
        leaving_type=UserTimePreferenceType.DEPARTING,
        return_hour = "09",
        return_min = "15",
        return_day = "09",
        return_month = "06",
        return_year = "24",
        return_type=UserTimePreferenceType.ARRIVING,
        num_of_adult_passengers="1",
        num_of_child_passengers="0",
        railcard=True,
    )
    
    print(results)
    assert results["user_ticket_preference"] is UserTicketPreference.EARLIEST
    assert len(results["journeys_outbound"]["journeys"]) > 1
    
def test_scraper_success_changeovers_with_no_platforms():
    results = scraper.get_scraped_train_details(
        user_ticket_preference=UserTicketPreference.EARLIEST,
        user_ticket_type=UserTicketType.RETURN,
        start_loc="Daisy Hill",
        end_loc="Dundee",
        hour="08",
        min="30",
        day="07",
        month="06",
        year="24",
        leaving_type=UserTimePreferenceType.DEPARTING,
        return_hour = "09",
        return_min = "15",
        return_day = "09",
        return_month = "06",
        return_year = "24",
        return_type=UserTimePreferenceType.ARRIVING,
        num_of_adult_passengers="1",
        num_of_child_passengers="0",
        railcard=True,
    )
    
    print(results)
    assert results["user_ticket_preference"] is UserTicketPreference.EARLIEST
    assert len(results["journeys_outbound"]["journeys"]) > 1
    assert any(journey["start_platform"] is None for journey in results["journeys_outbound"]["journeys"])
    
def test_scraper_failure_no_path_found():
    results = scraper.get_scraped_train_details(
        user_ticket_preference=UserTicketPreference.EARLIEST,
        user_ticket_type=UserTicketType.RETURN,
        start_loc="OAKENGATES",
        end_loc="PADDOCK WOOD",
        hour="08",
        min="30",
        day="07",
        month="06",
        year="24",
        leaving_type=UserTimePreferenceType.DEPARTING,
        return_hour = "08",
        return_min = "30",
        return_day = "09",
        return_month = "05",
        return_year = "24",
        return_type=UserTimePreferenceType.ARRIVING,
        num_of_adult_passengers="0",
        num_of_child_passengers="2",
        railcard=True,
    )
    
    print(results)
    assert results["status"] is "unsuccessful"

def test_scraper_bad_start_location_CRS_error():
    results = scraper.get_scraped_train_details(
        user_ticket_preference=UserTicketPreference.CHEAPEST,
        user_ticket_type=UserTicketType.SINGLE,
        start_loc="notexistantigde",
        end_loc="London Liverpool Street",
        hour="08",
        min="09",
        day="07",
        month="06",
        year="24",
        leaving_type=UserTimePreferenceType.DEPARTING,
        return_hour = None,
        return_min = None,
        return_day=None,
        return_month=None,
        return_year=None,
        return_type=None,
        num_of_adult_passengers="1",
        num_of_child_passengers="0",
        railcard=True,
    )
    
    assert results["status"] is "unsuccessful"

