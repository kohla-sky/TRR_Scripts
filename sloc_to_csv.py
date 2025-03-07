import re
import csv
import sys
import subprocess
import os

def parse_sloc_output(input_file=None):
    """
    Parse SLOC output and convert to CSV format.
    If input_file is provided, read from that file, otherwise read from stdin.
    """
    lines = []
    if input_file:
        with open(input_file, 'r') as f:
            lines = f.readlines()
    else:
        # Read from stdin if no file is provided
        lines = sys.stdin.readlines()
    
    results = []
    pattern = r'(\.\/[^:]+):\s+(\d+)\s+SLOC'
    
    for line in lines:
        line = line.strip()
        match = re.match(pattern, line)
        if match:
            file_path = match.group(1)
            sloc_count = int(match.group(2))
            
            # Extract the first folder and filename for matching
            path_parts = file_path.split('/')
            if len(path_parts) > 2:
                match_key = f"{path_parts[1]}/{path_parts[-1]}"
            else:
                match_key = path_parts[-1]
            
            results.append((file_path, match_key, sloc_count))
    
    return results

def read_file_list(csv_file):
    """Read the list of files from a CSV file."""
    files = []
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        # Skip header
        next(reader, None)
        for row in reader:
            if row and row[0]:  # Ensure row is not empty
                files.append(row[0])
    return files

def count_sloc_for_file(file_path):
    """Count SLOC for a single file using the logic from sloc.py."""
    if not os.path.exists(file_path):
        return 0
        
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            in_multiline_comment = False
            sloc = 0
            
            for line in lines:
                line = line.strip()
                if not line:  # Skip empty lines
                    continue
                    
                # Handle multi-line comments
                if '/*' in line:
                    in_multiline_comment = True
                if '*/' in line:
                    in_multiline_comment = False
                    continue
                
                # Skip comments and empty lines
                if (not line.startswith('//') and 
                    not in_multiline_comment and 
                    not line.startswith('/*')):
                    sloc += 1
        
        return sloc
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return 0

def count_sloc_for_files(files, search_dir='.'):
    """Count SLOC for each file in the list."""
    results = []
    
    for filename in files:
        # Check if the filename has a prefix (contains underscore)
        if '_' in filename:
            prefix = filename.split('_')[0]
            actual_filename = filename[len(prefix)+1:]  # +1 for the underscore
            
            # Look for the file in the directory with the prefix
            prefix_dir = os.path.join(search_dir, prefix)
            if os.path.exists(prefix_dir):
                found = False
                for root, _, filenames in os.walk(prefix_dir):
                    if actual_filename in filenames:
                        file_path = os.path.join(root, actual_filename)
                        # Use our internal SLOC counting function instead of external command
                        sloc_count = count_sloc_for_file(file_path)
                        results.append((file_path, filename, sloc_count))
                        found = True
                        break
                
                if not found:
                    results.append(("Not found", filename, 0))
        else:
            # For files without prefix, search in all directories
            found = False
            for root, _, filenames in os.walk(search_dir):
                if filename in filenames:
                    file_path = os.path.join(root, filename)
                    # Use our internal SLOC counting function instead of external command
                    sloc_count = count_sloc_for_file(file_path)
                    results.append((file_path, filename, sloc_count))
                    found = True
                    break
            
            # If file not found, record it with 0 SLOC
            if not found:
                results.append(("Not found", filename, 0))
    
    return results

def write_csv(results, output_file='sloc_count.csv'):
    """Write the parsed results to a CSV file."""
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Filename', 'SLOC'])  # Updated header
        for result in results:
            writer.writerow([result[1], result[2]])  # Only write filename and SLOC
    
    print(f"Results written to {output_file}")

def main():
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python sloc_to_csv.py <file_list.csv> [output_file.csv] [search_directory]")
        sys.exit(1)
    
    file_list_csv = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'sloc_count.csv'
    search_dir = sys.argv[3] if len(sys.argv) > 3 else '.'
    
    # Read the list of files from the CSV
    files = read_file_list(file_list_csv)
    
    # Count SLOC for each file
    results = count_sloc_for_files(files, search_dir)
    
    # Write results to CSV
    write_csv(results, output_file)

if __name__ == "__main__":
    main()

#sample command : python3 sloc_to_csv.py duplicate_files_report.csv sloc_results.csv .
