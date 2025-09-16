import os
import json

# Input folder path
input_folder = r"C:\Users\DELL\OneDrive - invincibleocean.com 1 (1)\Python Projects\Kolkata_Police_WebScrapping\missing_vehicles_pages"
output_folder = os.path.join(input_folder, "converted")  # Save converted files in a new subfolder

# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)

def transform_record(record):
    """Transform a single record into the required schema."""
    return {
        "state": "WEST BENGAL",
        "district": "",
        "police_station": "",
        "fir_number": "",
        "fir_date": "",
        "case_no": record.get("CaseNo") or record.get("Case_No", ""),
        "under_section": record.get("Under_Section", ""),
        "vehicle_registration_no": record.get("RegistrationNo", ""),
        "vehicle_type": record.get("Model", ""),
        "status": "Stolen",  # Hardcoded mapping
        "control_room_no.": "",
        "complainant": record.get("Complainant_Name", ""),
        "complainant_address": record.get("Complainant_Address", ""),
        "vehicle_engine_no.": record.get("EngineNo", ""),
        "vehicle_chasis_no.": record.get("ChassisNo", ""),
        "vehicle_make": record.get("Manufacturer", ""),
        "vehicle_color": record.get("Color", ""),
        "vehicle_model": record.get("Model", ""),
        "stolen_from": record.get("Lost_From", ""),
        "stolen_date": record.get("Lost_On") or record.get("LostOn", ""),
        "Select_Vehicle": record.get("Select_Vehicle", ""),
        "Select_Status": record.get("Select_Status", ""),
        "Trace_Address": record.get("Trace_Address", ""),
        "Date_Of_Trace": record.get("Date_Of_Trace", ""),
        "Presently_At": record.get("Presently_At", ""),
        "Display": record.get("Display", "")
    }

def process_json_file(file_path, output_path):
    """Read, transform, and save JSON file."""
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print(f"Skipping invalid JSON: {file_path}")
            return

    # Handle both single record and list of records
    if isinstance(data, dict):
        transformed = transform_record(data)
    elif isinstance(data, list):
        transformed = [transform_record(record) for record in data]
    else:
        print(f"Unexpected JSON format in {file_path}")
        return

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(transformed, f, ensure_ascii=False, indent=4)

def main():
    for filename in os.listdir(input_folder):
        if filename.endswith(".json"):
            input_file = os.path.join(input_folder, filename)
            output_file = os.path.join(output_folder, filename)
            process_json_file(input_file, output_file)
            print(f"Processed: {filename}")

if __name__ == "__main__":
    main()
