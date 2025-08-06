import re
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
import asyncio
from crawl4ai import CrawlerRunConfig, AsyncWebCrawler
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
import re
import google.generativeai as genai



def clean_text(raw_text: str) -> str:
    lines = raw_text.splitlines()
    return "\n".join(line for line in lines if not is_noise_line(line))


def is_noise_line(line: str) -> bool:
    return bool(re.search(r"\[.*?\]", line.strip()))

async def async_crawl_and_clean(url: str) -> str:
    config = CrawlerRunConfig(
        deep_crawl_strategy=BFSDeepCrawlStrategy(max_depth=1, max_pages=1, include_external=False),
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


def summarize_with_gemini(text: str, api_key: str) -> str:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
    "gemini-2.5-flash-lite",
    generation_config=genai.types.GenerationConfig(
        temperature=0.4,

        max_output_tokens=1024,
        stop_sequences=None
    )
)

    prompt = (
        f'''Carefully analyze the following cleaned website content and extract all useful, business-relevant information directly mentioned or implied in the text.
Your summary should be:

Factual, based only on the given content (do not assume or invent).

Well-structured, using clear paragraphs and concise language.

Rich in detail, capturing all key elements if they exist such as:

The company’s name and brand identity

Core mission and strategic vision

Primary services, technologies, or solutions offered

Industries or markets served

Any mentioned global presence, partnerships, or clients

Relevant values, approach, or innovation strategy

Any noted events, initiatives, or unique value propositions

Make sure the output reads like a professional, high-quality executive summary and fully utilizes the information available.

Avoid repeating the same phrases or sentences. Keep the summary focused and well-structured.

Website Content:

{text}
'''
    )

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Gemini API Error: {e}"


def run_crawl_pipeline(url: str, gemini_api_key: str) -> str:
    print(f"🔍 Starting crawl for {url}...")
    cleaned = crawl_and_clean(url)
    print("cleaned cbon")
    print(cleaned)
    return summarize_with_gemini(cleaned, gemini_api_key)

