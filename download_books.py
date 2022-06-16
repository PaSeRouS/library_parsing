import os

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from requests import HTTPError


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


if __name__ == '__main__':
    for x in range(10):
        url = f'http://tululu.org/txt.php?id={x+1}'

        book_url = f'https://tululu.org/b{x+1}/'
        book_response = requests.get(book_url)
        book_response.raise_for_status()

        soup = BeautifulSoup(book_response.text, 'lxml')
        title_tag = soup.find('body').find('table').find('h1')
        book_data = title_tag.text.split('::')

        download_txt(url, book_data[0])