import csv
import os
from datetime import datetime
import pytz

def log_datetime_to_csv():
    csv_file = "datetime_log.csv"
    
    # Get current time in India (IST)
    ist_tz = pytz.timezone('Asia/Kolkata')
    now_ist = datetime.now(ist_tz)
    
    # Format date and time
    current_date = now_ist.strftime("%d-%m-%Y")
    current_time = now_ist.strftime("%I:%M %p")
    
    # Check if file exists to determine if we need headers
    file_exists = os.path.isfile(csv_file)
    
    try:
        # Open file in append mode
        with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            # Write header if creating a new file
            if not file_exists:
                writer.writerow(["Date", "Time"])
                
            # Append the current date and time
            writer.writerow([current_date, current_time])
            
        print(f"Successfully logged to CSV: {current_date} at {current_time} IST")
        
    except Exception as e:
        print(f"Error writing to CSV: {e}")

if __name__ == "__main__":
    log_datetime_to_csv()
