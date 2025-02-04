import httpx
from selectolax.parser import HTMLParser
from urllib.parse import urljoin
import pandas as pd
import time

def get_html(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
           'Accept-Encoding': 'gzip, deflate',
           'Accept-Language': 'en-US,en;q=0.9'
    }
    try:
        resp = httpx.get(url, headers=headers, follow_redirects=True)
        resp.raise_for_status()
    except httpx.HTTPStatusError as exc:
        print(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.")
        return None
    return HTMLParser(resp.text)

def extract_text(element, selector):
    try:
        return element.css_first(selector).text()
    except AttributeError:
        return None

def extract_texts(html, selector):
    try:
        elements = html.css(selector)
        return [element.text() for element in elements if element.text()]
    except AttributeError:
        return []

def parser_pages(html):
    properties = html.css("li.a37d52f0")
    for property in properties:
        link = urljoin("https://www.bayut.eg/", property.css_first('a').attributes.get('href'))
        yield link

def get_property_info(link):
    html = get_html(link)
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
            "Agent name": extract_text(item, ".d8185451")
        }
        property_data.append(property_info)
    return property_data

def get_urls(number_pages):
    # URLs for properties for rent
    base_url_rent = "https://www.bayut.eg/en/egypt/properties-for-rent/page-"
    first_page_url_rent = "https://www.bayut.eg/en/egypt/properties-for-rent/"
    rent_urls = [first_page_url_rent] + [base_url_rent + str(page) + '/' for page in range(2, int(number_pages) + 1)]
    
    # URLs for properties for sale
    base_url_sale = "https://www.bayut.eg/en/egypt/properties-for-sale/page-"
    first_page_url_sale = "https://www.bayut.eg/en/egypt/properties-for-sale/"
    sale_urls = [first_page_url_sale] + [base_url_sale + str(page) + '/' for page in range(2, int(number_pages) + 1)]
    
    # Combine both lists
    combined_urls = rent_urls + sale_urls
    return combined_urls

def main(urls):
    all_properties = []
    for url in urls:
        html = get_html(url)
        if html is not None:
            data = parser_pages(html)
            for item in data:
                property_info = get_property_info(item)
                if property_info:
                    all_properties.extend(property_info)
        else:
            print(f"Skipping URL {url} due to error.")
        time.sleep(5)
    return all_properties