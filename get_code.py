import requests
import sys
import json
import os

def get_contract_address(contract_name=None):
    # Placeholder for contract addresses
    contract_addresses = {
        # "contract_name": "contract_address",
    }
    
    if contract_name is None:
        return contract_addresses
    
    return contract_addresses.get(contract_name)

def save_contract_source(contract_address, file_name, api_key):
    url = f"https://api.etherscan.io/api?module=contract&action=getsourcecode&address={contract_address}&apikey={api_key}"
    response = requests.get(url).json()
    
    if response["status"] != "1":
        print(f"Error: {response['message']}")
        sys.exit(1)
    
    source_code = response["result"][0]["SourceCode"]
    
    if source_code.startswith("{") and source_code.endswith("}"):
        try:
            if source_code.startswith("{{") and source_code.endswith("}}"):
                source_code = source_code[1:-1]
            
            source_json = json.loads(source_code)
            
            if "sources" in source_json:
                base_dir = file_name
                os.makedirs(base_dir, exist_ok=True)
                
                for file_path, content in source_json["sources"].items():
                    full_path = os.path.join(base_dir, file_path)
                    dir_name = os.path.dirname(full_path)
                    os.makedirs(dir_name, exist_ok=True)
                    
                    with open(full_path, "w") as file:
                        file.write(content["content"])
                    
                    print(f"Saved: {full_path}")
                return
        except json.JSONDecodeError:
            pass
    
    with open(f"{file_name}.sol", "w") as file:
        file.write(source_code)
    
    print(f"Contract saved as {file_name}.sol")

# Placeholder for API key
api_key = "YOUR_API_KEY"

if len(sys.argv) > 1:
    contract_name = sys.argv[1]
    contract_address = get_contract_address(contract_name)
    if contract_address:
        file_name = contract_name
        save_contract_source(contract_address, file_name, api_key)
    else:
        print(f"Contract '{contract_name}' not found.")
        sys.exit(1)
else:
    all_contracts = get_contract_address()
    
    for contract_name, contract_address in all_contracts.items():
        print(f"Processing contract: {contract_name}")
        file_name = contract_name
        save_contract_source(contract_address, file_name, api_key)
        print(f"Completed processing {contract_name}\n")
