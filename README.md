# Deployment
1. (follow instructions)[https://www.geeksforgeeks.org/how-to-install-python-packages-for-aws-lambda-layers/]
1. `docker cp 1ac0a8674994:/layer/mypackage.zip C:\Users\mwham\Documents\repos\cta-tracker\dependency_layer`
2. `python deploy.py`


# TODO
4. Convert arrival time to seconds after midnight to show late night runs
5. Figure out weekday, saturday, sunday schedule
6. Identify trips that are just subtrips of another and merge them (be sure to shift if the starts are different)
7. Figure out zoom
8. merge parsed and rollup into just rollup