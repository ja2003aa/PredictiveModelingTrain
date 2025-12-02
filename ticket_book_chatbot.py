import time
import spacy
from spacy.matcher import Matcher
import streamlit as st
import predefined_chat_messages
from scraper import scraper
from scraper.models import UserTicketPreference, UserTicketType, UserTimePreferenceType

nlp = spacy.load('en_core_web_lg')
matcher = Matcher(nlp.vocab)

def response_generator(response):
    for word in response.split():
        yield word + " "
        time.sleep(0.09)

#set page title
st.title("TicketHelper: Book a train ticket and check delays")

# initialize chat history and output initial greeting
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": predefined_chat_messages.INITIAL_GREETING})

# display chat messages from history on app rerun (because the script reruns after every input from the user)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# handling user input
if prompt := st.chat_input("Type your message here"):
    # display user message in a chat message 
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # PROCESS MESSAGE
    # MAKE SURE TO DEFINE YOUR RESPONSE INTO `response`

    # split input
    if prompt.startswith("NR"):        
        # sample input
        # NR,cheapest,return,norwich,liverpool street london,13,30,20,07,24,arrive by,14,30,25,07,24,depart at,2,2,railcard
        parts = prompt.split(",")
        print(parts)
        
        # initial response
        waitText = f"Searching for your ticket from {parts[3].capitalize()} to {parts[4].capitalize()} now, please wait..."
        with st.chat_message("assistant"):
            st.write_stream(response_generator(waitText))
        # add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": waitText})
        
        parts = prompt.split(",")
        
        if parts[1] == "cheapest":
            ticket_preference = UserTicketPreference.CHEAPEST
        else:
            ticket_preference = UserTicketPreference.EARLIEST
            
        if parts[2] == "single":
            ticket_type = UserTicketType.SINGLE
        else:
            ticket_type = UserTicketType.RETURN
            
        hour=parts[5]
        min=parts[6]
        day=parts[7]
        month=parts[8]
        year=parts[9]
        
        if parts[10] == "arrive by":
            leaving_type=UserTimePreferenceType.ARRIVING
        elif parts[10] == "depart at":
            leaving_type=UserTimePreferenceType.DEPARTING 
            
        return_hour = parts[11]
        return_min = parts[12]
        return_day = parts[13]
        return_month = parts[14]
        return_year = parts[15]
        
        if parts[16] == "arrive by":
            return_type=UserTimePreferenceType.ARRIVING
        elif parts[16] == "depart at":
            return_type=UserTimePreferenceType.DEPARTING 
            
        num_of_adult_passengers = parts[17]
        num_of_child_passengers = parts[18]
        
        if parts[19] == "railcard":
            railcard = True
        else:
            railcard = False
        print(leaving_type, return_type)
        results = scraper.get_scraped_train_details(
            user_ticket_preference=ticket_preference,
            user_ticket_type=ticket_type,
            start_loc=parts[3],
            end_loc=parts[4],
            hour=hour,
            min=min,
            day=day,
            month=month,
            year=year,
            leaving_type=leaving_type,
            return_hour=return_hour,
            return_min=return_min,
            return_day=return_day,
            return_month=return_month,
            return_year=return_year,
            return_type=return_type,
            num_of_adult_passengers=num_of_adult_passengers,
            num_of_child_passengers=num_of_child_passengers,
            railcard=railcard,
        )
        
        # # error handling
        # if results.get(["status"])
        
        print(results)
        # put extracted data into variables defined above
        if ticket_type == UserTicketType.SINGLE:
            response = f"""
            The {"cheapest" if ticket_preference == UserTicketPreference.CHEAPEST else "earliest"} ticket 
            from {results["start_location"]} 
            to {results["end_location"]} is as follows:
            {results["ticket_price"]} for {num_of_adult_passengers} adults 
            and {num_of_child_passengers} {"child" if int(num_of_child_passengers) == 1 else "children"},
            {"with" if railcard else "without" } a railcard. 
            
            The outbound train leaves 
            from {results["start_location"]} 
            at {results["journeys_outbound"]["journeys"][0]["start_time"]} 
            on {day}/{month}/{year}.
            and arrives 
            at {results["end_location"]} 
            at {results["journeys_outbound"]["journeys"][-1]["end_time"]} 
            on {day}/{month}/{year}.
            The outbound journey time is: {results["journeys_outbound"]["time"]}.
            You will be stopping at 
            {",".join([journey["end_loc"] for journey in results["journeys_outbound"]["journeys"]])}.
            
            You can book your journey here:
            {results["ticket_purchase_link"]}
            """
            
            
        elif ticket_type == UserTicketType.RETURN:
            response = [f"""
            The 
            {"cheapest" if ticket_preference == UserTicketPreference.CHEAPEST else "earliest"} ticket
            from {results["start_location"]} 
            to {results["end_location"]} is 
            {results["ticket_price"]} for 
            {num_of_adult_passengers} adults 
            and {num_of_child_passengers} {"child" if int(num_of_child_passengers) == 1 else "children"},
            {"with" if railcard else "without" } a railcard.
            """,
            f"""
            The outbound train leaves 
            from {results["start_location"]} 
            at {results["journeys_outbound"]["journeys"][0]["start_time"]} 
            on {day}/{month}/{year}
            and arrives 
            at {results["end_location"]} 
            at {results["journeys_outbound"]["journeys"][-1]["end_time"]} 
            on {day}/{month}/{year}.
            The outbound journey time is: {results["journeys_outbound"]["time"]}.
            
            
            The return train leaves 
            from {results["end_location"]} 
            at {results["journeys_return"]["journeys"][0]["start_time"]} 
            on {return_day}/{return_month}/{return_year} 
            and arrives 
            at {results["start_location"]} 
            at {results["journeys_return"]["journeys"][-1]["end_time"]}
            on {return_day}/{return_month}/{return_year}.
            The return journey time is: {results["journeys_return"]["time"]}. You will be stopping at 
            {",".join([journey["end_loc"] for journey in results["journeys_return"]["journeys"]])}.
            """,
            f"""
            You can book your journey here:
            {results["ticket_purchase_link"]}
            """]
        # response = results
        
    elif "book" or "buy" in prompt:
        response = predefined_chat_messages.BOOKING_INFO
        
    else:
        response = "Sorry, I could not detect all required information. Please provide the following missing information: "

    if type(response) is list:
        for response_part in response:
            # OUTPUT MESSAGE HANDLING
            # display output in chat message container
            with st.chat_message("assistant"):
                st.write_stream(response_generator(response_part))
            # add response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response_part})
    else:
        # OUTPUT MESSAGE HANDLING
        # display output in chat message container
        with st.chat_message("assistant"):
            st.write_stream(response_generator(response))
        # add response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
    
