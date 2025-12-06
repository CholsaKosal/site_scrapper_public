import os
import logging

# --- Configuration ---
PROCESSED_DIR = "processed_content"
LINES_TO_REMOVE_FILE = "remove_lines.txt"
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def remove_lines_from_files():
    """
    Reads a list of exact lines from a configuration file and removes those
    lines from all .md files in the processed directory.
    """
    # 1. Load the set of lines to be removed for efficient lookup
    try:
        with open(LINES_TO_REMOVE_FILE, 'r', encoding='utf-8') as f:
            # Use a set for O(1) average time complexity checks
            lines_to_remove = {line.strip() for line in f if line.strip()}
    except FileNotFoundError:
        logging.error(f"Error: The file '{LINES_TO_REMOVE_FILE}' was not found.")
        logging.info("Please create this file and add the lines you want to remove, one per line.")
        return

    if not lines_to_remove:
        logging.warning(f"'{LINES_TO_REMOVE_FILE}' is empty. No lines will be removed.")
        return

    logging.info(f"Loaded {len(lines_to_remove)} unique lines to remove.")

    # 2. Get the list of files to process
    try:
        files_to_process = [f for f in os.listdir(PROCESSED_DIR) if f.endswith('.md')]
    except FileNotFoundError:
        logging.error(f"Error: The directory '{PROCESSED_DIR}' could not be found.")
        return

    logging.info(f"Checking {len(files_to_process)} files in '{PROCESSED_DIR}'...")

    # 3. Process each file
    modified_files_count = 0
    for filename in files_to_process:
        filepath = os.path.join(PROCESSED_DIR, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                original_lines = f.readlines()

            # Create a new list containing only the lines we want to keep
            kept_lines = [line for line in original_lines if line.strip() not in lines_to_remove]

            # If the number of lines has changed, the file needs to be updated
            if len(kept_lines) < len(original_lines):
                logging.info(f"Removing {len(original_lines) - len(kept_lines)} lines from '{filename}'.")
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.writelines(kept_lines)
                modified_files_count += 1
                
        except Exception as e:
            logging.error(f"Failed to process file {filepath}: {e}")

    logging.info("--- Line Removal Complete ---")
    logging.info(f"Total files modified: {modified_files_count}")

if __name__ == "__main__":
    remove_lines_from_files()