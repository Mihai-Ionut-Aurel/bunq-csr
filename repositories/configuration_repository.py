from pymongo import MongoClient

from models.configuration import Configuration


class ConfigurationRepository(object):

    def __init__(self, url, port):
        """
        :type url: str
        :type port: int
        """
        self.client = MongoClient(url,
                                  port)

                                  # username=user,
                                  # password=password,
                                  # authMechanism='SCRAM-SHA-256')
        self.database = self.client.bunq_csr
        self.configuration_collection = self.database.configurations

    def create(self, configuration):
        """
        :type configuration: Configuration
        :rtype: list[Configuration]
        """
        if configuration is not None:
            self.configuration_collection.insert(configuration.get_as_json())
        else:
            raise Exception("Nothing to save, because project parameter is None")

    def read(self, configuration_id=None):
        """
        :rtype: Configuration
        """
        if configuration_id is None:
            return self.configuration_collection.find_one({})
        else:
            return self.configuration_collection.find({"_id": configuration_id})

    def update(self, configuration):
        """
        :rtype: Configuration
        """
        if configuration is not None:
            self.configuration_collection.save(configuration.get_as_json())
        else:
            raise Exception("Nothing to update, because project parameter is None")
