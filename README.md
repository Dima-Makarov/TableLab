# TableLab
В качестве базы будет использоваться PostgreSQL.
Скрипт инициализации вместе с тестовыми данными находится в файле init.sql

## Справочник 1: Модели телефонов
- id
- Модель (varchar)
- Дата выхода на рынок (date)
- Используемый процессор (ссылка на вторую таблицу) (foreign key)
- Количество камер (int)
- Масса (numeric(10,2))

## Справочник 2: Модель процессора
- id
- Название (varchar)
- Дата выхода (date)
- Мощность, ватт (numeric(10,2))
- Количество ядер (int)

# Инструкция по запуску:
1. Создать PostgreSQL базу с названием makarov, зайти в нее и запустить в ней скрипт init.py
2. Далее, запустить программу main.exe, ввести логин и пароль от базы и наслаждаться :)
3. Или, если предыдущий пункт почему-то не сработал, то запустить сразу код питона. Я делал на версии Python 3.11, запускать тоже желательно на этой версии, предварительно установив необходимые пакеты через $pip install psycopg2 tkcalendar
