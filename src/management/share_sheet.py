import argparse
import logging

from models.account import Account
from services.google_sheet_service import GoogleSheetService

VALID_ROLES = ["reader", "writer"]

parser = argparse.ArgumentParser(description="Share a worksheet for an account id")
parser.add_argument(
    "--account_id", dest="account_id", help="Account to share the worksheet with"
)
parser.add_argument(
    "--share_with_email",
    dest="share_with_email",
    help="Email to share the worksheet with",
)
parser.add_argument(
    "--role", dest="role", default="reader", choices=VALID_ROLES, help="Role to assign"
)

args = parser.parse_args()

google_sheet_service = GoogleSheetService()
try:
    Account.get(args.account_id)
except Account.DoesNotExist:
    logging.error("The account provided does not exist")
    exit(1)

logging.info(
    "Sharing sheet with {} as role {}".format(args.share_with_email, args.role)
)
spreadsheet = google_sheet_service.share_spreadsheet_with_email(
    args.account_id, args.share_with_email, role=args.role
)
