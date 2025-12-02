import json
import time
import random
import spacy
from experta import *
from spacy.matcher import Matcher
import streamlit as st
#from knowledgebase import expert_response
import knowledgebase
import predefined_chat_messages
from knowledgebase import validate_city, validate_delay_query, extract_delay_information, DelayQuery, TicketBot, Delay

#from scraper import scraper
#from scraper.models import UserTicketPreference, UserTicketType

# Load intents from JSON file
with open('intentions.json') as file:
    intents = json.load(file)

# Load actions from JSON file
with open('actions.json') as file:
    actions = json.load(file)

nlp = spacy.load('en_core_web_lg')
matcher = Matcher(nlp.vocab)

def response_generator(response):
    if response is None:
        yield "no response"
        return
    for word in response.split():
        yield word + " "
        time.sleep(0.09)

def check_intention_by_keyword(user_input):
    for intent_name, intent_data in intents.items():
        for pattern in intent_data['patterns']:
            if pattern.lower() in user_input.lower():
                return intent_name
    return None

def check_actions_by_keyword(user_input):
    actions_found = []
    for actions_name, actions_data in actions.items():
        for pattern in actions_data['patterns']:
            if pattern.lower() in user_input.lower():
                actions_found.append(actions_name)
    return actions_found

def get_response(intent):
    if intent and intent in intents:
        return random.choice(intents[intent]['responses'])
    else:
        return "Sorry, I don't understand that. Please rephrase your statement."

# Set page title
st.title("TicketHelper: Book a train ticket and check delays")

# Initialize chat history and output initial greeting
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": predefined_chat_messages.INITIAL_GREETING})
    st.session_state.action = None
    st.session_state.params = {}

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handling user input
def check_params_by_keyword(prompt):
    pass

def get_answer_for_simple_intention(prompt):
    intention = check_intention_by_keyword(prompt)
    if intention == "restart":
        st.session_state.params = {}
        st.session_state.engine = None
    if intention is None:
        return None
    response = get_response(intention)
    return response


def check_actions_complete_():
    return True

def complete_delay_query(user_query):
    missing_information = []
    invalid_information = []
    print(user_query)

    if user_query.get('start_loc'):
        start_loc = user_query.get('start_loc')
        valid_city = validate_city(start_loc)
        if valid_city:
            user_query['start_loc'] = valid_city
        else:
            invalid_information.append("start location")
    else:
        missing_information.append("start location")

    if user_query.get('end_loc'):
        end_loc = user_query.get('end_loc')
        valid_city = validate_city(end_loc)
        if valid_city:
            user_query['end_loc'] = valid_city
        else:
            invalid_information.append("end_loc")
    else:
        missing_information.append("end_loc")

    if not user_query.get('initial_delay'):
        missing_information.append("initial delay")
    if not user_query.get('planned_arrival'):
        missing_information.append("planned arrival")
    if not user_query.get('actual_departure'):
        missing_information.append("actual departure")
    return missing_information, invalid_information


def extract_cheapest_information(prompt):
    pass


def validate_cheapest_query(params):
    pass


def complete_cheapest_query(params):
    pass


def get_answer_for_actions(prompt):
    # Recognize actions start

    print("DEBUG TEST 1")
    actions = check_actions_by_keyword(prompt)
    print(actions)

    if len(actions) > 1:
        return "BOT: I am not sure do you want to do, buy or check a delay."
    #
    elif len(actions) == 1:
        if st.session_state.action is not None:
            if actions[0] == st.session_state.action:
                pass
            else:
                return "BOT: I am already doing an action write restart if you want to restart"

        # ask user if they want cancel current action and start new one
        else:
            st.session_state.action = actions[0]
            print("SET NEW ACTION")
            st.session_state.params = {}
            st.session_state.engine = TicketBot()
            st.session_state.engine.reset()
            if st.session_state.action == "delay":
                st.session_state.engine.declare(DelayQuery(**st.session_state.params))
                st.session_state.engine.run()

    if st.session_state.action is not None:
        if check_actions_complete_():
            if st.session_state.action == "cheapest":
                st.session_state.params = {**st.session_state.params, **extract_cheapest_information(prompt)}
                validate_cheapest_query(st.session_state.params)
                missing, invalid = complete_cheapest_query(st.session_state.params)
                if len(missing) > 0:
                    return "missing " + str(missing)
                if len(invalid) > 0:
                    return "invalid " + str(invalid)
                if len(missing) == 0 and len(invalid) == 0:
                    print("ALL PARAMS VALID")
                st.session_state.engine.find_cheapest_ticket(st.session_state.params.get("start_loc"),
                                                      st.session_state.params.get("end_loc"),
                                                      st.session_state.params.get("planned_arrival"),
                                                      st.session_state.params.get("railcard"))
                fact = list(st.session_state.engine.facts.values())[-1]
                print(fact)
                return f"BOT: Your train ticket  {fact['price']}"

            if st.session_state.action == "delay":
                print(st.session_state.params)
                st.session_state.params = {**st.session_state.params, **extract_delay_information(prompt)}
                print(st.session_state.params)
                validate_delay_query(st.session_state.params)
                missing, invalid = complete_delay_query(st.session_state.params)
                if len(missing) > 0:
                    return "missing " + str(missing)
                if len(invalid) > 0:
                    return "invalid " + str(invalid)
                if len(missing) == 0 and len(invalid) == 0:
                    print("ALL PARAMS VALID")
                    st.session_state.engine.predict_delay(st.session_state.params.get("start_loc"),
                                                          st.session_state.params.get("end_loc"),
                                                          st.session_state.params.get("actual_departure"),
                                                          st.session_state.params.get("planned_arrival"),
                                                          st.session_state.params.get("initial_delay"))
                    fact = list(st.session_state.engine.facts.values())[-1]
                    print(fact)
                    return f"BOT: Your train is predicted to be delayed by {fact['delay_minutes']} minutes at {fact['current_station']}."


if prompt := st.chat_input("Type your message here"):
    # Display user message in a chat message
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Recognize intent
    response = get_answer_for_simple_intention(prompt);

    if response is None:
        response = get_answer_for_actions(prompt)


    # if intention == "national rail":
    #     waitText = "Searching for your ticket now, please wait..."
    #     with st.chat_message("assistant"):
    #         st.write_stream(response_generator(waitText))
    #     # Add assistant response to chat history
    #     st.session_state.messages.append({"role": "assistant", "content": waitText})
    #
    #     # Mock variables for ticket booking
    #     start_loc = "norwich"
    #     end_loc = "Dundee"
    #     hour = "09"
    #     min = "45"
    #     day = "05"
    #     month = "06"
    #     year = "24"
    #     num_of_adult_passengers = "2"
    #     num_of_child_passengers = "0"
    #     railcard = True
    #
    #     # Return specific params
    #     ticket_preference = UserTicketPreference.CHEAPEST
    #     ticket_type = UserTicketType.RETURN
    #     return_hour = "10"
    #     return_min = "30"
    #     return_day = "10"
    #     return_month = "06"
    #     return_year = "24"
    #
    #     results = scraper.get_scraped_train_details(
    #         user_ticket_preference=ticket_preference,
    #         user_ticket_type=ticket_type,
    #         start_loc=start_loc,
    #         end_loc=end_loc,
    #         month=month,
    #         day=day,
    #         hour=hour,
    #         min=min,
    #         year=year,
    #         return_hour=return_hour,
    #         return_min=return_min,
    #         return_day=return_day,
    #         return_month=return_month,
    #         return_year=return_year,
    #         num_of_adult_passengers=num_of_adult_passengers,
    #         num_of_child_passengers=num_of_child_passengers,
    #         railcard=railcard,
    #     )
    #
    #     response = f"""The cheapest ticket from {results["start_location"]} to {results["end_location"]} is as follows:
    #     {results["ticket_price"]} for {num_of_adult_passengers} adults and {num_of_child_passengers} {"child" if int(num_of_child_passengers) == 1 else "children"},
    #     {"with" if railcard else "without" } a railcard. The train leaves from {results["start_location"]} at {results["journeys_outbound"]["journeys"][0]["start_time"]} and arrives at {results["end_location"]} at {results["journeys_outbound"]["journeys"][-1]["end_time"]}"""

    # Output message handling
    with st.chat_message("assistant"):
        st.write_stream(response_generator(response))
    # Add response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
