import os
import subprocess
import json
import csv

def get_unique_filenames(csv_file_path):
    """Read the CSV file to get a list of unique filenames."""
    unique_filenames = set()

    with open(csv_file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header
        for row in reader:
            unique_filenames.add(row[0])
    return unique_filenames

def parse_inheritance_json(json_file_path, base_path, unique_filenames):
    """Parse the JSON file to extract inheritance depth information."""
    
    # Load JSON output
    with open(json_file_path, "r") as f:
        data = json.load(f)

    inheritance_map = data["results"]["printers"][0]["additional_fields"]["child_to_base"]

    def get_depth(contract):
        """Recursively calculates inheritance depth."""
        if contract not in inheritance_map or not inheritance_map[contract]["immediate"]:
            return 0
        return 1 + max(get_depth(parent) for parent in inheritance_map[contract]["immediate"])

    # Compute depth for each contract
    depths = {contract: get_depth(contract) for contract in inheritance_map}

    # Prepare inheritance data for CSV
    inheritance_data = []
    for contract, depth in depths.items():
        parent = base_path
        # Ensure the contract name ends with .sol
        if not contract.endswith('.sol'):
            contract += '.sol'
        inheritance_data.append({
            "file": contract,
            "parent": parent,  # Adjust as needed if file name is available
            "inheritance_depth": depth
        })

    return inheritance_data

def run_slither_on_files(sol_files_list):
    """Run slither inheritance analysis on a list of Solidity files."""
    inheritance_data = []  # List to store inheritance depth information

    # Get unique filenames from the CSV
    unique_filenames = get_unique_filenames("./duplicate_files_report.csv")

    for sol_file_path in sol_files_list:
        if os.path.isfile(sol_file_path) and sol_file_path.endswith('.sol'):
            print(f"Running slither on {sol_file_path}...")
            try:
                # Extract the base path from the file path
                base_path = sol_file_path.split('/')[0]
                
                # Run slither with inheritance printer and additional arguments
                cmd = (
                    f'slither "{sol_file_path}" --print inheritance '
                    f'--solc-remaps "@openzeppelin=./{base_path}/@openzeppelin @chainlink=./{base_path}/@chainlink" '
                    f'--json {base_path}_inheritance.json '
                    f'--solc-args="--via-ir --optimize --optimize-runs 200"'
                )
                result = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                print(result.stderr.decode())

                # Parse the JSON output immediately after generating it
                json_file_path = f"{base_path}_inheritance.json"
                inheritance_data.extend(parse_inheritance_json(json_file_path, base_path, unique_filenames))

            except subprocess.CalledProcessError as e:
                print(f"Error running slither on {sol_file_path}: {e}")
                print(f"Error output: {e.stderr.decode() if e.stderr else 'None'}")
        else:
            print(f"Warning: {sol_file_path} is not a valid Solidity file and will be skipped.")

    # Write the inheritance data to a CSV file
    with open("inheritance_depth.csv", "w", newline='') as csvfile:
        fieldnames = ["file", "parent", "inheritance_depth"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        written_files = set()



        writer.writeheader()
        for entry in inheritance_data:
            # Check if the file is in unique_filenames and not already written
            if entry['file'] in unique_filenames and entry['file'] not in written_files:
                print("file in unique_filenames")
                print('file: ', entry['file'])
                writer.writerow(entry)
                print('written_files: ', written_files)
                written_files.add(entry['file'])
            else:
                # Construct the parent file name with a prefix
                parent_file_with_prefix = f"{entry['parent']}_{entry['file']}"

                print('written_files: ', written_files)
                
                # Check if the parent file with prefix is in unique_filenames and not already written
                if parent_file_with_prefix in unique_filenames and parent_file_with_prefix not in written_files:
                    # Write the entry with the parent as the file
                    writer.writerow({
                        "file": parent_file_with_prefix,
                        "parent": entry['parent'],
                        "inheritance_depth": entry['inheritance_depth']
                    })
                    written_files.add(parent_file_with_prefix)
                else:
                    # Optionally log or handle the case where neither condition is met
                    print(f"Skipping entry: {entry['file']} with parent {entry['parent']}")

    # Print or process the inheritance data
    for entry in inheritance_data:
        print(f"File: {entry['file']}, Parent: {entry['parent']}, Inheritance Depth: {entry['inheritance_depth']}")

def write_inheritance_to_csv(inheritance_data, csv_file_path):
    """Write the inheritance data to a CSV file."""

    with open(csv_file_path, "w", newline='') as csvfile:
        fieldnames = ["file", "parent", "inheritance_depth"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for entry in inheritance_data:
            writer.writerow(entry)

def main():
    # List of Solidity files to analyze
    sol_files_list = [

      #"contract": "contract file path",..

    ]
    
    run_slither_on_files(sol_files_list)

if __name__ == "__main__":
    main()

