from pynamodb.constants import NUMBER

from models.custom_attributes import BooleanAsNumberAttribute


class TestBooleanAsNumberAttribute:
    """
    Tests boolean attributes
    """

    def test_boolean_as_number_attribute(self):
        """
        BooleanAsNumberAttribute.default
        """
        attr = BooleanAsNumberAttribute()
        assert attr is not None

        assert attr.attr_type == NUMBER
        attr = BooleanAsNumberAttribute(default=True)
        assert attr.default is True

    def test_boolean_as_number_serialize(self):
        """
        BooleanAsNumberAttribute.serialize
        """
        attr = BooleanAsNumberAttribute()
        assert attr.serialize(True) == "1"
        assert attr.serialize(False) == "0"
        assert attr.serialize(None) is None

    def test_boolean_as_number_deserialize(self):
        """
        BooleanAsNumberAttribute.deserialize
        """
        attr = BooleanAsNumberAttribute()
        assert attr.deserialize(True) is True
        assert attr.deserialize(False) is False
