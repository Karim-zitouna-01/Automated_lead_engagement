import os
import re

from enrichment.youtube_folder.yt import lanceYoutubeSearch

def sanitize_filename(name: str) -> str:
    """Sanitize filename to remove unsafe characters."""
    return re.sub(r'[\\/*?:"<>|]', "_", name)


#################

def append_youtube_results(companies: list,api_key: str,):
    """
    Appends YouTube search results to company text files in 'crawled_data'.
    Creates the file if it doesn't exist.
    """
    output_dir = "crawled_data"
    os.makedirs(output_dir, exist_ok=True)

    for company in companies:
        company_name = sanitize_filename(company["company_name"])
        print("Processing company:", company_name)
        file_path = os.path.join(output_dir, f"{company_name}.txt")

        try:
            yt_results = lanceYoutubeSearch(api_key,company["company_name"],company["company_name"])
        except Exception as e:
            yt_results = f"Failed to fetch YouTube results: {e}"

        with open(file_path, "a", encoding="utf-8") as file:
            file.write("\n--- YouTube Search Results ---\n")
            if isinstance(yt_results, list):
                for result in yt_results:
                    file.write(f"- {result}\n")
            else:
                file.write(f"{yt_results}\n")


