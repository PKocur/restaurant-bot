import configparser
import json
from typing import Text, Any, Dict

from rasa_sdk import Action
from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

configuration_file_name = "restaurant.config"
configuration_directory = "config"
configuration_menu_path = "MENU_FILE_PATH"
configuration_opening_hours_path = "OPENING_HOURS_FILE_PATH"


def get_json_file_content(config_property):
    config_parser = configparser.RawConfigParser()
    config_file_path = configuration_directory + "/" + configuration_file_name
    config_parser.read(config_file_path)
    filename = config_parser.get("PATHS", config_property)
    with open(configuration_directory + "/" + filename) as json_file:
        return json.load(json_file)['items']


def get_menu_data():
    return get_json_file_content(configuration_menu_path)


def get_opening_hours_data():
    return get_json_file_content(configuration_opening_hours_path)


class ActionFinishOrder(Action):

    def name(self) -> Text:
        return "action_finish_order"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]):
        meal_list = tracker.get_slot("meal_list")
        menu_data = get_menu_data()
        dispatcher.utter_message("Great, the order would be ready to pick-up in our restaurant in "
                                 + str(self.get_total_time(meal_list, menu_data)) + " minutes.")
        dispatcher.utter_message(
            "Thanks for making this order, it was a pleasure for me. Come back whenever you want and enjoy your meal!")
        return [SlotSet("meal", None), SlotSet("request", None), SlotSet("meal_list", [])]

    def get_total_time(self, meal_list, menu_data):
        total_time = 0
        for meal in meal_list:
            meal_name = meal.split(",")[0].capitalize()
            time = self.get_time_for_meal(meal_name, menu_data)
            total_time += time
        return total_time

    def get_time_for_meal(self, meal, menu_data):
        for menu_entry in menu_data:
            if menu_entry["name"] == meal:
                return menu_entry["preparation_time"]


class ActionConfirmOrder(Action):

    def name(self) -> Text:
        return "action_confirm_order"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]):
        dispatcher.utter_message("Okay, so your order consists...")
        meal_list = tracker.get_slot("meal_list")
        if meal_list is None or not meal_list:
            dispatcher.utter_message("Nothing, feel free to order something!")
            return
        menu_data = get_menu_data()
        response, total_price = self.get_response_with_total_price(meal_list, menu_data)
        dispatcher.utter_message(response)
        dispatcher.utter_message("That sums up to " + str(total_price) + " zł, everything okay?")

    def get_response_with_total_price(self, meal_list, menu_data):
        response = ""
        total_price = 0
        for meal in meal_list:
            meal_name = meal.split(",")[0].capitalize()
            price = self.get_price_of_meal(meal_name, menu_data)
            response += self.get_meal(meal, price)
            response += "\n"
            total_price += price
        return response, total_price

    def get_meal(self, meal, price):
        return meal.capitalize() + " for " + str(price) + " zł"

    def get_price_of_meal(self, meal, menu_data):
        for menu_entry in menu_data:
            if menu_entry["name"] == meal:
                return menu_entry["price"]


class ActionFinishMeal(Action):

    def name(self) -> Text:
        return "action_finish_meal"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]):
        intent = tracker.latest_message['intent'].get('name')
        if intent != "deny":
            dispatcher.utter_message(
                "Thanks, I'm appending your order with the " + tracker.get_slot("meal")
                + " and additional request - " + tracker.get_slot("request") + ".")
        else:
            dispatcher.utter_message("Thanks, I'm appending your order with the " + tracker.get_slot("meal") + ".")


class ActionResetMealSlot(Action):

    def name(self) -> Text:
        return "action_reset_meal_slot"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]):
        return [SlotSet("meal", None), SlotSet("request", None)]


class ValidateOrderForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_order_form"

    def validate_meal(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ):
        if slot_value is None:
            slot_value = ""
        menu_data = get_menu_data()
        if self.meal_exists(slot_value.capitalize(), menu_data):
            return {"meal": slot_value}
        else:
            dispatcher.utter_message("Sorry, we don't have such meal in our menu. Please choose another one.")
            return {"meal": None}

    def meal_exists(self, meal, menu_data):
        for meal_data in menu_data:
            if meal_data['name'] == meal:
                return True
        return False

    def validate_request(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ):
        intent = tracker.latest_message['intent'].get('name')
        meal_list = tracker.get_slot("meal_list")
        if intent != "deny":
            meal_list.append(tracker.get_slot("meal") + ", " + slot_value)
            return {"request": slot_value, "meal_list": meal_list}
        else:
            meal_list.append(tracker.get_slot("meal"))
            return {"request": "", "meal_list": meal_list}


class ActionMenuShow(Action):

    def name(self) -> Text:
        return "action_show_menu"

    def run(self, dispatcher, tracker, domain):
        menu_data = get_menu_data()
        response = self.get_response(menu_data)
        dispatcher.utter_message(response)

    def get_response(self, menu_data):
        response = ""
        for meal_data in menu_data:
            response += self.get_meal(meal_data)
            response += "\n"
        return response

    def get_meal(self, meal_data):
        return meal_data['name'] + " for " + str(meal_data['price']) + " zł "


class ActionOpenTimeResponse(Action):

    def name(self) -> Text:
        return "action_open_time"

    def run(self, dispatcher, tracker, domain):
        day, hour = self.get_day_and_hour(tracker)
        open_time_data = get_opening_hours_data()
        response = self.get_response(day, hour, open_time_data)
        dispatcher.utter_message(response)
        return [SlotSet("day", None), SlotSet("hour", None)]

    def get_day_and_hour(self, tracker):
        day = tracker.get_slot('day')
        hour = tracker.get_slot('hour')
        if day is None:
            day = ""
        else:
            day = day.capitalize()
        if hour is not None:
            try:
                hour = int(hour)
            except ValueError:
                hour = -1
        else:
            hour = -1
        return day, hour

    def get_response(self, day, hour, open_time_data):
        no_information_provided = day not in open_time_data
        if no_information_provided:
            return "Tell me what time do you want to come?"
        else:
            is_hour_provided = 1 <= hour <= 24
            if is_hour_provided:
                is_restaurant_open_at_day = open_time_data[day]['open'] <= hour <= open_time_data[day]['close']
            else:
                is_restaurant_open_at_day = open_time_data[day]['open'] != 0 and open_time_data[day]['close'] != 0
            if is_restaurant_open_at_day:
                return "Yeah, the restaurant is open that time. Feel free to come!"
            else:
                return "Sorry, the restaurant is closed that time."
