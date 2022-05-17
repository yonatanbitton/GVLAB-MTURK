from gvlab.send_gvlab_tasks import mturk, create_or_get_qualification


def main():
    first_batch_0_100_workers_results = {'A104V8NZIQFN2F': 81, 'A1FA3QRISJ1RIP': 100, 'A1WY3YGT618GC0': 74, 'A281Q8U3T9H7JS': 76, 'A2BK45LZGGWPLX': 80, 'A2LU259QPV1I4V': 73, 'A2M9JNCHRKMCC4': 74, 'A2N9U74YIPDQ9F': 87, 'A2UAHW3Q7S45JP': 83, 'A30BPQ2QGZOXN8': 86, 'A3135Y3RMFC3PK': 90, 'A36P1ZQ0GYF567': 88, 'AB7MYP65HZ2MH': 77, 'AXFTXWW2B0Y5B': 96, 'AXID3RPK6NZT6': 72}
    first_batch_0_100_workers_results_above_75 = {k:v for k,v in first_batch_0_100_workers_results.items() if v >= 75}
    more_good_public_solvers = {'A1FA3QRISJ1RIP': 98, 'A1WY3YGT618GC0': 86, 'A3UJSDFJ9LBQ6Z': 100, 'A19UED74G8FXN3': 96, 'A2M9JNCHRKMCC4': 96, 'A2QX3YJXAAHHVV': 93, 'A30BPQ2QGZOXN8': 96, 'A3FQNVDMR1ORAT': 93, 'AHB3QFZSFN9DL': 87, 'A2K607J3Z68WRR': 91, 'A36P1ZQ0GYF567': 96, 'A382S0KJMW3K9S': 97, 'A3HE29W5IDR394': 100, 'AB7MYP65HZ2MH': 87, 'A2V3P1XE33NYC3': 90, 'A3135Y3RMFC3PK': 90, 'A18WSAKX5YN2FB': 92, 'A68UG55LKRKMS': 100}
    more_good_public_solvers_not_sent = {k:v for k,v in more_good_public_solvers.items() if k not in first_batch_0_100_workers_results.keys()}
    solvers_of_first_create = {'A104V8NZIQFN2F': 82, 'A18WSAKX5YN2FB': 87, 'A2BK45LZGGWPLX': 83, 'A2UAHW3Q7S45JP': 84, 'A2UCKZZI9KBBCV': 87,
                               'A3135Y3RMFC3PK': 84, 'A36P1ZQ0GYF567': 88, 'A3FQNVDMR1ORAT': 81, 'AB7MYP65HZ2MH': 80, 'AHB3QFZSFN9DL': 90, 'AKQAI78JTXXC9': 80}
    print(f"All workers: {len(first_batch_0_100_workers_results)}, above 75: {len(first_batch_0_100_workers_results_above_75)}, more_good_public_solvers_not_sent: {len(more_good_public_solvers_not_sent)}")
    # all_workers_that_solved = {'A2UAHW3Q7S45JP', 'A104V8NZIQFN2F', 'A302KOFOYLD89A', 'AKQAI78JTXXC9', 'A1FA3QRISJ1RIP', 'A3135Y3RMFC3PK', 'A1PBRKFHSF1OF8', 'A1W1X3S1Y0RKF3', 'A18WSAKX5YN2FB', 'A36P1ZQ0GYF567', 'A2VUF0V7HT51Q3', 'AXID3RPK6NZT6', 'A2ONILC0LZKG6Y', 'A382S0KJMW3K9S', 'A1WY3YGT618GC0', 'A1OZPLHNIU1519', 'A14GKRTUEHBLBZ', 'A3UJSDFJ9LBQ6Z', 'A3BUWQ5C39GRQC', 'A2LU259QPV1I4V', 'A68UG55LKRKMS', 'A2BK45LZGGWPLX', 'A2V3P1XE33NYC3', 'A2K607J3Z68WRR', 'AB7MYP65HZ2MH'}
    # all_creators = {'A377LTGWJKY2IW', 'A3RTW9UWYKSNWX', 'A2M3C5YIO7IZ6G', 'A16184N1RO5OJV', 'AHB3QFZSFN9DL', 'A2ONILC0LZKG6Y', 'A2UCKZZI9KBBCV', 'A2K607J3Z68WRR', 'A3UJSDFJ9LBQ6Z', 'A302KOFOYLD89A', 'A2QX3YJXAAHHVV', 'A382S0KJMW3K9S', 'AKQAI78JTXXC9', 'A1PBRKFHSF1OF8', 'A2V3P1XE33NYC3', 'AZLZA0Q87TJZO', 'A1OZPLHNIU1519', 'A19UED74G8FXN3', 'A1HKYY6XI2OHO1', 'A2SDOD67560IN8'}
    # rovoked_bad_solvers = {'A1WY3YGT618GC0', 'A2LU259QPV1I4V', 'A2M9JNCHRKMCC4', 'AXID3RPK6NZT6'}
    # workers_not_creators_nor_bad_solvers = list(all_workers_that_solved.difference(all_creators.union(rovoked_bad_solvers)))
    # print(f"workers_not_creators: {len(workers_not_creators_nor_bad_solvers)}")
    # SubjectNewQualification = 'GVLAB: New solve batch is available: "GVLAB: Solve Visual Associations created by users (Fun!) - (0-100)"'
    # MessageText_new_batch = 'Hello, You are welcome to solve the new batch "GVLAB: Solve Visual Associations created by users (Fun!) - (0-100)", Have Fun!'
    # SubjectNewQualification = 'New GVLAB "solve" batch available (300-500) for experienced solvers (you)'
    SubjectNewQualification = 'GVLAB: Your solving results and batch available (300-500)'
    # for k,v in first_batch_0_100_workers_results_above_75.items():
    #     message = f"Hello. Your previously annotated GVLAB 'solve'. Your score was {v}, which is above the acceptable bar. Good job!." \
    #               f"\n A new batch is available for you: 'GVLAB: Solve Visual Associations created by users (Fun!) - (100-300)'. " \
    #               f"\n More will be available soon."
    #     response = mturk.notify_workers(Subject=SubjectNewQualification, MessageText=message,
    #                                     WorkerIds=[k])  # response['NotifyWorkersFailureStatuses']
    #     print(response)

    # response = mturk.notify_workers(Subject=SubjectNewQualification, MessageText=MessageText_new_batch,
    #                                 WorkerIds=workers_not_creators_nor_bad_solvers)  # response['NotifyWorkersFailureStatuses']
    # print(response)

    annotated_gvlab_swow_solve = {
        "Name": "First GVLAB Solve Batch Performance",
        "Description": "First GVLAB Solve Batch Performance",
        "QualificationTypeStatus": "Active",
        "AutoGranted": False,
    }
    annotated_gvlab_swow_solve_type_id = create_or_get_qualification(annotated_gvlab_swow_solve)
    for k,v in solvers_of_first_create.items():
        worker_score = v
        # response_assign = mturk.associate_qualification_with_worker(
        #     QualificationTypeId=annotated_gvlab_swow_solve_type_id,  # the public qual
        #     WorkerId=k,
        #     IntegerValue=worker_score,
        #     SendNotification=True
        # )
        # message = f"Hello. Your previously annotated GVLAB 'solve' in good score. Good job!." \
        #           f"\n A new batch is available for you: 'GVLAB: Solve Visual Associations created by users (Fun!) - (300-500)'. " \
        #           f"\n You should now have the qual to do it. " \
        #           f"\b This is more challenging data, created by users to fool-the-AI, please solve it carefully." \
        #           f"\n Solvers with low scores are at risk for losing the qualification" \
        #           f"\n More will be available soon."
        message = f"Hello. You annotated the previous GVLAB game batch (100-300) in a score of ... {v}. Good! Try to be even better in the current batch: 'GVLAB: Solve Visual Associations created by users (Fun!) - (300-500)'"
        print(message)
        response = mturk.notify_workers(Subject=SubjectNewQualification, MessageText=message,
                                        WorkerIds=[k])  # response['NotifyWorkersFailureStatuses']
        print(response)

    print("Done")

if __name__ == '__main__':
    main()