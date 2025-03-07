import re
import subprocess
import csv

# List of Solidity files to analyze
sol_files_list = [
    # Contract Path goes here for each file 
]

def generate_slither_report(sol_file_path):
    base_path = sol_file_path.split('/')[0]
    print(f"Running slither on {base_path}...")
    cmd = (
        f'slither "{sol_file_path}" --print function-summary '
        f'--solc-remaps "@openzeppelin=./{base_path}/@openzeppelin @chainlink=./{base_path}/@chainlink" '
        f'--solc-args="--via-ir --optimize --optimize-runs 200"'
        f'&> function-summary.txt'
    )
    subprocess.run(cmd, shell=True, check=True)

def process_slither_reports():
    csv_data = []

    for sol_file_path in sol_files_list:
        try:
            generate_slither_report(sol_file_path)
        except subprocess.CalledProcessError as e:
            print(f"Error processing {sol_file_path}: {e}")
            continue  # Skip to the next file

        # Read Slither output file
        with open("function-summary.txt", "r") as f:
            content = f.read()

        # Split the content into sections based on "INFO:Printers:"
        sections = content.split("INFO:Printers:")

        # Regex to match table rows
        row_pattern = re.compile(r"^\|(.+)\|$")
        # Regex to extract contract name
        contract_name_pattern = re.compile(r"Contract\s+(\w+)")

        # Process each section
        for section in sections:
            if not section.strip():
                continue

            headers = []
            total_tcc = 0  # Total Cyclomatic Complexity
            total_tec = 0  # Total External Calls

            lines = section.splitlines()

            # Extract contract name using regex
            contract_name_match = contract_name_pattern.search(section)
            contract_name = contract_name_match.group(1) if contract_name_match else "Unknown Contract"

            # Skip processing if contract name is "Unknown Contract"
            if contract_name == "Unknown Contract":
                continue

            # Extract header row
            for line in lines:
                if "Function" in line and "Cyclomatic Complexity" in line:
                    headers = [h.strip() for h in line.split("|")[1:-1]]
                    continue

                # Extract table data
                match = row_pattern.match(line)
                if match:
                    row_values = [v.strip() for v in match.group(1).split("|")]

                    if len(row_values) == len(headers):  # Ensure row matches header count
                        func_data = dict(zip(headers, row_values))

                        # Extract Cyclomatic Complexity (TCC)
                        try:
                            tcc = int(func_data.get("Cyclomatic Complexity", "0"))
                        except ValueError:
                            tcc = 0

                        # Extract Total External Calls (TEC)
                        try:
                            external_calls = func_data.get("External Calls", "[]")
                            if external_calls and external_calls != "[]":
                                tec = len(eval(external_calls))  # Convert string list to actual list and count
                            else:
                                tec = 0
                        except:
                            tec = 0  # Fallback if parsing fails

                        # Sum totals
                        total_tcc += tcc
                        total_tec += tec

            # Extract base path and filename
            base_path_filename = f"{sol_file_path.split('/')[0]}_{contract_name}.sol"

            # Add contract data to CSV data
            csv_data.append({
                "contract": f"{contract_name}.sol",
                "total_tcc": total_tcc,
                "total_tec": total_tec,
                "base_path_filename": base_path_filename
            })

            # Print section results
            print("=====================================")
            print(f"Contract Name: {contract_name}")
            print(f"✅ Total Cyclomatic Complexity (TCC): {total_tcc}")
            print(f"✅ Total External Calls (TEC): {total_tec}")
            print("=====================================")

    # Write the CSV data to a file
    with open("function_summary.csv", "w", newline='') as csvfile:
        fieldnames = ["contract", "total_tcc", "total_tec", "base_path_filename"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for entry in csv_data:
            writer.writerow(entry)

def filter_function_summary():
    # Read duplicate files into a set for quick lookup
    with open('duplicate_files_report.csv', 'r') as dup_file:
        reader = csv.reader(dup_file)
        next(reader)  # Skip header
        duplicate_files = {row[0] for row in reader}

    filtered_data = []

    # Read function summary and filter based on duplicates
    with open('function_summary.csv', 'r') as func_file:
        reader = csv.DictReader(func_file)
        for row in reader:
            base_path_filename = row['base_path_filename']
            contract_name = row['contract']

            # Check if either base_path_filename or contract_name is in duplicate files
            if base_path_filename in duplicate_files or contract_name in duplicate_files:
                # Determine which name to use as the filename
                filename = base_path_filename if base_path_filename in duplicate_files else contract_name
                filtered_data.append({
                    'filename': filename,
                    'total_tcc': row['total_tcc'],
                    'total_tec': row['total_tec']
                })

    # Remove duplicates based on 'filename'
    unique_entries = {entry['filename']: entry for entry in filtered_data}

    # Write the filtered and unique data to a new CSV
    with open('filtered_function_summary.csv', 'w', newline='') as output_file:
        fieldnames = ['filename', 'total_tcc', 'total_tec']
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)

        writer.writeheader()
        for entry in unique_entries.values():
            writer.writerow(entry)

if __name__ == "__main__":
    process_slither_reports()
    filter_function_summary()
