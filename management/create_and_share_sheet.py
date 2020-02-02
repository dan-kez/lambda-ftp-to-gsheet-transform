import argparse
import logging

from xml_to_sheet.gspread_client import get_sheet

VALID_ROLES = ['reader', 'writer']

parser = argparse.ArgumentParser(description='Create and/or share a worksheet.')
parser.add_argument('--attempt_create',  action='store_true', help='If set attempt to create sheet')
parser.add_argument('--share_with_email', dest='share_with_email', help='Account to share the worksheet with')
parser.add_argument('--role', dest='role', default='reader', choices=VALID_ROLES, help='Role to assign')

args = parser.parse_args()

sheet = get_sheet(attempt_to_create=args.attempt_create)

if args.share_with_email:
    logging.info('Sharing sheet with {} as role {}'.format(args.share_with_email, args.role))
    sheet.spreadsheet.share(args.share_with_email, perm_type='user', role=args.role)
