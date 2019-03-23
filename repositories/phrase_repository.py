from pymongo import MongoClient

from models.phrase import Phrase


class PhraseRepository(object):

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
        self.phrase_collection = self.database.phrases

    def create(self, phrase):
        """
        :type phrase: Phrase
        :rtype: Phrase
        """
        if phrase is not None:
            self.phrase_collection.insert(phrase.get_as_json())
        else:
            raise Exception("Nothing to save, because project parameter is None")

    def read(self, phrase_id=None):
        """
        :rtype: list[Phrase]
        """
        if phrase_id is None:
            return self.phrase_collection.find({})
        else:
            return self.phrase_collection.find({"_id": phrase_id})
