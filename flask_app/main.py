import os

from flask import Flask, request, jsonify
import requests

import socket
import json
from os.path import isfile
import socket

import requests
from bunq.sdk.client import Pagination
from bunq.sdk.context import ApiContext
from bunq.sdk.context import ApiEnvironmentType
from bunq.sdk.context import BunqContext
from bunq.sdk.exception import BunqException
from bunq.sdk.model.generated import endpoint
from bunq.sdk.model.generated.object_ import Pointer, Amount, NotificationFilter, NotificationUrl
from bunq.sdk.context import ApiEnvironmentType
from bunq_util.bunq_lib import BunqLib
import logging
import bunq.sdk.json.adapters
import bunq.sdk.json.converter
from bunq.sdk.model.core import BunqModel

application = Flask(__name__)

# app.wsgi_app = ProxyFix(app.wsgi_app)

# set config
app_settings = os.getenv('APP_SETTINGS')
application.config.from_object(app_settings)

# import sys
#
# sys.path.append("pycharm-debug-py3k.egg")
# sys.path.append("C:\\Users\\Freakyjo\\.IntelliJIdea2017.2\\config\\plugins\\python\\helpers\\pydev\\pydevd.py")
# import pydevd
#
# pydevd.settrace('localhost', port=12345, stdoutToServer=True, stderrToServer=True)

bunqLib = BunqLib(ApiEnvironmentType.SANDBOX)


def serialize(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, BunqModel):
        serial = obj.to_json()
        return serial

    return obj.__dict__


@application.route('/')
def index():
    return 'Index Page'


@application.route('/hello')
def hello():
    return 'Hello, World'


@application.route('/user/information')
def get_user():
    """
    :vartype user: UserCompany|UserPerson
    """
    user = bunqLib.get_current_user()

    return user.to_json()


@application.route('/user/accounts')
def get_user_accounts():
    """
    :vartype accounts: list[endpoint.MonetaryAccountBank]
    """
    accounts = bunqLib.get_all_monetary_account_active()

    return json.dumps(accounts, default=serialize)


@application.route('/user/transactions')
def get_user_transactions():
    """
    :vartype transactions: list[Payment]
    """
    transactions = bunqLib.get_all_payment()

    return json.dumps(transactions, default=serialize)


@application.route('/user/payment')
def user_payment():
    """
    :vartype response: list[Payment]
    """
    response = bunqLib.make_payment('0.89', 'Test Payment', 'veronika.lancaster@bunq.nl')

    return json.dumps(response, default=serialize)


@application.route('/user/top-up')
def user_top_up():
    """
    :vartype response: list[Payment]
    """
    response = bunqLib.make_payment('0.89', 'Test Payment', 'veronika.lancaster@bunq.nl')

    return json.dumps(response, default=serialize)


@application.route('/user/notification-filters')
def get_user_notification_filters():
    """
    :vartype notifications_filters: list[NotificationFilter]
    """
    # reponse = bunqLib.add_callback_url('https://469d72cd.ngrok.io/user/balance/modified')
    # print(json.dumps(reponse, default=serialize))
    notifications_filters = bunqLib.get_callback_urls

    return json.dumps(notifications_filters, default=serialize)


@application.route('/user/balance/modified', methods=['POST'])
def user_ballance_changes(notification_data):
    # TODO check if an ammount can be substracted
    """
   :type notification_data: NotificationUrl
   :rtype: str
    """

    print("received notification2")

    return ""


@application.route('/user/refresh')
def user_refresh():
    # TODO check if an ammount can be substracted
    bunqLib.update_context()

    return ""


print("Before main {0}".format(__name__))

if __name__ == "__main__":
    # Only for debugging while developing
    logging.info("Listening to {0}:{1}".format(application.config['SERVER_HOST'], application.config['SERVER_PORT']))
    print("Listening to {0}:{1}".format(application.config['SERVER_HOST'], application.config['SERVER_PORT']))
    bunqLib.add_callback_url("https://469d72cd.ngrok.io/user/balance/modified")
    application.run(host=application.config['SERVER_HOST'], debug=application.config['DEBUG'],
                    port=application.config['SERVER_PORT'])
