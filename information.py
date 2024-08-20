import psycopg2
from psycopg2.sql import SQL, Identifier


# Функция, создающая структуру БД (таблицы)
def create_db(conn):
    with conn.cursor() as cur:
        cur.execute("""
        DROP TABLE Phone;
        DROP TABLE Client;
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS Client(
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(80) NOT NULL,
            last_name VARCHAR(80) NOT NULL,
            email VARCHAR(80) NOT NULL UNIQUE
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS Phone(
            phone_id SERIAL PRIMARY KEY,
            phone VARCHAR(15),
            client_id INTEGER REFERENCES Client(id)
        );
        """)
        conn.commit()


# Функция, позволяющая добавить нового клиента
def add_client(conn, first_name, last_name, email, phone=None):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO Client (first_name, last_name, email)
            VALUES (%s, %s, %s)
            RETURNING id, first_name, last_name, email;
            """, (first_name, last_name, email))
        return cur.fetchone()


# Функция, позволяющая добавить телефон для существующего клиента
def add_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO Phone(client_id, phone)
            VALUES(%s, %s)
            RETURNING client_id, phone;
            """, (client_id, phone))
        return cur.fetchone()


# Функция, позволяющая изменить данные о клиенте
def change_client(conn, id, first_name=None, last_name=None, email=None):
    with conn.cursor() as cur:
        arg_list = {'first_name': first_name,
                    'last_name': last_name, 'email': email}
        for key, arg in arg_list.items():
            if arg:
                cur.execute(SQL('UPDATE Client SET {}=%s WHERE id = %s'
                                ).format(Identifier(key)), (arg, id))
        cur.execute("""
            SELECT * FROM Client
            WHERE id = %s;
            """, id)
        return cur.fetchall()


# # Функция, позволяющая удалить телефон для существующего клиента
def delete_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM Phone
            WHERE client_id=%s
            RETURNING client_id;
            """, (client_id,))
        return cur.fetchone()


# Функция, позволяющая удалить существующего клиента.
def delete_client(conn, id):
    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM Client
            WHERE id = %s
            """, (id,)) 
        return cur.fetchone()


# Функция, позволяющая найти клиента по его данным: имени, фамилии, email
def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT * FROM Client c
            LEFT JOIN Phone p ON c.id = p.client_id
            WHERE c.first_name=%s OR c.last_name=%s OR c.email=%s OR p.phone=%s;
            """, (first_name, last_name, email, phone,))
        return cur.fetchone()[0]


if __name__ == '__main__':
    with psycopg2.connect(database='pysql', user='postgres',
                          password='d01m07y10') as conn:
        create_db(conn)
        print(add_client(conn, 'Asi', 'Reit', 'Asi@mail.ru'))
        print(add_phone(conn, '1', '89895280495'))
        print(change_client(conn, '1', 'Hi', 'Sor'))
        print(delete_phone(conn, '1', '89895280495'))
        print(delete_client(conn, 1))
        print(find_client(conn, 'Hi'))

conn.close()
