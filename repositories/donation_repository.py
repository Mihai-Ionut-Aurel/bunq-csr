from pymongo import MongoClient

from models.donation import Donation


class DonationRepository(object):

    def __init__(self, url, port):
        """
        :type url: str
        :type port: int
        :type user: str
        :type password: str
        """
        self.client = MongoClient(url,
                                  port)

                                  # username=user,
                                  # password=password,
                                  # authMechanism='SCRAM-SHA-256')
        self.database = self.client.bunq_csr
        self.donations_collection = self.database.donations

    def create(self, donation):
        """
        :type donation: Donation
        :rtype: Donation
        """
        if donation is not None:
            self.donations_collection.insert(donation.get_as_json())
        else:
            raise Exception("Nothing to save, because project parameter is None")

    def read(self, donation_id=None):
        """
        :rtype: list[Donation]
        """
        if donation_id is None:
            return self.donations_collection.find({})
        else:
            return self.donations_collection.find({"_id": donation_id})
