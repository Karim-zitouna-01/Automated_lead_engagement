from common.llms import call_gemini_flash, call_mistral
from ddgs import DDGS
import os
import re
import time
import asyncio
from crawl4ai import CrawlerRunConfig, AsyncWebCrawler
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
import json
import re

# utils.py



def generate_search_queries(icp: dict) -> list[str]:
    """
    Use an LLM to generate intelligent search queries based on the ICP.
    """
    try:
        prompt = f"""
You are an expert market researcher and lead generation specialist. Your goal is to generate highly effective and diverse search queries to identify companies and relevant content that perfectly match a given Ideal Customer Profile (ICP).

The ICP will be provided in a JSON format. Your task is to extract key attributes from this ICP and combine them intelligently to create search queries that would be used on a general-purpose search engine (like Google) or professional networks (like LinkedIn).

Focus on generating queries that uncover:
1.  **Companies** fitting the demographic, technographic, and geographic criteria.
2.  **News, articles, press releases, or reports** indicating the company is experiencing the specified pain points, pursuing the buying motivations/business goals, or has recently triggered a "buying trigger."
3.  **Content** published by the target audience or discussing their challenges/goals within their preferred channels (e.g., industry publications, analyst reports).

**Query Generation Guidelines:**
* Generate queries of varying specificity: some broad, some highly targeted.
* Combine 2-4 key ICP elements per query to ensure relevance (e.g., Industry + Pain Point + Technology Stack).
* Prioritize "Tier 1 Core Focus" industries but also include "Tier 2 Opportunistic Growth" in a smaller proportion of queries.
* Incorporate geographical terms where highly relevant, especially for Francophone Europe/Tunisia.
* Use keywords related to the "service" ("AI Consulting") in combination with other ICP elements.
* Think about how decision-makers (CIO, CFO, etc.) might phrase their challenges or interests.
* Include terms related to "buying triggers" to find companies actively looking.
* Suggest searches within "preferred channels" where applicable (e.g., "Gartner report [topic]").
* Avoid redundant queries. Aim for diversity in focus and keyword combinations.
* Prefix queries with search operators where beneficial (e.g., `site:linkedin.com` or `intitle:`), but sparingly.
* Generate queries for both English and French if the geography suggests it (Francophone Europe).

**output format**:
You MUST return only a valid Python list of 7 queries. Do not include any other text, explanation, or formatting outside of the list itself.


ICP (Ideal Customer Profile):
{json.dumps(icp, indent=2)}


"""

        llm_response = call_mistral(prompt=prompt, temperature=0.5, max_tokens=300)

        # Attempt to parse the response into a list
        queries = []
        for line in llm_response.splitlines():
            line = line.strip("-• \n")
            if line:
                queries.append(line)

        
        return queries

    except Exception as e:
        print(f"❌ Query generation failed: {e}")
        return []




def search_duckduckgo(query: str, top_k: int = 10) -> list[str]:
    print(f"\n🔍 [DuckDuckGo] Searching: {query}")
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=top_k):
                url = r.get("href") or r.get("url")
                if url:
                    results.append(url)
                if len(results) >= top_k:
                    break
        print(f"✅ Found URLs:\n" + "\n".join(results))
    except Exception as e:
        print(f"❌ Search failed: {e}")
    return results




def is_noise_line(line: str) -> bool:
    return bool(re.search(r"\[.*?\]", line.strip()))

def clean_text(raw_text: str) -> str:
    lines = raw_text.splitlines()
    return "\n".join(line for line in lines if not is_noise_line(line))

async def async_crawl_and_clean(url: str) -> str:
    config = CrawlerRunConfig(
        deep_crawl_strategy=BFSDeepCrawlStrategy(max_depth=1, max_pages=5, include_external=False),
        scraping_strategy=LXMLWebScrapingStrategy(),
        verbose=False,
    )

    cleaned_texts = []
    try:
        async with AsyncWebCrawler() as crawler:
            results = await crawler.arun(url=url, config=config)
            for result in results:
                raw = result.markdown or ""
                cleaned = clean_text(raw)
                cleaned_texts.append(cleaned)
    except Exception as e:
        print(f"❌ Crawling failed for {url}: {e}")
    return "\n\n".join(cleaned_texts)

def crawl_and_clean(url: str) -> str:
    return asyncio.run(async_crawl_and_clean(url))

 # or mistral, gemini, etc.


 

def extract_json_from_response(response_text: str) -> str:
    """
    Extracts and returns the first JSON-like object from a string by capturing the text between the first pair of curly braces.
    If no braces found, returns empty string.
    """
    match = re.search(r'\{.*?\}', response_text, re.DOTALL)
    return match.group(0).strip() if match else ""




def summarize_page(content: str, icp) -> str:
    if not content.strip():
        return "[Empty page content]"
    
    summary_prompt = f"""
You are an assistant helping evaluate if a web page matches an Ideal Customer Profile (ICP).

1. Read the following content.
2. If you find a match, extract:
   - The company name
   - A short summary of the page
   - A reason why the company seems to match the ICP
   - A list of key personnel names with their roles, if any are mentioned
   - A list of relevant urls (like LinkedIn profiles, company websites, etc.) if any are mentioned

If the content clearly does **not** match the ICP, return `"reason_for_match": null`.

ICP:
{json.dumps(icp, indent=2)}

Content:
\"\"\"
{content}
\"\"\"

Return the result strictly in JSON format, with the following fields:
- company_name: str
- summary: str
- reason_for_match: str or null
- key_personal: list of str (can be empty)
- relevant_urls: list of str (can be empty)
"""


    try:
        summary= call_gemini_flash(
            prompt=content,
            system_prompt=summary_prompt,
            temperature=0.3,
            max_tokens=300
        )
        return extract_json_from_response(summary)
    except Exception as e:
        print(f"❌ Summarization failed: {e}")
        return "[Summary generation failed]"


