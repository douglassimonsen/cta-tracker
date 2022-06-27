# Deployment
## Lambda
1. (follow instructions)[https://www.geeksforgeeks.org/how-to-install-python-packages-for-aws-lambda-layers/]
1. `docker cp 1ac0a8674994:/layer/mypackage.zip C:\Users\mwham\Documents\repos\cta-tracker\dependency_layer`
2. `python deploy.py`

## Database
1. Run `infrastructure/cloudformation/main.py`. This deploys the users, DB, VPC, and subnets for the project
2. Run `infrastructure/db/download_sched.py` for the schedule information. This info is mostly static (aka, I haven't thought of a good update mechanism), so we load it at the start.
3. Run `infrastructure/db/fill_db`. This will create the schema and load the schedule data by copying from `/schedules/raw` in the S3 bucket.

# Website Design
## Frontend
The frontend uses Vue for state management and D3 for the chart visualization
## Backend
The backend uses flask. Currently it's organized into the following files:

- `app.py` global configuration is set here
- `main.py` handles import order to avoid circular dependencies. The backend is run by calling this function
- `routes.py` contains all API endpoints
- `utils.py` contains utility functions that are used throughout the backend portion of the project

# TODO
4. Convert arrival time to seconds after midnight to show late night runs
5. Figure out weekday, saturday, sunday schedule
6. Identify trips that are just subtrips of another and merge them (be sure to shift if the starts are different)
8. merge parsed and rollup into just rollup
9. Zoom should keep x, y axes constant