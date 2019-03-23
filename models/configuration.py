from bson.objectid import ObjectId


class Configuration(object):
    """A class for storing Project related information"""

    def __init__(self, configuration_id=None, last_donation_value=0.0, active_charity=None):
        if configuration_id is None:
            self._id = ObjectId()
        else:
            self._id = configuration_id
        self.last_donation_value = last_donation_value
        self.active_charity = active_charity

    def get_as_json(self):
        """ Method returns the JSON representation of the Donation object, which can be saved to MongoDB """
        return self.__dict__

    @staticmethod
    def build_from_json(json_data):
        """ Method used to build Donation objects from JSON data returned from MongoDB """
        if json_data is not None:
            try:
                return Configuration(json_data.get('_id', None),
                                     json_data['last_donation_value'],
                                     json_data['active_charity'])
            except KeyError as e:
                raise Exception("Key not found in json_data: {}".format(e.message))
        else:
            raise Exception("No data to create Project from!")
