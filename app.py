from flask import Flask, render_template, request, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import json
import os

app = Flask(__name__)

# Google Sheets setup using environment variable
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
SPREADSHEET_NAME = "TimberTable"

try:
    # Load credentials from environment variable
    credentials_json = os.getenv("GOOGLE_SHEETS_CREDENTIALS")

    if credentials_json:
        credentials_dict = json.loads(credentials_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, SCOPE)
        client = gspread.authorize(creds)
        sheet = client.open(SPREADSHEET_NAME).sheet1
    else:
        raise ValueError("⚠️ GOOGLE_SHEETS_CREDENTIALS environment variable is not set.")
except Exception as e:
    print(f"⚠️ Error connecting to Google Sheets: {e}")
    sheet = None  # Prevent errors if the sheet is unavailable



@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/", methods=["POST"])
def submit():
    if not sheet:
        return jsonify({"success": False, "message": "❌ Google Sheets connection failed!"}), 500

    try:
        date = request.form.get("date")  # Expecting YYYY-MM-DD from frontend
        item_no = request.form.get("item_no")
        machine_no = request.form.get("machine_no")
        munsi_name = request.form.get("munsi_name")
        order_no = request.form.get("order_no")
        cft = request.form.get("cft")

        # Debugging: Print raw date
        print(f"🔹 Raw Date from Form: {date}")

        # Check if any field is missing
        if not all([date, item_no, machine_no, munsi_name, order_no, cft]):
            return jsonify({"success": False, "message": "❌ All fields are required!"}), 400

        # Convert YYYY-MM-DD (from form) to DD-MM-YYYY (for Google Sheets)
        formatted_date = datetime.strptime(date, "%Y-%m-%d").strftime("%d-%m-%Y")

        # Debugging: Print formatted date
        print(f"✅ Formatted Date: {formatted_date}")
        print(f"✅ Data to be saved: {[formatted_date, item_no, machine_no, munsi_name, order_no, cft]}")

        # Append the formatted date to Google Sheets
        sheet.append_row([formatted_date, item_no, machine_no, munsi_name, order_no, cft])

        return jsonify({"success": True, "message": "✅ Data saved successfully!"})

    except Exception as e:
        print(f"⚠️ Error storing data: {e}")
        return jsonify({"success": False, "message": f"❌ Error saving data! {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)