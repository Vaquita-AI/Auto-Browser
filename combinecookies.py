import os
import json
import random
from datetime import datetime

def combine_cookies(cookie_directory, combined_filename_prefix="combined_cookies", words_to_exclude=None, num_files_to_select=None):
    if words_to_exclude is None:
        words_to_exclude = []

    combined_cookies = []

    # Get all cookie files in the directory
    cookie_files = [
        filename for filename in os.listdir(cookie_directory)
        if filename.endswith('_cookies.json') and not filename.startswith(combined_filename_prefix)
    ]

    # If num_files_to_select is specified, randomly select that number of files
    if num_files_to_select is not None and num_files_to_select < len(cookie_files):
        cookie_files = random.sample(cookie_files, num_files_to_select)

    # Iterate over the selected cookie files
    for filename in cookie_files:
        filepath = os.path.join(cookie_directory, filename)
        with open(filepath, 'r') as file:
            cookies = json.load(file)

            # Filter out cookies whose domain contains any of the words to exclude
            filtered_cookies = [
                cookie for cookie in cookies
                if not any(word in cookie.get('domain', '') for word in words_to_exclude)
            ]

            combined_cookies.extend(filtered_cookies)

    # Generate a unique filename using the current timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    combined_filename = f"{combined_filename_prefix}_{timestamp}.json"
    combined_filepath = os.path.join(cookie_directory, combined_filename)

    # Save the combined cookies to a new file
    with open(combined_filepath, 'w') as combined_file:
        json.dump(combined_cookies, combined_file)

    print(f"------------------- Combined cookies saved to {combined_filepath} -----------")

    # Delete all original cookie files in the directory except the combined cookie files
    """
    for filename in os.listdir(cookie_directory):
        if filename.endswith('_cookies.json') and not filename.startswith(combined_filename_prefix):
            filepath = os.path.join(cookie_directory, filename)
            os.remove(filepath)
            print(f"Deleted {filepath}")
    """

# Combine the cookies with the option to select a random subset of files
combine_cookies(
    cookie_directory=r"PLACEHOLDER_PATH",
    words_to_exclude=["google", "amazon"],
    num_files_to_select=200  # Change this number to select a different number of files
)