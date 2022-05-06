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

    all_responses = []
    for lst in tqdm(all_workers_lists, desc='Notifying Workers...', total=len(all_workers_lists)):
        response = mturk.notify_workers(Subject=Subject, MessageText=MessageText_intro, WorkerIds=lst) # response['NotifyWorkersFailureStatuses']
        all_responses.append(response)

    notifications_path = os.path.join('notifications', 'greeting.pickle')
    print(f"Dumping all responses {len(all_responses)} to {notifications_path}")
    pickle.dump(all_responses, open(notifications_path, 'wb'))

    print("Done")

if __name__ == '__main__':
    main()