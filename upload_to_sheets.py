import os
import pandas as pd
import pickle
from typing import List, Optional
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from google.oauth2 import service_account

# If modifying these scopes, delete any existing token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive.file']

def authenticate_google():
    """Authenticates using Service Account (preferred) or OAuth 2.0."""
    creds = None
    
    # Check for Service Account first (better for automation)
    if os.path.exists('service_account.json'):
        print("Authenticating with Service Account...")
        return service_account.Credentials.from_service_account_file(
            'service_account.json', scopes=SCOPES)

    # Fallback to OAuth 2.0
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
            
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                print("Error: Neither 'service_account.json' nor 'credentials.json' found.")
                print("Please download your Service Account JSON key or OAuth client credentials.")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def format_sheet(service, spreadsheet_id, sheet_id, num_rows, num_cols):
    """Formats the Google Sheet for better readability."""
    requests = [
        # 1. Bold the header row
        {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 0,
                    "endRowIndex": 1
                },
                "cell": {
                    "userEnteredFormat": {
                        "textFormat": {"bold": True},
                        "backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.9},
                        "horizontalAlignment": "CENTER"
                    }
                },
                "fields": "userEnteredFormat(textFormat,backgroundColor,horizontalAlignment)"
            }
        },
        # 2. Freeze the header row
        {
            "updateSheetProperties": {
                "properties": {
                    "sheetId": sheet_id,
                    "gridProperties": {
                        "frozenRowCount": 1
                    }
                },
                "fields": "gridProperties.frozenRowCount"
            }
        },
        # 3. Auto-resize columns
        {
            "autoResizeDimensions": {
                "dimensions": {
                    "sheetId": sheet_id,
                    "dimension": "COLUMNS",
                    "startIndex": 0,
                    "endIndex": num_cols
                }
            }
        }
    ]
    
    try:
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": requests}
        ).execute()
        print("Sheet formatting applied successfully.")
    except Exception as e:
        print(f"Warning: Could not format sheet: {e}")

def create_spreadsheet(service, title="Engram Scored Leads"):
    """Creates a new Google Spreadsheet and returns its ID and first sheet ID."""
    spreadsheet = {
        'properties': {
            'title': title
        }
    }
    spreadsheet = service.spreadsheets().create(body=spreadsheet, fields='spreadsheetId,sheets').execute()
    sheet_id = spreadsheet.get('sheets')[0].get('properties').get('sheetId')
    return spreadsheet.get('spreadsheetId'), sheet_id

def upload_leads(csv_path: str, spreadsheet_id: Optional[str] = None):
    """Reads the CSV and uploads relevant columns to Google Sheets."""
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        return

    print(f"Loading data from {csv_path}...")
    df = pd.read_csv(csv_path)

    # Column Mapping (Target columns -> potential CSV column names)
    mapping = {
        "Name": ["username", "name", "author"],
        "Platform": ["platform"],
        "Problem": ["problem", "problem_description", "issue"],
        "Intent Score": ["intent_score", "intent score"],
        "Lead Score": ["lead_score", "lead score", "score"],
        "Contact Info": ["contact_info", "contact info", "email"],
        "Link": ["url", "source_link", "link"]
    }

    final_df_data = {}
    for target_col, source_options in mapping.items():
        found = False
        for opt in source_options:
            if opt in df.columns:
                final_df_data[target_col] = df[opt]
                found = True
                break
        if not found:
            print(f"Warning: Column for '{target_col}' not found in CSV. Using empty values.")
            final_df_data[target_col] = ""

    final_df = pd.DataFrame(final_df_data)
    
    # Sort by Lead Score if possible
    if "Lead Score" in final_df.columns:
        try:
            final_df["Lead Score"] = pd.to_numeric(final_df["Lead Score"], errors='coerce')
            final_df = final_df.sort_values(by="Lead Score", ascending=False)
        except:
            pass

    # Prepare data for upload (Header + Values)
    values = [final_df.columns.tolist()] + final_df.fillna("").values.tolist()

    # Authenticate
    creds = authenticate_google()
    if not creds:
        return

    try:
        service = build('sheets', 'v4', credentials=creds)
        
        # Create or Connect
        if not spreadsheet_id:
            print("No Spreadsheet ID provided. Creating a new one...")
            spreadsheet_id, sheet_id = create_spreadsheet(service)
            print(f"New Spreadsheet Created! ID: {spreadsheet_id}")
            print(f"View it here: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
        else:
            # Get sheet id of the first sheet
            sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            sheet_id = sheet_metadata['sheets'][0]['properties']['sheetId']
            print(f"Connecting to existing Spreadsheet: {spreadsheet_id}")

        # Clear existing data and write new data
        range_name = 'Sheet1!A1'
        body = {
            'values': values
        }
        
        # Clear sheet first (optional but keeps things clean)
        service.spreadsheets().values().clear(spreadsheetId=spreadsheet_id, range='Sheet1!A:Z').execute()
        
        # Update values
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range=range_name,
            valueInputOption='USER_ENTERED', body=body).execute()
        print(f"{result.get('updatedCells')} cells updated.")

        # Apply formatting
        format_sheet(service, spreadsheet_id, sheet_id, len(values), len(final_df.columns))

    except HttpError as err:
        print(f"An error occurred: {err}")

if __name__ == "__main__":
    # Prioritize final_leads_master.csv if it exists, otherwise scored_leads.csv
    final_csv = "data/final/final_leads_master.csv"
    if not os.path.exists(final_csv):
        final_csv = "scored_leads.csv"
        
    spreadsheet_id = os.getenv("SPREADSHEET_ID")
    upload_leads(final_csv, spreadsheet_id)
