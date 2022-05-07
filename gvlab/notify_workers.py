import os
import pickle

import pandas as pd
from tqdm import tqdm

from gvlab.gvlab_swow import mturk

workers_data_path = os.path.join('accepted_workers', 'all_huji_workers.csv')

def main():
    df = pd.read_csv(workers_data_path)
    all_workers = list(set(df['Worker ID'].values))
    all_workers_lists = [all_workers[i:i + 100] for i in range(0, len(all_workers), 100)]

    Subject = 'New Visual Associations Task (GVLAB) - Check it out (Fun!)'
    MessageText_intro = """Greetings! 
You received this email because you have previously annotated for us. 
We have a new task for Visual Associations, check out our project website: https://gvlab-dataset.github.io/. 
Those who wish to participate must pass a test titled "GVLAB: Visual Associations - test for future HITs (Fun!)". 
Upon completing the test, inform us so we can authorize you to do the full HITs.
Thank you :)
"""
    MessageText_passed = 'Hello. You passed the qualification test. You can proceed to the full HITs, titled "GVLAB: Visual Associations - (solve items 550-650)". More will be available soon.'
    MessageText_failed = 'Hello. You did not pass the qualification test. You can proceed to the full HITs, titled "GVLAB: Visual Associations - (solve items 550-650)". More will be available soon.'
    MessageText_new_batch = 'Hello, thanks for annotating GVLAB before, you did a good job :). A new batch is available: "GVLAB: Visual Associations - (solve items 650-1200)", Thanks!'
    SubjectNewBatch = 'New GVLAB batch is available "GVLAB: Visual Associations - (solve items 650-1200)"'
    workers_to_notify_public = ['A1FA3QRISJ1RIP', 'A1WY3YGT618GC0', 'A3UJSDFJ9LBQ6Z', 'AKQAI78JTXXC9']  # public workers
    workers_to_notify_private = ['A1OZPLHNIU1519', 'A2BK45LZGGWPLX', 'A2ONILC0LZKG6Y', 'A2UAHW3Q7S45JP', 'A302KOFOYLD89A', 'A3135Y3RMFC3PK', 'A382S0KJMW3K9S', 'A3BUWQ5C39GRQC']
    workers_to_notify = workers_to_notify_public + workers_to_notify_private
    # all_responses, notifications_path = greeting_message(MessageText_intro, Subject, all_workers_lists)
    response = mturk.notify_workers(Subject=SubjectNewBatch, MessageText=MessageText_new_batch,
                                    WorkerIds=workers_to_notify)  # response['NotifyWorkersFailureStatuses']
    notifications_path = os.path.join('notifications', 'new_batch_650-1200.pickle')
    print(f"Dumping all responses {len(response)} to {notifications_path}")
    pickle.dump(response, open(notifications_path, 'wb'))

    print("Done")


def greeting_message(MessageText_intro, Subject, all_workers_lists):
    all_responses = []
    for lst in tqdm(all_workers_lists, desc='Notifying Workers...', total=len(all_workers_lists)):
        response = mturk.notify_workers(Subject=Subject, MessageText=MessageText_intro,
                                        WorkerIds=lst)  # response['NotifyWorkersFailureStatuses']
        all_responses.append(response)
    notifications_path = os.path.join('notifications', 'greeting.pickle')
    return all_responses, notifications_path


if __name__ == '__main__':
    main()