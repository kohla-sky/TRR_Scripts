import re
import csv
import sys
import os

def remove_comments(lines):
    cleaned_lines = []
    block_comment = False

    for line in lines:
        # Detect the start and end of block comments
        if "/*" in line:
            block_comment = True
        if "*/" in line:
            block_comment = False
            continue  # Skip this line as it closes a comment

        if block_comment:
            continue  # Ignore lines inside block comments

        # Remove single-line comments (//...)
        line = re.sub(r"//.*", "", line).strip()

        if line:  # Avoid adding empty lines
            cleaned_lines.append(line)

    return cleaned_lines

def count_decision_points(cleaned_lines):
    """
    Count occurrences of decision points
    """
    # Keywords indicating decision points
    decision_patterns = [r"\bif\b", r"\belse\b", r"\bwhile\s*\(", r"\bfor\s*\(",
                         r"\brequire\s*\(", r"\bassert\s*\(", r"\brevert\b"]
    count = 0
    
    # Count occurrences of decision-making statements
    for line in cleaned_lines:
        if any(re.search(pattern, line) for pattern in decision_patterns):
            count += 1
            
    return count

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

def count_decisions_for_file(file_path):
    """Count decision points for a single file."""
    if not os.path.exists(file_path):
        return 0
        
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            
        # Clean comments
        cleaned_lines = remove_comments(lines)
        
        # Count decision points
        return count_decision_points(cleaned_lines)
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return 0

def count_decisions_for_files(files, search_dir='.'):
    """Count decision points for each file in the list."""
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
                        decision_count = count_decisions_for_file(file_path)
                        results.append((file_path, filename, decision_count))
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
                    decision_count = count_decisions_for_file(file_path)
                    results.append((file_path, filename, decision_count))
                    found = True
                    break
            
            # If file not found, record it with 0 decision points
            if not found:
                results.append(("Not found", filename, 0))
    
    return results

def write_csv(results, output_file='decision_points.csv'):
    """Write the parsed results to a CSV file."""
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Filename', 'Decision Points'])
        for result in results:
            writer.writerow([result[1], result[2]])  # Only write filename and decision points
    
    print(f"Results written to {output_file}")

def main():
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python decisions_to_csv.py <file_list.csv> [output_file.csv] [search_directory]")
        sys.exit(1)
    
    file_list_csv = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'decision_points.csv'
    search_dir = sys.argv[3] if len(sys.argv) > 3 else '.'
    
    # Read the list of files from the CSV
    files = read_file_list(file_list_csv)
    
    # Count decision points for each file
    results = count_decisions_for_files(files, search_dir)
    
    # Write results to CSV
    write_csv(results, output_file)

if __name__ == "__main__":
    main()

#sample command : python3 decisions_to_csv.py duplicate_files_report.csv decision_results.csv .
