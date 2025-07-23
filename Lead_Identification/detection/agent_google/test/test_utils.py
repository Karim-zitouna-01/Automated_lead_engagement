import sys
import os
import json

# Ensure the parent directory is in the path so we can import utils.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from detection.agent_google import utils

# Sample ICP for testing
sample_icp = {
    "service": "Data & AI Consulting",
    "ideal_customer_profile": {
        "industry": ["Banking"],
        "company_size": {
            "employees": {"min": 1000},
            "annual_revenue_eur": {"min": 200000000}
        },
        "geography": ["France"],
        "technology_maturity": "Intermediate to Advanced",
        "existing_stack": ["Azure", "Snowflake"],
        "key_decision_makers": ["Chief Data Officer (CDO)"],
        "pain_points": ["Data silos between business units"],
        "buying_motivation": ["Need to operationalize AI across departments"],
        "budget": {
            "consulting_project_range_eur": {
                "min": 300000,
                "max": 3000000
            }
        },
        "business_goals": [
            "Accelerate digital roadmap"
        ],
        "sales_cycle_duration": "3 to 6 months",
        "preferred_engagement_model": [
            "Phased roadmap execution (audit → roadmap → implementation)"
        ]
    }
}


def test_generate_queries():
    print(" testing queries generation \n[🔍] Generating Search Queries...\n")
    queries = utils.generate_search_queries(sample_icp)
    print("\n[✅] Generated Queries:")
    for q in queries:
        print("-", q)
    assert isinstance(queries, list) and len(queries) > 0


def test_search_duckduckgo():
    print("testing DuckDuckGo search \n[🔍] Searching DuckDuckGo...\n")
    results = utils.search_duckduckgo("site:linkedin.com/in \"Chief Data Officer\" AND Banking AND France", top_k=3)
    print("\n[✅] DuckDuckGo Search URLs:")
    for url in results:
        print("-", url)
    assert isinstance(results, list)


def test_crawl_and_clean():
    print("testing crawling and cleaning \n[🌐] Crawling and Cleaning Content...\n")
    # Use a lightweight example URL to avoid hitting complex pages
    url = "https://www.talan.com/en/"
    content = utils.crawl_and_clean(url)
    print("\n[✅] Crawled & Cleaned Content:")
    print(content[:500], "...\n")  # Print first 500 chars
    assert isinstance(content, str)


def test_summarize_page():
    print("testing page summarization \n[📝] Summarizing Page Content...\n")
    dummy_content = """
    Talan is a consulting firm specializing in innovation and transformation through technology. With experience in banking and data transformation projects using Snowflake and Azure, they target large enterprises in France. CDOs and CIOs are among their clients.
    """
    summary = utils.summarize_page(dummy_content, sample_icp)
    print("\n[✅] Page Summary:")
    print(summary)
    assert "summary" in summary.lower()


if __name__ == "__main__":
    test_generate_queries()
    test_search_duckduckgo()
    test_crawl_and_clean()
    test_summarize_page()
