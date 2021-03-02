# Unit/Systems testing with Pytest & FastAPI

##### TL;DR:

- `pytest` is a well modern, well-known testing framework that uses runtime dependency injection in order to cut down on code repetition. It achieves this by using functions that can be run anywhere in the testing suite called `fixtures`.
- Systems tests are structures by module -> endpoint -> individual tests
  - System (end-to-end) tests only send requests through the FastAPI test client
  - Executing `util` code directly here is forbidden unless it is to check the validity of the returned data



## Pytest Fixtures

[Fixtures](https://docs.pytest.org/en/stable/fixture.html) enable us to write functions that make tests isolated, repeatable, predictable, and easily refactored. 

All fixtures should go in a special file at every testing directory called [`conftest.py`](https://docs.pytest.org/en/stable/fixture.html?highlight=conftest#conftest-py-sharing-fixtures-across-multiple-files)



Fixtures can:

- Be used to do relevant setup/teardown actions that run around each test automatically (e.g. wipe test database)
- Provide stable dependency injection for tests that require other objects to run
- Cut down on code repetition by sharing fixtures with all submodules and subtests



`pytest` docs are pretty awful when it comes to actually explaining how to use or write fixtures so here's a little crash course.

### Global setup/teardown

Two special methods exist for setup/teardown. Both are found in `tests/conftest.py`.

- `pytest_configure`
  - The first method call here is to change the environment variable flag for testing. This line MUST be the first one executed.
  - Put all global setups here (e.g. cache inits)
- `pytest_unconfigure`
  - Global teardown calls
  - the `os.environ["_called_from_test"] = "False"` **MUST** be the first call here. (else wrong databases will be erased)



### Fixtures that "run around" tests

The `@pytest.fixture(autouse=True)` decorator lets us make a function that executes after (or before) each test is run. 

This can be super useful for ensuring that the global state of the application is exactly the same going into a test as well as coming out.



### Scoped Fixtures

By far the most common type of fixture (and the most useful). Using the `@pytest.fixture(scope="function")` decorator we can create a method that can be used anywhere and can even return a function.

Fixtures are not meant to be called directly (pytest will complain). Instead they are meant to be passed into a function as a parameter. Here's an example:

- ##### Pytest fixture example - dependency injection

  - Let's say we needed a `datetime` object in order to run a test. The significance of the actual value of the `datetime` object is important but not constant, meaning that it might need to be refactored in the near future

  - The test might look something like:

    - ```python
      class TestDatetimeClass:
        def test_datetime_object_valid(self):
          datetime_to_test = create_datetime_object()
          assert check_datetime_object_is_valid(datetime_to_test)
      ```

      - Assume `create_datetime_object()` and `check_datetime_object_is_valid()` are valid helper functions that already exist and work correctly

  - This works and is fine, but what if we want to modify `datetime_to_test`? 

    - The code inside the test can become complex and overwhelming, even with just a few extra method calls
    - Code that doesn't directly affect the test shouldn't be _in_ the test to begin with, they just obfuscate the intent

  - The logical step is to change the `create_datetime_object()` method itself to include the modifications

    - While this works, it has two downsides:
      1. we're still having to create a temporary object inside the test, which makes it unclear if we need the object (i.e. the object created is test-impactful) or if it is not
      2. Other modules that want to use this function must now import it, meaning that there is a single source of functions (or even worse, a spread of functions) that must be imported from random test files to be shared.

  - Pytest fixtures fix all of these problems. Here's what the test would look like using a fixture:

    - ```python
      class TestDatetimeClass:
        def test_datetime_object_valid(self, datetime_object):
          assert check_datetime_object_is_valid(datetime_object)
        
          
      # this is what the fixture could would look like inside a separate `conftest.py` file
      @pytest.fixture(scope="function")
      def datetime_object():
        valid_datetime = datetime.now()
        return valid_datetime
      ```

  - Couple of things to note about this:

    - Clarity and intent is immediate - the dependency needed for the test is shown _in the method signature_ itself; no need to guess what objects inside the test are the important ones or what utility methods are vital.
    - This fixture can be called **anywhere** in the test path, including other tests in different files and utility methods.

  While simple, the example above should be useful enough to at least show the power and expressiveness we get from using fixtures. For more complex examples you can look to the pytest docs (links above) or some of the `conftest.py` methods in our codebase.





## Test Structure (Unit/Systems)

The structure of the tests might look a little scary at first because of the nested classes but it's actually a very simple structure that allows us to be flexible and modular with how we run our tests.



#### Test classes and files

Basically, The easiest way to explain the structure of a test and its classes is to show one, but here are some general pointers:

- Tests should be separated on a per-file-basis unless they share a lot of small util functions that don't quite deserve to be fixtures, or if the tests make sense together (e.g. users util unit tests).
  - This lets us make as many meaningful util functions as we want that all make sense within the scope of the test file



Take our systems test for user login endpoints as a simple example:

- We start with the purpose (or scope) of what is being tested in the file as a whole

  - ```python
    # file: tests/test_user_login.py
    
    class TestUserLoginEndpoint:
    ```

    - Keep in mind that the only reason we use classes is to make it easy to see what test is being ran and to make meaningful self-documenting code, so as long as the class tells what it's gonna be testing, it's probably good
    - The classes, both top-level and nested, should start with `Test` 

  - Finally, we can write the tests in their corresponding subclass.

    - ```python
      class TestUserLoginEndpoint:
        def test_login_response_token_good(self):
          """
          Logs in and tries to decode the token, expecting success.
          """
          pass
      
        def test_nonexistent_user_fail(self):
          """
          Tries to login with a nonexistent user, expecting a 404.
          """
          pass
      ```

    - Good test naming is important and can be verbose; brevity is 100x less important than clarity and know what the tests are actually testing on a single look

    - Tests should be pretty self-documenting, but it's a great habit to leave a method docstring that explains exactly what the test is actually testing and if it expects failure or success. If it needs to be refactored later on, the original intent will be clear even if the code is outdated.



### Final notes about tests

Opt for a more verbose and abstraction-abusing style when writing tests. Although it may seem easy now to just write in a couple of lines that do something very specific in a test because it's quicker, if that test ever needs to be refactored, it will be a pain to track those loose lines down and change them

Write tests with care and write enough of them to cover at least the major pass/fail scenarios for whatever you're testing. 



_"If you let your tests rot, then your code will rot too"_
