from datetime import datetime

import boto3 as boto3
import pytz as pytz

is_sandbox = True
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
    # hit_type_id = '33YYKPVHQWOFWHXT42PLKMHFT7O0UZ'
    # hit_type_id = '3L31T0COU9OKFS1X1VUK9952NPRQG3'
    # hit_type_id = '3KAKS2ULSF7XZIPBT2MARJ0M3I2MTL'
    # hit_type_id = '3KAKS2ULSF7XZIPBT2MARJ0M3I2MTL'
    # hit_type_id = '31WLO1EP3YLN5XAOWVO1YNO5B0LQSN'
    # hit_type_id = 'GVLAB: Solve Visual Associations created by users (Fun!) - (100-300)'
    # hit_type_id = '3UZRKKY9ATT1I0VXRH0EXJF3SXH4O7'
    # hit_type_id = '3H5KS3F36QZTFBNOIXZ2T6QE72IZYO'
    # title = 'GVLAB: Visual Associations - (solve items 100-300)'
    # title = 'GVLAB: Solve Visual Associations created by users (Fun!) - (0-100)'
    # title = 'GVLAB: Visual Associations - (create items 0-100)'
    # title = 'GVLAB: Visual Associations - (solve items 100-300)'
    # title = 'GVLAB: Solve Visual Associations created by users (Fun!)'
    # title = 'GVLAB: Visual Associations - (solve items 100-500)'
    # title = 'GVLAB: Solve Visual Associations created by users (Fun!) - (0-100)'
    # title = 'GVLAB: Visual Associations - Create (create_random_10_12_candidates items 0-100) - (Higher probablity for bonuses)'
    # title = 'GVLAB: Visual Associations - Create (create_random items 0-100)'
    # title = "GVLAB: Solve Visual Associations created by users (Fun!) - Solve carefully - it's a test (Increased pay)"
    # title = "GVLAB: Solve Visual Associations created by users (Fun!) - (100-250)"
    # title = "GVLAB: Visual Associations - Create (create_random items 100-250)"
    # title = "GVLAB: Visual Associations - Create (create items 100-250) - increased pay!"
    title ="GVLAB: Visual Associations - Create (create_random items 0-200)"
    for i in range(50):
        hits = mturk.list_hits()['HITs']
        print(f"There are {len(hits)} HITs")
        if len(hits) == 0:
            break
        deleted = []
        for h in hits:
            # if h['HITTypeId'] != hit_type_id:
            #     continue
            if h['Title'] not in [title]:
                print(f"Not same title {h['Title']}")
                continue
            try:
                expiration_time = datetime(2000,1,1, 1, 1, 1, tzinfo=pytz.timezone('GMT'))
                response = mturk.update_expiration_for_hit(
                    HITId=h['HITId'],
                    ExpireAt=datetime(2015, 1, 1)
                )
                h_new = mturk.get_hit(HITId=h['HITId'])
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
            # deleted.append((h['HITId'], hit_type_id))
        print(f'deleted: {deleted}')