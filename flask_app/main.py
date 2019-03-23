import json
import logging
import os
import random
from bunq.sdk.context import ApiEnvironmentType
from bunq.sdk.model.core import BunqModel
from bunq.sdk.model.generated.object_ import NotificationUrl
from flask import Flask, request
import decimal
from bunq_util.bunq_lib import BunqLib
from models.donation import Donation
from models.configuration import Configuration
from models.phrase import Phrase
from repositories.donation_repository import DonationRepository
from repositories.phrase_repository import PhraseRepository
from repositories.configuration_repository import ConfigurationRepository
from bson.json_util import dumps

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
# p
# pydevd.settrace('localhost', port=12345, stdoutToServer=True, stderrToServer=True)

bunqLib = BunqLib(ApiEnvironmentType.SANDBOX)
donationsRepository = DonationRepository('127.0.0.1', 27017)
phraseRepository = PhraseRepository('127.0.0.1', 27017)
configurationRepository = ConfigurationRepository('127.0.0.1', 27017)

charities = ['NL26BUNQ9900198964', 'NL03BUNQ9900196759', 'NL23BUNQ9900198727', 'NL07BUNQ9900198336',
             'NL73BUNQ9900198700']
charities_name = {'NL26BUNQ9900198964': "tom.bowie@bunq.org",
                  'NL03BUNQ9900196759': "veronika.hamilton@bunq.org",
                  'NL23BUNQ9900198727': "cristin.pool@bunq.nl",
                  'NL07BUNQ9900198336': "edoardo.pool@bunq.bar",
                  'NL73BUNQ9900198700': "doloris.pierce@bunq.bar"}


def calculate_donations_total(donations):
    donation_total = decimal.Decimal(0.0)
    for donation_json in donations:
        donation = Donation.build_from_json(donation_json)
        donation_total += decimal.Decimal(donation.value)
    return float(donation_total)


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
    reponse = bunqLib.add_callback_url('https://d20977b4.ngrok.io/user/balance/modified')
    print(json.dumps(reponse, default=serialize))
    notifications_filters = bunqLib.get_callback_urls

    return json.dumps(reponse, default=serialize)


@application.route('/user/balance/modified', methods=['POST'])
def user_ballance_changes():
    # TODO check if an ammount can be substracted
    """
   :type notification_data: NotificationUrl
   :rtype: str
    """
    print("received notification2")
    print(request.data[19:-1])
    data = json.loads(request.data[19:-1])
    # print(d)
    # transaction = json.loads(request.data[19:-1])
    # print(transaction.object_.Payment.amount.value)

    amount = decimal.Decimal(data['object']['Payment']['amount']['value'])
    print(amount)
    receiver = data['object']['Payment']['counterparty_alias']['iban']
    print(receiver)
    if amount < 0 and receiver \
            not in charities:
        donation = (5 + ((amount * 100) % 5)) / 100
        print(donation)
        if donation > 0 and donation < 0.05:
            configuration_json = configurationRepository.read()
            configuration = Configuration.build_from_json(configuration_json)
            payment = bunqLib.make_payment(str(donation), 'Donation', charities_name[configuration.active_charity])
            print(json.dumps(dict(payment.headers)))
            donationsRepository.create(Donation(value=float(donation), charity=receiver))
    return ""


@application.route('/user/donations/total')
def get_user_donations_total():
    donations = donationsRepository.read()
    donations_total = calculate_donations_total(donations)
    return str(donations_total)


@application.route('/user/refresh')
def user_refresh():
    # TODO check if an ammount can be substracted
    bunqLib.update_context()

    return ""


@application.route('/configuration/update', methods=['POST'])
def update_configuration():
    if request.is_json:
        try:
            json_data = request.get_data()
            active_charity = json_data['active_charity']
            configuration_json = configurationRepository.read()
            configuration = Configuration.build_from_json(configuration_json)
            if configuration is None:
                configuration = Configuration(
                    last_donation_value=0.0,
                    active_charity=active_charity)
                configurationRepository.create(configuration)
            else:
                configuration.active_charity = active_charity
                configurationRepository.update(configuration)
        except KeyError as e:
            raise Exception("Key not found in json_data: {}".format(e.message))

    configuration = Configuration.build_from_json(configurationRepository.read())
    return dumps(configuration.get_as_json())


@application.route('/phrase/check')
def check_phrase_donation():
    donations = donationsRepository.read()
    donations_total = calculate_donations_total(donations)
    print(donations_total)
    configuration_json = configurationRepository.read()
    configuration = Configuration.build_from_json(configuration_json)

    if (((decimal.Decimal(donations_total) - decimal.Decimal(configuration.last_donation_value)) * 100) % 2) > 0:
        phrases = phraseRepository.read()
        charity_phrases = [phrase for phrase in phrases \
                           if Phrase.build_from_json(phrase).charity == configuration.active_charity]
        print(dumps(charity_phrases))
        configuration.last_donation_value = donations_total
        print(configuration.last_donation_value)
        configurationRepository.update(configuration)
        return dumps(random.choice(charity_phrases))
    else:
        return '0'


@application.route('/phrases/add', methods=['POST'])
def add_phrase():
    if request.is_json:
        try:
            json_data = request.get_json()
            text = json_data['text']
            charity = json_data['charity']
            phrase = Phrase(text=text,
                            charity=charity)
            result = phraseRepository.create(phrase)

            return dumps(result)
        except KeyError as e:
            raise Exception("Key not found in json_data: {}".format(e.message))

    return ''


print("Before main {0}".format(__name__))

if __name__ == "__main__":
    # Only for debugging while developing
    logging.info("Listening to {0}:{1}".format(application.config['SERVER_HOST'], application.config['SERVER_PORT']))
    print("Listening to {0}:{1}".format(application.config['SERVER_HOST'], application.config['SERVER_PORT']))
    bunqLib.add_callback_url("https://469d72cd.ngrok.io/user/balance/modified")
    application.run(host=application.config['SERVER_HOST'], debug=application.config['DEBUG'],
                    port=application.config['SERVER_PORT'])
