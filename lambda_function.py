import json
import requests
import boto3

def lambda_handler(event, context):
    
    url = "https://ws.ovh.ca/order/dedicated/servers/ws.dispatcher/getPossibleOptionsAndAvailability?callback=angular.callbacks._3&params={%22sessionId%22:%22classic%2Fanonymous-5e8f745803691030060818a7281ad55a%22,%22billingCountry%22:%22KSCA%22,%22dedicatedServer%22:%22"+event['server']+"%22,%22installFeeMode%22:%22directly%22,%22duration%22:%221m%22}"
    response = requests.get(url)
    responDict = json.loads(response.text.replace("angular.callbacks._3(", "").replace(");", ""));
    availability = False;
    realName = responDict['answer'][0]['mainReferences'][0]['designation'].split(" ")[0];
    for zone in responDict['answer'][0]['zones']:
        print(zone['availability'])
        if zone['availability'] != -1:
            client = boto3.client('sns')
            client.publish(
                PhoneNumber=event['phone'],
                Message=realName+" is available in "+zone['zone']
            )
            availability = True;
            break;
    
    # TODO implement
    return {
        'availability': availability
    }
