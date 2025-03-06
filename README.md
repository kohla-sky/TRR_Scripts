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
- `requests` library: You can install it using `pip install requests`.

### Usage

1. **Command-Line Arguments**: The script can be run with or without command-line arguments.

   - **With a Contract Name**: If you provide a contract name as an argument, the script will fetch and save the source code for that specific contract.
     ```bash
     python get_code.py <contract_name>
     ```
     Replace `<contract_name>` with the desired contract name from the predefined list in the script.

   - **Without a Contract Name**: If no argument is provided, the script will process all contracts listed in the `contract_addresses` dictionary.
     ```bash
     python get_code.py
     ```

2. **API Key**: The script uses a hardcoded API key for Etherscan. Ensure that the key is valid and has the necessary permissions to access the API.

### Expected Output

- **Single-File Contracts**: The source code will be saved as a `.sol` file named after the contract.
- **Multi-File Contracts**: The source code will be saved in a directory named after the contract, with each file saved in its respective path as defined in the contract's source.


- If the contract address is not found in the dictionary, the script will print an error message and exit.
- If the Etherscan API returns an error, the script will print the error message and exit.
