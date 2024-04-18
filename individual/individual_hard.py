#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from datetime import datetime

import psycopg2


DATABASE = "database_name"
USER = "username"
PASSWORD = "password"
HOST = "localhost"
PORT = "5432"


def create_db() -> None:
    """
    Создает базу данных, если она не существует, и инициализирует таблицы.
    """
    conn = psycopg2.connect(
        database=DATABASE, user=USER, password=PASSWORD, host=HOST, port=PORT
    )
    cursor = conn.cursor()

    # Создание таблицы должностей
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS posts (
            post_id SERIAL PRIMARY KEY,
            post_title TEXT NOT NULL
        )
        """
    )

    # Создание таблицы сотрудников
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS workers (
            id SERIAL PRIMARY KEY,
            surname TEXT NOT NULL,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            post_id INTEGER NOT NULL REFERENCES posts(post_id),
            date TEXT NOT NULL
        )
    """
    )
    conn.commit()
    conn.close()


def add_worker(
    surname: str, name: str, post: str, phone: str, date: datetime
) -> None:
    """
    Добавляет работника в базу данных.
    """
    conn = psycopg2.connect(
        database=DATABASE, user=USER, password=PASSWORD, host=HOST, port=PORT
    )
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT post_id FROM posts WHERE post_title = %s
        """,
        (post,),
    )
    row = cursor.fetchone()
    if row is None:
        cursor.execute(
            """
            INSERT INTO posts (post_title) VALUES (%s) RETURNING post_id
            """,
            (post,),
        )
        post_id = cursor.fetchone()[0]
    else:
        post_id = row[0]
    cursor.execute(
        """
        INSERT INTO workers (surname, name, post_id, phone, date)
        VALUES (%s, %s, %s, %s, %s)
    """,
        (surname, name, post_id, phone, date),
    )
    conn.commit()
    conn.close()


def display_workers(lst) -> None:
    """
    Отобразить список работников.
    """
    # Проверить, что список работников не пуст.
    if lst:
        # Блок заголовка таблицы
        line = "+-{}-+-{}-+-{}-+-{}-+-{}-+".format(
            "-" * 4, "-" * 30, "-" * 20, "-" * 15, "-" * 15
        )
        print(line)
        print(
            f'| {"№":^4} | {"Фамилия":^30} | {"Имя":^20} | '
            f'{"Номер телефона":^15} | {"Дата рождения":^15} |'
        )

        print(line)
        # Вывести данные о всех сотрудниках.
        for idx, worker in enumerate(lst, 1):
            print(
                f'| {idx:>4} | {worker.get("surname", ""):<30} | '
                f'{worker.get("name", ""):<20}'
                f' | {worker.get("phone", 0):>15}'
                f' | {worker.get("date", 0):>15} |'
            )

        print(line)
    else:
        print("Список работников пуст.")


def select_all():
    """
    Выбрать всех работников.
    """
    conn = psycopg2.connect(
        database=DATABASE, user=USER, password=PASSWORD, host=HOST, port=PORT
    )
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT workers.surname, workers.name, workers.phone, workers.date
        FROM workers
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {"surname": row[0], "name": row[1], "phone": row[2], "date": row[3]}
        for row in rows
    ]


def phone(numbers_phone):
    conn = psycopg2.connect(
        database=DATABASE, user=USER, password=PASSWORD, host=HOST, port=PORT
    )
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM workers WHERE phone = %s", (numbers_phone,))
    i = cursor.fetchone()
    if i:
        print(
            f"Фамилия: {i[1]}\n"
            f"Имя: {i[2]}\n"
            f"Номер телефона: {i[3]}\n"
            f"Дата рождения: {i[5]}"
        )
    else:
        print("Работник с таким номером телефона не найден.")


def main():
    parser = argparse.ArgumentParser(
        description="Управление базой данных работников"
    )

    subparsers = parser.add_subparsers(dest="command", help="Доступные команды")

    parser_add = subparsers.add_parser("add", help="Добавить нового работника")
    parser_add.add_argument("--surname", type=str, help="Фамилия")
    parser_add.add_argument("--name", type=str, help="Имя")
    parser_add.add_argument(
        "-p", "--post", action="store", help="The worker's post"
    )
    parser_add.add_argument("--phone", type=str, help="Телефон")
    parser_add.add_argument("--date", type=str, help="Дата рождения")

    subparsers.add_parser("display", help="Отобразить всех работников")

    # Добавление субпарсера для выбора работника по номеру телефона.
    select_phone = subparsers.add_parser(
        "select", help="Select worker by phone"
    )
    select_phone.add_argument("-p", "--phone", action="store", required=True)

    args = parser.parse_args()
    create_db()
    match args.command:
        case "add":
            add_worker(
                args.surname, args.name, args.post, args.phone, args.date
            )
        case "display":
            display_workers(select_all())
        case "select":
            phone(args.phone)


if __name__ == "__main__":
    main()
