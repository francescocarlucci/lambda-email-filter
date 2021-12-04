import boto3
import email

def get_email_message(message_id):
    
    workmail = boto3.client('workmailmessageflow', region_name='us-east-1')
    
    raw_message = workmail.get_raw_message_content(messageId=message_id)

    parsed_message = email.message_from_bytes(raw_message['messageContent'].read())
    
    return parsed_message

def lambda_handler(event, context):
    
    action_type = 'DEFAULT' # 'MOVE_TO_JUNK'
    
    try:
        
        from_address = event['envelope']['mailFrom']['address']
        
        subject = event['subject']
        
        flow_direction = event['flowDirection']
        
        message_id = event['messageId']
        
        full_message = get_email_message(message_id)

        print(f"Received {flow_direction} email from {from_address}")
        
        print(f"Content:{full_message}") 
        
        # custom logic goes here 
    
    except Exception as e:
        print(e)
        raise e
    
    print(f"Returning action type: {action_type}")
    
    return {
          'actions': [
          {
            'allRecipients': True,
            'action' : {
                'type' : action_type
            }
          }
        ]
    }

"""

Parameters
----------
event: dict, required
    AWS WorkMail Message Summary Input Format
    For more information, see https://docs.aws.amazon.com/workmail/latest/adminguide/lambda.html

    {
        "summaryVersion": "2019-07-28",                              # AWS WorkMail Message Summary Version
        "envelope": {
            "mailFrom" : {
                "address" : "from@domain.test"                       # String containing from email address
            },
            "recipients" : [                                         # List of all recipient email addresses
               { "address" : "recipient1@domain.test" },
               { "address" : "recipient2@domain.test" }
            ]
        },
        "sender" : {
            "address" :  "sender@domain.test"                        # String containing sender email address
        },
        "subject" : "Hello From Amazon WorkMail!",                   # String containing email subject (Truncated to first 256 chars)"
        "messageId": "00000000-0000-0000-0000-000000000000",         # String containing message id for retrieval using workmail flow API
        "invocationId": "00000000000000000000000000000000",          # String containing the id of this lambda invocation. Useful for detecting retries and avoiding duplication
        "flowDirection": "INBOUND",                                  # String indicating direction of email flow. Value is either "INBOUND" or "OUTBOUND"
        "truncated": false                                           # boolean indicating if any field in message was truncated due to size limitations
    }

Returns
-------
Amazon WorkMail Sync Lambda Response Format. For more information, see https://docs.aws.amazon.com/workmail/latest/adminguide/lambda.html#synchronous-schema
    return {
      'actions': [                                              # Required, should contain at least 1 list element
      {
        'action' : {                                            # Required
          'type': 'string',                                     # Required. For example: "BOUNCE", "DEFAULT". For full list of valid values, see https://docs.aws.amazon.com/workmail/latest/adminguide/lambda.html#synchronous-schema
          'parameters': { <various> }                           # Optional. For bounce, <various> can be {"bounceMessage": "message that goes in bounce mail"}
        },
        'recipients': list of strings,                          # Optional if allRecipients is present. Indicates list of recipients for which this action applies.
        'allRecipients': boolean                                # Optional if recipients is present. Indicates whether this action applies to all recipients
      }
    ]}

"""
