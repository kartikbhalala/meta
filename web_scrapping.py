import os
import requests
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import A4
from reportlab.lib import fonts
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.enums import TA_LEFT

URL_CATEGORIES = {
    'accessible-and-inclusive-content': "Accessible_and_Inclusive_Content.pdf",
    'writing-and-designing-content': "Writing_and_Designing_Content.pdf",
    'grammar-punctuation-and-conventions': "Grammar_Punctuation_and_Conventions.pdf",
    'structuring-content': "Structuring_Content.pdf",
    'referencing-and-attribution': "Referencing_and_Attribution.pdf",
}

def parse_sitemap(sitemap_url):
    response = requests.get(sitemap_url)
    response.encoding = 'utf-8'

    if response.status_code != 200:
        print(f"Failed to fetch sitemap: {sitemap_url}")
        return []

    soup = BeautifulSoup(response.text, 'lxml')
    urls = [loc.get_text() for loc in soup.find_all('loc')]
    print(f"Found {len(urls)} URLs in the sitemap.")
    return urls

def clean_html(content):
    soup = BeautifulSoup(content, 'html.parser')
    for tag in soup.find_all(['em', 'strong', 'b', 'i']):
        tag.unwrap()
    return str(soup)

def scrape_relevant_content(url):
    response = requests.get(url)
    response.encoding = 'utf-8'
    if response.status_code != 200:
        print(f"Failed to fetch page: {url}")
        return ""
    
    soup = BeautifulSoup(response.text, 'html.parser')
    main_content = soup.find('main') or soup.find('article')

    if not main_content:
        print(f"No main content found for: {url}")
        return ""

    content = []
    skip_sections = ['References', 'Help us improve', 'Release notes', 'Last updated']
    for element in main_content.find_all(['h1', 'h2', 'h3', 'p', 'ul', 'ol']):
        if any(skip in element.get_text() for skip in skip_sections):
            continue
        if element.name.startswith('h'):
            content.append({'type': 'heading', 'text': clean_html(element.get_text(strip=True))})
        elif element.name == 'p':
            cleaned_paragraph = clean_html(element.get_text(strip=True))
            content.append({'type': 'paragraph', 'text': cleaned_paragraph})
        elif element.name in ['ul', 'ol']:
            list_items = [clean_html(li.get_text(strip=True)) for li in element.find_all('li')]
            content.append({'type': 'list', 'items': list_items})
    
    return content

def create_pdf_with_reportlab(content_list, output_file):
    doc = SimpleDocTemplate(output_file, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    for item in content_list:
        if item['type'] == 'heading':
            elements.append(Spacer(1, 0.5 * cm))
            heading_style = styles['Heading1'] if 'h1' in item['text'].lower() else styles['Heading2']
            heading_style.alignment = TA_LEFT
            elements.append(Paragraph(item['text'], heading_style))
        elif item['type'] == 'paragraph':
            elements.append(Spacer(1, 0.2 * cm))
            paragraph_style = styles['BodyText']
            paragraph_style.alignment = TA_LEFT
            try:
                elements.append(Paragraph(item['text'], paragraph_style))
            except ValueError as e:
                print(f"Error in parsing paragraph, skipping: {item['text']}")
        elif item['type'] == 'list':
            list_items = [ListItem(Paragraph(li, styles['BodyText']), leftIndent=1 * cm) for li in item['items']]
            elements.append(ListFlowable(list_items, bulletType='bullet'))
    
    doc.build(elements)
    print(f"PDF created successfully: {output_file}")

def scrape_all_pages(sitemap_url):
    urls = parse_sitemap(sitemap_url)
    categorized_content = {key: [] for key in URL_CATEGORIES.keys()}

    for url in urls:
        print(f"Scraping content from: {url}")
        content = scrape_relevant_content(url)

        if content:
            url_parts = url.split('/')
            if len(url_parts) > 3:
                category_key = url_parts[3]
                if category_key in categorized_content:
                    categorized_content[category_key].extend(content)
                else:
                    print(f"Skipping unknown category: {category_key}")
    
    for category, content in categorized_content.items():
        if content:
            output_file = URL_CATEGORIES[category]
            create_pdf_with_reportlab(content, output_file)
        else:
            print(f"No content found for category: {category}")

def main():
    sitemap_url = "https://www.stylemanual.gov.au/sitemap.xml"
    scrape_all_pages(sitemap_url)

if __name__ == "__main__":
    main()
