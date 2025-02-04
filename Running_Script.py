import asyncio
import httpx
from selectolax.parser import HTMLParser
from urllib.parse import urljoin
import pandas as pd

async def fetch(client, url, retries=3):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    for attempt in range(retries):
        try:
            resp = await client.get(url, headers=headers, follow_redirects=True)
            resp.raise_for_status()
            return HTMLParser(resp.text)
        except httpx.HTTPStatusError as exc:
            print(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.")
            await asyncio.sleep(2)
        except Exception as e:
            print(f"Error while requesting {url}: {e}")
            await asyncio.sleep(2)
    return None

def extract_texts(html, selector):
    try:
        elements = html.css(selector)
        return [element.text() for element in elements if element.text()]
    except AttributeError:
        return []

def extract_text(html, selector):
    try:
        element = html.css_first(selector)
        return element.text() if element else ''
    except AttributeError:
        return ''

def parser_pages(html):
    properties = html.css("li.a37d52f0")
    for property in properties:
        link = urljoin("https://www.bayut.eg/", property.css_first('a').attributes.get('href'))
        yield link

async def get_property_info(client, link):
    html = await fetch(client, link)
    if html is None:
        print(f"Skipping URL {link} due to error.")
        return []
    items = html.css("div._0919f096")
    property_data = []
    for item in items:
        property_info = {
            "Title": extract_text(item, "._06d09310"),
            "Price": extract_text(item, "._2d107f6e"),
            "Location": extract_text(item, ".e4fd45f0"),
            "More Info": extract_texts(html, "._2fdf7fc5"),
            "Description": extract_text(item, "span._3547dac9"),
            "Agency name": extract_text(item, "._02db0128"),
            "Agent name": extract_text(item, ".d8185451"),
            "Link": link
        }
        property_data.append(property_info)
    return property_data

def get_urls(number_pages):
    base_url_rent = "https://www.bayut.eg/en/egypt/properties-for-rent/page-"
    first_page_url_rent = "https://www.bayut.eg/en/egypt/properties-for-rent/"
    rent_urls = [first_page_url_rent] + [base_url_rent + str(page) + '/' for page in range(2, int(number_pages) + 1)]

    base_url_sale = "https://www.bayut.eg/en/egypt/properties-for-sale/page-"
    first_page_url_sale = "https://www.bayut.eg/en/egypt/properties-for-sale/"
    sale_urls = [first_page_url_sale] + [base_url_sale + str(page) + '/' for page in range(2, int(number_pages) + 1)]

    return rent_urls + sale_urls

def save_data(data, filename="properties.csv"):
    df = pd.DataFrame(data)
    df.to_csv(filename,  index=False, encoding='utf-8')
    print(f"Data saved to {filename}")

async def main(urls):
    async with httpx.AsyncClient() as client:
        all_properties = []
        for i, url in enumerate(urls):
            try:
                print(f"Fetching URL {i+1}/{len(urls)}: {url}")
                html = await fetch(client, url)
                if html is not None:
                    data = list(parser_pages(html))
                    for item in data:
                        property_info = await get_property_info(client, item)
                        if property_info:
                            all_properties.extend(property_info)
                else:
                    print(f"Skipping URL {url} due to error.")
                if i % 20 == 0 and all_properties: 
                    save_data(all_properties)
                await asyncio.sleep(1)  # Small delay to avoid overwhelming the server
            except Exception as e:
                print(f"Error processing URL {url}: {e}")
        if all_properties:
            save_data(all_properties)
        return pd.DataFrame(all_properties)

if __name__ == "__main__":
    urls = get_urls(200)  # Adjust the number of pages as needed
    df = asyncio.run(main(urls))
    print(df.head())
