import scraper.scraper
from scraper.models import UserTicketPreference, UserTicketType, UserTimePreferenceType

# mock data
start_loc = "norwich"
end_loc = "LIVERPOOL STREET LONDON"
hour = "09"
min = "00"
day = "20"
month = "06"
year = "24"
num_of_adult_passengers = "2"
num_of_child_passengers = "0"
railcard = False
ticket_preference = UserTicketPreference.CHEAPEST
leaving_type=UserTimePreferenceType.ARRIVING
ticket_type = UserTicketType.RETURN

# return specific params
return_hour = "09"
return_min = "00"
return_day = "25"
return_month = "06"
return_year = "24"

results = scraper.scraper.get_scraped_train_details(
    user_ticket_preference=ticket_preference,
    user_ticket_type=ticket_type,
    start_loc=start_loc,
    end_loc=end_loc,
    month=month,
    day=day,
    hour=hour,
    min=min,
    year=year,
    leaving_type=leaving_type,
    return_hour=return_hour,
    return_min=return_min,
    return_day=return_day,
    return_month=return_month,
    return_year=return_year,
    return_type=leaving_type,
    num_of_adult_passengers=num_of_adult_passengers,
    num_of_child_passengers=num_of_child_passengers,
    railcard=railcard,
)

print(results)
