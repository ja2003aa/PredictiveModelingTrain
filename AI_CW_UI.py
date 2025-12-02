import streamlit as st
import json

def generate_url_national_rail_single(
    start_loc_crs,
    end_loc_crs,
    month,
    day,
    hour,
    min,
    year,
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

    if num_of_adult_passengers_int > 0 and num_of_child_passengers_int < 1:
        if railcard == True:
            national_rail_url = f"https://www.nationalrail.co.uk/journey-planner/?type={ticket_type}&origin={start_loc_crs}&destination={end_loc_crs}&leavingType=departing&leavingDate={day}{month}{year}&leavingHour={hour}&leavingMin={min}&adults={num_of_adult_passengers}&railcards=YNG|1"
        else:
            national_rail_url = f"https://www.nationalrail.co.uk/journey-planner/?type={ticket_type}&origin={start_loc_crs}&destination={end_loc_crs}&leavingType=departing&leavingDate={day}{month}{year}&leavingHour={hour}&leavingMin={min}&adults={num_of_adult_passengers}"
    elif num_of_child_passengers_int > 0:
        national_rail_url = f"https://www.nationalrail.co.uk/journey-planner/?type={ticket_type}&origin={start_loc_crs}&destination={end_loc_crs}&leavingType=departing&leavingDate={day}{month}{year}&leavingHour={hour}&leavingMin={min}&adults={num_of_adult_passengers}&children={num_of_child_passengers}"
    return national_rail_url

st.title("TicketHelper")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        

response = "How can I help you today"
with st.chat_message("assistant",avatar = "🚂"):
    st.markdown(response)

prompt = st.chat_input()

if prompt == "Hi":
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = "I am on holiday and cannot help at the moment. Come back later"
    with st.chat_message("assistant",avatar = "🚂"):
        st.markdown(response)

    
    st.session_state.messages.append({"role": "assistant", "content": response,"avatar" : "🚂"})
    prompt = ""
    #"['NRW','CDF','06','05','09','45','24','2','2','True']"
elif prompt and prompt.startswith("["):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    args = list(eval(prompt))
    with st.chat_message("assistant",avatar = "🚂"):
        st.markdown(generate_url_national_rail_single(args[0],args[1],int(args[2]),int(args[3]),int(args[4]),int(args[5]),int(args[6]),int(args[7]),int(args[8]),bool(args[9])))
    #st.session_state.messages.append({"role": "assistant", "content": response,"avatar" : "🚂"})

    """
    response = "Please send the info"
    with st.chat_message("assistant",avatar = "🚂"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response,"avatar" : "🚂"})
    prompt = ""
    #['NRW','CDF','06','05','09','45','24','2','2','True']
    if prompt := st.chat_input(key = "2"):
        args = json.loads(prompt)
        with st.chat_message("assistant",avatar = "🚂"):
            st.markdown(generate_url_national_rail_single(args[0],args[1],args[2],args[3],args[4],args[5],args[6],args[7],args[8]))
        st.session_state.messages.append({"role": "assistant", "content": response,"avatar" : "🚂"})
    
"""


        
    
    

        
    


