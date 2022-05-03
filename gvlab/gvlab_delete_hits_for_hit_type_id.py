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
    hit_type_id = '3DCJP2JIFL2FRFFQ1YM56ARCF5J3C1'
    for i in range(12):
        hits = mturk.list_hits()['HITs']
        print(f"There are {len(hits)} HITs")
        if len(hits) == 0:
            break
        deleted = []
        for h in hits:
            if h['HITTypeId'] != hit_type_id:
                continue
            expiration_time = datetime(2000,1,1, 1, 1, 1, tzinfo=pytz.timezone('GMT'))
            response = mturk.update_expiration_for_hit(
                HITId=h['HITId'],
                ExpireAt=datetime(2015, 1, 1)
            )
            h_new = mturk.get_hit(HITId=h['HITId'])
            h_new["HIT"]['Expiration']
            mturk.delete_hit(HITId=h['HITId'])
            deleted.append((h['HITId'], hit_type_id))
        print(f'deleted: {deleted}')