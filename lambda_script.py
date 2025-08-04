import json
import urllib.request
import boto3
import email

SLACK_WEBHOOK_URL = "slack webhook url here"
S3_BUCKET = "backet here"

s3 = boto3.client('s3')

def lambda_handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        response = s3.get_object(Bucket=bucket, Key=key)
        raw_email = response['Body'].read().decode('utf-8')

        msg = email.message_from_string(raw_email)
        subject = msg['Subject']
        body = ""

        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode()
                    break
        else:
            body = msg.get_payload(decode=True).decode()

        # ✅ Send payload matching Slack workflow variable
        payload = {
            "alert_message": f"📊 QuickSight Alert\n*{subject}*\n{body}"
        }
        req = urllib.request.Request(
            SLACK_WEBHOOK_URL,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        urllib.request.urlopen(req)

    return {"status": "success"}
