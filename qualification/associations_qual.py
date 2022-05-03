import boto3
questions = open(file='one_external_question.xml', mode='r').read()

mturk = boto3.client('mturk', region_name='us-east-1', endpoint_url='https://mturk-requester-sandbox.us-east-1.amazonaws.com')
# mturk = boto3.client('mturk', region_name='us-east-1', endpoint_url='https://mturk-requester.us-east-1.amazonaws.com')

qual_response = mturk.create_qualification_type(
                        Name='associations_qual_one_instance',
                        Keywords='test, qualification, sample, analogies, analogy, visual analogies',
                        Description='This is Visual Associations Qualification',
                        QualificationTypeStatus='Active',
                        Test=questions,
                        TestDurationInSeconds=9999,
                        RetryDelayInSeconds=86400)

id = qual_response['QualificationType']['QualificationTypeId']
