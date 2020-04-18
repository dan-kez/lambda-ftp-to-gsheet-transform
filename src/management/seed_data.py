from models.account import Account
from models.column import AccountColumn
from services.account_service import AccountService

"""
Helper file to create all tables in one command
"""

if __name__ == "__main__":
    account_seed_data = {
        "002113": [
            AccountColumn(
                "002113",
                "Customer Reference No",
                xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY/CUSTOMER_REFERENCE_NO",
            ),
            AccountColumn(
                "002113",
                "HTS",
                xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY/INVOICE/ITEM/HTS",
                has_multiple=True,
            ),
            AccountColumn(
                "002113", "File ID", xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY/FILE_NO"
            ),
            AccountColumn(
                "002113",
                "US_ENTRY_PORT",
                xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY/US_ENTRY_PORT",
            ),
            AccountColumn(
                "002113",
                "MASTER",
                xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY/MANIFEST/MASTER",
            ),
            AccountColumn(
                "002113",
                "ENTRY_DATE",
                xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY/ENTRY_DATE",
            ),
            AccountColumn(
                "002113",
                "ESTIMATED_ARRIVAL_DATE",
                xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY/ESTIMATED_ARRIVAL_DATE",
            ),
            AccountColumn(
                "002113",
                "RELEASE_DATE_TIME",
                xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY/CURRENT_STATUS/RELEASE_DATE_TIME",
            ),
            AccountColumn(
                "002113",
                "ISSUER_CODE",
                xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY/MANIFEST/ISSUER_CODE",
            ),
        ],
        "001940": [
            AccountColumn(
                "001940",
                "Type",
                xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY/HEADER_ADDRESS/TYPE",
            ),
            AccountColumn(
                "001940",
                "Broker",
                xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY/COMPANY_CODE",
            ),
            AccountColumn(
                "001940",
                "MAWB / HAWB",
                xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY/CONTAINERS/STATUS_HISTORY/MSG_DATA",
            ),
            AccountColumn(
                "001940",
                "Filer Code",
                xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY/FILTER_CODE",
            ),
            AccountColumn(
                "001940", "Entry #", xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY/ENTRY_NO",
            ),
            AccountColumn(
                "001940",
                "Shipper",
                xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY/ENTRY_IDENTIFIER",
            ),
            AccountColumn(
                "001940",
                "Ultimate Consignee",
                xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY/CONTAINERS/INVOICE/ITEM/PGA_FDA/PGA_FDA_ENTITY_ADDRESS/NAME",
            ),
            AccountColumn(
                "001940",
                "Mode",
                xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY/MODE_OF_TRANSPORTATION",
            ),
            AccountColumn(
                "001940", "PO#", xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY/CLIENT_REF_NO",
            ),
            AccountColumn(
                "001940",
                "Invoice Number / Material #",
                xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY/DESCRIPTION_2",
            ),
            AccountColumn(
                "001940",
                "Line item Number on the Invoice",
                xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY/LINE_ITEM_COUNT",
            ),
            AccountColumn(
                "001940",
                "Product Description",
                xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY/CONTAINERS/INVOICE/DESCRIPTION_1",
            ),
            AccountColumn(
                "001940",
                "Total Pallets in Shipment",
                xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY/INVOICE/DESCRIPTION_1",
            ),
            AccountColumn(
                "001940",
                "Country of Origin for US Customs Purposes",
                xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY/INVOICE/ITEM/COUNTRY_OF_ORIGIN",
            ),
            AccountColumn(
                "001940",
                "Shipment Origin",
                xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY/INVOICE/ITEM/COUNTRY_OF_EXPORT",
            ),
            AccountColumn(
                "001940",
                "Destination Port",
                xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY/INVOICE/ITEM/PGA_FDA/ANTICIPATED_ARRIVAL_LOCATION_DESCRIPTION",
            ),
            AccountColumn(
                "001940",
                "Estimated Arrival Date",
                xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY/INVOICE/ITEM/PGA_FDA/ANTICIPATED_ARRIVAL_DATE_TIME",
            ),
            AccountColumn(
                "001940",
                "Actual Arrival Date",
                xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY/MANIFEST/DELIVERY_ORDER/ARRIVAL_DATE",
            ),
        ],
    }
    account_service = AccountService()

    for account_id, columns in account_seed_data.items():
        account_service.create_account(account_id)
        for column in columns:
            column.save()
