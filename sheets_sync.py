import gspread
import pandas as pd
from datetime import datetime

def create_and_sync_sheet():
    # Connect using OAuth
    gc = gspread.oauth()
    
    # Create a new spreadsheet
    sheet_title = f"Productivity Tracker - {datetime.now().strftime('%Y-%m-%d')}"
    sh = gc.create(sheet_title)
    
    # Share it with yourself (replace with your email)
    sh.share('your-email@gmail.com', perm_type='user', role='writer')
    
    print(f"Created new sheet: {sh.url}")
    return sh

if __name__ == "__main__":
    sheet = create_and_sync_sheet()