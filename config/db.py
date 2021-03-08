"""
Global settings manager + instanciator of the database client instance.

No module other than this one has direct access to the database client;
this ensures that we have a single source of truth in regards to transactions
as well as making sure that we never accidentally swap from the production
database to the testing database.
"""
import os
from uuid import uuid4
from pymongo import MongoClient
from config.main import DB_URI


def get_database() -> MongoClient:
    """
    Returns a valid client to the database.

    Even if called multiple times, the same object will
    always be returned.
    """
    db_instance = _get_global_database_instance()
    return db_instance.get_database_client()


def close_connection_to_mongo() -> None:
    """
    Public facing method for closing the database connection
    """
    db_instance = _get_global_database_instance()
    db_instance.close_client_connection()


def get_database_client_name() -> str:
    """
    Returns the name of the database singleton.

    Should always have the database instanciated prior,
    in the impossible case that it doesn't, it raises an exception.
    """
    db_instance = _get_global_database_instance()
    #  breakpoint()
    return db_instance.get_database_name()


# Utils for the file that don't have any need to be actually inside the class
def _is_testing() -> bool:
    """
    Simple but dynamic function that returns the testing status.
    Can be used for things other than database config.
    """
    return os.environ.get("_called_from_test") == "True"


def _get_database_name_str() -> str:
    """
    Dynamically return the name of the current database.

    Returns the production database name if not testing.
    """
    if _is_testing():
        test_db_name = _generate_test_database_name()
        return test_db_name

    production_db_name = "underline"
    return production_db_name


def _generate_test_database_name() -> str:
    """
    Generates a unique but identifiable database name for testing.
    """
    testing_db_name_prefix = "pytest-"

    # we need to truncate to 38 bytes for mongo
    random_uuid_str = str(uuid4())[:10]

    testing_db_name_str = testing_db_name_prefix + random_uuid_str
    return testing_db_name_str


class Database:
    """
    Utility class that holds the main database client instance.
    """
    def __init__(self):
        """
        Creates a Database instance with a MongoClient set to the global DB_URI.
        """
        self.client = MongoClient(DB_URI)
        self.database_name = _get_database_name_str()

    def get_database_client(self) -> MongoClient:
        """
        Returns the instance's db client.
        """
        return self.client

    def close_client_connection(self) -> None:
        """
        Closes the client's connection to mongo.
        """
        self.client.close()

    def get_database_name(self) -> str:
        """
        Get the mongo client's current database name
        """
        return self.database_name

    def clear_test_collections(self) -> None:
        """
        Runs through every collection in the testing database and deletes
        all of the documents within that collection.

        Will not interact with the production database at all.
        """
        current_db_is_for_tests = self.__check_current_db_is_for_testing()

        if current_db_is_for_tests:
            db_name = self.database_name
            test_database = self.client[db_name]
            test_collection_names = test_database.list_collection_names()

            for collection in test_collection_names:
                test_database[collection].delete_many({})

    def delete_test_database(self) -> None:
        """
        Deletes the current testing database.

        Will never delete the production database, even if it
        is the current database being used.
        """
        current_db_is_for_tests = self.__check_current_db_is_for_testing()

        if current_db_is_for_tests:
            test_database_name = self.database_name
            self.client.drop_database(test_database_name)

    def __check_current_db_is_for_testing(self) -> bool:  # pylint: disable=invalid-name
        """
        Safety guard that checks the name of the current database as well
        as the current testing status flags to ensure the database is for tests.
        """
        return "test" in self.database_name and _is_testing()


# enforces singleton pattern behind the scenes
# must start uninstanciated so the env vars can load in prior
global_database_instance = None


def _get_global_database_instance() -> Database:
    """
    Primitive and dangerous method to get the database instance

    Assures that if you call this, the `global_database_instance` will
    be successfully instanciated before being returned.
    """
    global global_database_instance
    database_already_instanciated = __check_global_db_already_exists()

    if not database_already_instanciated:
        global_database_instance = Database()

    return global_database_instance


def __check_global_db_already_exists() -> bool:  # pylint: disable=invalid-name
    return isinstance(global_database_instance, Database)
