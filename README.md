# SparkDev x FUT Backend ![Pytest Status](https://github.com/SparkDevTeams/underline-backend/workflows/Python%20application/badge.svg?branch=master)

## Developer Bootstrap

### Core dependencies

The project uses:

- `Python 3.9.1`
- `pip 20.2.3 (python 3.9)`

### Running the server locally

- `python` requirements can be installed with `pip install -r requirements.txt`
- the local server can be ran with `uvicorn app:app` 

### Deploying the server in production mode

- The current server is setup to run with heroku, and has both `Procfile` and `runtime.txt` files
- If deploying outside of heroku, the main script to run is `run.sh` which will install the dependencies (if any updates have occured) and run the production server
  - the core command to run the web server in production mode is:
    - `gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app --bind 0.0.0.0:$PORT --access-logfile - --log-level info`
    - where `$PORT` is the local open port set by the environment.
- Before deployment, make sure all of the environment variables for the project have been set (check the `Keys and variables` section of this document)

### REST API Documentation

- `FastAPI` offers dynamic REST API documentation with swagger and redoc, using the openAPI spec.
  - these docs can be found in the `/docs` and `/redoc` endpoints respectively
- The auto-generated docs rely on `pydantic` models for data types, and docstrings for each endpoint (held in the `docs` folder). Both of these are mentioned later on in the `Project Structure` section in detail.

### Linter & Test suite (`pylint` + `pytest`)

- A `pylintrc` file with the standard Google lint config is in the root folder and will provide detailed reports for `pylint`
- to run the linter on ALL project files at once (useful for CI/CD pipelines and checks), use the `lint.sh` script
- `pytest` is used to run all of the unit and integration tests for the project, all of which are located in the `tests/` folder

## Project Struture

### Main Code Sources

These are the modules that have most of the core logic and handle almost all of the code execution.

Modules here are grouped by their actions and their data so as to avoid table-sharing; providing the other modules with an interface for interacting with that data.

For example, if an endpoint for events (located in `routes/events.py`) needs to make a change to a `user` document in the database, it would have to go through the `user` interface laid out in `utils/users.py`.

This saves us the gigantic headache of coupled database tables, enabling us to change the internals of the modules as we please so long as we honor the interface we provide.

- #### Routes

  - Entry point for the actual routes that will be put on display through `FastAPI`. Here, routes and sub-routers are added along with input and output doc strings, models, and other pieces of documentation that outline how the client interacts with the backend.
  - Not a ton of code should be here, just incoming data, calls to the appropriate handler in `utils` and then outgoing data.
  - If changes to the core procedure being laid out in the handling of a route are made, it is critical to update the `description` and `summary` (declared in the `@router` decorators) as well to ensure up-to-date information reaches the documentation users.
  - For more info on the `@router` decorators, or any other `FastAPI` specific info, refer to the [`FastAPI` docs](https://fastapi.tiangolo.com/)

- #### Models

  - Using a modeling framework like `pydantic` helps tremendously in ensuring that the data coming in is valid and type secure.

    - Models can be pretty complex and have nested user-defined types, allowing the codebase to share a standard set of code and core models through inheritance.
    - All `pydantic` models import `BaseModel` for some added niceties (e.g. direct typecasting to `dicts` and `json`)
  - There is one **major** problem with pydantic and pymongo:
    - mongo relies on a unique `_id` field to be set either by the document, or by the database upon insertion. 
    - `pydantic` reads fields marked with a leading `_` as private/hidden and does not export them with exporting functions (such as `model.dict()`)
    - to get around this problem, we use some utility functions and special classes (covered later)
  - Some key notes on `pydantic` and `BaseModel`:
    - Special model classes were made to represent data _in the database_ _**as is**_. 
    - E.g. `models.users.User`, `models.events.Event`, etc.
    - These models inherit from a modified version of `pydantic.BaseModel` (located in `models.commons`) called `ExtendedBaseModel`.
      - This version of `BaseModel` will provide some extra features for it's children:
        - an auto-setter (upon instanciation) for the `_id` field that assigns a random uuid4 string to the field value
        - a `get_id` function that is guaranteed to return a valid ID (this should be the **only** way to ever access a pydantic model's `_id` field due to the mongo v. pydantic naming conflict)
        - an overriden `dict()` method that fixes the `_id` problem when casting the model to a python dict by calling `model.dict()`
  - Little code should recide in these models outside of just classes. If a module has a recurring import or user defined type they can be put here as well to avoid repeating code.

- #### Utils

  - Files in `utils` hold the interface for interacting with the database documents.
  - There are a handful of ulity functions that all either return, or operate on, a top-level model for the module
    - e.g. most of the handlers in `utils.users` operate on or return a `models.users.User` object
  - All of the methods here should be `async` to comply with `FastAPI` (it won't complain but it is a massive slowdown if we use mostly sync functions)
  - Helper methods and internals can be kept here as well, so long as the major outward module facing interface methods (e.g. `register_user`) are kept simple and clean.

### Assisting Code

Code here provides additional support to the main files or holds a small amount of semi-inelastic responsibilities that are easy to change but would have massive ripples accross the architecture if they weren't quarantined off.

- #### Docs

  - Holds simple strings with `FastAPI` documentation. This eventually ends up in the generated endpoint docs so write as if you were consuming the routes yourself.

- #### Config

  - #### Main

    - High level app-wide configuration as well as middleware goes here. Shouldn't really need to be touched a lot.
    - Also holds some key exports, namely `app`, the main `FastAPI` router object.

  - #### Database

    - Database configuration and instanciation. All instances and batch moves to the database are stored here, including helper methods for testing and constructors/destructors for the database instances.
    
  - Both of these modules, as well as all of the project-wide config, will be talked about in the next section

## Critical Knowledge

Being a monolithic project with lots of user based operations, there are many critical centers of code which can break the entire system if changed unwittingly. The next section will cover the most critical points of code which carry significant change that has effects on the whole system, and should be handled with the utmost care.

### Points of systemic change

#### Static Critical points

#### `config.main`

- the `config.main` module has two key jobs:
  1. instanciate the global `FastAPI` router instance that all subrouters get added to
  2. read and export the global secret environment variables
- the newly instanciated `FastAPI` router shouldn't be touched outside of the root `app` module, or the tests module.

#### `config.db`

- Instanciates and sets up the database connection to the `mongo` server using a singleton pattern that only ever allows for a single client object to exist
- Also handles the dynamic creation of testing databases and indexes

### Dynamic Critical points

These modules need to be updated anytime data is updated elsewhere for the project to run

#### the root `app` module

- the `app` module assembles three key components of the project:
  1. Adds the CORS hosts and origins to the `CORSMiddleware` handler for the entire router instance
     - if frontend domain names OR backend server hosts change, this list of hosts/origins **MUST** be updated to avoid CORS errors
  2. Imports and adds all of the subrouters from the `routes` module to the main router
     - if a new router is added, it must be imported and added here with an `app.include_router` call
  3. Setting up documentation schema, logging, and other middleware

### Keys and variables

There are two secret env vars that must be exported for the program to work on local/serverside deployments as well as CI/CD pipelines:

- `MONGO_DB_URI`: the db URI (with authentication embedded)
  - current value: `mongodb+srv://sparkdev:0sJQqy9n25Isx5Ui@cluster0.lw2ch.mongodb.net/?retryWrites=true&w=majority`
- `JWT_SECRET_KEY`: the key used for `JWT` token creation
  - current value: `00cb508e977fd82f27bf05e321f596b63bf2d9f2452829e787529a52e64e7439`



## Links & Resources

[FastAPI Docs](https://fastapi.tiangolo.com/)

[Pydantic Docs](https://pydantic-docs.helpmanual.io/usage/models/)

[Current heroku endpoint docs](https://sparkdev-underline.herokuapp.com/redoc)

lead backend maintainer: [@astherath](https://github.com/astherath)