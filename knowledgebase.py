import re
import enum as Enum
from experta import *
from fuzzywuzzy import process
import scraper.scraper
from scraper.models import UserTicketPreference, UserTicketType
from datetime import datetime

# List of cities along the route from Liverpool to Norwich
CITIES_ON_ROUTE = [
    "liverpool", "london", "colchester", "maningtree", "ipswich",
    "stowmarket", "diss", "norwich"
]

class Ticket(Fact):
    """Info about the ticket."""
    start_loc = Field(str)
    start_loc_crs = Field(str)
    end_loc = Field(str)
    end_loc_crs = Field(str)
    ticket_type = Field(str)
    month = Field(int)
    day = Field(int)
    hour = Field(int)
    minute = Field(int)
    year = Field(int)
    return_hour = Field(int)
    return_min = Field(int)
    return_day = Field(int)
    return_month = Field(int)
    return_year = Field(int)
    railcard = Field(bool)
    price = Field(float)
    pass


class Station(Fact):
    """Info about the station"""
    name = Field(str)
    crs = Field(str)
    pass

class Delay(Fact):
    """Prediction model for delays"""
    current_station = Field(str)
    delay_minutes = Field(int)
    pass

class Action(Fact):
    """Prediction model for delays"""
    name = Field(str)
    pass

class Parameter(Fact):
    name = Field(str)
    value = Field(str)

class PredictionModel(Fact):
    """Model for predicting delay"""
    model_data = Field(dict)
    pass

class DelayQuery(Fact):
    """User input details"""
    start_loc = Field(str, mandatory=False)
    end_loc = Field(str, mandatory=False)
    actual_departure = Field(str, mandatory=False)
    planned_arrival = Field(str, mandatory=False)
    initial_delay = Field(int, mandatory=False)  # Initial delay announced
    pass

class UserQuery(Fact):
    """User input details"""
    start_loc = Field(str, mandatory=True)
    end_loc = Field(str, mandatory=True)
    planned_arrival = Field(str, mandatory=True)
    initial_delay = Field(int, mandatory=True)  # Initial delay announced
    ticket_query = Field(bool, mandatory=True)
    railcard = Field(bool, mandatory=True)
    pass

class TicketBot(KnowledgeEngine):

    @Rule(DelayQuery(start_loc=MATCH.start, end_loc=MATCH.end, actual_departure=MATCH.departure, planned_arrival=MATCH.arrival, initial_delay=MATCH.delay))
    def predict_delay(self, start, end, departure, arrival, delay):
        # Placeholder for actual delay prediction model logic
        current_station = start
        predicted_delay = delay + 10  # Example delay calculation
        self.declare(Delay(current_station=current_station, delay_minutes=predicted_delay))


    @Rule(UserQuery(start_loc=MATCH.start, end_loc=MATCH.end, ticket_type=MATCH.ticket_type,
                    travel_date=MATCH.date, travel_time=MATCH.time, railcard=MATCH.railcard,
                    num_adults=MATCH.num_adults, num_children=MATCH.num_children))
    def find_cheapest_ticket(self, start, end, ticket_type, date, time, railcard, num_adults, num_children):
        travel_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")

        ticket_details = scraper.get_scraped_train_details(
            user_ticket_preference=UserTicketPreference.CHEAPEST,
            user_ticket_type=UserTicketType.SINGLE,
            start_loc=start,
            end_loc=end,
            month=travel_datetime.strftime("%m"),
            day=travel_datetime.strftime("%d"),
            hour=travel_datetime.strftime("%H"),
            min=travel_datetime.strftime("%M"),
            year=travel_datetime.strftime("%Y"),
            return_hour=None,
            return_min=None,
            return_day=None,
            return_month=None,
            return_year=None,
            num_of_adult_passengers=str(num_adults),
            num_of_child_passengers=str(num_children),
            railcard=railcard
        )

        self.declare(Ticket(
            start_loc=start,
            end_loc=end,
            ticket_type=ticket_type,
            month=int(travel_datetime.strftime("%m")),
            day=int(travel_datetime.strftime("%d")),
            hour=int(travel_datetime.strftime("%H")),
            minute=int(travel_datetime.strftime("%M")),
            year=int(travel_datetime.strftime("%Y")),
            railcard=railcard,
            price=ticket_details["ticket_price"],
            purchase_link=ticket_details["ticket_purchase_link"]
        ))
        @Rule(Ticket(price=MATCH.price, purchase_link=MATCH.link))
        def present_cheapest_ticket(self, price, link):
            print(f"BOT: The cheapest ticket available is £{price}. You can purchase it here: {link}.")

def get_user_input(prompt):
    return input(prompt).strip().lower()

def determine_intent(user_input):
    ticket_keywords = ['book', 'ticket', 'cheapest', 'buy']
    delay_keywords = ['delay', 'late', 'status', 'predict']

    for word in ticket_keywords:
        if word in user_input:
            return 'ticket'
    for word in delay_keywords:
        if word in user_input:
            return 'delay'
    return None

def extract_delay_information(user_input):
    # Regex patterns to extract from, to, initial delay, and planned arrival
    from_pattern = r'from\s(\w+)'
    to_pattern = r'to\s(\w+)'
    delay_pattern = r'(\d+)\sminutes\sdelay'
    arrival_pattern = r"planned\sarrival\s+(\d{1,2}):(\d{2})"
    actual_pattern = r"actual\sdeparture\s+(\d{1,2}):(\d{2})"

    start_loc = re.search(from_pattern, user_input)
    end_loc = re.search(to_pattern, user_input)
    initial_delay = re.search(delay_pattern, user_input)
    planned_arrival = re.search(arrival_pattern, user_input)
    actual_departure = re.search(actual_pattern, user_input)

    info = {
        'start_loc': start_loc.group(1) if start_loc else None,
        'end_loc': end_loc.group(1) if end_loc else None,
        'initial_delay': int(initial_delay.group(1)) if initial_delay else None,
        'planned_arrival': planned_arrival.group(1) + ":" + planned_arrival.group(2) if planned_arrival else None,
        'actual_departure': actual_departure.group(1) + ":" + actual_departure.group(2) if actual_departure else None
    }

    filtered = {k: v for k, v in info.items() if v is not None}
    info.clear()
    info.update(filtered)

    return info

def validate_delay_query(user_query):
    # Validate and correct city names
    if user_query.get('start_loc'):
        validated_city = validate_city(user_query['start_loc'])
        if validated_city:
            user_query['start_loc'] = validated_city
        else:
            print("BOT: Please enter a valid city along the route from Liverpool to Norwich.")
            return
    if user_query.get('end_loc'):
        validated_city = validate_city(user_query['end_loc'])
        if validated_city:
            user_query['end_loc'] = validated_city
        else:
            print("BOT: Please enter a valid city along the route from Liverpool to Norwich.")
            return

def validate_city(city):
    if city:
        best_match, score = process.extractOne(city, CITIES_ON_ROUTE)
        if score >= 80:  # Threshold for considering it a good match
            return best_match
        else:
            print("BOT: I only support cities along the route from Liverpool to Norwich.")
            return None
    return None


def nlp_confirm_user_input(user_input):
    positive_responses = ['yes', 'yep', 'yeah', 'sure', 'correct', 'right']
    negative_responses = ['no', 'nope', 'nah', 'wrong', 'incorrect']

    if any(word in user_input for word in positive_responses):
        return 'yes'
    elif any(word in user_input for word in negative_responses):
        return 'no'
    else:
        return 'unclear'


def confirm_user_intent(user_query):
    while True:
        confirmation = get_user_input(
            f"BOT: You want to predict the delay for your train from {user_query['start_loc']} to {user_query['end_loc']} with an initial delay of {user_query['initial_delay']} minutes and a planned arrival time of {user_query['planned_arrival']}. Is that correct? (yes/no) "
        )
        nlp_confirmation = nlp_confirm_user_input(confirmation)

        if nlp_confirmation == 'yes':
            return True
        elif nlp_confirmation == 'no':
            return False
        else:
            print("BOT: I'm sorry, is that a yes or a no?")


def complete_user_query(user_query):
    if not user_query.get('start_loc'):
        while True:
            start_loc = get_user_input("BOT: Where are you departing from? ")
            valid_city = validate_city(start_loc)
            if valid_city:
                user_query['start_loc'] = valid_city
                break
            else:
                print("BOT: Please enter a valid city along the route from Liverpool to Norwich.")
    if not user_query.get('end_loc'):
        while True:
            end_loc = get_user_input("BOT: Where are you going? ")
            valid_city = validate_city(end_loc)
            if valid_city:
                user_query['end_loc'] = valid_city
                break
            else:
                print("BOT: Please enter a valid city along the route from Liverpool to Norwich.")
    if not user_query.get('initial_delay'):
        user_query['initial_delay'] = int(get_user_input("BOT: What is the announced delay in minutes? "))
    if not user_query.get('planned_arrival'):
        user_query['planned_arrival'] = get_user_input("BOT: What is the planned arrival time? (e.g., 14:30) ")


def complete_delay_user_query(user_query):
    if not user_query.get('start_loc'):
        while True:
            start_loc = get_user_input("BOT: Where are you departing from? ")
            valid_city = validate_city(start_loc)
            if valid_city:
                user_query['start_loc'] = valid_city
                break
            else:
                print("BOT: Please enter a valid city along the route from Liverpool to Norwich.")
    if not user_query.get('end_loc'):
        while True:
            end_loc = get_user_input("BOT: Where are you going? ")
            valid_city = validate_city(end_loc)
            if valid_city:
                user_query['end_loc'] = valid_city
                break
            else:
                print("BOT: Please enter a valid city along the route from Liverpool to Norwich.")
    if not user_query.get('initial_delay'):
        user_query['initial_delay'] = int(get_user_input("BOT: What is the announced delay in minutes? "))
    if not user_query.get('planned_arrival'):
        user_query['planned_arrival'] = get_user_input("BOT: What is the planned arrival time? (e.g., 14:30) ")
    if not user_query.get('actual_departure'):
        user_query['actual_departure'] = get_user_input("BOT: What is the actual_departure time? (e.g., 14:30) ")



def main():
    user_query = {}

    user_intent_input = get_user_input("BOT: How can I assist you today? ")
    user_query['query_type'] = determine_intent(user_intent_input)

    if user_query['query_type'] == 'delay':
        extracted_info = extract_delay_information(user_intent_input)
        user_query.update(extracted_info)

        # Validate and correct city names
        if user_query.get('start_loc'):
            validated_city = validate_city(user_query['start_loc'])
            if validated_city:
                user_query['start_loc'] = validated_city
            else:
                print("BOT: Please enter a valid city along the route from Liverpool to Norwich.")
                return
        if user_query.get('end_loc'):
            validated_city = validate_city(user_query['end_loc'])
            if validated_city:
                user_query['end_loc'] = validated_city
            else:
                print("BOT: Please enter a valid city along the route from Liverpool to Norwich.")
                return

        complete_user_query(user_query)

        if not confirm_user_intent(user_query):
            print("BOT: Let's try again.")
            main()
            return

    else:
        print("BOT: Currently, I can only assist with predicting train delays.")
        return

    engine = TicketBot()
    engine.reset()
    #engine.declare(UserQuery(**user_query))
    engine.declare(DelayQuery(**user_query))
    engine.run()

    for fact in engine.facts.values():
        if isinstance(fact, Delay):
            print(
                f"BOT: Your train is predicted to be delayed by {fact['delay_minutes']} minutes at {fact['current_station']}.")
            print(f"BOT: The predicted delay is {fact['delay_minutes']} minutes. Please plan accordingly.")

    

if __name__ == "__main__":
    main()
