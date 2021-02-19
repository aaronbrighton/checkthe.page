import requests
import re
import boto3

def send_request(request_context, event):

    # Prepare the request args and kwargs
    args = (
        event[request_context]['method'], 
        event[request_context]['url']
    )
    kwargs = dict(
        params=event[request_context]['params'] if 'params' in event[request_context] else None,
        headers=event[request_context]['headers'] if 'headers' in event[request_context] else None,
        data=event[request_context]['data'] if 'data' in event[request_context] else None
    )

    # Send the request for the session ID
    request = requests.request(*args, **{k: v for k, v in kwargs.items() if v is not None})

    # Did the request succeed?
    if request:

        # Return the request response body.
        return request.text

    else:

        # Request failed
        print("Request failed, request response: "+request.text)
        return False


def lambda_handler(event, context):

    # Do we need to make preliminary call to get a session ID?
    if 'session_request' in event:
    
        # Send the request for the session ID
        session_request_text = send_request('session_request', event)

        # Did the request succeed?
        if session_request_text:
            
            # Search the response for a session ID - https://regex101.com/
            session_id_search = re.search(event['session_request']['session_identifier_regex'], session_request_text, flags=re.S)

            # Did we find a session ID?
            if session_id_search:

                # Store the session ID for later use
                session_id = session_id_search.group(1)

                # Search through the trigger_request object and replace any session identifier placeholders
                for request_property in ['params', 'headers']:
                    if request_property in event['trigger_request']:
                        for key, value in event['trigger_request'][request_property].items():
                            if isinstance(value, str):
                                event['trigger_request'][request_property][key] = event['trigger_request'][request_property][key].replace('{SESSIONID}', session_id)
                if 'body' in event['trigger_request']:
                    event['trigger_request']['body'] = event['trigger_request']['body'].replace('{SESSIONID}', session_id)

            else:
                
                # Failed to retrieve session ID, let's quit now.
                print("Failed to retrieve the session_id, request response: "+session_request.text)
                return False
        else:

            # Session request failed
            return False

    # Send the request for the page to search for the pattern in
    trigger_request_text = send_request('trigger_request', event)

    # Did the request succeed?
    if trigger_request_text:

        # Search the response for a session ID - https://regex101.com/
        trigger_pattern_search = re.search(event['trigger_request']['trigger_pattern_regex'], trigger_request_text, flags=re.S)

        # Did we find a match?
        if trigger_pattern_search:

            # Was this Lambda invoked by a CloudWatch Rule?
            if 'rule_arn' in event:

                # Extract the CloudWatch Rule name from the passed ARN
                event_rule_name = event['rule_arn'].rsplit('/', 1)[-1]

                # Get a list of targets for the CloudWatch Events Rule
                client = boto3.client('events')
                event_targets = client.list_targets_by_rule(
                    Rule=event_rule_name
                )

                # Remove the targets from the CloudWatch Events Rule
                client.remove_targets(
                    Rule=event_rule_name,
                    Ids=[
                        event_targets['Targets'][0]['Id'],
                    ]
                )

                # Delete the caller CloudWatch Events Rule
                client.delete_rule(
                    Name=event_rule_name
                )

            # Send SMS notification message
            client = boto3.client('sns')
            client.publish(
                PhoneNumber=event['notify_phone'],
                Message=event['notify_message']
            )

            return True

        else:

            print("Trigger pattern not found.")
            return True

    else:

        # Trigger request failed
        return False