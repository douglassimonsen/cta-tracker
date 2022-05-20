import boto3
ses = boto3.client('ses')


def send_email():
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
                    'Data': '<p>hi</p><p>bye</p>'
                }
            }
        }
    )