import requests
import os; os.chdir(os.path.dirname(os.path.abspath(__file__)))


def get_data():
    with open("sched.zip", "wb") as f:
        f.write(requests.get("https://www.transitchicago.com/downloads/sch_data/google_transit.zip").content)


def main():
    get_data()


if __name__ == '__main__':
    main()