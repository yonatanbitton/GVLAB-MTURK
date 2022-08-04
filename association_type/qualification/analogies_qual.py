import boto3
from boto3 import client
questions = open(file='association_type_question.xml', mode='r').read()
answers = open(file='association_type_answer.xml', mode='r').read()

mturk = boto3.client('mturk', region_name='us-east-1', endpoint_url='https://mturk-requester-sandbox.us-east-1.amazonaws.com')
# mturk = boto3.client('mturk', region_name='us-east-1', endpoint_url='https://mturk-requester.us-east-1.amazonaws.com')

qual_response = mturk.create_qualification_type(
                        Name='association_type_qualification_final_v4',
                        Keywords='test, qualification, sample, association, visual association',
                        Description='This is association task qualification',
                        QualificationTypeStatus='Active',
                        Test=questions,
                        AnswerKey=answers,
                        TestDurationInSeconds=9999,
                        RetryDelayInSeconds=86400)

id = qual_response['QualificationType']['QualificationTypeId']
