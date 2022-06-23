import argparse
import json
import os

import requests
from bs4 import BeautifulSoup
from pathlib import Path
from pathvalidate import sanitize_filename
from requests import ConnectionError, HTTPError
from urllib.parse import urljoin

from download_books import download_image, download_txt
from download_books import check_for_redirect, parse_book_page


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Парсер книг из большой бесплатной библиотеки'
    )

    parser.add_argument(
        '--start_page',
        help='Номер страницы, с которой скачивать',
        type=int
    )
    
    parser.add_argument(
        '--end_page',
        help='Номер страницы, на которой скачивание закончить',
        type=int
    )

    parser.add_argument(
        '--dest_folder',
        help='Путь к папке с результатами парсинга'
    )
    
    parser.add_argument(
        '--skip_imgs',
        help='Не скачивать картинки',
        action="store_true"
    )

    parser.add_argument(
        '--skip_txt',
        help='Не скачивать текстовые версии книг',
        action="store_true"
    )

    parser.add_argument(
        '--json_path',
        help='Путь для файла books.json'
    )

    args = parser.parse_args()

    if args.dest_folder:
        dest_folder = args.dest_folder
    else:
        dest_folder = ''

    if args.start_page:
        start_page = args.start_page - 1
    else:
        start_page = 1

    if args.end_page:
        end_page = args.end_page - 1
    else:
        end_page = 702

    books_descriptions = []

    for page_id in range(start_page, end_page):
        genre_books_url = f'https://tululu.org/l55/{page_id+1}'
        genre_books_response = requests.get(genre_books_url)
        genre_books_response.raise_for_status()

        soup = BeautifulSoup(genre_books_response.text, 'lxml')

        selector = 'table.d_book'
        books = soup.select(selector)

        for book in books:
            book_url = urljoin('https://tululu.org', book.find('a')['href'])
            book_page_response = requests.get(book_url)
            book_page_response.raise_for_status()

            soup = BeautifulSoup(book_page_response.text, 'lxml')
            book_params = parse_book_page(book_page_response)

            download_url = ''

            selector = 'table.d_book a'
            book_refs = soup.select(selector)
            for ref in book_refs:
                if ref.text == 'скачать txt':
                    download_url = urljoin(
                        'https://tululu.org/', 
                        ref['href']
                    )

            if download_url:
                books_descriptions.append(book_params)

                if not args.skip_txt:
                    download_txt(
                        download_url,
                        book_params['title'],
                        folder=f'{dest_folder}/books'
                    )
                
                if not args.skip_imgs:
                    download_image(
                        book_params['image_url'],
                        book_params['image_name'],
                        folder=f'{dest_folder}/images'
                    )

    if args.json_path:
        os.makedirs(args.json_path, exist_ok=True)
        json_filename = Path(args.json_path, 'books.json')
    elif not dest_folder:
        json_filename = 'books.json'
    else:
        os.makedirs(dest_folder, exist_ok=True)
        json_filename = Path(dest_folder, 'books.json')

    with open(json_filename, "w", encoding='utf8') as json_file:
        json.dump(
            books_descriptions, 
            json_file, 
            ensure_ascii=False
        )