# Google Sheets Integration Setup

This guide will help you set up Google Sheets integration for your productivity tracker so your data is automatically synced to the cloud.

## Prerequisites

- A Google account
- Python with `gspread` library installed

## Step 1: Install Required Package

```bash
pip install gspread
```

## Step 2: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Create Project" or select an existing project
3. Give your project a name (e.g., "Productivity Tracker")
4. Click "Create"

## Step 3: Enable Google Sheets API

1. In the Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Google Sheets API"
3. Click on it and press "Enable"

## Step 4: Create Service Account

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Enter a name (e.g., "productivity-tracker-service")
4. Click "Create and Continue"
5. Skip the optional steps and click "Done"

## Step 5: Generate Service Account Key

1. In the "Credentials" page, find your service account
2. Click on the service account email
3. Go to the "Keys" tab
4. Click "Add Key" > "Create New Key"
5. Choose "JSON" format
6. Click "Create"
7. The JSON file will download automatically

## Step 6: Set Up Credentials File

1. **IMPORTANT**: Rename the downloaded JSON file to `credentials.json`
2. Move `credentials.json` to your project folder (same directory as your Python files)
3. **SECURITY**: Never commit this file to version control!

## Step 7: Share Google Sheet (Optional)

If you want to access the sheet from your Google Drive:

1. Open the service account credentials file (`credentials.json`)
2. Find the `client_email` field (looks like: `your-service@project-id.iam.gserviceaccount.com`)
3. Copy this email address
4. After running the sync script (next step), you'll get a Google Sheets URL
5. Open that URL and click "Share"
6. Add your personal Gmail address as an editor

## Step 8: Run Initial Sync

```bash
python sync_to_gsheets.py
```

This will:
- Create a new Google Sheet called "Productivity Tracker"
- Upload all your existing CSV data
- Show you the Google Sheets URL

## Step 9: Test Real-time Sync

1. Run your stopwatch app: `python stop_watch.py`
2. Start and stop a timer session
3. Check your Google Sheet - the new session should appear automatically!

## Troubleshooting

### "credentials.json not found"
- Make sure the file is in the same directory as your Python scripts
- Check that the filename is exactly `credentials.json`

### "Permission denied" errors
- Make sure you've enabled the Google Sheets API
- Check that your service account has the correct permissions

### "Spreadsheet not found"
- Run `python sync_to_gsheets.py` first to create the initial spreadsheet

### Import errors
- Make sure you've installed gspread: `pip install gspread`

## Security Notes

- Keep your `credentials.json` file secure
- Don't share it or commit it to version control
- The service account only has access to sheets it creates or is explicitly shared with

## What Happens Next

Once set up:
- Every time you use the stopwatch, sessions are automatically saved to both CSV and Google Sheets
- You can access your data from anywhere via the Google Sheets URL
- The local CSV file remains as a backup
- If Google Sheets sync fails, the app continues working normally

Your Google Sheet URL will be displayed when you run the sync script! 