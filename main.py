import os
from pathlib import Path
from urllib.parse import urljoin, urlsplit

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
import requests


def download_image(url, folder='images/'):
    Path(folder.split('/')[0]).mkdir(parents=True, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    parsed_url = urlsplit(url)[2]
    collected_path = os.path.join(folder, parsed_url.split('/')[-1])
    read_file(collected_path, response.content)
    return collected_path


def download_txt(url, filename, folder='books/'):
    Path(folder.split('/')[0]).mkdir(parents=True, exist_ok=True)
    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()
    try:
        check_for_redirect(response)
    except requests.HTTPError:
        return
    valid_filename = sanitize_filename(filename)
    collected_path = os.path.join(folder, valid_filename)
    read_file(collected_path, response.content)
    return collected_path


def check_for_redirect(response):
    if response.status_code == 302:
        raise requests.HTTPError


def read_file(filename, content):
    with open(filename, 'wb') as file:
        file.write(content)


def parse_book_page(response):
    soup = BeautifulSoup(response.text, 'lxml')
    title_tag = soup.find('div', id='content').find('h1')
    book = title_tag.text.split('::')[0].strip()
    author = title_tag.text.split('::')[1].strip()
    url_to_image = soup.find('div', class_='bookimage').find('img')['src']
    comments = soup.find_all('div', class_='texts')
    for number, comment in enumerate(comments):
        comments[number] = comment.find('span', class_='black').text
    genres = soup.find('span', class_='d_book').find_all('a')
    for number, genre in enumerate(genres):
        genres[number] = genre.text
    info_book = {'title': book,
                 'author': author,
                 'genres': genres,
                 'comments': comments,
                 'path_to_image': url_to_image
                 }
    return info_book


def main():
    parsed_books = []
    for book_number in range(1, 11):
        url_for_txt = f"https://tululu.org/txt.php?id={book_number}"
        url_for_parsing = f"https://tululu.org/b{book_number}/"
        response = requests.get(url_for_parsing, allow_redirects=False)
        response.raise_for_status()
        try:
            check_for_redirect(response)
        except requests.HTTPError:
            continue
        parsed_book = parse_book_page(response)
        download_txt(url_for_txt, parsed_book.get('title'))
        abs_url_to_image = urljoin(url_for_parsing, parsed_book.get('path_to_image'))
        download_image(abs_url_to_image)
        parsed_books.append(parsed_book)

    print(parsed_books)


if __name__ == "__main__":
    main()
