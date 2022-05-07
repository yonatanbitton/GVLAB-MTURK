from datetime import datetime

import boto3 as boto3
import pytz as pytz

is_sandbox = False
if is_sandbox:
    endpoint_url = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'
else:
    endpoint_url = 'https://mturk-requester.us-east-1.amazonaws.com'

if __name__ == '__main__':
    print("Using sandobx: ", is_sandbox)
    mturk = boto3.client('mturk', endpoint_url=endpoint_url, region_name = 'us-east-1')
    # hit_type_id = '35EE6WR8LHPD5V6FND0B2VK1GAF17F'
    # hit_type_id = '3S942EFUVKZ59R1T0AKMY9A86SZJE7'
    # hit_type_id = '3S942EFUVKZ59R1T0AKMY9A86SZJE7'
    hit_type_id = '33YYKPVHQWOFWHXT42PLKMHFT7O0UZ'
    title = 'GVLAB: Visual Associations - (solve items 1200-1340)'
    for i in range(12):
        hits = mturk.list_hits()['HITs']
        print(f"There are {len(hits)} HITs")
        if len(hits) == 0:
            break
        deleted = []
        for h in hits:
            if h['HITTypeId'] != hit_type_id:
                continue
            # if h['Title'] not in [title]:
            #     print(f"Not same title {h['Title']}")
            #     continue
            expiration_time = datetime(2000,1,1, 1, 1, 1, tzinfo=pytz.timezone('GMT'))
            response = mturk.update_expiration_for_hit(
                HITId=h['HITId'],
                ExpireAt=datetime(2015, 1, 1)
            )
            h_new = mturk.get_hit(HITId=h['HITId'])
            try:
                mturk.delete_hit(HITId=h['HITId'])
            except Exception as ex:
                # h['HITStatus'] == 'Reviewable'
                print("Exception")
                # continue
                hit_assignments = mturk.list_assignments_for_hit(HITId=h['HITId'])
                if len(hit_assignments['Assignments']) > 0:
                    AssignmentId = hit_assignments['Assignments'][0]['AssignmentId']
                    AssignmentStatus = hit_assignments['Assignments'][0]['AssignmentStatus']
                    print(f"Approving: {AssignmentId, AssignmentStatus}")
                    mturk.approve_assignment(
                        AssignmentId=AssignmentId,
                        OverrideRejection=False,
                    )
            deleted.append((h['HITId'], hit_type_id))
        print(f'deleted: {deleted}')