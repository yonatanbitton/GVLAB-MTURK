import json
import os
from xml.sax.saxutils import escape as xml_escape

import boto3
import pandas as pd
from tqdm import tqdm
from time import gmtime, strftime

is_sandbox = False
if not is_sandbox:
    for i in range(100):
        print('*** NOT SANDBOX!!! THIS IS REAL!!! ***')
if is_sandbox:
    endpoint_url = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'
else:
    endpoint_url = 'https://mturk-requester.us-east-1.amazonaws.com'

print("Using sandbox: ", is_sandbox)
mturk = boto3.client('mturk', endpoint_url=endpoint_url, region_name = 'us-east-1')
print(f"Available Balance: {mturk.get_account_balance()['AvailableBalance']}")

# 30 days?
ten_minutes_sec = 60 * 10
one_hour_sec = 6 * ten_minutes_sec
# thirty_days_sec = 30 * 24 * one_hour_sec
three_days_sec = 3 * 24 * one_hour_sec
auto_approve_after_sec = three_days_sec
assign_duration = ten_minutes_sec

PercentAssignmentsApproved = "000000000000000000L0"
NumberHITsApproved = "00000000000000000040"
Worker_Locale = "00000000000000000071"

def assign_tasks(config):
    print(f"task_type, start, end: {config['task_type'], config['start_idx'], config['end_idx']}")
    df = pd.read_csv(os.path.join(f'urls', f'urls_{task_type}.csv'))
    print(f"read dataframe of size: {len(df)} ({task_type})")
    if 'qual' in task_type:
        df_sample = df
    elif 'test' not in task_type:
        df_sample = df.iloc[config['start_idx']:config['end_idx']]
        print(f"Taking indices: {(config['start_idx'],config['end_idx'])}, got df sample of size: {len(df_sample)}")
    elif 'test' in task_type:
        df_sample = df
        print(f"df at length {len(df_sample)}")
    gvlab_hit_type_id, gvlab_quals = create_gvlab_creation_hit_type(config)
    print(f"gvlab_hit_type_id: {gvlab_hit_type_id}")
    # exit()
    config['gvlab_hit_type_id'] = gvlab_hit_type_id

    print(f"Created qualifications")
    external_question = open("./external_question.xml").read()

    print(f"balance: {mturk.get_account_balance()['AvailableBalance']}")
    current_mturk_balance = mturk.get_account_balance()['AvailableBalance']
    config['current_mturk_balance'] = current_mturk_balance

    print("Uploading hits to: ", "Sandbox" if is_sandbox else "Production")
    print(f"max_assigns: {max_assigns} (is_sandbox: {is_sandbox})")
    hit_lifetime = 7 * 24 * 6 * ten_minutes_sec
    hit_responses = []
    if 'qual' in task_type:
        """ If in a qualification test, sending X number of test to accumulate workers that have this qualification """
        for i in range(number_of_annotators_for_qual):
            sand_hits(df_sample, external_question, gvlab_hit_type_id, hit_lifetime, hit_responses)
    else:
        sand_hits(df_sample, external_question, gvlab_hit_type_id, hit_lifetime, hit_responses)

    print(f"Finished uploading! {len(hit_responses)} responses")
    print(f'config')
    print(config)
    config['hit_responses'] = hit_responses
    config['current_mturk_balance_after_hits'] = mturk.get_account_balance()['AvailableBalance']
    print(f"current_mturk_balance_after_hits: {config['current_mturk_balance_after_hits']}")
    fname = f"hits_{config['current_time']}_{config['task_type']}_{config['start_idx']}-{config['end_idx']}.json"
    if is_sandbox:
        output_json_path = os.path.join('published_batches_sandbox', fname)
    else:
        output_json_path = os.path.join('published_batches', fname)
    json.dump(config, open(output_json_path,'w'))
    print(f"Wrote config to {output_json_path}")


def sand_hits(df_sample, external_question, gvlab_hit_type_id, hit_lifetime, hit_responses):
    for item_idx, item in df_sample.iterrows():
        escaped_url = xml_escape(item['ID'])
        this_question = external_question.format(url=escaped_url)
        response = mturk.create_hit_with_hit_type(
            HITTypeId=gvlab_hit_type_id,
            MaxAssignments=max_assigns,
            LifetimeInSeconds=hit_lifetime,
            Question=this_question
        )
        hit_responses.append(response['HIT']['HITId'])


def review_hits(hit_type_id):
    print(mturk.get_account_balance())
    print(f"Receiving HITs...")
    assignments = review_assignments(hit_type_id)
    print(f"Reviewed assignments: ")
    print(assignments)
    print("Done")


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


def get_quals(task_type):
    print("Listing qualifications for : ", "Sandobx" if is_sandbox else "Production")
    inadequate = {
        "Name": "inadequate",
        "Description": "inadequate",
        "QualificationTypeStatus": "Active",
        "AutoGranted": False,
    }

    gvlab_annotator = {
        "Name": "gvlab_annotator",
        "Description": "GVLAB annotator",
        "QualificationTypeStatus": "Active",
        "AutoGranted": False,
    }

    passed_gvlab_solve_qualification = {
        "Name": "passed_gvlab_solve_qualification",
        "Description": "Passed the GVLAB solve qualification",
        "QualificationTypeStatus": "Active",
        "AutoGranted": False,
    }

    passed_gvlab_create_qualification = {
        "Name": "passed_gvlab_create_qualification",
        "Description": "Passed the GVLAB create qualification",
        "QualificationTypeStatus": "Active",
        "AutoGranted": False,
    }

    annotated_gvlab_swow_solve = {
        "Name": "First GVLAB Solve Batch Performance",
        "Description": "First GVLAB Solve Batch Performance",
        "QualificationTypeStatus": "Active",
        "AutoGranted": False,
    }

    gvlab_annotator_qualification_type_id = create_or_get_qualification(gvlab_annotator)
    annotated_gvlab_swow_solve_type_id = create_or_get_qualification(annotated_gvlab_swow_solve)
    passed_gvlab_solve_qualification_type_id = create_or_get_qualification(passed_gvlab_solve_qualification)
    passed_gvlab_create_qualification_type_id = create_or_get_qualification(passed_gvlab_create_qualification)

    inadequate_type_id = create_or_get_qualification(inadequate)

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

    qual_needs_to_do_gvlab_solve_test = {
        "QualificationTypeId": passed_gvlab_solve_qualification_type_id,
        "Comparator": "DoesNotExist"
    }
    qual_passed_gvlab_solve_test = {
        "QualificationTypeId": passed_gvlab_solve_qualification_type_id,
        "Comparator": "Exists"
    }
    qual_gvlab_annotator = {
        "QualificationTypeId": gvlab_annotator_qualification_type_id,
        "Comparator": "Exists"
    }
    qual_not_gvlab_annotator = {
        "QualificationTypeId": gvlab_annotator_qualification_type_id,
        "Comparator": "DoesNotExist"
    }
    qual_needs_to_do_gvlab_create_test = {
        "QualificationTypeId": passed_gvlab_create_qualification_type_id,
        "Comparator": "DoesNotExist"
    }
    qual_passed_gvlab_create_test = {
        "QualificationTypeId": passed_gvlab_create_qualification_type_id,
        "Comparator": "Exists"
    }
    qual_didnt_annotated_gvlab_swow_solve = {
        "QualificationTypeId": annotated_gvlab_swow_solve_type_id,
        "Comparator": "DoesNotExist"
    }
    qual_annotated_gvlab_swow_solve = {
        "QualificationTypeId": annotated_gvlab_swow_solve_type_id,
        "Comparator": "Exists"
    }

    # quals = [qual_approve_percent, qual_not_rejected, qual_gvlab_annotator]
    quals = [qual_approve_percent, qual_not_rejected]
    print(f"Not requiring GVLAB Annotator")
    if task_type == "solve_qual_test":
        """ If the task is the solve qual, we need to make sure that the annotator didn't do it yet """
        quals.append(qual_needs_to_do_gvlab_solve_test)
    elif task_type == "create_qual_test":
        """ If the task is the create qual, we need to make sure that the annotator didn't do it yet """
        quals.append(qual_needs_to_do_gvlab_create_test)
        ''' GVLAB annotator only '''
        # quals.append(qual_gvlab_annotator)
        ''' Annotated solve '''
        # quals.append(qual_annotated_gvlab_swow_solve)
        print("Publishing PUBLIC qual, not demanding solve, but do demanding solve qual")
        quals.append(qual_not_gvlab_annotator)
        quals.append(qual_passed_gvlab_solve_test)
    elif task_type == 'solve':
        """ If the task is solve, we need to make sure that the annotator passed the solve qual """
        quals.append(qual_passed_gvlab_solve_test)
    elif task_type == 'solve_test':
        """ If it's the test, we need to make sure that it's different annotators """
        quals.append(qual_passed_gvlab_solve_test)
        quals.append(qual_didnt_annotated_gvlab_swow_solve)
    elif task_type == 'create':
        """ If the task is solve, we need to make sure that the annotator passed the solve qual """
        quals.append(qual_passed_gvlab_create_test)
    else:
        raise Exception(f"Exception, unknown task_type: {task_type}")
    if not is_sandbox:
        print("Not sandbox, adding two quals (number, locale)")
        quals += [qual_approve_number, qual_en_locale]

    return quals


def create_gvlab_creation_hit_type(config):
    gvlab_quals = get_quals(config['task_type'])
    print(f"Created qualifications")
    response = mturk.create_hit_type(
        AutoApprovalDelayInSeconds=thirty_days_sec,
        AssignmentDurationInSeconds=2 * ten_minutes_sec,
        Reward=config['reward_dollars'],
        Title=config['title'],
        Keywords=config['keywords'],
        Description=config['description'],
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
    current_time = strftime("%Y-%m-%d_%H:%M:%S", gmtime())
    # start_idx, end_idx = 100, 550 # 3DCJP2JIFL2FRFFQ1YM56ARCF5J3C1
    # start_idx, end_idx = 550, 650  # 3DCJP2JIFL2FRFFQ1YM56ARCF5J3C1
    # start_idx, end_idx = 650, 1200  # 3DCJP2JIFL2FRFFQ1YM56ARCF5J3C1
    start_idx, end_idx = 1200, 1340 # 3S942EFUVKZ59R1T0AKMY9A86SZJE7
    number_of_annotators_for_qual = 100
    # task_type = 'solve'
    # task_type = 'solve_test'
    # task_type = 'solve_qual_test'
    task_type = 'create_qual_test'

    title_full = f"GVLAB: Visual Associations - ({task_type} items {start_idx}-{end_idx})"
    title_qual = f"GVLAB: Visual Associations - test for future HITs (Fun!)"
    # title_qual_create = f"GVLAB: Visual Associations - test for 'create' future HITs (Fun!)"
    title_qual_create = f"GVLAB: Visual Associations - test for 'create' future HITs (Fun!) - public"
    title_solve_test = f"GVLAB: Visual Associations - Solve Test"
    create_keywords = "Fun, Association, Creativity, Visual Associations, Fool the AI"
    solve_keywords = "Fun, Association, Creativity, Visual Associations, Find Associations"
    solve_description = "Fun Visual Associations: Given images, choose the images that are most associated with the cue - To practice, visit https://gvlab-dataset.github.io/beat-the-ai, 'Guess The Associations' practice"
    create_description = "Try to create visual associations that fools an AI model! Additional bonus for fooling the AI! Additional bonus for not cheating! - To practice, visit https://gvlab-dataset.github.io/beat-the-ai, 'Give The Cue' practice"
    solve_qual_test_description = "Do this test only once: Pass this qualification for future HITs: Fun Visual Associations: Given images, choose the images that are most associated with the cue - To practice, visit https://gvlab-dataset.github.io/beat-the-ai, 'Guess The Associations' practice"
    create_qual_test_description = "Do this test only once: Pass this qualification for future HITs: Try to create visual associations that fools an AI model! Additional bonus for fooling the AI! Additional bonus for not cheating! - To practice, visit https://gvlab-dataset.github.io/beat-the-ai, 'Give The Cue' practice"

    max_assigns_full = 3
    max_assigns_qual = 1
    qual_test_reward = '0.01'  # minimum reward for qual test HIT
    solve_reward = '0.03'
    create_reward = '0.05'
    if task_type == 'solve':
        title, reward_dollars, keywords, description, max_assigns = title_full, solve_reward, solve_keywords, solve_description, max_assigns_full
    elif task_type == 'solve_test':
        title, reward_dollars, keywords, description, max_assigns = title_solve_test, solve_reward, solve_keywords, solve_description, max_assigns_full
    elif task_type == 'create':
        title, reward_dollars, keywords, description, max_assigns = title_full, create_reward, create_keywords, create_description, max_assigns_full
    elif task_type == 'solve_qual_test':
        title, reward_dollars, keywords, description, max_assigns = title_qual, qual_test_reward, solve_keywords, solve_qual_test_description, max_assigns_qual
    elif task_type == 'create_qual_test':
        title, reward_dollars, keywords, description, max_assigns = title_qual_create, qual_test_reward, create_keywords, create_qual_test_description, max_assigns_qual
    else:
        raise Exception(f"Unknown task_type: {task_type}")
    config = {'task_type': task_type, 'max_assigns': max_assigns, 'reward_dollars': reward_dollars, 'title': title, 'keywords': keywords, 'description': description, 'current_time': current_time, 'is_sandbox': is_sandbox, 'start_idx': start_idx, 'end_idx': end_idx}
    print(f'task_type: {task_type}, config: ')
    print(config)
    assign_tasks(config)
    # previous_hit_type_id = '3S9TI1T3V1BMECYL1FRG1OQLIS2AFE'
    # previous_hit_type_id = '3SJ5GB440HT43C8D6USJ0K8ZXKFQ4D'
    # previous_hit_type_id = '3KBOIXB476EMZVCDKZBT5CEDXGAQ5I'
    # review_hits(previous_hit_type_id)