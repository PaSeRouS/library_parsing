import os

import requests


os.makedirs("books", exist_ok=True)

for x in range(10):
    url = f'https://tululu.org/txt.php?id={x+1}'

    response = requests.get(url)
    response.raise_for_status() 

    filename = f'books/book{x+1}.txt'
    with open(filename, 'wb') as file:
        file.write(response.content)