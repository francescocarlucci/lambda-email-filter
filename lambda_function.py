import re
import email
import boto3

whitelist = [
    'francescocarlucci.com',
    'codeable.io'
]

stop_phrases = []

total_links_threshold = 5
    
def get_email_message(message_id):
    
    # make sure to match your WorkMail AWS region
    workmail = boto3.client('workmailmessageflow', region_name='us-east-1')
    
    raw_message = workmail.get_raw_message_content(messageId=message_id)

    parsed_message = email.message_from_bytes(raw_message['messageContent'].read())
    
    return parsed_message

def lambda_handler(event, context):
    
    action_type = 'DEFAULT' # MOVE_TO_JUNK, BYPASS_SPAM_CHECK
    
    try:
        
        from_address = event['envelope']['mailFrom']['address']
        
        from_domain = from_address.split('@')[1]
        
        recipients = event['envelope']['recipients']
        
        subject = event['subject']
        
        flow_direction = event['flowDirection']
        
        message_id = event['messageId']
        
        full_message = str(get_email_message(message_id))

        print(f"Received {flow_direction} email from {from_address}")
        
        if from_domain in whitelist:
            
            print(f"{from_domain} is whitelisted")
            
            action_type = 'BYPASS_SPAM_CHECK'
            
        else:
            
            for phrase in stop_phrases:
                
                if phrase in full_message.lower():
                    
                    print(f"The message contains stopwords: {phrase}")
                    
                    action_type = 'MOVE_TO_JUNK'
                    
                    break
                    
            if action_type == 'DEFAULT':
        
                # extract all the email links
                email_links = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', full_message)
                
                #print(email_links) # DEBUG
                
                print(f"The message contains {len(email_links)} links")
                
                # if the message contains more than X links, is probably SPAM
                if( len(email_links) > total_links_threshold ):
                    
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
