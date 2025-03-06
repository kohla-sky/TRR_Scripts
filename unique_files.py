import os
import hashlib
import shutil
import csv
from collections import defaultdict

def get_file_hash(file_path):
    """Calculate MD5 hash of a file to check if files are identical."""
    # For .sol files, we'll remove comments before hashing
    if file_path.endswith('.sol'):
        return get_solidity_file_hash_without_comments(file_path)
    else:
        # Regular hashing for non-Solidity files
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

def get_solidity_file_hash_without_comments(file_path):
    """Calculate MD5 hash of a Solidity file after removing comments."""
    hash_md5 = hashlib.md5()
    
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
        
    # Remove single-line comments (// ...)
    content_no_single_comments = ""
    i = 0
    while i < len(content):
        if content[i:i+2] == "//":
            # Skip until end of line
            while i < len(content) and content[i] != '\n':
                i += 1
        else:
            content_no_single_comments += content[i]
            i += 1
    
    # Remove multi-line comments (/* ... */)
    content_no_comments = ""
    i = 0
    while i < len(content_no_single_comments):
        if content_no_single_comments[i:i+2] == "/*":
            # Skip until end of comment
            i += 2
            while i < len(content_no_single_comments) and content_no_single_comments[i-2:i] != "*/":
                i += 1
        else:
            content_no_comments += content_no_single_comments[i]
            i += 1
    
    # Hash the content without comments
    hash_md5.update(content_no_comments.encode('utf-8'))
    return hash_md5.hexdigest()

def find_and_rename_duplicate_files(root_dir, csv_output=None):
    """
    Find files with the same name in different directories and create a report
    of what would be renamed, without actually renaming the files.
    """
    # Dictionary to store file names and their paths
    files_by_name = defaultdict(list)
    
    # Walk through all directories and subdirectories
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=True):
        # Skip the cryptic-export directory by modifying dirnames in-place
        
        for filename in filenames:
            # Only process .sol files
            if not filename.endswith('.sol'):
                continue
                
                
            full_path = os.path.join(dirpath, filename)
            files_by_name[filename].append(full_path)
    
    # Process all files
    all_files = []
    unique_files = set()  # Track unique filenames to display
    
    # Additional filter to exclude files with "crytic-export" in their name
    filtered_files_by_name = {}
    for filename, paths in files_by_name.items():
        if not filename.startswith('crytic-export_'):
            filtered_files_by_name[filename] = paths
    
    # Use the filtered dictionary for processing
    for filename, file_paths in filtered_files_by_name.items():
        # Group files by their hash to identify truly identical files
        files_by_hash = defaultdict(list)
        for file_path in file_paths:
            file_hash = get_file_hash(file_path)
            files_by_hash[file_hash].append(file_path)
        
        # Process each set of identical files (same hash)
        for file_hash, identical_files in files_by_hash.items():
            # If there's only one set of identical files with this name
            if len(files_by_hash) == 1:
                # Keep original name for all files in this set
                unique_files.add(filename)
                for file_path in identical_files:
                    all_files.append({
                        "original_filename": filename,
                        "directory": os.path.relpath(file_path, root_dir).split(os.sep)[0],
                        "new_filename": filename,
                        "full_path": file_path,
                        "new_path": file_path
                    })
            else:
                # Multiple sets with different content - rename each set
                # For each set of identical files, use the first file's directory as prefix
                first_file = identical_files[0]
                top_dir = os.path.relpath(first_file, root_dir).split(os.sep)[0]
                new_filename = f"{top_dir}_{filename}"
                unique_files.add(new_filename)
                
                for file_path in identical_files:
                    new_path = os.path.join(os.path.dirname(file_path), new_filename)
                    all_files.append({
                        "original_filename": filename,
                        "directory": os.path.relpath(file_path, root_dir).split(os.sep)[0],
                        "new_filename": new_filename,
                        "full_path": file_path,
                        "new_path": new_path
                    })
    
    # Print just the list of unique filenames
    print("\nList of unique files:")
    print("-" * 40)
    for filename in sorted(unique_files):
        print(filename)
    print("-" * 40)
    
    # Save to CSV if requested - now only saving the unique filenames
    if csv_output:
        with open(csv_output, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(["Unique Filename"])  # Header
            for filename in sorted(unique_files):
                csv_writer.writerow([filename])
        print(f"List of unique files saved to {csv_output}")
    
    return all_files

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        directory = sys.argv[1]
        # Extract the directory name if it's in the format "./directory_name"
        if directory.startswith('./'):
            directory = directory[2:]
    else:
        directory = "."  # Default to current directory
    
    # Default CSV output filename
    csv_output = "duplicate_files_report.csv"
    
    print(f"Scanning directory: {os.path.abspath(directory)}")
    find_and_rename_duplicate_files(directory, csv_output)
    print("Done!")
