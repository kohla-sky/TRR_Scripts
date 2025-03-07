# Scripts

## get_code.py

### Overview

The `get_code.py` script is designed to retrieve and save the source code of Ethereum smart contracts from Etherscan. It uses the Etherscan API to fetch the source code of a specified contract by its address. The script can handle both single-file and multi-file contracts, saving them appropriately on your local machine.

### Features

- Retrieve contract source code using the Etherscan API.
- Save single-file contracts as `.sol` files.
- Save multi-file contracts in a structured directory format.
- Fetch all contracts listed in the script if no specific contract name is provided.

### Prerequisites

- Python 3.x
- `requests` library: You can install it using `pip3 install requests`.

### Usage

1. **Command-Line Arguments**: The script can be run with or without command-line arguments.

   - **With a Contract Name**: If you provide a contract name as an argument, the script will fetch and save the source code for that specific contract.
     ```bash
     python3 get_code.py <contract_name>
     ```
     Replace `<contract_name>` with the desired contract name from the predefined list in the script.

   - **Without a Contract Name**: If no argument is provided, the script will process all contracts listed in the `contract_addresses` dictionary.
     ```bash
     python3 get_code.py
     ```

2. **API Key**: The script uses a hardcoded API key for Etherscan. Ensure that the key is valid and has the necessary permissions to access the API.

### Expected Output

- **Single-File Contracts**: The source code will be saved as a `.sol` file named after the contract.
- **Multi-File Contracts**: The source code will be saved in a directory named after the contract, with each file saved in its respective path as defined in the contract's source.

## unique_files.py

The `unique_files.py` script is designed to identify and manage duplicate Solidity files within a specified directory. It calculates the MD5 hash of each file to determine if files are identical, even if they have the same name but different content.

### Features

- **Identify Duplicate Files**: Scans a directory to find files with the same name and checks if they are identical by comparing their MD5 hashes.
- **Rename Files**: Suggests renaming files with the same name but different content by prefixing the directory name to ensure uniqueness.
- **CSV Report**: Optionally generates a CSV report listing all unique filenames.

### Prerequisites

- Python 3.x
- Standard Python libraries: `os`, `hashlib`, `shutil`, `csv`, `collections`

### Usage

1. **Command-Line Execution**: Run the script from the command line, specifying the directory to scan.

   ```bash
   python3 unique_files.py <directory>
   ```

   Replace `<directory>` with the path to the directory you want to scan. If no directory is specified, the current directory is used by default.

2. **CSV Output**: By default, the script generates a CSV report named `duplicate_files_report.csv` in the current directory. This report lists all unique filenames identified during the scan.

### Expected Output

- **Unique Filenames**: The script prints a list of unique filenames to the console.
- **CSV Report**: If enabled, a CSV file is created, listing all unique filenames.

## sloc_to_csv.py

### Overview

The `sloc_to_csv.py` script counts the Source Lines of Code (SLOC) for a list of files and outputs the results to a CSV file. It's designed to work with a list of filenames provided in a CSV file, which makes it useful for batch processing and analyzing code metrics across multiple files or projects.

### Features

- Count SLOC for multiple files listed in a CSV input file
- Handle files with or without directory prefixes
- Skip comments and empty lines when counting SLOC
- Output results to a CSV file for further analysis
- Search for files recursively in specified directories

### Prerequisites

- Python 3.x
- Standard Python libraries: `re`, `csv`, `sys`, `os`

### Usage

bash
python3 sloc_to_csv.py <file_list.csv> [output_file.csv] [search_directory]

- `<file_list.csv>`: Required. A CSV file containing a list of filenames to process (first column).
- `[output_file.csv]`: Optional. The output CSV file name (default: `sloc_count.csv`).
- `[search_directory]`: Optional. The directory to search for files (default: current directory).

### Example

bash
python3 sloc_to_csv.py duplicate_files_report.csv sloc_results.csv .


This command will:
1. Read filenames from `duplicate_files_report.csv`
2. Search for these files in the current directory
3. Count SLOC for each file
4. Write the results to `sloc_results.csv`

### How It Works

1. The script reads a list of filenames from the input CSV file.
2. For each filename:
   - If the filename contains a prefix (e.g., `dir_file.sol`), it looks for `file.sol` in the `dir` directory.
   - Otherwise, it searches for the file in all subdirectories.
3. For each found file, it counts the SLOC by:
   - Skipping empty lines
   - Ignoring single-line comments (`//`)
   - Handling multi-line comments (`/* */`)
4. The results are written to the output CSV file with columns for filename and SLOC count.

### Notes

- Files not found will be included in the output with 0 SLOC.
- The script can also parse output from an external SLOC counting tool if provided via stdin or a file.
