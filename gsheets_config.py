import gspread
import pandas as pd
from datetime import datetime
import os
import json

class GoogleSheetsManager:
    def __init__(self, credentials_file="credentials.json", sheet_name="Productivity Tracker"):
        """
        Initialize Google Sheets manager
        
        Args:
            credentials_file: Path to Google service account credentials JSON file
            sheet_name: Name of the Google Sheet to use
        """
        self.credentials_file = credentials_file
        self.sheet_name = sheet_name
        self.client = None
        self.sheet = None
        
    def connect(self):
        """Connect to Google Sheets"""
        try:
            if not os.path.exists(self.credentials_file):
                raise FileNotFoundError(f"Credentials file '{self.credentials_file}' not found")
            
            self.client = gspread.oauth()
            
            # Try to open existing sheet, create if doesn't exist
            try:
                spreadsheet = self.client.open(self.sheet_name)
                self.sheet = spreadsheet.sheet1
            except gspread.SpreadsheetNotFound:
                # Create new spreadsheet
                spreadsheet = self.client.create(self.sheet_name)
                self.sheet = spreadsheet.sheet1
                
                # Set up headers - only session_start and session_end
                self.sheet.update('A1:B1', [['session_start', 'session_end']])
                
                print(f"Created new spreadsheet: {self.sheet_name}")
                print(f"Share URL: {spreadsheet.url}")
                
            return True
            
        except Exception as e:
            print(f"Error connecting to Google Sheets: {e}")
            return False
    
    def upload_csv_data(self, csv_file="stopwatch_sessions.csv"):
        """Upload all data from local CSV to Google Sheets"""
        if not self.sheet:
            if not self.connect():
                return False
        
        try:
            # Read local CSV
            if not os.path.exists(csv_file):
                print(f"CSV file '{csv_file}' not found")
                return False
                
            df = pd.read_csv(csv_file)
            
            # Convert timestamps to strings to avoid JSON serialization issues
            df['session_start'] = pd.to_datetime(df['session_start']).dt.strftime('%Y-%m-%d %H:%M:%S')
            df['session_end'] = pd.to_datetime(df['session_end']).dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Clear existing data (except headers)
            self.sheet.clear()
            
            # Upload headers
            headers = ['session_start', 'session_end']
            self.sheet.update('A1:B1', [headers])
            
            # Convert DataFrame to list of lists for upload
            data_rows = df[headers].values.tolist()
            
            if data_rows:
                # Upload data starting from row 2
                range_name = f'A2:B{len(data_rows) + 1}'
                self.sheet.update(range_name, data_rows)
                
            print(f"Successfully uploaded {len(data_rows)} sessions to Google Sheets")
            return True
            
        except Exception as e:
            print(f"Error uploading data: {e}")
            return False
    
    def add_session(self, start_time, end_time):
        """Add a single session to Google Sheets"""
        if not self.sheet:
            if not self.connect():
                return False
        
        try:
            # Add row to sheet - only start and end times
            row_data = [start_time, end_time]
            self.sheet.append_row(row_data)
            
            print(f"Added session to Google Sheets: {start_time} — {end_time}")
            return True
            
        except Exception as e:
            print(f"Error adding session: {e}")
            return False
    
    def get_sheet_url(self):
        """Get the URL of the Google Sheet"""
        if self.sheet:
            return self.sheet.spreadsheet.url
        return None
    
    def download_data(self):
        """Download data from Google Sheets as DataFrame"""
        if not self.sheet:
            if not self.connect():
                return None
        
        try:
            # Get all data
            data = self.sheet.get_all_records()
            df = pd.DataFrame(data)
            
            if not df.empty:
                # Convert datetime columns
                df['session_start'] = pd.to_datetime(df['session_start'])
                df['session_end'] = pd.to_datetime(df['session_end'])
                # Ensure we only have the required columns
                df = df[['session_start', 'session_end']]
                # Calculate duration when needed
                df['duration_min'] = (df['session_end'] - df['session_start']).dt.total_seconds() / 60
                
            return df
            
        except Exception as e:
            print(f"Error downloading data: {e}")
            return None

# Global instance
gsheets_manager = GoogleSheetsManager() 