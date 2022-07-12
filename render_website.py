import json

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server, shell


def on_reload():
    with open("books.json", "r", encoding='utf8') as json_file:
        books = json.loads(json_file.read())

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')

    rendered_page = template.render(
        books=books
    )

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)


if __name__ == '__main__':
    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='.')