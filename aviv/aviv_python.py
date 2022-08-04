import boto3
from datetime import datetime
from xml.sax.saxutils import escape as xml_escape
from tqdm import tqdm
from xml.dom.minidom import parseString
import itertools
import json
import qgrid
import pandas as pd
from boto3.exceptions import Boto3Error
import jsonlines
from typing import List
from bs4 import BeautifulSoup



is_sandbox = False
if is_sandbox:
    endpoint_url = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'
else:
    endpoint_url = 'https://mturk-requester.us-east-1.amazonaws.com'

print("Using sandobx: ", is_sandbox)
mturk = boto3.client('mturk', endpoint_url=endpoint_url, region_name = 'us-east-1')
mturk.get_account_balance()


def paginate(operation, result_fn, max_results=None, **kwargs):
    results = []
    resp = operation(MaxResults=100, **kwargs)
    local_results = result_fn(resp)
    results.extend(local_results)
    next_token = resp.get('NextToken')
    with tqdm() as pbar:
        while (local_results and next_token):
            if max_results is not None and len(results) >= max_results:
                break
            resp = operation(MaxResults=100, NextToken=next_token, **kwargs)
            local_results = result_fn(resp)
            next_token = resp.get('NextToken')
            results.extend(local_results)
            pbar.update(len(local_results))
    return results


# 30 days?
ten_minutes_sec = 60 * 10
one_hour_sec = 6 * ten_minutes_sec
thirty_days_sec = 30 * 24 * one_hour_sec
auto_approve_after_sec = thirty_days_sec
assign_duration = ten_minutes_sec

PercentAssignmentsApproved = "000000000000000000L0"
NumberHITsApproved = "00000000000000000040"
Worker_Locale = "00000000000000000071"


def create_or_get_qualification(qualification):
    resp = mturk.list_qualification_types(Query=qualification['Name'],
                                          MustBeOwnedByCaller=True,
                                          MustBeRequestable=False)
    if not resp['QualificationTypes']:
        resp2 = mturk.create_qualification_type(**qualification)
        qual_type_id = resp2['QualificationType']['QualificationTypeId']
    else:
        qual_type_id = resp['QualificationTypes'][0]['QualificationTypeId']
    print(qualification['Name'], qual_type_id)
    return qual_type_id


def get_quals(phase):
    print("Listing qualification for : ", "Sandobx" if is_sandbox else "Production")
    inadequate = {
        "Name": "some name",
        "Description": "some description",
        "QualificationTypeStatus": "Active",
        "AutoGranted": False,
    }

    in_screening = {
        "Name": "some name",
        "Description": "some description",
        "QualificationTypeStatus": "Active",
        "AutoGranted": False,
    }

    in_training = {
        "Name": "some name",
        "Description": "some description",
        "QualificationTypeStatus": "Active",
        "AutoGranted": False,
    }

    inadequate_type_id = create_or_get_qualification(inadequate)

    in_screening_type_id = create_or_get_qualification(in_screening)

    in_training_type_id = create_or_get_qualification(in_training)

    qual_approve_percent = {
        "QualificationTypeId": PercentAssignmentsApproved,
        "Comparator": "GreaterThan",
        "IntegerValues": [98]
    }
    qual_approve_number = {
        "QualificationTypeId": NumberHITsApproved,
        "Comparator": "GreaterThan",
        "IntegerValues": [5000],
    }
    qual_en_locale = {
        "QualificationTypeId": Worker_Locale,
        "Comparator": "In",
        "LocaleValues": [{"Country": "US"},
                         {"Country": "AU"},
                         {"Country": "GB"},
                         {"Country": "NZ"},
                         {"Country": "CA"}]
    }

    qual_not_rejected = {
        "QualificationTypeId": inadequate_type_id,
        "Comparator": "DoesNotExist"
    }

    qual_not_in_screening = {
        "QualificationTypeId": in_screening_type_id,
        "Comparator": "DoesNotExist"
    }
    qual_in_screening = {
        "QualificationTypeId": in_screening_type_id,
        "Comparator": "Exists"
    }

    qual_in_training = {
        "QualificationTypeId": in_training_type_id,
        "Comparator": "Exists"
    }

    if is_sandbox:
        if phase == "train":
            quals = [qual_approve_percent, qual_not_rejected, qual_in_screening]
        else:
            quals = [qual_approve_percent, qual_not_rejected, qual_not_in_screening]
    elif phase == "train":
        quals = [qual_approve_percent, qual_approve_number, qual_en_locale, qual_not_rejected, qual_in_screening]

    return quals, inadequate_type_id, in_screening_type_id, in_training_type_id


mturk.get_account_balance()


def create_highlighting_extraction_hit_type(phase):
    title = "Some title"
    reward_dollars = "0.10"

    keywords = "Some keywords"
    description = "Some description"

    srl_quals, inadequate_type_id, in_screening_type_id, in_training_type_id = get_quals(phase)
    response = mturk.create_hit_type(
        AutoApprovalDelayInSeconds=thirty_days_sec,
        AssignmentDurationInSeconds=2 * ten_minutes_sec,
        Reward=reward_dollars,
        Title=title,
        Keywords=keywords,
        Description=description,
        QualificationRequirements=srl_quals
    )
    srl_hit_type_id = response['HITTypeId']
    return srl_hit_type_id, srl_quals


train_srl_hit_type_id, train_srl_quals = create_highlighting_extraction_hit_type("train")


srl_question = open("./srl_question.xml").read()
srl_df = pd.read_csv(r"./urls.csv")

print(srl_df.sample().url.item())
srl_data = srl_df.sample(frac=1.0).to_dict(orient='records')
n_assigns = len(srl_data)
half_idx = int(n_assigns/2)
print(half_idx)
# srl_data = srl_data[:half_idx]

mturk.get_account_balance()

print("Uploading hits to: ", "Sandbox" if is_sandbox else "Production")
max_assigns = 1
hit_lifetime = 7 * 24 * 6 * ten_minutes_sec
hit_resps = []
for item in srl_data:
    escaped_url = xml_escape(item['url'])
    print(item['url'])
    this_question = srl_question.format(url=escaped_url)
    response = mturk.create_hit_with_hit_type(
        HITTypeId=train_srl_hit_type_id,
        MaxAssignments=max_assigns,
        LifetimeInSeconds=hit_lifetime,
        Question=this_question
    )
    hit_resps.append(response)

mturk.get_account_balance()

def get_all_hits(max_results):
    print("Retrieving hits from: ", "Sandbox" if is_sandbox else "Production")
    hits = paginate(mturk.list_hits, lambda resp: resp['HITs'], max_results=max_results)
    return hits

my_hits = get_all_hits(200)


def get_reviewable_hits(hit_type_id):
    print("Reviewing hits from: ", "Sandbox" if is_sandbox else "Production")
    rev_hits = paginate(mturk.list_reviewable_hits, lambda resp: resp.get('HITs', []), HITTypeId=hit_type_id)
    hit_ids = [h['HITId'] for h in rev_hits]
    return hit_ids


def review_assignments(hit_type_id):
    print("Reviewing hits from: ", "Sandbox" if is_sandbox else "Production")
    hit_ids = get_reviewable_hits(hit_type_id)
    assignments_for_review = assignments_for_review = retrieve_assignments(hit_type_id, hit_ids)
    return assignments_for_review


def retrieve_assignments(hit_type_id, hit_ids):
    assignments_for_review = []
    for hit_id in hit_ids:
        assignments_for_hit = paginate(mturk.list_assignments_for_hit, lambda resp: resp.get('Assignments', []),
                                       HITId=hit_id)
    return assignments_for_hit

hit_type_id = "" # check in my_hits
assignments = review_assignments(hit_type_id)