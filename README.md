# Restaurant bot

Simple restaurant bot created in Rasa for the university class.

## Features

- Ask for the restaurant open time (i.e. _is the restaurant open on Monday at 11?_)
- Ask for the restaurant menu (i.e. _show me the menu_)
- Place the orders (i.e. _I want to order_)
- Confirm and finish order (i.e. _I want to pay_)
- Configure menu and opening hours by the appropriate **json** files (see `actions/config/restaurant.config` file)

## Integration

The bot is integrated with the Slack service. Change the `slack_token`, `slack_channel` and`slack_signing_secret`
properties in the `credentials.yaml` file for exposing it to the right workspace. Complete instruction could be found
here: https://rasa.com/docs/rasa/connectors/slack

**Author: Przemysław Kocur**