from datetime import datetime
import re
import time
from selenium.webdriver.common.by import By
from selenium.common import NoSuchElementException
from typing import Optional
from scraper.models import UserTicketPreference


# close feedback popup
# popup can occur on multiple pages so call func multiple times to check if popup is obscuring data
def close_feedback_popup(driver):
    try:
        time.sleep(2)
        driver.find_element(
            By.XPATH,
            "//*[@id='fsrFocusFirst']",
        ).click()
        print("info: Feedback popup clicked")
    except Exception as e:
        print("info: Feedback popup NOT found")
        # print(e)



def get_cheapest_ticket_national_rail(driver, return_ticket):
    time.sleep(2)
    # get cheapest ticket price from top of page
    cheapest_ticket_price = driver.find_element(
        By.XPATH,
        "/html/body/div[1]/div[1]/main/div[1]/div[2]/div/div/div[1]/fieldset/div/div[1]/label/span[2]/span[3]",
    )
    cheapest_ticket_price_text = cheapest_ticket_price.text
    print(f"Looking for cheapest journey at {cheapest_ticket_price_text}...")

    # iterate through displayed ticket prices on page to find first journey that matches cheapest ticket price from top of page
    outbound_id = 1
    if return_ticket:
        outbound_id = 2

    for i in range(1, 6):
        ticket_price_text = None
        try:
            ticket_price = driver.find_element(
                By.XPATH,
                f"/html/body/div[1]/div[1]/main/div[1]/div[2]/div/div/div[1]/div/div[{outbound_id}]/div/div/section/ul/li[{i}]/section/div/div/div[1]/button/span[3]",
            )
            ticket_price_text = ticket_price.text
            print(f"Journey: {i}, Price: {ticket_price_text}")
        except:
            print(f"Journey: {i} unavailable")

        if ticket_price_text == cheapest_ticket_price_text:
            print(f"Cheapest journey found at {i} with price {ticket_price_text}")
            journey_item_with_cheapest_price = i
            break

    return journey_item_with_cheapest_price


# get journey info from national rail
def get_route_national_rail_return(
    driver, url: str, user_ticket_preference: UserTicketPreference
):
    driver.get(url)
    time.sleep(2)
    driver.implicitly_wait(2)
    # original_window = driver.current_window_handle

    # close cookie pop up on initial page load
    close_feedback_popup(driver)

    # check if route is available
    try:
        # red error base page
        error_element_no_match_in_popup = driver.find_element(
            By.XPATH,
            "//*[@id='iconlabel-label-general']",
        )
        if (
            error_element_no_match_in_popup.text
            == "No matching journeys found. Please re-plan your journey below."
        ):
            raise BaseException("Journey unavailable")
    except NoSuchElementException:
        pass
    except BaseException as e:
        raise e
        
    try:
        # red error popup
        error_element_no_match = driver.find_element(
            By.XPATH,
            "/html/body/div[1]/div[1]/main/div[1]/div[1]/div/div/div/div[1]/div/p",
        )
        if (
            error_element_no_match.text
            == "No matching journeys found. Please re-plan your journey below."
        ):
            print("Journey unavailable")
            raise BaseException("Journey unavailable")
    except NoSuchElementException:
        pass
    except BaseException as e:
        raise e
        
    try:
        # yellow error base page
        error_element_not_permitted = driver.find_element(
            By.XPATH,
            "/html/body/div[1]/div[1]/main/div[1]/div[1]/div/div/div/div[1]/div/p",
        )
        if (
            error_element_not_permitted.text
            == "This journey is not a permitted route and may require multiple tickets. Please re-plan your journey"
        ):
            print("Journey unavailable")
            raise BaseException("Journey unavailable")
    except NoSuchElementException:
        pass
    except BaseException as e:
        raise e
        
    try:
        #yellow error popup
        error_element_not_permitted_popup = driver.find_element(
            By.XPATH,
            "//*[@id='iconlabel-label-general']",
        )
        if (
            error_element_not_permitted_popup.text
            == "We couldn't find any services for the journey you have requested. Please check your selection criteria."
        ):
            print("Journey unavailable")
            raise BaseException("Journey unavailable")
    except NoSuchElementException:
        pass                      
    except BaseException as e:
        raise e

    if user_ticket_preference is UserTicketPreference.CHEAPEST:
        cheapest_journey_item = get_cheapest_ticket_national_rail(
            driver, return_ticket=False
        )
        journeys_outbound = open_journey_details_extract_data_and_nav_back(
            driver, cheapest_journey_item, return_ticket=False
        )
    elif user_ticket_preference is UserTicketPreference.EARLIEST:
        journeys_outbound = open_journey_details_extract_data_and_nav_back(
            driver, cheapest_journey_item=None, return_ticket=False
        )

    time.sleep(1)

    # to pick the top card in case of EARLIEST preference, pass 1 since 1-1 = 0 which represents the top card in lines below
    if user_ticket_preference is UserTicketPreference.EARLIEST:
        cheapest_journey_item = 1

    # click correct journey card
    for attempt in range(0,5):
        try:
            driver.find_element(
                By.XPATH,
                # these iterate from 0, so subtract 1
                f"//*[@id='outward-{cheapest_journey_item-1}']",
            ).click()
            print("info: Journey selected")
            time.sleep(.5)
            break
        except:
            print(f"info: Journey card click #{attempt} failed")
            time.sleep(2)
    

    # click continue button to view return tickets
    driver.find_element(
        By.XPATH,
        "//*[@id='jp-summary-buy-link']",
    ).click()
    print("info: Continue button pressed")
    time.sleep(.5)

    close_feedback_popup(driver)

    if user_ticket_preference == UserTicketPreference.CHEAPEST:
        cheapest_journey_item_return = get_cheapest_ticket_national_rail(
            driver, return_ticket=True
        )
        journeys_return = open_journey_details_extract_data_and_nav_back(
            driver, cheapest_journey_item_return, return_ticket=True
        )
    elif user_ticket_preference == UserTicketPreference.EARLIEST:
        journeys_return = open_journey_details_extract_data_and_nav_back(
            driver, cheapest_journey_item=None, return_ticket=True
        )
    print(journeys_return)

    price = driver.find_element(
        By.XPATH,
        "/html/body/div[1]/div[1]/main/div[1]/div[2]/div/div/div[2]/div/div/div[2]/section/h2/span[2]",
    ).text
    print(price)

    return (journeys_outbound, journeys_return, price)


def open_journey_details_extract_data_and_nav_back(
    driver, cheapest_journey_item: Optional[int], return_ticket: bool
):
    journeys: list[dict[str, str]] = []

    outbound_id = 1
    if return_ticket:
        outbound_id = 2

    if cheapest_journey_item:
        journey_details_button = driver.find_element(
            By.XPATH,
            f"/html/body/div[1]/div[1]/main/div[1]/div[2]/div/div/div[1]/div/div[{outbound_id}]/div/div/section/ul/li[{cheapest_journey_item}]/section/div/div/div[4]/div/a",
        )
        
        # hack to scroll down to button, wait for scrolling to be performed, and then click again:
        for attempt in range(0,5):
            try:
                journey_details_button.click()
                break
            except:
                print(f"info: Journey details button #{attempt} failed")
                time.sleep(2)
    else:
        print("Selecting earliest journey...")
        driver.find_element(
            By.XPATH,
            f"/html/body/div[1]/div[1]/main/div[1]/div[2]/div/div/div[1]/div/div[{outbound_id}]/div/div/section/ul/li[1]/section/div/div/div[4]/div/a",
        ).click()

    close_feedback_popup(driver)

    # if journey is direct the journey details page looks different, so check the num of stops and find correct elements
    driver.implicitly_wait(2)
    num_of_changeovers_element = driver.execute_script(
        "return document.querySelector('.styled__StyledFooterContentLeft-sc-pt4cf1-5').textContent.trim();"
    )
    num_of_changeovers: int = re.search(r"(?<=m)\d+", num_of_changeovers_element).group(
        0
    )
    num_of_changeovers = int(num_of_changeovers)

    if num_of_changeovers == 0:
        extract_journey_details_from_page_no_changeovers(driver, journeys)
    if num_of_changeovers > 0:
        extract_journey_details_from_page_with_changeovers(
            driver, journeys, num_of_changeovers, return_ticket
        )

    driver.back()
    return journeys


def extract_journey_details_from_page_no_changeovers(driver, journeys):

    start_loc: str = driver.find_element(
        By.XPATH,
        "/html/body/div[1]/div[1]/main/div[2]/div/div/div/div/div/div[2]/div/section[1]/div[2]/div/div[3]/div[1]/span[2]/span",
    ).text
    start_time: str = driver.find_element(
        By.XPATH,
        "/html/body/div[1]/div[1]/main/div[2]/div/div/div/div/div/div[2]/div/section[1]/div[2]/div/div[3]/div[1]/span[1]/time",
    ).text
    try:
        start_platform: str = driver.find_element(
            By.XPATH,
            "/html/body/div[1]/div[1]/main/div[2]/div/div/div/div/div/div[2]/div/section[1]/div[2]/div/div[3]/div[1]/p[2]",
        ).text
    except:
        start_platform = None
    end_loc: str = driver.find_element(
        By.XPATH,
        f"/html/body/div[1]/div[1]/main/div[2]/div/div/div/div/div/div[2]/div/section[1]/div[2]/div/div[3]/div[2]/span[2]",
    ).text
    end_time: str = driver.find_element(
        By.XPATH,
        f"/html/body/div[1]/div[1]/main/div[2]/div/div/div/div/div/div[2]/div/section[1]/div[2]/div/div[3]/div[2]/span[1]",
    ).text
    try:
        end_platform: str = driver.find_element(
            By.XPATH,
            f"/html/body/div[1]/div[1]/main/div[2]/div/div/div/div/div/div[2]/div/section[1]/div[2]/div/div[3]/div[2]/p[2]",
        ).text
    except:
        end_platform = None

    journey_step: dict[str, str] = {
        "start_loc": start_loc,
        "start_time": start_time,
        "start_platform": start_platform,
        "end_loc": end_loc,
        "end_time": end_time,
        "end_platform": end_platform,
    }
    journeys.append(journey_step)


def extract_journey_details_from_page_with_changeovers(
    driver, journeys, num_of_changeovers, return_ticket: bool
):

    for i in range(1, num_of_changeovers + 2):

        quirkyReturnString = ""
        if return_ticket:
            quirkyReturnString = "[2]"

        start_loc: str = driver.find_element(
            By.XPATH,
            f"/html/body/div[1]/div[1]/main/div[2]/div/div/div/div/div/div[2]/div/ul/li[{i}]/section/div{quirkyReturnString}/div/div[2]/div[1]/span[2]",
        ).text
        start_time: str = driver.find_element(
            By.XPATH,
            f"/html/body/div[1]/div[1]/main/div[2]/div/div/div/div/div/div[2]/div/ul/li[{i}]/section/div{quirkyReturnString}/div/div[2]/div[1]/span[1]",
        ).text
        try:
            start_platform: str = driver.find_element(
                By.XPATH,
                f"/html/body/div[1]/div[1]/main/div[2]/div/div/div/div/div/div[2]/div/ul/li[{i}]/section/div{quirkyReturnString}/div/div[2]/div[1]/p[2]",
            ).text
        except:
            start_platform = None
        end_loc: str = driver.find_element(
            By.XPATH,
            f"/html/body/div[1]/div[1]/main/div[2]/div/div/div/div/div/div[2]/div/ul/li[{i}]/section/div{quirkyReturnString}/div/div[2]/div[2]/span[2]",
        ).text
        end_time: str = driver.find_element(
            By.XPATH,
            f"/html/body/div[1]/div[1]/main/div[2]/div/div/div/div/div/div[2]/div/ul/li[{i}]/section/div{quirkyReturnString}/div/div[2]/div[2]/span[1]",
        ).text
        try:
            end_platform: str = driver.find_element(
                By.XPATH,
                f"/html/body/div[1]/div[1]/main/div[2]/div/div/div/div/div/div[2]/div/ul/li[{i}]/section/div{quirkyReturnString}/div/div[2]/div[2]/p[2]",
            ).text
        except:
            start_platform = None

        journey_step: dict[str, str] = {
            "start_loc": start_loc,
            "start_time": start_time,
            "start_platform": start_platform,
            "end_loc": end_loc,
            "end_time": end_time,
            "end_platform": end_platform,
        }
        journeys.append(journey_step)


# get journey info from national rail
def get_route_national_rail_single(
    driver, url: str, user_ticket_preference: UserTicketPreference
):
    driver.get(url)
    time.sleep(2)
    driver.implicitly_wait(2)
    
    # close cookie pop up on initial page load
    try:
        driver.find_element(
            By.XPATH,
            "//*[@id='onetrust-reject-all-handler']",
        ).click()
        print("info: Cookie popup clicked")
        time.sleep(.5)
    except:
        print("info: Cookie popup NOT detected")
        
    close_feedback_popup(driver)

    if user_ticket_preference is UserTicketPreference.CHEAPEST:
        cheapest_journey_item = get_cheapest_ticket_national_rail(
            driver, return_ticket=False
        )
        journeys_outbound = open_journey_details_extract_data_and_nav_back(
            driver, cheapest_journey_item, return_ticket=False
        )
    elif user_ticket_preference is UserTicketPreference.EARLIEST:
        journeys_outbound = open_journey_details_extract_data_and_nav_back(
            driver, cheapest_journey_item=None, return_ticket=False
        )

    time.sleep(.5)
    
    close_feedback_popup(driver)
    # to pick the top card in case of EARLIEST preference, pass 1 since 1-1 = 0 which represents the top card in lines below
    if user_ticket_preference is UserTicketPreference.EARLIEST:
        cheapest_journey_item = 1
        for attempt in range(0,5):
            try:
                # click correct journey card
                driver.find_element(
                    By.XPATH,
                    # these iterate from 0, so subtract 1
                    f"//*[@id='outward-{cheapest_journey_item+attempt-1}']",
                ).click()
                print("info: Journey selected")
                time.sleep(.5)
                break
            except:
                print(f"info: Journey card click #{attempt} failed")
                time.sleep(2)
    # CHEAPEST CASE
    else:
        # click correct journey card
        for attempt in range(0,5):
            try:
                driver.find_element(
                    By.XPATH,
                    # these iterate from 0, so subtract 1
                    f"//*[@id='outward-{cheapest_journey_item-1}']",
                ).click()
                print("info: Journey selected")
                time.sleep(.5)
                break
            except:
                print(f"info: Journey card click #{attempt} failed")
                time.sleep(2)

    price = driver.find_element(
        By.XPATH,
        "/html/body/div[1]/div[1]/main/div[1]/div[2]/div/div/div[2]/div/div/div[2]/section/h2/span[2]",
    ).text
    return (journeys_outbound, price)


def calculate_total_journey_time(journeys: list):
    time_format = "%H:%M"
    start_time = datetime.strptime(journeys[0]["start_time"], time_format)
    finish_time = datetime.strptime(journeys[-1]["end_time"], time_format)

    midnight = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    # calculate the time difference
    time_difference = finish_time - start_time

    # calculate total journey time
    total_journey_time = datetime.strftime(midnight + time_difference, "%H:%M")
    return total_journey_time
