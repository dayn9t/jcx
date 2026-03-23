"""Tests for FrozenModel, EnumItem, and PydanticEnum."""

from enum import Enum

import pytest
from pydantic import ValidationError

from jcx.m.enum import EnumItem, FrozenModel, PydanticEnum


class TestFrozenModel:
    """Tests for FrozenModel immutability."""

    def test_frozen_model_is_immutable(self) -> None:
        """FrozenModel instance should raise error on attribute assignment."""

        class TestModel(FrozenModel):
            value: int

        model = TestModel(value=1)

        with pytest.raises(ValidationError):
            model.value = 2  # type: ignore[misc]


class TestEnumItem:
    """Tests for EnumItem fields and behavior."""

    def test_enum_item_has_required_fields(self) -> None:
        """EnumItem should have value, name, description fields."""
        item = EnumItem(value=1, name="test", description="Test item")

        assert item.value == 1
        assert item.name == "test"
        assert item.description == "Test item"

    def test_enum_item_description_default_empty(self) -> None:
        """EnumItem description should default to empty string."""
        item = EnumItem(value=1, name="test")

        assert item.description == ""

    def test_enum_item_rejects_extra_fields(self) -> None:
        """EnumItem should reject extra fields with validation error."""
        with pytest.raises(ValidationError):
            EnumItem(value=1, name="test", extra_field="not_allowed")  # type: ignore[call-arg]


class ColorEnum(PydanticEnum):
    """Test enum using EnumItem values."""

    RED = EnumItem(value=1, name="red", description="Red color")
    GREEN = EnumItem(value=2, name="green", description="Green color")
    BLUE = EnumItem(value=3, name="blue", description="Blue color")


class TestPydanticEnum:
    """Tests for PydanticEnum properties and iteration."""

    def test_value_int_returns_correct_value(self) -> None:
        """PydanticEnum.value_int should return the integer value."""
        assert ColorEnum.RED.value_int == 1
        assert ColorEnum.GREEN.value_int == 2
        assert ColorEnum.BLUE.value_int == 3

    def test_name_str_returns_correct_name(self) -> None:
        """PydanticEnum.name_str should return the string name."""
        assert ColorEnum.RED.name_str == "red"
        assert ColorEnum.GREEN.name_str == "green"
        assert ColorEnum.BLUE.name_str == "blue"

    def test_description_returns_correct_description(self) -> None:
        """PydanticEnum.description should return the description."""
        assert ColorEnum.RED.description == "Red color"
        assert ColorEnum.GREEN.description == "Green color"
        assert ColorEnum.BLUE.description == "Blue color"

    def test_iteration_yields_all_members(self) -> None:
        """PydanticEnum iteration should yield all members."""
        members = list(ColorEnum)

        assert len(members) == 3
        assert ColorEnum.RED in members
        assert ColorEnum.GREEN in members
        assert ColorEnum.BLUE in members
