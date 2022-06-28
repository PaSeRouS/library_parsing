import argparse
import os
from os.path import split, splitext

import requests
from bs4 import BeautifulSoup
from pathlib import Path
from pathvalidate import sanitize_filename
from requests import ConnectionError, HTTPError
from tqdm import tqdm
from urllib.parse import unquote, urljoin, urlsplit


def check_for_redirect(response):
    if response.history:
        raise HTTPError


def download_txt(url, filename, url_params={}, folder='books/'):
    response = requests.get(url, params=url_params)
    response.raise_for_status()

    check_for_redirect(response)
    os.makedirs(folder, exist_ok=True)

    filename = sanitize_filename(filename)
    filename = Path(folder, f'{filename.strip()}.txt')
    with open(filename, 'wb') as file:
        file.write(response.content)


def download_image(url, filename, folder='images/'):
    response = requests.get(url)
    response.raise_for_status()

    os.makedirs(folder, exist_ok=True)

    filename = Path(folder, filename)
    with open(filename, 'wb') as file:
        file.write(response.content)


def parse_book_page(book_page):
    book_params = {}

    soup = BeautifulSoup(book_page.text, 'lxml')

    selector = 'body table h1'
    title_tag = soup.select_one(selector)

    book_title, book_author = title_tag.text.split('::')
    book_title = book_title.strip()
    book_author = book_author.strip()

    selector = 'div.bookimage img'
    image_tag = soup.select_one(selector)['src']

    image_url = urljoin(book_page.url, image_tag)
    image_name = split(urlsplit(unquote(image_url)).path)[1]

    selector = 'div.texts'
    comments = soup.select(selector)
    comments_texts = [comment.find('span').text for comment in comments]

    selector = 'span.d_book a'
    genres_ref = soup.select(selector)
    genres = [genre.text for genre in genres_ref]

    book_params = {
        'title': book_title,
        'author': book_author,
        'image_url': image_url,
        'image_name': image_name,
        'comments': comments_texts,
        'genres': genres
    }

    return book_params


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Парсер книг из большой бесплатной библиотеки'
    )
    parser.add_argument(
        'start_id',
        help='ID книги, с которой скачивать',
        type=int
    )
    
    parser.add_argument(
        'end_id',
        help='ID книги, на которой скачивание закончить',
        type=int
    )
    
    args = parser.parse_args()

    for book_id in tqdm(range(args.start_id, args.end_id)):
        url_params = {
            'id': book_id
        }

        download_url = 'https://tululu.org/txt.php'

        try:
            book_url = f'https://tululu.org/b{book_id}/'
            book_page_response = requests.get(book_url)
            book_page_response.raise_for_status()

            check_for_redirect(book_page_response)

            book_params = parse_book_page(book_page_response)

            download_txt(download_url, book_params['title'], url_params)
            download_image(
                book_params['image_url'],
                book_params['image_name']
            )
        except HTTPError:
            if book_params:
                title = book_params['title']
                print(f'Книга "{title}" отсутствует.')
            else:
                print(f'Книга с id={book_id} отсутствует.')
        except ConnectionError:
            print('Нет подключения к сети.')