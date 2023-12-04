import os
import requests
from pathlib import Path
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup
def download_txt(url, payload, filename, folder='books/'):
    response = requests.get(url, params=payload, allow_redirects=False)
    response.raise_for_status()
    try:
        check_for_redirect(response)
    except requests.HTTPError:
        return
    valid_filename = sanitize_filename(filename)
    collected_path = os.path.join(folder,valid_filename)
    read_file(collected_path, response.content)
    return collected_path

def check_for_redirect(response):
    print(response.status_code)
    if response.status_code == 302:
        raise requests.HTTPError
def read_file(filename, content):
    with open(filename, 'wb') as file:
        file.write(content)

def main():
    path = 'books/id'
    Path(path.split('/')[0]).mkdir(parents=True, exist_ok=True)

    url = "https://tululu.org/txt.php"

    for book_number in range(1,11):
        url1 = f"https://tululu.org/b{book_number}/"
        payload = {'id':str(book_number)}
        response = requests.get(url1, params=payload, allow_redirects=False)
        response.raise_for_status()
        try:
            check_for_redirect(response)
        except requests.HTTPError:
            continue
        soup = BeautifulSoup(response.text, 'lxml')
        title_tag = soup.find('div', id='content').find('h1')
        book = title_tag.text.split('::')[0].strip()
        author = title_tag.text.split('::')[1].strip()
        path = download_txt(url, payload, book)
        print(path)

if __name__ == "__main__":
    main()

