from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_loaders.firecrawl import FireCrawlLoader
import asyncio  # Import asyncio to run the async function
import re


async def scrape_website_async(page_url, WebpageLoader):
    # lazy loading is performed according to the recommendation of the langchain
    # tutorial for greater efficiency
    if WebpageLoader == "free":
        loader = WebBaseLoader(
            web_paths=[page_url],
            header_template={"User_Agent": "MyWebScraper/1.0"}
        )
        docs = []
        async for doc in loader.alazy_load():
            docs.append(doc)
        assert len(docs) == 1
        return docs[0].page_content
    else:
        loader = FireCrawlLoader(
            api_key="fc-6b28cf779ae64356a30be1a4e7726faa", url=page_url, mode="scrape"
        )
        docs = []
        # Since FireCrawlLoader is synchronous, we can use a normal loop here
        for doc in loader.lazy_load():
            docs.append(doc)
        return docs[0].page_content


def scrape_website(url, WebpageLoader='free'):
    # Use asyncio.run to handle the event loop for async functions
    doc = asyncio.run(scrape_website_async(url, WebpageLoader))

    # Clean the text based on the loader type
    if WebpageLoader == 'free':
        cleaned_text = re.sub(r'\s+', ' ', doc.strip())
    else:
        cleaned_text = doc.strip()

    return cleaned_text

