import psycopg2


# Вывод "меню"
def print_menu():
    print("1. Создать структуру базы данных\n"
          "2. Добавить нового клиента\n"
          "3. Добавить номер телефона для существующего клиента\n"
          "4. Изменить данные существующего клиента\n"
          "5. Удалить номер телефона существующего клиента\n"
          "6. Удалить все данные клиента\n"
          "7. Найти id клиента\n"
          "8. Вывести все данные из базы данных\n"
          "9. Вывести все данные конкретного клиента\n"
          "10. Удалить всю базу данных\n"
          "11. Выход")


# Функция для создания структуры БД (таблиц)
def create_db(conn):
    with conn.cursor() as cur:
        cur.execute("""
                CREATE TABLE IF NOT EXISTS client_info(
                    client_id SERIAL PRIMARY KEY,
                    first_name VARCHAR(60) NOT NULL,
                    last_name VARCHAR(60) NOT NULL,
                    email VARCHAR(120) NOT NULL
                    );
                """)
        conn.commit()
        cur.execute("""
                CREATE TABLE IF NOT EXISTS phones(
                    phone_id SERIAL PRIMARY KEY,
                    phone VARCHAR(60) NOT NULL
                    );
                """)
        conn.commit()
        cur.execute("""
                   CREATE TABLE IF NOT EXISTS client_phones(
                        phone_id INTEGER NOT NULL REFERENCES phones(phone_id),
                        client_id INTEGER NOT NULL REFERENCES client_info(client_id)
                        );
                    """)
        conn.commit()
        print("Таблицы успешно созданы!")


# Функция для добавления нового клиента
def add_client(conn, first_name, last_name, email, phone=None):
    with conn.cursor() as cur:
        cur.execute(f"""
                    INSERT INTO client_info(first_name, last_name, email) 
                        VALUES
                        ('{first_name}', '{last_name}', '{email}');
                    """)
        conn.commit()
        cur.execute(f"""
                    INSERT INTO phones(phone) 
                        VALUES
                        ('{phone}');
                    """)
        conn.commit()
        cur.execute("""
                    INSERT INTO client_phones(phone_id, client_id) 
                        VALUES((select MAX(phone_id) from phones), (select MAX(client_id) from client_info))
                    """)
        conn.commit()
    print("Данные клиента успешно добавлены!")


# Функция для добавления номера телефона для существующего клиента
def add_phone(conn, client_id, phone):
    if client_id == "":
        pass
    else:
        with conn.cursor() as cur:
            cur.execute(f"""
                    INSERT INTO phones(phone) 
                        VALUES
                        ('{phone}');
                        """)
            conn.commit()
            cur.execute(f"""
                    INSERT INTO client_phones(phone_id, client_id) 
                        VALUES((SELECT MAX(phone_id) from phones), '{client_id}');
                    """)
            conn.commit()
        print("Новый контактный телефон клиента успешно добавлен!")


# Функция для изменения данных клиента клиента
def change_client(conn, client_id, first_name=None, last_name=None, email=None, phone=None):
    with conn.cursor() as cur:
        if first_name == "":
            pass
        else:
            cur.execute(f"""
                    UPDATE client_info
                        SET first_name = '{first_name}'
                        WHERE client_id = '{client_id}';
                    """)
            conn.commit()
        if last_name == "":
            pass
        else:
            cur.execute(f"""
                    UPDATE client_info
                        SET last_name = '{last_name}'
                        WHERE client_id = '{client_id}';
                    """)
            conn.commit()
        if email == "":
            pass
        else:
            cur.execute(f"""
                    UPDATE client_info
                        SET email  = '{email}'
                        WHERE client_id = '{client_id}';
                    """)
            conn.commit()
        if phone == "":
            pass
        else:
            cur.execute(f"""
                    UPDATE phones
                        SET phone  = '{phone}'
                        WHERE phone_id = (SELECT phone_id FROM client_phones
                            GROUP BY client_id, phone_id
                            HAVING client_id = '{client_id}');
                    """)
            conn.commit()
    print("Данные клиента успешно изменены!")


# Функция для удаления телефона существующего клиента
def delete_phone(conn, client_id, phone):
    if client_id == "":
        pass
    else:
        with conn.cursor() as cur:
            cur.execute(f"""
                    DELETE FROM client_phones
                        WHERE phone_id = (SELECT DISTINCT p.phone_id FROM phones AS p
                            JOIN client_phones cp ON cp.phone_id = p.phone_id
                            JOIN client_info ci ON ci.client_id = cp.client_id
                            WHERE ci.client_id = '{client_id}' AND p.phone = '{phone}');
                   """)
            conn.commit()
            cur.execute(f"""
                    DELETE FROM phones
                        WHERE phone = '{phone}';
                    """)
            conn.commit()
        print("Контактный телефон клиента успешно удален!")


# Функция для удаления существующего клиента
def delete_client(conn, client_id):
    if client_id == "":
        pass
    else:
        with conn.cursor() as cur:
            cur.execute(f"""
                    DELETE FROM client_phones
                        WHERE phone_id = (SELECT p.phone_id FROM phones AS p
                            JOIN client_phones cp ON cp.phone_id = p.phone_id
                            JOIN client_info ci ON ci.client_id = cp.client_id
                            WHERE ci.client_id = '{client_id}');
                   """)
            conn.commit()
            cur.execute(f"""
                    DELETE FROM phones
                        WHERE phone_id = (SELECT p.phone_id FROM phones AS p
                            JOIN client_phones cp ON cp.phone_id = p.phone_id
                            JOIN client_info ci ON ci.client_id = cp.client_id
                            WHERE ci.client_id = '{client_id}');
                   """)
            conn.commit()
            cur.execute(f"""
                    DELETE FROM client_info 
                        WHERE client_id  = '{client_id}';
                    """)
            conn.commit()
        print("Данные клиента успешно удалены!")


# Функция для поиска клиента по имени, фамилии, email-у или номеру телефона
def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    if first_name == "" and last_name == "" and email == "" and phone == "":
        print("Недостаточно данных для поиска, запустите команду заново и укажите какие-либо данные!")
        pass
    else:
        with conn.cursor() as cur:
            cur.execute(f"""
                        SELECT DISTINCT  ci.client_id, ci.first_name, ci.last_name, ci.email, p.phone FROM client_info ci 
                            JOIN client_phones cp ON cp.client_id = ci.client_id 
                            JOIN phones p ON p.phone_id = cp.phone_id 
                            WHERE ci.first_name = '{first_name}' OR ci.last_name = '{last_name}' 
                                OR ci.email = '{email}' OR p.phone = '{phone}';
                        """)
            conn.commit()
            print("Клиент найден!")
            print(cur.fetchall())


# Функция для вывода всей информации о всех клиентах
def show_data_base(conn):
    with conn.cursor() as cur:
        cur.execute("""
                    SELECT ci.client_id, ci.first_name, ci.last_name, ci.email, p.phone FROM client_info ci
                        JOIN client_phones cp ON cp.client_id = ci.client_id 
                        JOIN phones p ON p.phone_id = cp.phone_id;
                    """)
        conn.commit()
        print(cur.fetchall())


# Функция для вывода всей информации о конкретном клиенте
def show_client_info(conn, client_id):
    if client_id == "":
        print("Недостаточно данных, запустите команду заново и укажите ID")
        pass
    else:
        with conn.cursor() as cur:
            cur.execute(f"""
                        SELECT ci.client_id, ci.first_name, ci.last_name, ci.email, p.phone FROM client_info ci
                            JOIN client_phones cp ON cp.client_id = ci.client_id 
                            JOIN phones p ON p.phone_id = cp.phone_id
                            WHERE ci.client_id = '{client_id}';
                        """)
            conn.commit()
            print(cur.fetchall())


# Функция для удаления БД
def delete_all(conn):
    with conn.cursor() as cur:
        cur.execute("""
                    DROP SCHEMA public CASCADE;
                    """)
        conn.commit()
        cur.execute("""
                    CREATE SCHEMA public;
                    """)
        conn.commit()
    print("База данных успешно удалена!")


with psycopg2.connect(database="", user="postgres", password="") as conn:
    command = ""
    while command != 11:
        print_menu()
        command = input("Введите команду:")
        if command.isdigit():
            if int(command) == 1:
                create_db(conn)
            elif int(command) == 2:
                print("Укажите данные клиента")
                first_name = input("Имя клиента: ")
                last_name = input("Фамилия клиента: ")
                email = input("Электронная почта клиента: ")
                phones = input("Телефон клиента: ")
                add_client(conn, first_name, last_name, email, phones)
            elif int(command) == 3:
                print("Добавить телефон клиента:")
                client_id = input("ID клиента: ")
                phone = input("Телефон клиента: ")
                add_phone(conn, client_id, phone)
            elif int(command) == 4:
                print("Укажите новые данные клиента")
                client_id = input("ID клиента: ")
                first_name = input("Имя клиента: ")
                last_name = input("Фамилия клиента: ")
                email = input("Электронная почта клиента: ")
                phones = input("Телефон клиента: ")
                change_client(conn, client_id, first_name, last_name, email, phones)
            elif int(command) == 5:
                print("Удалить телефон клиента")
                client_id = input("ID клиента: ")
                phone = input("Телефон клиента: ")
                delete_phone(conn, client_id, phone)
            elif int(command) == 6:
                print("Удалить данные клиента")
                client_id = input("ID клиента: ")
                delete_client(conn, client_id)
            elif int(command) == 7:
                print("Найти клиента")
                first_name = input("Имя клиента: ")
                last_name = input("Фамилия клиента: ")
                email = input("Электронная почта клиента: ")
                phone = input("Телефон клиента: ")
                find_client(conn, first_name, last_name, email, phone)
            elif int(command) == 8:
                show_data_base(conn)
            elif int(command) == 9:
                client_id = input("ID клиента: ")
                show_client_info(conn, client_id)
            elif int(command) == 10:
                delete_all(conn)
            elif int(command) == 11:
                print("Всего доброго!")
                break
            elif int(command) > 11 or int(command) < 1:
                print("Введена неверная команда! Введите число от 1 до 11!")
        else:
            print("Введена неверная команда! Введите число от 1 до 11!")
conn.close()
