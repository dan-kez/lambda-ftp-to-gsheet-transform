from datetime import datetime, timedelta
from pathlib import Path

import pytest

from models.column import AccountColumn
from models.editrade_file_update import EditradeFileUpdate
from models.editrade_merged_file import EditradeMergedFile
from services.editrade_file_service import _procces_xml_and_columns, EditradeFileService

account_id = "123"


@pytest.fixture()
def test_xml_string():
    path_to_test_data = (Path(__file__).parent / "./example_data/12312.XML").resolve()
    with open(path_to_test_data) as file_object:
        yield file_object.read()


@pytest.mark.parametrize(
    "columns,expected_dict",
    [
        [[], dict()],
        [
            [
                AccountColumn(
                    account_id,
                    "Check Digit",
                    xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY/CHECK_DIGIT",
                )
            ],
            {"Check Digit": "5"},
        ],
        [
            [
                AccountColumn(
                    account_id,
                    "Check Digit",
                    xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY/CHECK_DIGIT",
                ),
                AccountColumn(
                    account_id,
                    "HTS Has Many",
                    xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY//HTS",
                    has_multiple=True,
                ),
            ],
            {"Check Digit": "5", "HTS Has Many": "9603908050,3926903500,6911102500"},
        ],
        [
            [
                AccountColumn(
                    account_id,
                    "Check Digit",
                    xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY/CHECK_DIGIT",
                ),
                AccountColumn(
                    account_id,
                    "HTS Has Many",
                    xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY//HTS",
                    has_multiple=True,
                ),
                AccountColumn(
                    account_id,
                    "SHOULD NOT BE PRESENT",
                    xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY//HTasdasdS",
                    has_multiple=True,
                ),
            ],
            {"Check Digit": "5", "HTS Has Many": "9603908050,3926903500,6911102500"},
        ],
        [
            [
                AccountColumn(
                    account_id,
                    "HTS but without has_multiple",
                    xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY//HTS",
                ),
            ],
            {"HTS but without has_multiple": "9603908050"},
        ],
    ],
    ids=[
        "No Columns",
        "One Scalar Column",
        "Test Has Multiple Mixed",
        "Inaccessible Path is not included",
        "Multiple entries but without has_multiple set",
    ],
)
def test__procces_xml_and_columns(columns, expected_dict, test_xml_string):
    parsed_dict = _procces_xml_and_columns(test_xml_string, columns)
    assert parsed_dict == expected_dict


@pytest.mark.parametrize(
    "records_to_create,expected_uuids",
    [
        [[], []],
        [
            [
                EditradeFileUpdate(
                    file_uuid="uuid1",
                    editrade_upload_date=datetime.utcnow(),
                    account_id=account_id,
                    file_id="2223",
                    s3_xml_path="BS FILE PATH",
                )
            ],
            ["uuid1"],
        ],
        [
            [
                EditradeFileUpdate(
                    file_uuid="uuid1",
                    editrade_upload_date=datetime.utcnow(),
                    account_id=account_id,
                    file_id="2223",
                    s3_xml_path="BS FILE PATH",
                ),
                EditradeFileUpdate(
                    file_uuid="uuid2",
                    editrade_upload_date=datetime.utcnow(),
                    account_id=account_id,
                    file_id="2223",
                    s3_xml_path="BS FILE PATH",
                ),
            ],
            ["uuid1", "uuid2"],
        ],
        [
            [
                EditradeFileUpdate(
                    file_uuid="uuid1",
                    editrade_upload_date=datetime.utcnow(),
                    account_id=account_id,
                    file_id="2223",
                    s3_xml_path="BS FILE PATH",
                    needs_processing=False,
                ),
            ],
            [],
        ],
        [
            [
                EditradeFileUpdate(
                    file_uuid="uuid1",
                    editrade_upload_date=datetime.utcnow(),
                    account_id=account_id,
                    file_id="2223",
                    s3_xml_path="BS FILE PATH",
                ),
                EditradeFileUpdate(
                    file_uuid="uuid2",
                    editrade_upload_date=datetime.utcnow(),
                    account_id=account_id,
                    file_id="2223",
                    s3_xml_path="BS FILE PATH",
                    needs_processing=False,
                ),
            ],
            ["uuid1"],
        ],
    ],
    ids=[
        "No Files to Process",
        "One File diff that needs processing",
        "Multiple UUIDs",
        "One file that does not need processing",
        "Blend of files that need / don't need processing",
    ],
)
@pytest.mark.integration
def test_get_files_to_process(
    records_to_create, expected_uuids, fixture_model_management
):
    for record in records_to_create:
        record.save()

    # Sort here as we don't care about ordering
    assert (
        list(EditradeFileService().get_files_to_process()).sort()
        == expected_uuids.sort()
    )
    for record in records_to_create:
        record.delete()


@pytest.mark.parametrize(
    "records_to_create,days_back,expected_dict",
    [
        [[], 0, {}],
        [
            [
                EditradeFileUpdate(
                    file_uuid="uuid1",
                    editrade_upload_date=datetime.utcnow(),
                    account_id=account_id,
                    file_id="1111",
                    s3_xml_path="BS FILE PATH",
                    parsed_data={"k1": "v1"},
                    parsed_time=datetime.utcnow(),
                    needs_processing=False,
                ),
            ],
            None,
            {"1111": {"k1": "v1"},},
        ],
        [
            [
                EditradeFileUpdate(
                    file_uuid="uuid1",
                    editrade_upload_date=datetime.utcnow(),
                    account_id=account_id,
                    file_id="1111",
                    s3_xml_path="BS FILE PATH",
                    parsed_data={"k1": "v1"},
                    parsed_time=datetime.utcnow(),
                    needs_processing=False,
                ),
            ],
            0,
            {"1111": {"k1": "v1"},},
        ],
        [
            [
                EditradeFileUpdate(
                    file_uuid="uuid1",
                    editrade_upload_date=datetime.utcnow() - timedelta(days=1),
                    account_id=account_id,
                    file_id="1111",
                    s3_xml_path="BS FILE PATH",
                    parsed_data={"k1": "v1"},
                    parsed_time=datetime.utcnow(),
                    needs_processing=False,
                ),
            ],
            0,
            {},
        ],
        [
            [
                EditradeFileUpdate(
                    file_uuid="uuid1",
                    editrade_upload_date=datetime.utcnow(),
                    account_id=account_id,
                    file_id="1111",
                    s3_xml_path="BS FILE PATH",
                    parsed_data={"k1": "v1"},
                    parsed_time=datetime.utcnow(),
                    needs_processing=False,
                ),
                EditradeFileUpdate(
                    file_uuid="uuid2",
                    editrade_upload_date=datetime.utcnow() - timedelta(days=1),
                    account_id=account_id,
                    file_id="2222",
                    s3_xml_path="BS FILE PATH",
                    parsed_data={"k2": "v2"},
                    parsed_time=datetime.utcnow(),
                    needs_processing=False,
                ),
            ],
            0,
            {"1111": {"k1": "v1"}},
        ],
        [
            [
                EditradeFileUpdate(
                    file_uuid="uuid1",
                    editrade_upload_date=datetime.utcnow(),
                    account_id=account_id,
                    file_id="1111",
                    s3_xml_path="BS FILE PATH",
                    parsed_data={"k1": "v1"},
                    parsed_time=datetime.utcnow(),
                    needs_processing=False,
                ),
                EditradeFileUpdate(
                    file_uuid="uuid2",
                    editrade_upload_date=datetime.utcnow() - timedelta(days=1),
                    account_id=account_id,
                    file_id="1111",
                    s3_xml_path="BS FILE PATH",
                    parsed_data={"k2": "v2"},
                    parsed_time=datetime.utcnow(),
                    needs_processing=False,
                ),
            ],
            0,
            {"1111": {"k1": "v1", "k2": "v2"}},
        ],
        [
            [
                EditradeFileUpdate(
                    file_uuid="uuid1",
                    editrade_upload_date=datetime.utcnow(),
                    account_id=account_id,
                    file_id="1111",
                    s3_xml_path="BS FILE PATH",
                    parsed_data={"k1": "v1"},
                    parsed_time=datetime.utcnow(),
                    needs_processing=False,
                ),
                EditradeFileUpdate(
                    file_uuid="uuid2",
                    editrade_upload_date=datetime.utcnow() - timedelta(days=1),
                    account_id=account_id,
                    file_id="1111",
                    s3_xml_path="BS FILE PATH",
                    parsed_data={"k2": "v2"},
                    parsed_time=datetime.utcnow(),
                    needs_processing=False,
                ),
                EditradeFileUpdate(
                    file_uuid="uuid3",
                    editrade_upload_date=datetime.utcnow() - timedelta(days=3),
                    account_id=account_id,
                    file_id="1111",
                    s3_xml_path="BS FILE PATH",
                    parsed_data={"k3": "v3"},
                    parsed_time=datetime.utcnow(),
                    needs_processing=False,
                ),
            ],
            0,
            {"1111": {"k1": "v1", "k2": "v2", "k3": "v3"}},
        ],
        [
            [
                EditradeFileUpdate(
                    file_uuid="uuid1",
                    editrade_upload_date=datetime.utcnow(),
                    account_id=account_id,
                    file_id="1111",
                    s3_xml_path="BS FILE PATH",
                    parsed_data={"k1": "v1"},
                    parsed_time=datetime.utcnow(),
                    needs_processing=False,
                ),
                EditradeFileUpdate(
                    file_uuid="uuid2",
                    editrade_upload_date=datetime.utcnow() - timedelta(days=1),
                    account_id=account_id,
                    file_id="1111",
                    s3_xml_path="BS FILE PATH",
                    parsed_data={"k2": "v2"},
                    parsed_time=datetime.utcnow(),
                    needs_processing=False,
                ),
                EditradeFileUpdate(
                    file_uuid="uuid3",
                    editrade_upload_date=datetime.utcnow(),
                    account_id=account_id,
                    file_id="2222",
                    s3_xml_path="BS FILE PATH",
                    parsed_data={"k3": "v3"},
                    parsed_time=datetime.utcnow(),
                    needs_processing=False,
                ),
            ],
            0,
            {"1111": {"k1": "v1", "k2": "v2"}, "2222": {"k3": "v3"}},
        ],
        [
            [
                EditradeFileUpdate(
                    file_uuid="uuid1",
                    editrade_upload_date=datetime.utcnow(),
                    account_id=account_id,
                    file_id="1111",
                    s3_xml_path="BS FILE PATH",
                    parsed_data={"k1": "v1"},
                    parsed_time=datetime.utcnow(),
                    needs_processing=False,
                ),
                EditradeFileUpdate(
                    file_uuid="uuid2",
                    editrade_upload_date=datetime.today() - timedelta(days=1),
                    account_id=account_id,
                    file_id="2222",
                    s3_xml_path="BS FILE PATH",
                    parsed_data={"key1": "val1"},
                    parsed_time=datetime.utcnow(),
                    needs_processing=False,
                ),
                EditradeFileUpdate(
                    file_uuid="uuid3",
                    editrade_upload_date=datetime.today() - timedelta(days=5),
                    account_id=account_id,
                    file_id="1111",
                    s3_xml_path="BS FILE PATH",
                    parsed_data={"k1": "old hidden value", "k2": "old value but shown"},
                    parsed_time=datetime.utcnow(),
                    needs_processing=False,
                ),
                EditradeFileUpdate(
                    file_uuid="uuid4",
                    editrade_upload_date=datetime.today() - timedelta(days=7),
                    account_id=account_id,
                    file_id="3333",
                    s3_xml_path="BS FILE PATH",
                    parsed_data={"k1": "v1"},
                    parsed_time=datetime.utcnow(),
                    needs_processing=False,
                ),
            ],
            3,
            {
                "1111": {"k1": "v1", "k2": "old value but shown"},
                "2222": {"key1": "val1"},
            },
        ],
    ],
    ids=[
        "No Files to Process",
        "All time, record today",
        "Today, file today",
        "Today, file yesterday",
        "Today, one file yesterday and different one today",
        "Today, same file one file yesterday and today, combine data",
        "Today, same file over three days",
        "Today, two files of data",
        "File with overwritten key that is older than requested date range but recent file in the range",
    ],
)
@pytest.mark.integration
def test_merge_recent_processed_files_for_account_id(
    records_to_create, days_back, expected_dict, fixture_model_management
):
    for record in records_to_create:
        record.save()

    file_id_merge_file_object = {
        file_id: merged_file_object.parsed_data
        for file_id, merged_file_object in EditradeFileService.merge_recent_processed_files_for_account_id(
            account_id, days_back=days_back
        ).items()
    }

    assert file_id_merge_file_object == expected_dict

    for record in records_to_create:
        record.delete()


@pytest.mark.parametrize(
    "ftp_path,records_to_create,expected_result",
    [
        [
            "/Usr/macship/EDITRADEOUT/001940/EntryExtract-141888-D37{2020-04-04-094106}{A5058E79-2160-4F4E-8E3D-9F406D918449}.xml",
            [
                EditradeFileUpdate(
                    file_uuid="A5058E79-2160-4F4E-8E3D-9F406D918449",
                    editrade_upload_date=datetime.today(),
                    account_id=account_id,
                    file_id="141888",
                    s3_xml_path="BS FILE PATH",
                    parsed_data={"k1": "v1"},
                    parsed_time=datetime.utcnow(),
                    needs_processing=False,
                )
            ],
            True,
        ],
        [
            "/Usr/macship/EDITRADEOUT/001940/EntryExtract-141888-D37{2020-04-04-094106}{A5058E79-2160-4F4E-8E3D-9F406D918449}.xml",
            [
                EditradeFileUpdate(
                    file_uuid="Some other UUID FOR Same file",
                    editrade_upload_date=datetime.today(),
                    account_id=account_id,
                    file_id="141888",
                    s3_xml_path="BS FILE PATH",
                    parsed_data={"k1": "v1"},
                    parsed_time=datetime.utcnow(),
                    needs_processing=False,
                )
            ],
            False,
        ],
        [
            "/Usr/macship/EDITRADEOUT/001940/EntryExtract-141888-D37{2020-04-04-094106}{A5058E79-2160-4F4E-8E3D-9F406D918449}.xml",
            [
                EditradeFileUpdate(
                    file_uuid="A5058E79-2160-4F4E-8E3D-9F406D918449",
                    editrade_upload_date=datetime.today(),
                    account_id=account_id,
                    file_id="141888",
                    s3_xml_path="BS FILE PATH",
                    parsed_data={"k1": "v1"},
                    parsed_time=datetime.utcnow(),
                    needs_processing=False,
                ),
                EditradeFileUpdate(
                    file_uuid="Some other UUID FOR Different file",
                    editrade_upload_date=datetime.today(),
                    account_id=account_id,
                    file_id="12211",
                    s3_xml_path="BS FILE PATH",
                    parsed_data={"k1": "v1"},
                    parsed_time=datetime.utcnow(),
                    needs_processing=False,
                ),
            ],
            True,
        ],
        [
            "/Usr/macship/EDITRADEOUT/001940/EntryExtract-141888-D37{2020-04-04-094106}{A5058E79-2160-4F4E-8E3D-9F406D918449}.xml",
            [
                EditradeFileUpdate(
                    file_uuid="Some other UUID FOR Same file",
                    editrade_upload_date=datetime.today(),
                    account_id=account_id,
                    file_id="141888",
                    s3_xml_path="BS FILE PATH",
                    parsed_data={"k1": "v1"},
                    parsed_time=datetime.utcnow(),
                    needs_processing=False,
                )
            ],
            False,
        ],
    ],
    ids=[
        "File is in db, uuid matches",
        "File is in db but uuid does not match",
        "File is in db with matching uuid and non matching uuid",
        "File is not in db",
    ],
)
@pytest.mark.integration
def test__has_ftp_path_been_processed(
    ftp_path, records_to_create, expected_result, fixture_model_management
):
    for record in records_to_create:
        record.save()
    assert EditradeFileService._has_ftp_path_been_processed(ftp_path) == expected_result
    for record in records_to_create:
        record.delete()


@pytest.mark.parametrize(
    "records_to_create,input_timedelta,expected_result",
    [
        [[], timedelta(days=10), False],
        [
            [
                EditradeFileUpdate(
                    file_uuid="A5058E79-2160-4F4E-8E3D-9F406D918449",
                    editrade_upload_date=datetime.today() - timedelta(hours=2),
                    account_id=account_id,
                    file_id="141888",
                    s3_xml_path="BS FILE PATH",
                    parsed_data={"k1": "v1"},
                    parsed_time=datetime.utcnow() - timedelta(hours=2),
                    needs_processing=False,
                )
            ],
            timedelta(hours=1),
            False,
        ],
        [
            [
                EditradeFileUpdate(
                    file_uuid="A5058E79-2160-4F4E-8E3D-9F406D918449",
                    editrade_upload_date=datetime.today() - timedelta(hours=2),
                    account_id=account_id,
                    file_id="141888",
                    s3_xml_path="BS FILE PATH",
                    parsed_data={"k1": "v1"},
                    parsed_time=datetime.utcnow() - timedelta(hours=2),
                    needs_processing=False,
                )
            ],
            timedelta(hours=3),
            True,
        ],
    ],
    ids=["No Files", "Processed before window", "Processed within window",],
)
@pytest.mark.integration
def test_is_last_parsed_time_for_account_within_days(
    records_to_create, input_timedelta, expected_result, fixture_model_management
):
    for record in records_to_create:
        record.save()
    assert (
        EditradeFileService.is_last_parsed_time_for_account_within_timedelta(
            account_id, input_timedelta
        )
        == expected_result
    )
    for record in records_to_create:
        record.delete()


column1 = AccountColumn(account_id, "Col1", xpath_query="foo")
column2 = AccountColumn(account_id, "Col2", xpath_query="foo")


@pytest.mark.parametrize(
    "columns_to_create,merged_file_definitions_to_create,expected_result",
    [
        [[], [], [[]]],
        [
            [column1],
            [
                EditradeMergedFile(
                    account_id, "111", parsed_data={column1.column_name: "value"}
                ),
            ],
            [[column1.column_name], ["value"]],
        ],
        [
            [column1],
            [
                EditradeMergedFile(
                    account_id, "111", parsed_data={column1.column_name: "value"}
                ),
                EditradeMergedFile(
                    account_id, "222", parsed_data={column1.column_name: "value2"}
                ),
            ],
            [[column1.column_name], ["value"], ["value2"]],
        ],
        [
            [column2, column1],
            [
                EditradeMergedFile(
                    account_id, "111", parsed_data={column1.column_name: "value"}
                ),
            ],
            [[column1.column_name, column2.column_name], ["value", None]],
        ],
        [
            [column2, column1],
            [
                EditradeMergedFile(
                    account_id, "111", parsed_data={column1.column_name: "value"}
                ),
                EditradeMergedFile(
                    "randaccount",
                    "111",
                    parsed_data={column1.column_name: "VALUE FOR OTHER ACCOUNT"},
                ),
            ],
            [[column1.column_name, column2.column_name], ["value", None]],
        ],
        [
            [column2, column1],
            [
                EditradeMergedFile(
                    account_id,
                    "111",
                    parsed_data={
                        column1.column_name: "value",
                        "randomcol": "value should not appear",
                    },
                ),
            ],
            [[column1.column_name, column2.column_name], ["value", None]],
        ],
    ],
    ids=[
        "Empty Case",
        "One column one file",
        "One column multiple files",
        "File does not have column",
        "Multiple Accounts",
        "Parsed data includes columns that are not in the columns list",
    ],
)
@pytest.mark.integration
def test_create_all_file_report_for_account_id(
    columns_to_create,
    merged_file_definitions_to_create,
    expected_result,
    fixture_model_management,
):
    all_records_to_create = [*columns_to_create, *merged_file_definitions_to_create]
    for record in all_records_to_create:
        record.save()
    assert (
        EditradeFileService.create_all_file_report_for_account_id(account_id)
        == expected_result
    )
    for record in all_records_to_create:
        record.delete()
