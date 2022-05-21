import os
import json
import pandas as pd

test_sets_path = 'test_sets'

qual_data_lst = ['3PS3UFWQYLQKDK1X8G5P73OFYLYRYM', '3J3XIOMSTTYANQ2TAL071JT4ZC0I08' ,'3U6Z1K5VYX5KJGIN25QEZ6V34978N2', '3ZT4KTA7QP12TXNO45XYG1KUDSO32E']

solve_hit_types_ids = ['36R4ILE2GAQ1OZ6Z7L174EFT51AFHG', '3ABSYNXI57NPRZT5O7RK079PHQZMWU', '34W4CI95J0NSJKQ6AHJ0UUUX2GUI9K', '3029CDJAWE2TGO6JR9IGKSJA2ZBDSO', '3S942EFUVKZ59R1T0AKMY9A86SZJE7', '31UK836KROSS8RVV3KINI5EVNBTG3A', '3PS3UFWQYLQKDK1X8G5P73OFYLZYRU', '3ES7ZYWJECSULNMPGJB6W8UQ8OKHC9', '32A8IZJLQFI72Z2UI57PMZF56GCGHI','30AWZEBKT3DFB0EBAD1EFM7MVTVCAU', '3DIFNAQ3LD1WDWH1NKHUHOTKD50T3V']

def main():
    all_workers2details = get_qual_data()
    print(f"Got total of {len(all_workers2details)} workers")

    # num workers, average score for workers, avg bonus

    swow = pd.read_csv(os.path.join(test_sets_path, 'gvlab_swow_split.csv'))
    game = pd.read_csv(os.path.join(test_sets_path, 'gvlab_game_split.csv'))
    print("Done")


def get_qual_data():
    all_workers_info = pd.DataFrame()
    all_workers2details = {}
    for q in qual_data_lst:
        q_df = pd.read_csv(os.path.join('results', f'results_hit_type_id_{q}.csv'))
        q_df = q_df[~q_df['personal_details'].isna()]
        if 'score' not in q_df:
            q_df['solve_score'] = q_df['jaccard']
            q_df['create_score'] = -1
            q_df['task_type'] = 'solve'
        else:
            q_df['task_type'] = 'create'
            q_df['create_score'] = q_df['score']
            q_df['solve_score'] = -1
        q_df = q_df[['WorkerId', 'personal_details', 'task_type', 'solve_score', 'create_score']].drop_duplicates()
        q_df['personal_details'] = q_df['personal_details'].apply(lambda x: json.loads(x.replace("'", '"')))
        q_workers_info = q_df[['WorkerId', 'personal_details', 'solve_score', 'create_score', 'task_type']]
        worker2details = dict(q_df[['WorkerId','personal_details']].values)
        all_workers2details = {**all_workers2details, **worker2details}
        all_workers_info = pd.concat([all_workers_info, q_workers_info])
    # workers_items = []
    # for worker, worker_df in all_workers_info.groupby('WorkerId'):
    #     worker_solve = worker_df[worker_df['task_type'] == 'solve']
    #     worker_create = worker_df[worker_df['task_type'] == 'create']
    #     workers_items.append(
    #         {'worker': worker, 'num_solve': len(worker_solve), 'solve_score': worker_solve['solve_score'].mean(),
    #          'num_create': len(worker_create), 'create_score': worker_df['create_score'].mean(), 'personal_details': personal_details})
    # workers_items_df = pd.DataFrame(workers_items)
    return all_workers2details


if __name__ == '__main__':
    main()