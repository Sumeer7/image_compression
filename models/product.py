from datetime import datetime


class ProductModel:
    def __init__(self, MySQLConnection):
        self.db_connection = MySQLConnection
        self.db_connection.connect()

    def create_product(self, product_id, request_id, serial_number, product_name):
        """Create a new product record."""
        created_at = datetime.utcnow()
        self.db_connection.insert(
            '''
            INSERT INTO products (id, request_id, serial_number, product_name, created_at)
            VALUES (%s, %s, %s, %s, %s)
            ''',
            (product_id, request_id, serial_number, product_name, created_at)
        )

    def get_product_id(self, product_id):
        """Retrieve a product record by product_id."""
        return self.db_connection.get(
            'SELECT id, request_id, serial_number, product_name, created_at, updated_at FROM products WHERE id = %s',
            (product_id,)
        )

    def get_request_id(self, product_id):
        """Retrieve a product record by product_id."""
        return self.db_connection.get(
            'SELECT request_id FROM products WHERE id = %s',
            (product_id,)
        )

    def update_product(self, product_id, new_name):
        """Update a product's name."""
        updated_at = datetime.utcnow()
        self.db_connection.insert(
            'UPDATE products SET product_name = %s, updated_at = %s WHERE id = %s',
            (new_name, updated_at, product_id)
        )

    def __del__(self):
        """Ensure the database connection is closed when the object is deleted."""
        self.db_connection.close()
