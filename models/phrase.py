from bson.objectid import ObjectId


class Phrase(object):
    """A class for storing Project related information"""

    def __init__(self, phrase_id=None, text='', charity=None):
        if phrase_id is None:
            self._id = ObjectId()
        else:
            self._id = phrase_id
        self.text = text
        self.charity = charity

    def get_as_json(self):
        """ Method returns the JSON representation of the Donation object, which can be saved to MongoDB """
        return self.__dict__

    @staticmethod
    def build_from_json(json_data):
        """ Method used to build Donation objects from JSON data returned from MongoDB """
        if json_data is not None:
            try:
                return Phrase(json_data.get('_id', None),
                              json_data['text'],
                              json_data['charity'])
            except KeyError as e:
                raise Exception("Key not found in json_data: {}".format(e.message))
        else:
            raise Exception("No data to create Project from!")
