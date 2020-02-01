from oauth2client.service_account import ServiceAccountCredentials
import gspread
import settings

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_dict(
    settings.GOOGLE_SERVICE_ACCOUNT_CREDENTIAL_JSON,
    scope,
)

gspread_client = gspread.authorize(credentials)
