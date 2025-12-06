import re

def extract_links(input_file, output_file):
    """
    Reads a text file, extracts http/https links, and saves them to an output file.
    """
    # 1. Define the Regular Expression pattern for URLs
    # This pattern looks for http or https, followed by non-whitespace characters
    url_pattern = r'https?://\S+'

    try:
        # 2. Open and read the input file
        with open(input_file, 'r', encoding='utf-8') as file:
            content = file.read()

        # 3. Find all matches in the content
        links = re.findall(url_pattern, content)

        # 4. Clean up links (optional but recommended)
        # Sometimes a link at the end of a sentence includes the period or comma.
        # This removes trailing punctuation.
        cleaned_links = [link.rstrip('.,;)"\'') for link in links]

        # 5. Write the links to the output file
        if cleaned_links:
            with open(output_file, 'w', encoding='utf-8') as file:
                for link in cleaned_links:
                    file.write(link + '\n')
            
            print(f"Success! Found {len(cleaned_links)} links.")
            print(f"Links have been saved to: {output_file}")
        else:
            print("No links were found in the file.")

    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# --- Configuration ---
# Change 'data.txt' to the name of your actual text file
input_filename = 'urls_to_fetch.txt' 
output_filename = 'links_only.txt'

if __name__ == "__main__":
    extract_links(input_filename, output_filename)