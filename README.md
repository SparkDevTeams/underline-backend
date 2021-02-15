# SparkDev x Underline Backend

![Pytest Status](https://github.com/SparkDevTeams/underline-backend/workflows/Python%20application/badge.svg?branch=master)



### Environment Setup

- WSL
  - If you are running windows you might want to look into using [Windows Subsystem for Linux](https://docs.microsoft.com/en-us/windows/wsl/install-win10)
  - This will allow you to run a UNIX environment and make your life 10x easier on windows

- Python environment setup
  - The project uses python3.9, install instructions [here](https://www.python.org/downloads/release/python-390/)
- `pip` dependencies
  - Once python3.9 is installed (you should be able to run `python3.9 --version` ), we have to install the packages for the project
  - In the root repo directory (where all of the folders are) run `python3.9 -m pip install -r requirements.txt`
- Adding environment variables
  - [Unix](https://kb.iu.edu/d/abcl)
  - [Windows](https://www.architectryan.com/2018/08/31/how-to-change-environment-variables-on-windows-10/)
- Running tests
  - The project uses `pytest` to test the code before passing the CI/CD pipeline
  - Run `pytest` in the root directory of the repo to run all of the tests (the `pytest` binary should install automatically with the other `pip` packages)