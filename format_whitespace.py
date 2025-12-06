import os
import logging

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def format_file_whitespace(filepath):
    """
    Removes leading/trailing whitespace from each line and deletes
    completely blank lines from the specified file.

    Args:
        filepath (str): The path to the file to be formatted.
    """
    if not os.path.exists(filepath):
        logging.error(f"Error: The file '{filepath}' does not exist. Please check the path in the script.")
        return

    try:
        # Read all lines from the file into memory first
        with open(filepath, 'r', encoding='utf-8') as f:
            original_lines = f.readlines()

        logging.info(f"Read {len(original_lines)} lines from '{filepath}'.")

        # Process lines: strip them and keep only the non-empty ones.
        cleaned_lines = []
        for line in original_lines:
            stripped_line = line.strip()
            if stripped_line:  # This condition filters out blank lines
                cleaned_lines.append(stripped_line + '\n') # Add the cleaned line back with a single newline

        # Write the cleaned content back to the same file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(cleaned_lines)

        logging.info(f"Successfully formatted whitespace in '{filepath}'.")
        logging.info(f"Original line count: {len(original_lines)}, New line count: {len(cleaned_lines)}.")

    except Exception as e:
        logging.error(f"An unexpected error occurred while processing {filepath}: {e}")

if __name__ == "__main__":
    # --- Specify the file you want to clean here ---
    target_file = "combined_content/unified_content.md"  # <--- EDIT THIS LINE WITH YOUR FILE PATH

    logging.info(f"Starting whitespace formatting for: {target_file}")
    format_file_whitespace(target_file)