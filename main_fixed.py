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
def create_db(cur):
    cur.execute("""
            CREATE TABLE IF NOT EXISTS client_info(
                client_id SERIAL PRIMARY KEY,
                first_name VARCHAR(60) NOT NULL,
                last_name VARCHAR(60) NOT NULL,
                email VARCHAR(120) NOT NULL
                );
            """)
    cur.execute("""
            CREATE TABLE IF NOT EXISTS phones(
                phone_id SERIAL PRIMARY KEY,
                phone VARCHAR(60) NOT NULL
                );
            """)
    cur.execute("""
            CREATE TABLE IF NOT EXISTS client_phones(
                phone_id INTEGER NOT NULL REFERENCES phones(phone_id),
                client_id INTEGER,
                FOREIGN KEY (client_id) REFERENCES client_info(client_id)
                );
            """)
    cur.close()
    print("Таблицы успешно созданы!")


# Функция для добавления нового клиента
def add_client(cur, first_name, last_name, email, phone):
    values = ({"first_name": first_name, "last_name": last_name, "email": email, "phone": phone})
    cur.execute("""
            INSERT INTO client_info(first_name, last_name, email)
                VALUES
                (%(first_name)s, %(last_name)s, %(email)s);
            """, values)
    cur.execute("""
            INSERT INTO phones(phone)
                VALUES
                (%(phone)s);
            """, values)
    cur.execute("""
            INSERT INTO client_phones(phone_id, client_id)
                VALUES((select MAX(phone_id) from phones), (select MAX(client_id) from client_info))
            """)
    cur.close()
    print("Данные клиента успешно добавлены!")


# Функция для добавления номера телефона для существующего клиента
def add_phone(cur, client_id, phone):
    if client_id == "":
        pass
    else:
        value = ({"phone": phone})
        cur.execute("""
            INSERT INTO phones(phone) 
                VALUES
                (%(phone)s);
                """, value)
        values = ({"client_id": client_id})
        cur.execute("""
            INSERT INTO client_phones(phone_id, client_id) 
                VALUES((SELECT MAX(phone_id) from phones), %(client_id)s);
            """, values)
        cur.close()
    print("Новый контактный телефон клиента успешно добавлен!")


# Функция для изменения данных клиента клиента
def change_client(cur, client_id, first_name=None, last_name=None, email=None, phone=None):
    if first_name == "":
        pass
    else:
        values = ({"first_name": first_name, "client_id": client_id})
        cur.execute("""
                UPDATE client_info
                    SET first_name = %(first_name)s
                    WHERE client_id = %(client_id)s;
                """, values)
    if last_name == "":
        pass
    else:
        values = ({"last_name": last_name, "client_id": client_id})
        cur.execute("""
                UPDATE client_info
                    SET last_name = %(last_name)s
                    WHERE client_id = %(client_id)s;
                """, values)
    if email == "":
        pass
    else:
        values = ({"email": email, "client_id": client_id})
        cur.execute("""
                UPDATE client_info
                    SET email  = %(email)s
                    WHERE client_id = %(client_id)s;
                """, values)
    if phone == "":
        pass
    else:
        values = ({"phone": phone, "client_id": client_id})
        cur.execute("""
                UPDATE phones
                    SET phone  = %(phone)s
                    WHERE phone_id = (SELECT phone_id FROM client_phones
                        GROUP BY client_id, phone_id
                        HAVING client_id = %(client_id)s);
                """, values)
    cur.close()
    print("Данные клиента успешно изменены!")


# Функция для удаления телефона существующего клиента
def delete_phone(cur, client_id, phone):
    if client_id == "":
        pass
    else:
        values = ({"phone": phone, "client_id": client_id})
        cur.execute("""
                DELETE FROM client_phones
                    WHERE phone_id = (SELECT DISTINCT p.phone_id FROM phones AS p
                        JOIN client_phones cp ON cp.phone_id = p.phone_id
                        JOIN client_info ci ON ci.client_id = cp.client_id
                        WHERE ci.client_id = %(client_id)s AND p.phone = %(phone)s);
                """, values)
        value = ({"phone": phone})
        cur.execute("""
                DELETE FROM phones
                    WHERE phone = %(phone)s;
                """, value)
        cur.close()
    print("Контактный телефон клиента успешно удален!")


# Функция для удаления существующего клиента
def delete_client(cur, client_id):
    if client_id == "":
        print("Не введен ID клиента! Введите ID клиента")
        pass
    else:
        value = ({"client_id": client_id})
        cur.execute("""
                DELETE FROM client_phones
                    WHERE phone_id = (SELECT p.phone_id FROM phones AS p
                        JOIN client_phones cp ON cp.phone_id = p.phone_id
                        JOIN client_info ci ON ci.client_id = cp.client_id
                        WHERE ci.client_id = %(client_id)s);
                """, value)
        cur.execute("""
                DELETE FROM phones
                    WHERE phone_id = (SELECT p.phone_id FROM phones AS p
                        JOIN client_phones cp ON cp.phone_id = p.phone_id
                        JOIN client_info ci ON ci.client_id = cp.client_id
                        WHERE ci.client_id = %(client_id)s);
                """, value)
        cur.execute("""
                DELETE FROM client_info 
                    WHERE client_id  = %(client_id)s;
                """, value)
        cur.close()
    print("Данные клиента успешно удалены!")


# Функция для поиска клиента по имени, фамилии, email-у или номеру телефона
def find_client(cur, first_name=None, last_name=None, email=None, phone=None):
    if first_name == "" and last_name == "" and email == "" and phone == "":
        print("Недостаточно данных для поиска, запустите команду заново и укажите какие-либо данные!")
        pass
    else:
        values = ({"first_name": first_name, "last_name": last_name, "email": email, "phone": phone})
        cur.execute("""
                    SELECT DISTINCT  ci.client_id, ci.first_name, ci.last_name, ci.email, p.phone FROM client_info ci 
                        JOIN client_phones cp ON cp.client_id = ci.client_id 
                        JOIN phones p ON p.phone_id = cp.phone_id 
                        WHERE ci.first_name = %(first_name)s OR ci.last_name = %(last_name)s 
                            OR ci.email = %(email)s OR p.phone = %(phone)s;
                    """, values)
        cur.close()
        print("Клиент найден!")
        print(cur.fetchall())


# Функция для вывода всей информации о всех клиентах
def show_data_base(cur):
    cur.execute("""
                SELECT ci.client_id, ci.first_name, ci.last_name, ci.email, p.phone FROM client_info ci
                    JOIN client_phones cp ON cp.client_id = ci.client_id 
                    JOIN phones p ON p.phone_id = cp.phone_id;
                """)
    cur.close()
    print(cur.fetchall())


# Функция для вывода всей информации о конкретном клиенте
def show_client_info(cur, client_id):
    if client_id == "":
        print("Недостаточно данных, запустите команду заново и укажите ID")
        pass
    else:
        value = ({"client_id": client_id})
        cur.execute("""
                    SELECT ci.client_id, ci.first_name, ci.last_name, ci.email, p.phone FROM client_info ci
                        JOIN client_phones cp ON cp.client_id = ci.client_id 
                        JOIN phones p ON p.phone_id = cp.phone_id
                        WHERE ci.client_id = %(client_id)s;
                    """, value)
        cur.close()
        print(cur.fetchall())


# Функция для удаления БД
def delete_all(cur):
    cur.execute("""
                DROP SCHEMA public CASCADE;
                """)
    cur.execute("""
                CREATE SCHEMA public;
                """)
    cur.close()
    print("База данных успешно удалена!")


with psycopg2.connect(database="555", user="postgres", password="89223395963") as conn:

        command = ""
        while command != 11:
            print_menu()
            command = input("Введите команду:")
            if command.isdigit():
                if int(command) == 1:
                    with conn.cursor() as cur:
                        create_db(cur)
                elif int(command) == 2:
                    with conn.cursor() as cur:
                        print("Укажите данные клиента")
                        first_name = input("Имя клиента: ")
                        last_name = input("Фамилия клиента: ")
                        email = input("Электронная почта клиента: ")
                        phones = input("Телефон клиента: ")
                        add_client(cur, first_name, last_name, email, phones)
                elif int(command) == 3:
                    with conn.cursor() as cur:
                        print("Добавить телефон клиента:")
                        client_id = input("ID клиента: ")
                        phone = input("Телефон клиента: ")
                        add_phone(cur, client_id, phone)
                elif int(command) == 4:
                    with conn.cursor() as cur:
                        print("Укажите новые данные клиента")
                        client_id = input("ID клиента: ")
                        first_name = input("Имя клиента: ")
                        last_name = input("Фамилия клиента: ")
                        email = input("Электронная почта клиента: ")
                        phones = input("Телефон клиента: ")
                        change_client(cur, client_id, first_name, last_name, email, phones)
                elif int(command) == 5:
                    with conn.cursor() as cur:
                        print("Удалить телефон клиента")
                        client_id = input("ID клиента: ")
                        phone = input("Телефон клиента: ")
                        delete_phone(cur, client_id, phone)
                elif int(command) == 6:
                    with conn.cursor() as cur:
                        print("Удалить данные клиента")
                        client_id = input("ID клиента: ")
                        delete_client(cur, client_id)
                elif int(command) == 7:
                    with conn.cursor() as cur:
                        print("Найти клиента")
                        first_name = input("Имя клиента: ")
                        last_name = input("Фамилия клиента: ")
                        email = input("Электронная почта клиента: ")
                        phone = input("Телефон клиента: ")
                        find_client(cur, first_name, last_name, email, phone)
                elif int(command) == 8:
                    with conn.cursor() as cur:
                        show_data_base(cur)
                elif int(command) == 9:
                    with conn.cursor() as cur:
                        client_id = input("ID клиента: ")
                        show_client_info(cur, client_id)
                elif int(command) == 10:
                    with conn.cursor() as cur:
                        delete_all(cur)
                elif int(command) == 11:
                    print("Всего доброго!")
                    break
                elif int(command) > 11 or int(command) < 1:
                    print("Введена неверная команда! Введите число от 1 до 11!")
            else:
                print("Введена неверная команда! Введите число от 1 до 11!")
conn.close()
