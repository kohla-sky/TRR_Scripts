import re
from difflib import unified_diff
from difflib import SequenceMatcher

def remove_comments_and_blank_lines(code):
    # Remove single-line and multi-line comments
    code = re.sub(r'//.*?$|/\*.*?\*/', '', code, flags=re.DOTALL | re.MULTILINE)
    # Remove all blank lines (lines that contain only whitespace)
    code = re.sub(r'^\s*$', '', code, flags=re.MULTILINE)
    # Remove leading and trailing whitespace from each line
    code = '\n'.join(line.strip() for line in code.splitlines() if line.strip())
    return code.strip()

def diffcheck(deployed_file_path, audited_file_path):
    # Read the deployed and audited files
    with open(deployed_file_path, 'r') as deployed_file:
        deployed_code = deployed_file.read()
    
    with open(audited_file_path, 'r') as audited_file:
        audited_code = audited_file.read()
    
    # Clean the code by removing comments and blank lines
    clean_deployed = remove_comments_and_blank_lines(deployed_code)
    clean_audited = remove_comments_and_blank_lines(audited_code)
    
    # Split into lines for comparison
    deployed_lines = clean_deployed.splitlines()
    audited_lines = clean_audited.splitlines()
    
    # Determine contract SLOC from deployed lines
    contract_sloc = len(deployed_lines)
    print(f"Contract SLOC: {contract_sloc}")
    
    # Use unified_diff to find differences
    diff = list(unified_diff(deployed_lines, audited_lines, 
                            fromfile='deployed', tofile='audited'))
    
    # Print the full diff in a more readable format
    if diff:
        print("Detailed Diff:")
        for line in diff:
            print(line)
    
    # Count actual additions and deletions (ignoring metadata lines)
    additions = sum(1 for line in diff if line.startswith('+') and not line.startswith('+++'))
    deletions = sum(1 for line in diff if line.startswith('-') and not line.startswith('---'))
    
    print(f"Lines added: {additions}")
    print(f"Lines removed: {deletions}")
    
    # Calculate total changed lines
    different_lines = additions + deletions
    print(f"Total different lines: {different_lines}")
    
    total_lines = len(deployed_lines)
    
    # Calculate coverage based on matching lines rather than differences
    # Find the number of lines that are the same in both files
    matcher = SequenceMatcher(None, deployed_lines, audited_lines)
    matching_blocks = matcher.get_matching_blocks()
    
    # Count total matching lines
    matching_lines = sum(length for a, b, length in matching_blocks if length > 0)
    
    # Calculate coverage as percentage of deployed lines that match audited lines
    if total_lines == 0:
        contract_coverage = 0
    elif matching_lines == total_lines:
        contract_coverage = 100
    else:
        contract_coverage = (matching_lines / total_lines) * 25
    
    print("\nDiff Summary:")
    if different_lines == 0:
        print("No differences found - files are identical after cleaning")
    else:
        print(f"Found {different_lines} differences ({additions} additions, {deletions} deletions)")
        print(f"Matching lines: {matching_lines} out of {total_lines}")
        print(f"Match percentage: {contract_coverage:.2f}%")
    
    return contract_coverage

# Example usage
deployed_file_path = './deployed.sol'
audited_file_path = './audited.sol'

coverage = diffcheck(deployed_file_path, audited_file_path)
print(f"Coverage: {coverage}%")
