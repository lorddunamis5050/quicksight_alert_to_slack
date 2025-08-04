# QuickSight Alerts to Slack

This repository contains the **AWS Lambda function and instructions** to forward **Amazon QuickSight KPI alerts** to **Slack** automatically.  
The solution uses **SES → S3 → Lambda → Slack** to convert QuickSight email alerts into Slack messages.

---

## 📌 Architecture

**Flow:**
QuickSight Alert → Amazon SES → S3 → AWS Lambda → Slack

**How It Works:**
1. QuickSight sends a **KPI alert email** to a verified **SES email address**.
2. Amazon SES stores the **raw email** in an **S3 bucket**.
3. An **S3 Event Notification** triggers the **Lambda function**.
4. Lambda parses the **email subject & body** and sends it to **Slack** using an **Incoming Webhook**.

---

## 🛠 Setup Instructions

### 1️⃣ Configure Amazon SES
1. **Verify your domain** in SES.
2. **Add MX record** in your domain DNS:
Host/Name: alerts
Value: inbound-smtp.<your-region>.amazonaws.com

3. **Create a Receipt Rule**:
- Condition: Email to `alerts@yourdomain.com`
- Action: Store in **S3 bucket** (e.g., `slack-alerts-bucket`)
- Enable the rule set

---

### 2️⃣ Configure S3 Bucket
1. Create an S3 bucket (e.g., `slack-alerts-bucket`).
2. Enable **Event Notification**:
- Event type: `All object create events`
- Trigger: **Lambda function**

---

### 3️⃣ Create the Lambda Function
1. Runtime: **Python 3.12+**
2. Attach IAM Role with:
- `AmazonS3ReadOnlyAccess`
- `AWSLambdaBasicExecutionRole`
3. Deploy the **Lambda code**:

```python
import json
import urllib.request
import boto3
import email

SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/XXX/YYY/ZZZ"
S3_BUCKET = "slack-alerts-bucket"  

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

     payload = {"text": f"📊 QuickSight Alert\n*{subject}*\n{body}"}
     req = urllib.request.Request(
         SLACK_WEBHOOK_URL,
         data=json.dumps(payload).encode('utf-8'),
         headers={'Content-Type': 'application/json'}
     )
     urllib.request.urlopen(req)
 return {"status": "success"}
```
4️⃣ Test the Workflow
Trigger a QuickSight KPI alert.

Check that the raw email is stored in S3.

Confirm Lambda logs in CloudWatch.

Verify that the Slack channel receives the alert.


   


