# Deployment
1. (follow instructions)[https://www.geeksforgeeks.org/how-to-install-python-packages-for-aws-lambda-layers/]
1. `docker cp 1ac0a8674994:/layer/mypackage.zip C:\Users\mwham\Documents\repos\cta-tracker\dependency_layer`
2. `python deploy.py`


# TODO
1. get schedule and stop order for bus
2. get schedule and stop order for train
3. Group stops into trips