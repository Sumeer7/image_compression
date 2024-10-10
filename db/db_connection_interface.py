from abc import ABC, abstractmethod


class DBConnection(ABC):
    @abstractmethod
    def connect(self):
        """Establish a connection to the database."""
        pass

    @abstractmethod
    def insert(self, query, params=None):
        """Insert data into the database."""
        pass

    @abstractmethod
    def get(self, query, params=None):
        """Retrieve data from the database."""
        pass

    @abstractmethod
    def close(self):
        """Close the database connection."""
        pass
