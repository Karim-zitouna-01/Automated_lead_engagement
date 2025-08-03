import os
import json
import re


def sanitize_filename(name: str) -> str:
    """Sanitize filename to remove unsafe characters."""
    return re.sub(r'[\\/*?:"<>|]', "_", name)

def save_company_jsons(companies, output_dir = "crawled_data"):
    os.makedirs(output_dir, exist_ok=True)

    for company in companies:
        company_name = sanitize_filename(company["company_name"])
        file_path = os.path.join(output_dir, f"{company_name}.txt")

        # Open in append mode only if file exists, else create
        with open(file_path, "a", encoding="utf-8") as file:
            file.write(json.dumps(company, indent=2, ensure_ascii=False))
            file.write("\n\n")  # Add space between entries



################

# companies=[
#   {
#     "company_name": "Talan Group",
#     "summary": "Talan Group is a global technology and consulting firm that accelerates digital transformation for businesses and public institutions through innovation, technology, and data.",
#     "description": "For over 20 years, Talan Group has guided enterprises and public institutions in transformation and innovation projects worldwide. Present on four continents in 20 countries with over 7,000 professionals, the firm focuses on technology-driven services such as artificial intelligence, data intelligence, blockchain, and IoT. Armed with a dedicated research and innovation center, Talan emphasizes a positive innovation philosophy, aiming to use technology responsibly to enhance human potential while driving business growth.",
#     "reason_for_match": "Talan Group is relevant to contexts involving digital consulting and enterprise innovation. Its expertise in technology and data-driven transformations makes it a strong partner for projects in digital transformation, cloud modernization, and AI-driven solutions.",
#     "key_personal": [
#       {
#         "name": "Philippe Cassoulat",
#         "role": "Co-founder and CEO"
#       },
#       {
#         "name": "Mehdi Houas",
#         "role": "Co-founder and President"
#       }
#     ],
#     "relevant_urls": [
#       "https://www.talan.com",

#     ]
#   },
#   {
#     "company_name": "Ernst & Young",
#     "summary": "EY (Ernst & Young) is a multinational professional services network, known as one of the Big Four accounting firms, providing audit, tax, consulting, and advisory services worldwide.",
#     "description": "EY operates as a global network of member firms in more than 150 countries with nearly 400,000 employees. It offers assurance (audit), tax advisory, consulting, strategy and transactions, and advisory services, often focusing on technology areas such as cybersecurity, cloud, and AI. According to its stated purpose, EY aims to \"build a better working world\" by creating long-term value for clients, people, and society, and by helping build trust in the capital markets.",
#     "reason_for_match": "EY is relevant to contexts involving finance, risk, or large-scale transformation. As a Big Four firm, it provides expertise in audit and financial services, and has extensive technology and management consulting capabilities. Companies tackling major digital transformation, regulatory compliance, or sustainability initiatives often engage EY for its global advisory and assurance expertise.",
#     "key_personal": [
#       {
#         "name": "Janet Truncale",
#         "role": "Global Chair and CEO (from July 2024)"
#       },
#       {
#         "name": "Jamie Miller",
#         "role": "Global CFO (from 2023)"
#       }
#     ],
#     "relevant_urls": [
#       "https://www.ey.com",
#     ]
#   }
# ]


# save_company_jsons(companies)