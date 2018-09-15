# Foodprint-backend

## To Run locally

Prerequisites:
  1. Have docker installed
  2. Have `make` installed
  3. You need to have file called `local_settings.py` in the root of the repo. 
     It's gitignore-d as it should contain the DB connection settings as well
     as a SECRET_KEY random string var

Running commands:
  - Run `make` to have the application container built and started locally.
    This creates a Django development server instance running on
    http://127.0.0.1:8000/

  - If you want to instead drop into a shell in the container, or run a 
    command different than the default, you can do e.g. `make run /bin/bash`
