import re
import email
import boto3

def get_email_message(message_id):
    
    # make sure to match your WorkMail AWS region
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
        
        full_message = str(get_email_message(message_id))

        print(f"Received {flow_direction} email from {from_address}")
        
        #print(f"Content: {full_message}") # DEBUG
        
        # extract all the email links
        email_links = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', full_message)
        
        print(email_links) # DEBUG
        
        print(f"The message contains {len(email_links)} links")
        
        # if the message contains more than X links, is probably SPAM
        if( len(email_links) > 4 ):
            
            action_type = 'MOVE_TO_JUNK'
    
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
