
import boto3

MTURK_SANDBOX = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'
mturk = boto3.client('mturk',
   region_name='us-east-1',
   endpoint_url = MTURK_SANDBOX
)

def main():
    print("I have $" + mturk.get_account_balance()['AvailableBalance'] + " in my Sandbox account")

    question = open('questions.xml', mode='r').read()
    new_hit = mturk.create_hit(
        Title = 'Is this Tweet happy, angry, excited, scared, annoyed or upset?',
        Description = 'Read this tweet and type out one word to describe the emotion of the person posting it: happy, angry, scared, annoyed or upset',
        Keywords = 'text, quick, labeling',
        Reward = '0.15',
        MaxAssignments = 1,
        LifetimeInSeconds = 172800,
        AssignmentDurationInSeconds = 600,
        AutoApprovalDelayInSeconds = 14400,
        Question=question,
    )
    print("A new HIT has been created. You can preview it here:")
    print("https://workersandbox.mturk.com/mturk/preview?groupId=" + new_hit['HIT']['HITGroupId'])
    # print("https://workersandbox.mturk.com/mturk/preview?groupId=" + new_hit['HIT']['HITTypeId'])
    print("HITID = " + new_hit['HIT']['HITId'] + " (Use to Get Results)")


if __name__ == '__main__':
    main()
