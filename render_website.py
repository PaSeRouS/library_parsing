import json
import math
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server, shell
from more_itertools import chunked
from pathvalidate import sanitize_filename

BOOKS_PER_PAGE = 20
COLUMNS_PER_PAGE = 2


def on_reload():
    with open("books.json", "r", encoding='utf8') as json_file:
        books = json.load(json_file)

    for book in books:
        book['title'] = sanitize_filename(book['title'])

    os.makedirs('pages', exist_ok=True)

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')

    chunked_books = list(chunked(books, BOOKS_PER_PAGE))
    number_of_pages = len(chunked_books)

    for page_number, books_on_page in enumerate(chunked_books, start=1):
        chunked_books_on_page = list(chunked(books_on_page, COLUMNS_PER_PAGE))

        rendered_page = template.render(
            chunked_books=chunked_books_on_page,
            number_of_pages=number_of_pages,
            current_page=page_number
        )

        filename = f'pages/index{page_number}.html'

        with open(filename, 'w', encoding="utf8") as file:
            file.write(rendered_page)


if __name__ == '__main__':
    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='.', default_filename='pages/index1.html')