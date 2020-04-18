import json

from pynamodb.attributes import Attribute
from pynamodb.constants import NUMBER


class BooleanAsNumberAttribute(Attribute):
    """
    A class for boolean stored ast Number attributes
    """

    attr_type = NUMBER

    def serialize(self, value):
        if value is None:
            return None
        elif value:
            return json.dumps(1)
        else:
            return json.dumps(0)

    def deserialize(self, value):
        return bool(int(value))
