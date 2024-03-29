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
        type=int,
        default=1
    )
    
    parser.add_argument(
        '--end_page',
        help='Номер страницы, на которой скачивание закончить',
        type=int,
        default=702
    )

    parser.add_argument(
        '--dest_folder',
        help='Путь к папке с результатами парсинга',
        default=''
    )
    
    parser.add_argument(
        '--skip_imgs',
        help='Не скачивать картинки',
        action="store_true",
        default=False
    )

    parser.add_argument(
        '--skip_txt',
        help='Не скачивать текстовые версии книг',
        action="store_true",
        default=False
    )

    parser.add_argument(
        '--json_path',
        help='Путь для файла books.json',
        default='/books'
    )

    args = parser.parse_args()

    books_descriptions = []

    os.makedirs(args.json_path, exist_ok=True)
    json_filename = Path(args.json_path, 'books.json')

    for page_id in range(args.start_page, args.end_page):
        try:
            books_page = []

            genre_books_url = f'https://tululu.org/l55/{page_id}'
            genre_books_response = requests.get(genre_books_url)
            genre_books_response.raise_for_status()

            check_for_redirect(genre_books_response)
            soup = BeautifulSoup(genre_books_response.text, 'lxml')

            selector = 'table.d_book'
            books_page = soup.select(selector)
        except HTTPError:
            print('Некорректная ссылка')
        except ConnectionError:
            print('Нет подключения к сети.')

        for book in books_page:
            try:
                book_url = urljoin(
                    'https://tululu.org', 
                    book.find('a')['href']
                )
                book_page_response = requests.get(book_url)
                book_page_response.raise_for_status()
                check_for_redirect(book_page_response)

                soup = BeautifulSoup(book_page_response.text, 'lxml')
                book_params = parse_book_page(book_page_response)

                download_url = ''

                selector = 'table.d_book a'
                ref = soup.select(selector)[-3]
                download_url = urljoin(
                    'https://tululu.org/', 
                    ref['href']
                )

                if download_url:
                    books_descriptions.append(book_params)

                    if not args.skip_txt:
                        folder = Path(args.dest_folder, '/books')

                        download_txt(
                            download_url,
                            book_params['title'],
                            folder=folder
                        )

                    if not args.skip_imgs:
                        folder = Path(args.dest_folder, '/image')

                        download_image(
                            book_params['image_url'],
                            book_params['image_name'],
                            folder=folder
                        )
            except HTTPError:
                print('Некорректная ссылка')
            except ConnectionError:
                print('Нет подключения к сети.')

    if args.dest_folder:
        os.makedirs(args.dest_folder, exist_ok=True)
        json_filename = Path(args.dest_folder, 'books.json')

    with open(json_filename, "w", encoding='utf8') as json_file:
        json.dump(
            books_descriptions, 
            json_file, 
            ensure_ascii=False
        )