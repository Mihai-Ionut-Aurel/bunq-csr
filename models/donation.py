from bson.objectid import ObjectId


class Donation(object):
    """A class for storing Project related information"""

    def __init__(self, donation_id=None, value=0.0, charity=None):
        if donation_id is None:
            self._id = ObjectId()
        else:
            self._id = donation_id
        self.value = value
        self.charity = charity

    def get_as_json(self):
        """ Method returns the JSON representation of the Donation object, which can be saved to MongoDB """
        return self.__dict__

    @staticmethod
    def build_from_json(json_data):
        """ Method used to build Donation objects from JSON data returned from MongoDB """
        if json_data is not None:
            try:
                return Donation(json_data.get('_id', None),
                                json_data['value'],
                                json_data['charity'])
            except KeyError as e:
                raise Exception("Key not found in json_data: {}".format(e.message))
        else:
            raise Exception("No data to create Project from!")
