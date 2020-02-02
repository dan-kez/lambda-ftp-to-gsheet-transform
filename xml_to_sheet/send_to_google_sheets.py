import logging

import boto3
import gspread
from bs4 import BeautifulSoup
from retry import retry

import settings
from xml_to_sheet.gspread_client import get_sheet
from xml_to_sheet.headers import IDENTIFYING_HEADER, HEADERS

s3 = boto3.client('s3')


@retry(gspread.exceptions.APIError, tries=4, delay=10, backoff=2)
def parse_s3_xml_file_to_sheet(s3_path):
    """
    Primary run method. Given an s3 path, download, parse and update the associated google sheet

    :param s3_path: str
    :return: Not meaningful
    """
    _ensure_headers_are_set()
    header_value_mapping = _download_and_get_header_value_mapping(s3_path)
    _write_or_update_row(header_value_mapping)


########################################
# Helper Functions - Writing to Google #
########################################

def _ensure_headers_are_set():
    """
    Ensure that all hardcoded headers are set. Raise if the headers are out of order so we don't accidentally
    write incorrect data.

    If we find that we need to frequently reorganize headers, we may want to have the script reorder automatically.
    At time of writing, this does not seem likely.

    :return: Not meaningful
    """
    header_row_range = get_sheet().range('A1:GA1')
    current_headers = [header_row_cell.value for header_row_cell in header_row_range if header_row_cell.value]
    for i, hard_coded_header in enumerate(HEADERS):
        try:
            if current_headers[i] != hard_coded_header.name:
                raise ValueError('Headers in google sheet do not match hard coded list')
        except IndexError:
            logging.info('New header "{}" is being added.'.format(hard_coded_header))
            pass
        # Update value as we may be appending more headers after a code change
        header_row_range[i].value = hard_coded_header.name
    get_sheet().update_cells(header_row_range)


def _write_or_update_row(header_value_mapping):
    """
    Given a dict of values write the data to the sheet. If the IDENTIFYING_HEADER is in the sheet and
    in the associated column rewrite that row instead.

    Value ordering is done by following COMBINED_HEADERS_LIST

    :param header_value_mapping: dict of header names to the associated value to write
    :return: Not meaningful
    """
    row_to_write = [header_value_mapping.get(header.name) for header in HEADERS]

    index_of_id_header = HEADERS.index(IDENTIFYING_HEADER)
    found_existing_row_for_id = None

    for cell in get_sheet().findall(str(header_value_mapping.get(IDENTIFYING_HEADER.name))):
        # Google sheets is 1 indexed and python lists are 0 indexed
        if cell.col == (index_of_id_header + 1):
            found_existing_row_for_id = cell

    # Insert row at bottom of sheet (Multi user conflict?)
    if found_existing_row_for_id:
        existing_data_row_range = get_sheet().range(
            'A{row_num}:GA{row_num}'.format(row_num=found_existing_row_for_id.row))
        for i, value in enumerate(row_to_write):
            existing_data_row_range[i].value = value
        get_sheet().update_cells(existing_data_row_range)
    else:
        get_sheet().append_row(row_to_write)


##########################################
# Helper Functions - Parsing the s3 file #
##########################################

def _download_and_get_header_value_mapping(s3_path):
    """
    Download a given s3 file and parse it.

    :param s3_path: s3 file path
    :return: dict of header to value for the given file
    """
    s3_file_response = s3.get_object(Bucket=settings.S3_BUCKET_NAME, Key=s3_path)

    xml_string = s3_file_response['Body'].read().decode('utf-8')
    return _parse_header_value_mapping_from_file(xml_string)


def _parse_header_value_mapping_from_file(file_object):
    """
    Given a string or file like object. Parse it using Beautiful soup.

    Loop through all headers and parse the necessary value

    :param file_object:
    :return: dict of header to value
    """
    soup = BeautifulSoup(file_object, 'lxml-xml')
    header_value_mapping = {}

    for header in HEADERS:
        if header.is_csv_value:
            nodes = soup.CUSTOMS_ENTRY_FILE.find_all(header.name)
            if nodes:
                # Use a set to dedupe
                header_value_mapping[header.name] = ','.join(set([node.string for node in nodes]))
        else:
            node = soup.CUSTOMS_ENTRY_FILE.find(header.name)
            if node and node.string:
                header_value_mapping[header.name] = node.string

    return header_value_mapping
