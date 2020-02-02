from dataclasses import dataclass


@dataclass(frozen=True)
class Header:
    name: str
    is_csv_value: bool = False
    identifying_header: bool = False


IDENTIFYING_HEADER = Header(name='FILE_NO', identifying_header=True)

# Order here matters and cannot be updated without manually moving data in the spreadsheet. The script is
# resilient to adding additional columns at the end of the list.
HEADERS = [
    Header(name='CUSTOMER_REFERENCE_NO'),
    Header(name='HTS', is_csv_value=True),
    IDENTIFYING_HEADER,
    Header(name='IMPORT_DATE'),
    Header(name='US_ENTRY_PORT'),
    Header(name='MASTER'),
    Header(name='ENTRY_DATE'),
    Header(name='ESTIMATED_ARRIVAL_DATE'),
    Header(name='RELEASE_DATE_TIME'),
    Header(name='ISSUER_CODE'),
]

# Assert there is only one identifying header
assert len([header for header in HEADERS if header.identifying_header]) == 1
