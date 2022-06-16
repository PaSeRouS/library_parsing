import os
from os.path import split, splitext

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from requests import HTTPError
from urllib.parse import unquote, urlsplit


def check_for_redirect(response):
    for record in response.history:
        if record.status_code == 302:
            raise HTTPError


def download_txt(url, filename, folder='books/'):
    response = requests.get(url)
    response.raise_for_status()

    try: 
        check_for_redirect(response)
        os.makedirs(folder, exist_ok=True)

        filename = filename.replace(':', '-')
        filename = f'{folder}{x+1}. {filename.strip()}.txt'
        with open(filename, 'wb') as file:
            file.write(response.content)
    except HTTPError:
        print(f'Книга "{filename}" отсутствует.')


def download_image(url, filename, folder='images/'):
    response = requests.get(url)
    response.raise_for_status()

    os.makedirs(folder, exist_ok=True)

    filename = f'{folder}{filename}'
    with open(filename, 'wb') as file:
        file.write(response.content)


def parse_book_page(html):
    book_params = {}

    soup = BeautifulSoup(html.text, 'lxml')

    # Данные о названии
    title_tag = soup.find('body').find('table').find('h1')
    book_data = title_tag.text.split('::')

    # Данные об изображении
    image_tag = soup.find(
        'div',
        class_='bookimage'
    ).find('img')['src']

    image_url = f'http://tululu.org{image_tag}'
    image_name = split(urlsplit(unquote(image_url)).path)[1]

    # Данные о комментариях
    comments = soup.find_all('div', class_='texts')
    comments_texts = []
    for comment in comments:
        comments_texts.append(comment.find('span').text)

    # Данные о жанрах
    genres_ref = soup.find('span', class_='d_book').find_all('a')
    genres = []
    for genre in genres_ref:
        genres.append(genre.text)

    book_params['title'] = book_data[0].strip()
    book_params['image_url'] = image_url
    book_params['image_name'] = image_name
    book_params['comments'] = comments_texts
    book_params['genres'] = genres

    return book_params


if __name__ == '__main__':
    for x in range(10):
        url = f'http://tululu.org/txt.php?id={x+1}'

        book_url = f'https://tululu.org/b{x+1}/'
        book_html = requests.get(book_url)
        book_html.raise_for_status()

        try:
            check_for_redirect(book_html)

            book_params = parse_book_page(book_html)

            # download_txt(url, book_params['title'])
            # download_image(
            #     book_params['image_url'],
            #     book_params['image_name']
            # )
        except HTTPError:
            print(f'Книга с id={x+1} отсутствует.')