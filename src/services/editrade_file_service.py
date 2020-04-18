from datetime import timedelta, datetime
from functools import cached_property, reduce
from typing import List, Set, Dict

import boto3
from lxml import etree
from pynamodb.models import BatchWrite

import settings
from models.column import AccountColumn
from models.editrade_file_update import (
    FilesToProcessIndex,
    EditradeFileUpdate,
    FileDiffsByAccountIndex,
    FileDiffsByFileIDIndex,
    AccountIDByParseTime,
)
from models.editrade_merged_file import EditradeMergedFile, MergedFileByUpdateTime
from services.editrade_ftp_file_parser import EditradeFTPFileParser
from services.ftp_to_s3 import editrade_ftp_service
from utils.merge_dicts import merge_dicts

xmlparser = etree.HTMLParser()


def _upload_to_s3_and_create_diff(
    ftp_path: str, editrade_file_update: EditradeFileUpdate, autosave: bool = True
) -> None:
    editrade_ftp_service.transfer_file_from_ftp_to_s3(
        ftp_path, editrade_file_update.s3_xml_path
    )

    # Save file record as the file has been uploaded to s3
    if autosave:
        editrade_file_update.save()


def _procces_xml_and_columns(
    xml_string: str, columns: List[AccountColumn]
) -> Dict[str, str]:
    """
    Given the xml and column set, do an in memory only transformation to a serializable to json python dict
    :param xml_string: XML to parse
    :param columns: List of column objects
    :return: An unordered dict mapping the column name to the value
    """
    parsed_dict = {}
    tree = etree.fromstring(xml_string)
    for column in columns:
        values = tree.xpath(column.xpath_query)
        if values:
            if column.has_multiple:
                value_to_set = ",".join([value.text for value in values if value.text])
                if value_to_set:
                    parsed_dict[column.column_name] = value_to_set
            else:
                if values[0].text:
                    parsed_dict[column.column_name] = values[0].text
    return parsed_dict


class EditradeFileService(object):
    @cached_property
    def s3_connection(self):
        return boto3.client("s3")

    @staticmethod
    def get_files_to_process() -> List[str]:
        """
        Query the files that need to be processed
        :return: list of uuids to process
        """
        for record in FilesToProcessIndex.query(True):
            yield record.file_uuid

    def create_file_update_from_ftp_path(self, ftp_path: str) -> EditradeFileUpdate:
        editrade_file_update = EditradeFTPFileParser(ftp_path).to_editrade_file_update()

        # TODO: Would be good to not download the file twice.
        _upload_to_s3_and_create_diff(ftp_path, editrade_file_update)
        editrade_file_object = self.process_by_editrade_file_update_object(
            editrade_file_update
        )
        self.merge_file_diffs_for_file_id(editrade_file_object.file_id)

    def _get_xml_string_from_s3(self, s3_xml_path: str) -> str:
        """
        Get XML File to string in memory from s3 path
        :param s3_xml_path:
        :return: xml string
        """
        s3_file_response = self.s3_connection.get_object(
            Bucket=settings.S3_BUCKET_NAME, Key=s3_xml_path
        )

        return s3_file_response["Body"].read().decode("utf-8")

    def process_by_editrade_file_update_object(
        self, editrade_file_update: EditradeFileUpdate, batch=None,
    ) -> EditradeFileUpdate:
        """
        Given a EditradeFileUpdate instance, download the file from s3 and parse the file. Returns
        the same instance with all appropriately set attributes.

        :param editrade_file_update:
        :param batch:
        :return: Original instance with all appropriately set attributes
        """
        xml_string = self._get_xml_string_from_s3(editrade_file_update.s3_xml_path)
        columns = AccountColumn.get_columns_for_account_id(
            editrade_file_update.account_id
        )

        parsed_dict = _procces_xml_and_columns(xml_string, columns)

        editrade_file_update.set_parsed_data(parsed_dict)
        if batch:
            batch.save(editrade_file_update)
        else:
            editrade_file_update.save()

        return editrade_file_update

    def reprocess_files(
        self, account_id: str, needs_processing_only: bool = None
    ) -> None:
        """
        Reprocess all files for account_id

        :param account_id:
        :param needs_processing_only: if set filter to only those that need processing
        :return:
        """
        condition = EditradeFileUpdate.account_id == account_id
        if needs_processing_only is not None:
            condition = condition | (
                EditradeFileUpdate.needs_processing == needs_processing_only
            )
        editrade_files_to_update = list(EditradeFileUpdate.scan(condition))
        with EditradeFileUpdate.batch_write() as file_update_batch:
            for file in editrade_files_to_update:
                self.process_by_editrade_file_update_object(
                    file, batch=file_update_batch
                )
        file_ids_reprocessed = {file.file_id for file in editrade_files_to_update}

        with EditradeMergedFile.batch_write() as merged_file_batch:
            for file_id in file_ids_reprocessed:
                self.merge_file_diffs_for_file_id(file_id, batch=merged_file_batch)

    @staticmethod
    def filter_known_files_from_ftp_path(ftp_paths: Set[str]) -> Set[str]:
        """
        Given a set of ftp paths, check filter those that exist in the db
        :param ftp_paths:
        :return:
        """
        # TODO: Change this to a batch approach. This is making a db call in a loop
        return {
            ftp_path
            for ftp_path in ftp_paths
            if not EditradeFileService._has_ftp_path_been_processed(ftp_path)
        }

    @staticmethod
    def _has_ftp_path_been_processed(ftp_path: str) -> bool:
        """
        Helper method primarily for use in stubbing during testing
        """
        editrade_file_update_object = EditradeFTPFileParser(
            ftp_path
        ).to_editrade_file_update()

        return EditradeFileUpdate.record_exists(editrade_file_update_object.file_uuid)

    @staticmethod
    def is_last_parsed_time_for_account_within_timedelta(
        account_id: str, input_timedelta: timedelta
    ) -> bool:
        """
        Check if the last time a file was processed for an account is within the provided timedelta

        :param account_id:
        :param input_timedelta:
        :return:
        """
        result = AccountIDByParseTime.query(
            account_id,
            AccountIDByParseTime.parsed_time >= (datetime.utcnow() - input_timedelta),
        )

        try:
            result.next()
            return True
        except StopIteration:
            return False

    @staticmethod
    def merge_file_diffs_for_file_id(file_id: str, batch=None):
        ordered_file_diffs = list(FileDiffsByFileIDIndex.query(file_id))
        account_id = ordered_file_diffs[0].account_id

        ordered_parsed_data = [record.parsed_data for record in ordered_file_diffs]
        merged_parsed_data_for_file = dict(
            reduce(merge_dicts, [{}] + ordered_parsed_data)
        )

        merged_file_data = EditradeMergedFile(
            account_id, file_id, parsed_data=merged_parsed_data_for_file
        )

        if batch:
            batch.save(merged_file_data)
        else:
            merged_file_data.save()
        return merged_file_data

    @staticmethod
    def merge_recent_processed_files_for_account_id(
        account_id: str, days_back: int = None, autosave: bool = True
    ) -> Dict[str, EditradeMergedFile]:
        """
        Method to merge all file diffs and optionally save them.

        :param account_id: Account id to process
        :param days_back: If None, then process all file diffs for the account. If set, limit by days back inclusive.
        :param autosave: If true, save the merged parsed file values to the shared table
        :return: the merged result by file id
        """
        # Get file ids to check based on days back attribute
        additional_filters = []
        if days_back is not None:
            additional_filters.append(
                FileDiffsByAccountIndex.editrade_upload_date
                >= datetime.today() - timedelta(days=days_back)
            )

        file_ids_to_query: Set[str] = {
            record.file_id
            for record in FileDiffsByAccountIndex.query(account_id, *additional_filters)
        }

        merged_by_file_id = {
            file_id: EditradeFileService.merge_file_diffs_for_file_id(
                file_id, autosave=autosave
            )
            for file_id in file_ids_to_query
        }
        return merged_by_file_id

    @staticmethod
    def create_all_file_report_for_account_id(account_id):
        """
        This is a bulk method that will get all the merged file data, assemble into a list of lists format (csv-esque)
        with the appropriate ordering based on the column definitions for the account.

        The approach here should be reconsidered when the data set gets larger. It's wasteful to have to fully
        calculate and create a "csv" from the start of time. That said it's fine for now knowing rate of file additions.

        :param account_id: the account id to process for
        :return: List[List[str]]
        """
        columns = AccountColumn.get_columns_for_account_id(account_id)
        ordered_headers = [column.column_name for column in columns]

        csv_result: List[List[str]] = [ordered_headers]
        for merged_file in EditradeMergedFile.query(account_id):
            row_data = [
                merged_file.parsed_data.get(header) for header in ordered_headers
            ]
            csv_result.append(row_data)
        return csv_result

    @staticmethod
    def get_accounts_with_updated_files_in_timedelta(
        input_timedelta: timedelta = None,
    ) -> List[str]:
        """
        Get all the accounts to process that have had file updates in the input time delta.
        :param input_timedelta:
        :return: List of account ids
        """
        # Very annoying that we have to scan the whole table to get the unique set of account ids.
        # Consider having a manual table that is the unique set of ids to remove this need.
        if input_timedelta:
            records = EditradeMergedFile.scan(
                EditradeMergedFile.updated_time >= datetime.utcnow() - input_timedelta,
                attributes_to_get=["account_id"],
            )
        else:
            records = EditradeMergedFile.scan(attributes_to_get=["account_id"],)

        # Set to remove duplicates
        account_ids = {record.account_id for record in records}
        return list(account_ids)
