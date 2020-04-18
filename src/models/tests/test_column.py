from datetime import datetime
from unittest.mock import patch

import pytest
from dateutil.tz import tzutc

from models.column import AccountColumn


@pytest.mark.integration
def test_account_column_base_query(fixture_model_management):
    col = AccountColumn(
        account_id="123", column_name="Test Column", xpath_query="/status", order=1
    )
    col.save()

    result = list(AccountColumn.query("123"))

    assert len(result) == 1
    assert result[0].column_name == "Test Column"

    col2 = AccountColumn(
        account_id="123", column_name="Test Column 2", xpath_query="/status2", order=0
    )
    col2.save()

    result = list(AccountColumn.query("123"))

    assert len(result) == 2
    assert result[0].column_name == "Test Column"
    assert result[1].column_name == "Test Column 2"

    # should update
    col2_dupe = AccountColumn(
        account_id="123", column_name="Test Column 2", xpath_query="updated", order=0
    )
    col2_dupe.save()

    result = list(AccountColumn.query("123"))
    assert len(result) == 2
    assert result[0].column_name == "Test Column"
    assert result[1].column_name == "Test Column 2"
    assert result[1].xpath_query == "updated"


@pytest.mark.integration
def test_raises_if_xpath_not_set_on_save(fixture_model_management):
    col = AccountColumn(account_id="123", column_name="Test Column")
    with pytest.raises(ValueError, match="Attribute 'xpath_query' cannot be None"):
        col.save()


@pytest.mark.integration
@patch("models.model_mixins.datetime")
def test_created_datetime_is_set(mock_datetime, fixture_model_management):
    sentinel_datetime = datetime(1901, 2, 1, tzinfo=tzutc())
    mock_datetime.utcnow.return_value = sentinel_datetime
    col = AccountColumn(account_id="123", column_name="Test Column", xpath_query="foo")
    col.save()
    queried_column = AccountColumn.get("123", "Test Column")
    assert queried_column.created_time == sentinel_datetime


@pytest.mark.integration
@pytest.mark.parametrize(
    "account_id, account_columns_to_create, expected_columns",
    [
        [
            "123",
            [
                AccountColumn(
                    account_id="123", column_name="A", xpath_query="/status",
                ),
                AccountColumn(
                    account_id="123", column_name="B", xpath_query="/status",
                ),
            ],
            ["A", "B"],
        ],
        [
            "123",
            [
                AccountColumn(
                    account_id="123", column_name="A", xpath_query="/status", order=1
                ),
                AccountColumn(
                    account_id="123", column_name="B", xpath_query="/status", order=0
                ),
            ],
            ["B", "A"],
        ],
        [
            "123",
            [
                AccountColumn(
                    account_id="123", column_name="A", xpath_query="/status", order=0
                ),
                AccountColumn(
                    account_id="123", column_name="B", xpath_query="/status", order=1
                ),
                AccountColumn(
                    account_id="123", column_name="C", xpath_query="/status", order=0
                ),
            ],
            ["A", "C", "B"],
        ],
        [
            "123",
            [
                AccountColumn(account_id="123", column_name="A", xpath_query="/status"),
                AccountColumn(account_id="222", column_name="B", xpath_query="/status"),
                AccountColumn(account_id="123", column_name="C", xpath_query="/status"),
            ],
            ["A", "C"],
        ],
    ],
    ids=["Alpha no order key", "sort by order key", "mixed sort", "mixed account ids"],
)
def test_account_column_get_columns_for_account_id_ordering(
    account_id, account_columns_to_create, expected_columns, fixture_model_management
):
    for column in account_columns_to_create:
        column.save()

    fetched_columns = AccountColumn.get_columns_for_account_id(account_id)
    assert len(fetched_columns) == len(expected_columns)
    for index, fetched_column in enumerate(fetched_columns):
        assert fetched_column.column_name == expected_columns[index]
