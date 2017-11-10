import json
import psycopg2
from psycopg2.extras import execute_values
from itertools import product
import re


def db_connection():
    """Creates a connection to postgres or prints the error"""
    try:
        return psycopg2.connect(
            """ dbname='name' user='username'
            host='localhost' password='password' """)
    except (Exception, psycopg2.DatabaseError) as error:
        print('Cannot connect to database')
        print(error)


def create_table(connection):
    """Creates tables to store email data on first run of the script"""
    cursor = connection.cursor()
    tables = (
        """
        CREATE TABLE emails (
            email_id SERIAL PRIMARY KEY,
            timestamp TIMESTAMPTZ
        )
        """,
        """
        CREATE TABLE recipients (
            email_id INTEGER PRIMARY KEY,
            address TEXT [],
            FOREIGN KEY (email_id)
            REFERENCES emails (email_id)
        )
        """,
        """
        CREATE TABLE words (
            address VARCHAR(255),
            word VARCHAR(255),
            count INTEGER NOT NULL
        )
        """)

    for table in tables:
        cursor.execute(table)
    connection.commit()
    cursor.close()


words = {}


def save_email_data(emails):
    """Parse each email thread and create inserts for each email.
    Instead of inserting each email and word occurance I used a dict
    cache with a tuple of the word and email as a key to store all
    occurances in the file. Disabled auto commit and only commit
    once to improve performance."""
    cursor = connection.cursor()

    for email in emails['emails']:
        timestamp = email['timestamp']
        recipients = email['recipients']
        subject = re.sub("[^\w]", " ", email['subject']).split()

        try:
            cursor.execute("""INSERT INTO emails (timestamp)
                VALUES (%s) RETURNING email_id;""", (timestamp,))
            email_id = cursor.fetchone()[0]
            cursor.execute("INSERT INTO recipients VALUES (%s, %s);",
                           (email_id, recipients))
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

        for pair in product(recipients, subject):
            if pair in words:
                words[pair] += 1
            else:
                words[pair] = 1

    connection.commit()
    cursor.close()


def parse_json(filename):
    """Parse the file and commit each upload. Once finished parsing,
    Transform the words dictionary into a list of tuples. Then using
    batch insert put all records in the db in one commit."""
    with open(filename, 'r') as f:
        data = json.load(f)

        for emails in data['uploads']:
            save_email_data(emails)

        words_data = []
        for k, v in words.items():
            e, w = k
            words_data.append((e, w, v))

        try:
            cursor = connection.cursor()
            execute_values(cursor, """INSERT INTO words (address, word, count)
             VALUES %s""", words_data)
            connection.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            connection.close()
            print('Upload Completed!')


if __name__ == '__main__':
    connection = db_connection()
    create_table(connection)
    parse_json('uploads.json')
