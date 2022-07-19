import json
import math
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server, shell
from more_itertools import chunked


def on_reload():
    with open("books.json", "r", encoding='utf8') as json_file:
        books = json.loads(json_file.read())

    for book in books:
        title = book['title']
        book['text_ref'] = f'../books/{title}.txt'

    os.makedirs('pages', exist_ok=True)

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')

    chunked_books = list(chunked(books, 20))
    number_of_pages = len(chunked_books)

    for page_number, books_on_page in enumerate(chunked_books):
        chunked_books_on_page = list(chunked(books_on_page, 2))

        rendered_page = template.render(
            chunked_books=chunked_books_on_page,
            number_of_pages=number_of_pages,
            current_page=page_number+1
        )

        filename = f'pages/index{page_number+1}.html'

        with open(filename, 'w', encoding="utf8") as file:
            file.write(rendered_page)


if __name__ == '__main__':
    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='pages/index1.html')