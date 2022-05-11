from tqdm import tqdm

from gvlab.gvlab_swow import create_or_get_qualification, mturk

def main():
    gvlab_annotator = '3ZNBPLV0N9WZ3TXWVJK01YGWNHRC2Y'
    first_gvlab_performance = '3JNQJJEQXO7VVJC4OVBSULOJWSKJU2'
    passed_gvlab_solve_qualification = '3NDLUB5I81QKQQ3IP6QL8DLKB9C46U'
    # gvlab_annotators_response = mturk.list_workers_with_qualification_type(QualificationTypeId=gvlab_annotator)
    # gvlab_annotators_workers_id = [x['WorkerId'] for x in gvlab_annotators_response['Qualifications']]
    first_gvlab_performance_workers = paginate(mturk.list_workers_with_qualification_type, lambda resp: set([x['WorkerId'] for x in resp['Qualifications']]), max_results=1000, QualificationTypeId=first_gvlab_performance)
    gvlab_annotator_workers = paginate(mturk.list_workers_with_qualification_type,
                                               lambda resp: set([x['WorkerId'] for x in resp['Qualifications']]),
                                               max_results=1000, QualificationTypeId=gvlab_annotator)
    both_solved_first_and_gvlab_annotator = set(first_gvlab_performance_workers).intersection(set(first_gvlab_performance_workers))
    print(f"gvlab_annotator_workers: {len(gvlab_annotator_workers)}, first_gvlab_performance_workers: {len(first_gvlab_performance_workers)}")
    # print(both_solved_first_and_gvlab_annotator)
    # relevant_workers = {'A2LU259QPV1I4V', 'A3UJSDFJ9LBQ6Z', 'AXID3RPK6NZT6', 'A1WY3YGT618GC0', 'AHB3QFZSFN9DL', 'A1OZPLHNIU1519',
    #  'A1FA3QRISJ1RIP', 'A2K607J3Z68WRR', 'A302KOFOYLD89A', 'A1PBRKFHSF1OF8', 'AB7MYP65HZ2MH', 'A18WSAKX5YN2FB',
    #  'A3BUWQ5C39GRQC', 'A382S0KJMW3K9S', 'A104V8NZIQFN2F', 'A68UG55LKRKMS', 'A2ONILC0LZKG6Y', 'A1W1X3S1Y0RKF3',
    #  'A2UAHW3Q7S45JP', 'A3135Y3RMFC3PK', 'A2V3P1XE33NYC3', 'AKQAI78JTXXC9', 'A2BK45LZGGWPLX', 'A14GKRTUEHBLBZ',
    #  'A36P1ZQ0GYF567'}
    # SubjectNewQualification = 'GVLAB: Create Qualification test available - solve it successfully get access to many rewarding HITs'
    # MessageText_new_batch = 'Hello, you are one of few chosen to annotate for GVLAB create task (if you want :)). Qual name: "GVLAB: Visual Associations - test for "create" future HITs (Fun!)". Instructions are in the qualification test and the TurkerNation group. Many rewarding HITs will be published in the upcoming days. Good luck!'
    # response = mturk.notify_workers(Subject=SubjectNewQualification, MessageText=MessageText_new_batch,
    #                                 WorkerIds=list(relevant_workers))  # response['NotifyWorkersFailureStatuses']
    # print(response)
    # print("Done")

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

if __name__ == '__main__':
    main()