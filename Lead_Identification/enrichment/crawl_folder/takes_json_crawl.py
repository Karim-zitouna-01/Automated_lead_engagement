import os
import re

from enrichment.crawl_folder.crawl import run_crawl_pipeline

def sanitize_filename(name: str) -> str:
    """Sanitize filename to remove unsafe characters."""
    return re.sub(r'[\\/*?:"<>|]', "_", name)



###################

def crawl_company_data(companies: list, api_key: str):
    """
    For each company in the list, crawl all relevant URLs
    and write the result to a text file named after the company.
    
    Parameters:
    - companies: list of company dictionaries.
    - crawl_url_func: function that takes a URL and returns crawled text.
    """
    output_dir = "crawled_data"
    os.makedirs(output_dir, exist_ok=True)

    for company in companies:
        company_name = sanitize_filename(company["company_name"])
        file_path = os.path.join(output_dir, f"{company_name}.txt")

        with open(file_path, "a", encoding="utf-8") as file:
            file.write(f"Company: {company_name}\n\n")

            if company["relevant_urls"]:
                for url in company["relevant_urls"]:
                    try:
                        content = run_crawl_pipeline(url,api_key)
                        file.write(f"URL: {url}\n")
                        file.write(f"Content:\n{content}\n\n")
                    except Exception as e:
                        file.write(f"URL: {url}\nFailed to crawl: {e}\n\n")
            else:
                file.write("No relevant URLs provided.\n")

###################






# Load your JSON list of companies (example below)
# companies = [
#     {
#         "company_name": "InnovaTech Solutions",
#         "summary": "...",
#         "description": "...",
#         "reason_for_match": "...",
#         "key_personal": [],
#         "relevant_urls": ["https://www.talan.com/global/en", "https://www.ey.com/en_tn"]
#     },
#     {
#         "company_name": "GreenEdge Energy",
#         "summary": "...",
#         "description": "...",
#         "reason_for_match": None,
#         "key_personal": [],
#         "relevant_urls": []
#     }
# ]

# crawl_company_data(companies, api_key)
