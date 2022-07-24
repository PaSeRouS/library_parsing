# Парсер книг с сайта tululu.org

Скрипт позволяет скачать книги с сайта [tululu.org](https://tululu.org/) в папку books, а также обложки книг в папку images.
Скрипт parse_tululu_category.py позволяет скачивать книги жанра "Научная фантастика" постранично.
Скрипт render_website сгенерирует сайт со скачанными книгами в удобном глазу виде. После генерации его надо разместить в интернете и он будет доступен.
Сайт из этого репозитория находится [здесь](https://paserous.github.io/library_parsing/pages/index1.html).

### Как установить

Python3 должен быть уже установлен. 
Затем используйте `pip` (или `pip3`, есть конфликт с Python2) для установки зависимостей:
```
pip install -r requirements.txt
```

### Аргументы download_books.py

Чтобы скрипт отработал правильно его нужно запустить с двумя числовыми параметрами, которые указывают диапазон скачиваемых с сайта книг.
Так, в примере ниже, скрипт скачает книги с 20 по 30 включительно.
```
python download_books.py 20 30
```

### Аргументы parse_tululu_category.py

```
python parse_tululu_category.py --start_page 700 # Скачаются все книги, начиная с 700-й страницы
python parse_tululu_category.py --start_page 700 --end_page 701 # Скачаются только книги с 700-й страницы
python parse_tululu_category.py --dest_folder books # Скачаются тексты книг, изображения и описания книг в папку books каталога,
                                                    # где лежит скрипт
python parse_tululu_category.py --skip_txt # Не будут скачиваться тексты книг
python parse_tululu_category.py --skip_imgs # Не будут скачиваться обложки книг
python parse_tululu_category.py --json_path description/all # Описания книг скачаются по указанному пути
```

### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).
