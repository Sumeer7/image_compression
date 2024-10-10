# db/mysql_connection.py
import mysql.connector
from mysql.connector import Error
import logging
from threading import Lock
from .db_connection_interface import DBConnection
import configparser
import os


class MySQLConnection(DBConnection):
    _instance = None
    _lock = Lock()  # Lock for thread-safe singleton access

    def __new__(cls, *args, **kwargs):
        with cls._lock:  # Acquire the lock to ensure thread safety
            if not cls._instance:
                cls._instance = super(MySQLConnection, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.load_config()
            self.connection = None
            self.initialized = True

    def load_config(self):
        # Load the database configuration from properties file
        config = configparser.ConfigParser()
        config_file_path = os.path.join(os.path.dirname(__file__), 'config.properties')

        if not os.path.exists(config_file_path):
            logging.error("Configuration file 'config.properties' not found.")
            raise FileNotFoundError("Configuration file 'config.properties' not found.")

        config.read(config_file_path)
        self.host = config['Database']['host']
        self.user = config['Database']['user']
        self.password = config['Database']['password']
        self.database = config['Database']['database']

    def connect(self):
        if self.connection is None or not self.connection.is_connected():
            try:
                self.connection = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database
                )
                if self.connection.is_connected():
                    logging.info(f"MySQL Database '{self.database}' connection successful")
            except Error as e:
                logging.error(f"Error '{e}' occurred during MySQL connection")
                self.connection = None

    def insert(self, query, params=None):
        cursor = self.connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            logging.info("Insert operation successful.")
        except Error as e:
            logging.error(f"Error '{e}' occurred during insert: {query}")
            self.connection.rollback()
        finally:
            cursor.close()

    def get(self, query, params=None):
        cursor = self.connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchall()
            logging.info("Select operation successful.")
            return result
        except Error as e:
            logging.error(f"Error '{e}' occurred during get: {query}")
            return None
        finally:
            cursor.close()

    def create_tables(self):
        cursor = self.connection.cursor()
        try:
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS requests (
                request_id VARCHAR(255) PRIMARY KEY,
                status VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id VARCHAR(36) PRIMARY KEY,
                request_id VARCHAR(255),
                serial_number INT,
                product_name VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (request_id) REFERENCES requests(request_id)
            )
            ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS images (
                id VARCHAR(36) PRIMARY KEY,
                product_id VARCHAR(36),
                input_url TEXT,
                output_url TEXT,
                status VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
            ''')

            self.connection.commit()
            logging.info("Database tables created or verified successfully.")

        except Exception as e:
            logging.error(f"An error occurred while creating tables: {e}")

        finally:
            cursor.close()

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logging.info("MySQL connection closed.")
