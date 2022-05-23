import boto3
from pprint import pprint
from email_sections import cost_visuals
ses = boto3.client('ses')


def send_email(vis):
    x = ses.send_email(
        Source='mwhamilton6@gmail.com',
        Destination={
            'ToAddresses': ['mwhamilton6@gmail.com'],
        },
        Message={
            'Subject': {
                'Data': 'Testing'
            },
            'Body': {
                'Html': {
                    'Data': f'{vis["daily_table"]}'
                }
            }
        }
    )


def main():
    vis = cost_visuals.main()
    send_email(vis)


if __name__ == '__main__':
    main()