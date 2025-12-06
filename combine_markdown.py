import os
import logging

# --- Configuration ---
# The directory containing the .md files you want to combine.
SOURCE_DIR = "processed_content"

# The name of the final combined markdown file.
OUTPUT_FILE = "combined_content/unified_content.md"

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def combine_markdown_files():
    """
    Finds all .md files in the SOURCE_DIR, combines them into a single
    .md file, and adds separators with source filenames.
    """
    if not os.path.isdir(SOURCE_DIR):
        logging.error(f"Source directory '{SOURCE_DIR}' not found. Please check the path.")
        return

    # Get a sorted list of .md files to ensure a consistent order every time
    try:
        markdown_files = sorted([f for f in os.listdir(SOURCE_DIR) if f.endswith('.md')])
    except FileNotFoundError:
        logging.error(f"Source directory '{SOURCE_DIR}' could not be accessed.")
        return
    
    if not markdown_files:
        logging.warning(f"No .md files were found in '{SOURCE_DIR}'. The output file will not be created.")
        return

    logging.info(f"Found {len(markdown_files)} markdown files to combine into '{OUTPUT_FILE}'.")

    # Open the output file in write mode
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as outfile:
            for index, filename in enumerate(markdown_files):
                filepath = os.path.join(SOURCE_DIR, filename)
                
                logging.info(f"Adding content from: {filename}")
                
                # Add a separator before each file except the very first one
                if index > 0:
                    outfile.write(f"\n\n---\n\n")
                
                # Add a header indicating the source file
                outfile.write(f"## Source File: {filename}\n\n")
                
                # Read the content of the source file and write it to the output file
                with open(filepath, 'r', encoding='utf-8') as infile:
                    content = infile.read()
                    outfile.write(content)
            
        logging.info("--- Combination Complete ---")
        logging.info(f"All files have been successfully combined into '{OUTPUT_FILE}'.")

    except IOError as e:
        logging.error(f"An error occurred while writing to the file: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    combine_markdown_files()