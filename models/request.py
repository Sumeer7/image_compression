from datetime import datetime


class RequestModel:
    def __init__(self, MySQLConnection):
        self.db_connection = MySQLConnection
        self.db_connection.connect()

    def create_request(self, request_id, status):
        """Create a new request record."""
        created_at = datetime.utcnow()
        updated_at = created_at
        self.db_connection.insert(
            '''
            INSERT INTO requests (request_id, status, created_at, updated_at)
            VALUES (%s, %s, %s, %s)
            ''',
            (request_id, status, created_at, updated_at)
        )

    def get_request(self, request_id):
        """Retrieve a request record by request_id."""
        return self.db_connection.get(
            'SELECT request_id, status, created_at, updated_at FROM requests WHERE request_id = %s',
            (request_id,)
        )

    def update_request_status(self, request_id, new_status):
        """Update the status of a request record."""
        updated_at = datetime.utcnow()
        self.db_connection.insert(
            'UPDATE requests SET status = %s, updated_at = %s WHERE request_id = %s',
            (new_status, updated_at, request_id)
        )

    def __del__(self):
        """Ensure the database connection is closed when the object is deleted."""
        self.db_connection.close()
