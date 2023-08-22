import os
import re

from bs4 import BeautifulSoup
import requests
import requests_cache

requests_cache.install_cache("scraps_cache", expire_after=86400)


BASE_URL = "https://scrapsfromtheloft.com"
LIST_PAGE = "/stand-up-comedy-scripts/"

ARTICLE_OUTPUT_FOLDER = "articles"



def fetch_urls():
    response = requests.get(BASE_URL + LIST_PAGE)
    soup = BeautifulSoup(response.content, "html.parser")

    urls = [
        link["href"]
        for link in soup.find_all("a", href=True)
        if link["href"].startswith("https://scrapsfromtheloft.com/comedy/")
        and link["href"].endswith("-transcript/")
    ]

    return urls

def simplify_url(url):
    """Converts a URL to a filename-friendly string."""
    # Remove protocol (http, https) and replace special characters with underscores
    simplified = re.sub(r'https?://', '', url).replace('.', '_').replace('/', '_')
    return simplified

def extract_and_save_content_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract content from the div with specified data-id attribute
    content_div = soup.find('div', {'data-id': '74af9a5b'})
    
    # If div is found, extract texts from each <p> tag and save to a file
    if content_div:
        # Extract text from each <p> tag inside the div and join with line breaks
        paragraphs = [p.get_text() for p in content_div.find_all('p')]
        content = '\n'.join(paragraphs)
        
        filename = f"{ARTICLE_OUTPUT_FOLDER}/{simplify_url(url)}.txt"
        
        with open(filename, "w", encoding='utf-8') as file:
            file.write(content)
        print(f"Content saved to {filename}")
    else:
        print(f"Div with data-id '74af9a5b' not found in {url}")


def save_to_file(urls):
    with open("comedy_transcript_urls.txt", "w") as file:
        for url in urls:
            file.write(url + "\n")
    print("URLs saved to comedy_transcript_urls.txt")


def wrap_text(text, max_len=88):
    """Wrap text at a space near the given length, without breaking words."""
    lines = []
    for line in text.split('\n'):
        while len(line) > max_len:
            split_at = line.rfind(' ', max_len - 10, max_len + 10)  # Search for a space near max_len
            if split_at == -1:  # If we don't find a space, split at max_len
                split_at = max_len
            lines.append(line[:split_at])
            line = line[split_at:].lstrip()
        lines.append(line)
    return '\n'.join(lines)

def combine_txt_files(folder_name, output_filename="combined.txt"):
    all_contents = []

    for filename in os.listdir(folder_name):
        if filename.endswith(".txt"):
            with open(os.path.join(folder_name, filename), 'r', encoding='utf-8') as file:
                content = wrap_text(file.read())
                all_contents.append(f"\n\n{filename[:-4]}\n\n{content}")

    with open(os.path.join("..", output_filename), 'w', encoding='utf-8') as output_file:
        output_file.write('\n\n'.join(all_contents))

    print(f"Contents combined and saved to {output_filename}")


if __name__ == "__main__":
    comedy_transcript_urls = fetch_urls()
    save_to_file(comedy_transcript_urls)

    for url in comedy_transcript_urls:
        extract_and_save_content_from_url(url)
    
    combine_txt_files(ARTICLE_OUTPUT_FOLDER)
