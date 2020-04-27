from models.column import AccountColumn
from services.account_service import AccountService

"""
Helper file to create all tables in one command
"""

if __name__ == "__main__":
    account_001940_relative_to_xpath = "/CUSTOMS_ENTRY_FILE/ENTRY/INVOICE/CLIENT_REF_NO"
    account_seed_data = {
        "002113": [
            AccountColumn(
                "002113",
                "Customer Reference No",
                xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY/CUSTOMER_REFERENCE_NO",
                order=1,
            ),
            AccountColumn(
                "002113",
                "HTS",
                xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY/INVOICE/ITEM/HTS",
                has_multiple=True,
                order=2,
            ),
            AccountColumn(
                "002113",
                "File ID",
                xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY/FILE_NO",
                order=3,
            ),
            AccountColumn(
                "002113",
                "US_ENTRY_PORT",
                xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY/US_ENTRY_PORT",
                order=4,
            ),
            AccountColumn(
                "002113",
                "MASTER",
                xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY/MANIFEST/MASTER",
                order=5,
            ),
            AccountColumn(
                "002113",
                "ENTRY_DATE",
                xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY/ENTRY_DATE",
                order=6,
            ),
            AccountColumn(
                "002113",
                "ESTIMATED_ARRIVAL_DATE",
                xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY/ESTIMATED_ARRIVAL_DATE",
                order=7,
            ),
            AccountColumn(
                "002113",
                "RELEASE_DATE_TIME",
                xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY/CURRENT_STATUS/RELEASE_DATE_TIME",
                order=8,
            ),
            AccountColumn(
                "002113",
                "ISSUER_CODE",
                xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY/MANIFEST/ISSUER_CODE",
                order=9,
            ),
        ],
        "001940": [
            AccountColumn(
                "001940",
                "Type",
                xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY/HEADER_ADDRESS/TYPE",
                relative_to_xpath=account_001940_relative_to_xpath,
                order=1,
            ),
            AccountColumn(
                "001940",
                "Broker",
                xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY/COMPANY_CODE",
                relative_to_xpath=account_001940_relative_to_xpath,
                order=2,
            ),
            AccountColumn(
                "001940",
                "MAWB",
                xpath_query="concat(/CUSTOMS_ENTRY_FILE/ENTRY/MANIFEST/ISSUER_CODE, /CUSTOMS_ENTRY_FILE/ENTRY/MANIFEST/MASTER)",
                relative_to_xpath=account_001940_relative_to_xpath,
                order=3,
            ),
            AccountColumn(
                "001940",
                "HAWB",
                xpath_query="concat(/CUSTOMS_ENTRY_FILE/ENTRY/MANIFEST/HOUSE_ISSUER_CODE, /CUSTOMS_ENTRY_FILE/ENTRY/MANIFEST/HOUSE)",
                relative_to_xpath=account_001940_relative_to_xpath,
                order=4,
            ),
            AccountColumn(
                "001940",
                "Entry #",
                xpath_query='concat(/CUSTOMS_ENTRY_FILE/ENTRY/FILER_CODE, "-", /CUSTOMS_ENTRY_FILE/ENTRY/ENTRY_NO, "-", /CUSTOMS_ENTRY_FILE/ENTRY/CHECK_DIGIT)',
                relative_to_xpath=account_001940_relative_to_xpath,
                order=5,
            ),
            AccountColumn(
                "001940",
                "Shipper",
                xpath_query="../ITEM/PGA_FDA/PGA_FDA_ENTITY_ADDRESS/NAME",
                relative_to_xpath=account_001940_relative_to_xpath,
                order=6,
            ),
            AccountColumn(
                "001940",
                "Ultimate Consignee",
                xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY/HEADER_ADDRESS/ENTITY_IDENTIFIER",
                relative_to_xpath=account_001940_relative_to_xpath,
                order=7,
            ),
            AccountColumn(
                "001940",
                "Mode",
                xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY/MODE_OF_TRANSPORTATION",
                relative_to_xpath=account_001940_relative_to_xpath,
                order=8,
            ),
            AccountColumn(
                "001940",
                "PO#",
                xpath_query="../CLIENT_REF_NO",
                relative_to_xpath=account_001940_relative_to_xpath,
                order=9,
            ),
            AccountColumn(
                "001940",
                "Invoice Number",
                xpath_query="substring-before(../DESCRIPTION_2/text(), '/')",
                relative_to_xpath=account_001940_relative_to_xpath,
                order=10,
            ),
            AccountColumn(
                "001940",
                "Line item Number on the Invoice",
                xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY/LINE_ITEM_COUNT",
                relative_to_xpath=account_001940_relative_to_xpath,
                order=11,
            ),
            AccountColumn(
                "001940",
                "Material #",
                xpath_query="substring-before(../DESCRIPTION_2/text(), '/')",
                relative_to_xpath=account_001940_relative_to_xpath,
                order=12,
            ),
            AccountColumn(
                "001940",
                "Product Description",
                xpath_query="../DESCRIPTION_1",
                relative_to_xpath=account_001940_relative_to_xpath,
                order=13,
            ),
            AccountColumn(
                "001940",
                "Total Pallets in Shipment",
                xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY/MANIFEST/DELIVERY_ORDER/DELIVERY_ORDER_ITEM/DESCRIPTION_1",
                relative_to_xpath=account_001940_relative_to_xpath,
                order=14,
            ),
            AccountColumn(
                "001940",
                "PAL Count",
                xpath_query='concat(../ITEM/PGA_FDA/UNITS[QTY_UOM = "PAL"]/QTY, " ", ../ITEM/PGA_FDA/UNITS[QTY_UOM = "PAL"]/QTY_UOM)',
                relative_to_xpath=account_001940_relative_to_xpath,
                order=15,
            ),
            AccountColumn(
                "001940",
                "BX Count",
                xpath_query='concat(../ITEM/PGA_FDA/UNITS[QTY_UOM = "BX"]/QTY, " ", ../ITEM/PGA_FDA/UNITS[QTY_UOM = "BX"]/QTY_UOM)',
                relative_to_xpath=account_001940_relative_to_xpath,
                order=16,
            ),
            AccountColumn(
                "001940",
                "PCS Count",
                xpath_query='concat(../ITEM/PGA_FDA/UNITS[QTY_UOM = "PCS"]/QTY, " ", ../ITEM/PGA_FDA/UNITS[QTY_UOM = "PCS"]/QTY_UOM)',
                relative_to_xpath=account_001940_relative_to_xpath,
                order=17,
            ),
            AccountColumn(
                "001940",
                "Country of Origin for US Customs Purposes",
                xpath_query="../ITEM/COUNTRY_OF_ORIGIN",
                relative_to_xpath=account_001940_relative_to_xpath,
                order=18,
            ),
            AccountColumn(
                "001940",
                "Shipment Origin",
                xpath_query="../ITEM/COUNTRY_OF_EXPORT",
                relative_to_xpath=account_001940_relative_to_xpath,
                order=19,
            ),
            AccountColumn(
                "001940",
                "Destination Port",
                xpath_query="../ITEM/PGA_FDA/ANTICIPATED_ARRIVAL_LOCATION_DESCRIPTION",
                relative_to_xpath=account_001940_relative_to_xpath,
                order=20,
            ),
            AccountColumn(
                "001940",
                "Customs Release Date",
                xpath_query="../ITEM/PGA_FDA/ANTICIPATED_ARRIVAL_DATE_TIME",
                relative_to_xpath=account_001940_relative_to_xpath,
                order=21,
            ),
            AccountColumn(
                "001940",
                "Estimated Arrival Date",
                xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY/ESTIMATED_ARRIVAL_DATE",
                relative_to_xpath=account_001940_relative_to_xpath,
                order=22,
            ),
            AccountColumn(
                "001940",
                "Actual Arrival Date",
                xpath_query="/CUSTOMS_ENTRY_FILE/ENTRY/MANIFEST/DELIVERY_ORDER/ARRIVAL_DATE",
                relative_to_xpath=account_001940_relative_to_xpath,
                order=23,
            ),
        ],
    }
    account_service = AccountService()

    for account_id, columns in account_seed_data.items():
        account_service.create_account(account_id)
        with AccountColumn.batch_write() as batch:
            # for column in AccountColumn.query(account_id):
            #     batch.delete(column)
            # sleep(5)

            for column in columns:
                # sleep(1)
                batch.save(column)
