<<<<<<< HEAD
"""
Global settings manager + instanciator of the database client instance.

No module other than this one has direct access to the database client;
this ensures that we have a single source of truth in regards to transactions
as well as making sure that we never accidentally swap from the production
database to the testing database.
"""
import os
import logging
from pymongo import MongoClient
from config.main import DB_URI


class Database:
    """
    Utility class that holds the main database client instance.
    """
    client: MongoClient = None

    def has_been_initialized(self) -> bool:
        """
        Returns true if the instance's MongoClient has been initialized,
        else returns false.
        """
        return bool(self.client) and isinstance(self.client, MongoClient)

    def connect_to_mongo(self) -> None:
        """
        Instanciates a connection of the mongo client to the given DB_URI.

        If the client is already instanciated, then is lazy and does nothing.
        """
        if not self.has_been_initialized():
            self.client = MongoClient(DB_URI)

    def close_connection_to_mongo(self) -> None:
        """
        Closes the client's connection to mongo if it has been initialized.
        """
        if self.has_been_initialized():
            self.client.close()


database_client = Database()


def is_testing() -> bool:
    """
    Simple but dynamic function that returns the testing status.
    Can be used for things other than database config.
    """
    return os.environ.get("_called_from_test") == "True"


def get_database_client_name() -> str:
    """
    Dynamically return the name of the current database.

    Returns the production database name if not testing.
    """
    db_name = "underline" if not is_testing() else "pytest"
    return db_name


def get_database():
    """
    Returns the global instance of the database client.

    Guarantees that the client is initialized. If it is not,
    then it bootstraps it within this function.
    """
    if not database_client.has_been_initialized():
        database_client.connect_to_mongo()
    return database_client.client


def clear_test_collections():
    """
    Runs through every collection in the testing database and deletes
    all of the documents within that collection.
    """
    test_database = database_client.client["pytest"]
    test_collection_names = test_database.list_collection_names()

    for collection in test_collection_names:
        test_database[collection].delete_many({})
=======
"""
Global settings manager + instanciator of the database client instance.

No module other than this one has direct access to the database client;
this ensures that we have a single source of truth in regards to transactions
as well as making sure that we never accidentally swap from the production
database to the testing database.
"""
import os
from pymongo import MongoClient
from config.main import DB_URI


class Database:
    """
    Utility class that holds the main database client instance.
    """
    client: MongoClient = None

    def has_been_initialized(self) -> bool:
        """
        Returns true if the instance's MongoClient has been initialized,
        else returns false.
        """
        return bool(self.client) and isinstance(self.client, MongoClient)

    def connect_to_mongo(self) -> None:
        """
        Instanciates a connection of the mongo client to the given DB_URI.

        If the client is already instanciated, then is lazy and does nothing.
        """
        if not self.has_been_initialized():
            self.client = MongoClient(DB_URI)

    def close_connection_to_mongo(self) -> None:
        """
        Closes the client's connection to mongo if it has been initialized.
        """
        if self.has_been_initialized():
            self.client.close()


database_client = Database()


def is_testing() -> bool:
    """
    Simple but dynamic function that returns the testing status.
    Can be used for things other than database config.
    """
    return os.environ.get("_called_from_test") == "True"


def get_database_client_name() -> str:
    """
    Dynamically return the name of the current database.

    Returns the production database name if not testing.
    """
    db_name = "underline" if not is_testing() else "pytest"
    return db_name


def get_database():
    """
    Returns the global instance of the database client.

    Guarantees that the client is initialized. If it is not,
    then it bootstraps it within this function.
    """
    if not database_client.has_been_initialized():
        database_client.connect_to_mongo()
    return database_client.client


def clear_test_collections():
    """
    Runs through every collection in the testing database and deletes
    all of the documents within that collection.
    """
    test_database = database_client.client["pytest"]
    test_collection_names = test_database.list_collection_names()

    for collection in test_collection_names:
        test_database[collection].delete_many({})
>>>>>>> 559d0efdd9290f5413cd1bad9600779541811d95
