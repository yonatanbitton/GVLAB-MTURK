from xml.sax.saxutils import escape as xml_escape

import boto3
import pandas as pd
from tqdm import tqdm

is_sandbox = False
if is_sandbox:
    endpoint_url = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'
else:
    endpoint_url = 'https://mturk-requester.us-east-1.amazonaws.com'
if not is_sandbox:
    for i in range(100):
        print('*** NOT SANDBOX!!! THIS IS REAL!!! ***')

print("Using sandobx: ", is_sandbox)
mturk = boto3.client('mturk', endpoint_url=endpoint_url, region_name = 'us-east-1')
mturk.get_account_balance()

# 30 days?
ten_minutes_sec = 60 * 10
one_hour_sec = 6 * ten_minutes_sec
thirty_days_sec = 30 * 24 * one_hour_sec
auto_approve_after_sec = thirty_days_sec
assign_duration = ten_minutes_sec

PercentAssignmentsApproved = "000000000000000000L0"
NumberHITsApproved = "00000000000000000040"
Worker_Locale = "00000000000000000071"

def create():
    train_gvlab_hit_type_id, train_gvlab_quals = create_gvlab_creation_hit_type("train")

    print(f"Created qualifications")
    external_question = open("./external_question.xml").read()
    gvlab_creation_df = pd.read_csv(r"./urls.csv")

    print(gvlab_creation_df.sample().url.item())
    # srl_data = srl_data[:half_idx]

    print(f"balance: {mturk.get_account_balance()}")
    print(mturk.get_account_balance())

    print("Uploading hits to: ", "Sandbox" if is_sandbox else "Production")
    max_assigns = 1
    # max_assigns = 3
    print(f"max_assigns: {max_assigns} (needs to be 3 in the full task!)")
    hit_lifetime = 7 * 24 * 6 * ten_minutes_sec
    hit_resps = []
    for item_idx, item in gvlab_creation_df.iterrows():
        escaped_url = xml_escape(item['url'])
        print(item['url'])
        this_question = external_question.format(url=escaped_url)
        response = mturk.create_hit_with_hit_type(
            HITTypeId=train_gvlab_hit_type_id,
            MaxAssignments=max_assigns,
            LifetimeInSeconds=hit_lifetime,
            Question=this_question
        )
        hit_resps.append(response)


    print(f"Finished uploading! {len(hit_resps)} responses")
    print(f"balance: {mturk.get_account_balance()}")


def review_hits(hit_type_id):
    print(f"review_hits")
    print(mturk.get_account_balance())
    print(f"Receiving HITs...")
    assignments = review_assignments(hit_type_id)
    print(f"Returning reviewed assignments")
    # print(assignments)
    return assignments


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
    print("Listing qualifications for : ", "Sandobx" if is_sandbox else "Production")
    inadequate = {
        "Name": "inadequate",
        "Description": "inadequate",
        "QualificationTypeStatus": "Active",
        "AutoGranted": False,
    }

    in_screening = {
        "Name": "in_screening",
        "Description": "in_screening",
        "QualificationTypeStatus": "Active",
        "AutoGranted": False,
    }

    in_training = {
        "Name": "in_training",
        "Description": "in_training",
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

    # if is_sandbox:
    #     if phase == "train":
    #         quals = [qual_approve_percent, qual_not_rejected, qual_in_screening]
    #     else:
    #         quals = [qual_approve_percent, qual_not_rejected, qual_not_in_screening]
    # elif phase == "train":
    #     quals = [qual_approve_percent, qual_approve_number, qual_en_locale, qual_not_rejected, qual_in_screening]

    if is_sandbox:
        if phase == "train":
            quals = [qual_approve_percent, qual_not_rejected]
        else:
            quals = [qual_approve_percent, qual_not_rejected]
    elif phase == "train":
        quals = [qual_approve_percent, qual_approve_number, qual_en_locale, qual_not_rejected]

    return quals, inadequate_type_id, in_screening_type_id, in_training_type_id


def create_gvlab_creation_hit_type(phase):
    title = "GVLAB Creation V3"
    reward_dollars = "0.4" # +0.3*2

    keywords = "Association, Creativity, Visual Associations, Fool the AI"
    description = "Try to create visual associations that fools an AI model! Additional bonus for fooling the AI! Additional bonus for not cheating!"

    gvlab_quals, inadequate_type_id, in_screening_type_id, in_training_type_id = get_quals(phase)
    print(f"Created qualifications")
    response = mturk.create_hit_type(
        AutoApprovalDelayInSeconds=thirty_days_sec,
        AssignmentDurationInSeconds=2 * ten_minutes_sec,
        Reward=reward_dollars,
        Title=title,
        Keywords=keywords,
        Description=description,
        QualificationRequirements=gvlab_quals
    )
    gvlab_hit_type_id = response['HITTypeId']
    print(f"Created HIT Type: {gvlab_hit_type_id}")
    return gvlab_hit_type_id, gvlab_quals



def get_all_hits(max_results):
    print("Retrieving hits from: ", "Sandbox" if is_sandbox else "Production")
    hits = paginate(mturk.list_hits, lambda resp: resp['HITs'], max_results=max_results)
    return hits


def get_reviewable_hits(hit_type_id):
    print("Reviewing hits from: ", "Sandbox" if is_sandbox else "Production")
    rev_hits = paginate(mturk.list_reviewable_hits, lambda resp: resp.get('HITs', []), HITTypeId=hit_type_id)
    hit_ids = [h['HITId'] for h in rev_hits]
    return hit_ids


def review_assignments(hit_type_id):
    print("Reviewing hits from: ", "Sandbox" if is_sandbox else "Production")
    hit_ids = get_reviewable_hits(hit_type_id)
    assignments_for_review = retrieve_assignments(hit_type_id, hit_ids)
    return assignments_for_review


def retrieve_assignments(hit_type_id, hit_ids):
    assignments_for_review = []
    for hit_id in hit_ids:
        assignments_for_hit = paginate(mturk.list_assignments_for_hit, lambda resp: resp.get('Assignments', []),
                                       HITId=hit_id)
        assignments_for_review.append(assignments_for_hit)
    return assignments_for_review

if __name__ == '__main__':
    # create()
    # previous_hit_type_id = '3S9TI1T3V1BMECYL1FRG1OQLIS2AFE'
    # previous_hit_type_id = '3SJ5GB440HT43C8D6USJ0K8ZXKFQ4D'
    # previous_hit_type_id = '3KBOIXB476EMZVCDKZBT5CEDXGAQ5I'
    previous_hit_type_id = '3DCJP2JIFL2FRFFQ1YM56ARCF5J3C1'
    review_hits(previous_hit_type_id)