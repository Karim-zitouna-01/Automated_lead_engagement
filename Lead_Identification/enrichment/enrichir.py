
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
import os
from Lead_Identification.enrichment.savetocloud import saveContentToCloudinary
from Lead_Identification.enrichment.json_putter import save_company_jsons
from Lead_Identification.enrichment.crawl_folder.takes_json_crawl import crawl_company_data
from Lead_Identification.enrichment.youtube_folder.takes_json_yt import append_youtube_results
from dotenv import load_dotenv
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

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




def enrich(companies):
    save_company_jsons(companies)
    crawl_company_data(companies,GEMINI_API_KEY)
    append_youtube_results(companies,GEMINI_API_KEY)
    urls = saveContentToCloudinary()
    
    return urls
