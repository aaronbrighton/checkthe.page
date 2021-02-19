import argparse
import sys
import boto3

parser = argparse.ArgumentParser(description='Creates a CloudWatch rule that periodically invokes the Notifer Lambda function.')
parser.add_argument('target_config', type=str, help='Path to the JSON file containing CloudWatch rule InputTransformer.InputTemplate.  Placholders SHOULD be wrapped in double quotes, to ensure the file is valid JSON (i.e. "rule_arn": "<resources>" not "rule_arn": <resource>).')
parser.add_argument('--name', dest='rule_name', required=True, type=str, help='Name to use for the CloudWatch rule.')
parser.add_argument('--period', dest='rule_period', required=True, type=str, default='15 minutes', help='How frequently to invoke the Notifier function (15 minutes)')
parser.add_argument('--role', dest='rule_role_arn', required=True, type=str, help='The ARN of the role created to invoked the Notifier Lambda function.')
parser.add_argument('--lambda-arn', dest='lambda_arn', required=True, type=str, help='The ARN of the Notifer Lambda function.')
args = parser.parse_args()

# Load the target config JSON file
f = open(args.target_config)
cloudwatch_target_configuration = f.read()

try:

    # Create the CloudWatch rule
    client = boto3.client('events')
    response = client.put_rule(
        Name=args.rule_name,
        ScheduleExpression="rate("+(args.rule_period)+")",
        RoleArn=args.rule_role_arn
    )

    # Add the target for the Notifier Lambda to the CloudWatch Rule
    response = client.put_targets(
        Rule=args.rule_name,
        Targets=[
            {
                'Id': '1',
                'Arn': args.lambda_arn,
                'InputTransformer': {
                    'InputPathsMap': {
                        'resources': '$.resources[0]'
                    },
                    'InputTemplate': cloudwatch_target_configuration.replace('"<resources>"', '<resources>') # Replace "<resource>" with <resource>, InputTemplates placeholders cannot be wrapped in quotes ¯\_(ツ)_/¯
                }
            }
        ]
    )

    print("Rule created successfully!")

except Exception as e:
    
    print(e)