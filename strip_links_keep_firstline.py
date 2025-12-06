import os
import re
import logging

# --- Configuration ---
PROCESSED_DIR = "processed_content"
# Regex to find markdown links like [text](url)
MARKDOWN_LINK_PATTERN = re.compile(r'\[([^\]]*)\]\(([^)]*)\)')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def strip_links_from_files():
    """
    Iterates through all .md files in the processed directory, preserving the
    first line and removing markdown links from the rest of the content.
    """
    try:
        files_to_process = [f for f in os.listdir(PROCESSED_DIR) if f.endswith('.md')]
    except FileNotFoundError:
        logging.error(f"Error: The directory '{PROCESSED_DIR}' was not found.")
        return

    logging.info(f"Found {len(files_to_process)} files to process in '{PROCESSED_DIR}'.")
    
    processed_count = 0
    for filename in files_to_process:
        filepath = os.path.join(PROCESSED_DIR, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            if not lines:
                logging.warning(f"File '{filename}' is empty. Skipping.")
                continue

            # Preserve the first line and join the rest
            first_line = lines[0]
            remaining_content = "".join(lines[1:])
            
            # Use regex to replace the markdown link with just the link's text
            # The r'\1' refers to the first captured group: ([^\]]*) which is the text inside []
            cleaned_content = MARKDOWN_LINK_PATTERN.sub(r'\1', remaining_content)
            
            # Write the modified content back to the file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(first_line)
                f.write(cleaned_content)
            
            processed_count += 1
            logging.info(f"Stripped links from '{filename}'.")

        except Exception as e:
            logging.error(f"Could not process file {filepath}: {e}")

    logging.info("--- Link Stripping Complete ---")
    logging.info(f"Total files processed: {processed_count}")

if __name__ == "__main__":
    strip_links_from_files()