import os
import json
import pandas as pd
pd.set_option('display.max_columns', 500)

from gvlab.send_gvlab_tasks import mturk

test_sets_path = 'test_sets'

qual_data_lst = ['3PS3UFWQYLQKDK1X8G5P73OFYLYRYM', '3J3XIOMSTTYANQ2TAL071JT4ZC0I08' ,'3U6Z1K5VYX5KJGIN25QEZ6V34978N2', '3ZT4KTA7QP12TXNO45XYG1KUDSO32E']

solve_hit_types_ids = ['36R4ILE2GAQ1OZ6Z7L174EFT51AFHG', '3ABSYNXI57NPRZT5O7RK079PHQZMWU', '34W4CI95J0NSJKQ6AHJ0UUUX2GUI9K', '3029CDJAWE2TGO6JR9IGKSJA2ZBDSO', '3S942EFUVKZ59R1T0AKMY9A86SZJE7', '31UK836KROSS8RVV3KINI5EVNBTG3A', '3PS3UFWQYLQKDK1X8G5P73OFYLZYRU', '3ES7ZYWJECSULNMPGJB6W8UQ8OKHC9', '32A8IZJLQFI72Z2UI57PMZF56GCGHI','30AWZEBKT3DFB0EBAD1EFM7MVTVCAU', '3DIFNAQ3LD1WDWH1NKHUHOTKD50T3V', '359956SLTZK0DLUYP1GZDVMJP6XRLX']
create_hit_types_ids = ['3K3YEJM751RRJS8ZW8AYJ5Y3VVB5WP', '3HMIRIJYITY39Q6S35I504KLG4XRVE', '325VGVP4D3PCDRAZVOXKTZLWGGX0L7', '3HMIRIJYITY39Q6S35I504KLG4XRVE']
swow_solve_test_hit_type_id = '3DIFNAQ3LD1WDWH1NKHUHOTKD50T3V'
game_solve_test_hit_type_id = '3RL1BYM2927VU09ARQF3354OO0N97K'

def main():
    get_workers_stats()

    swow = pd.read_csv(os.path.join(test_sets_path, 'gvlab_swow_split.csv'))
    swow_sampled_test_results_df = pd.read_csv(os.path.join('results', f'results_hit_type_id_{swow_solve_test_hit_type_id}.csv'))

    print("SWOW")
    get_splitted_results_for_split(swow, swow_sampled_test_results_df)

    game = pd.read_csv(os.path.join(test_sets_path, 'gvlab_game_split.csv'))
    game_sampled_test_results_df = pd.read_csv(os.path.join('results', f'results_hit_type_id_{game_solve_test_hit_type_id}.csv'))

    print(f"Game, jaccard: {game_sampled_test_results_df['jaccard'].mean()}")
    print("Game SWOW based")
    game_swow_based = game[game['images_source'] == 'swow']
    game_swow_sampled_test_results_df = game_sampled_test_results_df[
            game_sampled_test_results_df['id'].apply(lambda x: int(x.split("_")[-1]) in game_swow_based['ID'])]
    print(f"game_swow_based: {len(game_swow_based)}")
    get_splitted_results_for_split(game_swow_based, game_swow_sampled_test_results_df)

    print("Game Random images")
    game_game_based = game[game['images_source'] == 'random']
    game_game_sampled_test_results_df = game_sampled_test_results_df[
        game_sampled_test_results_df['id'].apply(lambda x: int(x.split("_")[-1]) in game_game_based['ID'])]
    print(f"game_game_based: {len(game_game_based)}")
    get_splitted_results_for_split(game_game_based, game_game_sampled_test_results_df)

    print("Done")


def get_splitted_results_for_split(dataset, swow_sampled_test_results_df):
    dataset_solve = swow_sampled_test_results_df
    print(f'Total human performance: mean: {dataset_solve["jaccard"].mean()}, std: {dataset_solve["jaccard"].std()}')
    dataset['num_candidates'] = dataset['candidates'].apply(lambda x: len(json.loads(x)))
    dataset_solve['num_candidates'] = dataset_solve['candidates'].apply(lambda x: len(json.loads(x.replace("'", '"'))))
    res_partitions = []
    general_res = []
    for num_candidates in set(dataset['num_candidates']):
        dataset_num_candidates = dataset[dataset['num_candidates'] == num_candidates]
        num_candidates_items = len(dataset_num_candidates)
        dataset_solve_num_candidates = dataset_solve[dataset_solve['num_candidates'] == num_candidates]
        num_candidates_performance = round(dataset_solve_num_candidates['jaccard'].mean(), 3)
        general_res.append({'num_candidates': num_candidates, 'num_candidates_items': num_candidates_items,
                                 'num_candidates_performance': num_candidates_performance})
        for num_associations in set(dataset['num_associations']):
            dataset_num_associations = dataset_num_candidates[
                dataset_num_candidates['num_associations'] == num_associations]
            num_associations_items = len(dataset_num_associations)
            dataset_solve_num_candidates = dataset_solve_num_candidates[
                dataset_solve_num_candidates['num_candidates'] == num_candidates]
            dataset_solve_num_candidates['num_associations'] = dataset_solve_num_candidates['labels'].apply(lambda x: len(json.loads(x.replace("{","[").replace("}",']').replace("'",'"'))))
            dataset_solve_num_associations = dataset_solve_num_candidates[dataset_solve_num_candidates['num_associations'] == num_associations]
            # print(f"Mean for {num_associations} {len(dataset_solve_num_associations)}")
            num_associations_performance = round(dataset_solve_num_associations['jaccard'].mean(), 4)
            res_partitions.append({'num_candidates': num_candidates,
                                     'num_associations': num_associations,
                                     'num_associations_items': num_associations_items,
                                     'num_associations_performance': num_associations_performance})

    print("General")
    general_res_df = pd.DataFrame(general_res)
    print(general_res_df)

    print("Partitions")
    res_partitions_df = pd.DataFrame(res_partitions)
    print(res_partitions_df)

    return res_partitions

def get_workers_stats():
    all_workers2details = get_qual_data()
    print(f"Got total of {len(all_workers2details)} workers")
    # num workers, average score for workers, avg bonus
    solvers_df = get_annotator_df(solve_hit_types_ids, annotator_type='solver')
    print_workers_stats(all_workers2details, solvers_df, annotator_type='solver')
    sorted_solvers = solvers_df.sort_values(by=['# items', 'jaccard'], ascending=[True, False])
    sorted_solvers['worker'] = sorted_solvers.index
    sorted_solvers = sorted_solvers[sorted_solvers['# items'] < 300]
    sorted_solvers = sorted_solvers[sorted_solvers['# items'] > 15]
    annotators_to_solve_game = sorted_solvers.query('jaccard > 0.90')
    testers_worker_ids = ['AXFTXWW2B0Y5B', 'A2V3P1XE33NYC3', 'A2QX3YJXAAHHVV', 'A19UED74G8FXN3',
       'A30BPQ2QGZOXN8', 'A36P1ZQ0GYF567', 'A382S0KJMW3K9S']
    subject = 'GVLAB: You were selected as a tester, an increased-paid batch is available + bonuses'
    message = "Hello. You previously solved Visual Associations and now you have been selected as a tester. \n" \
              " The batch name is 'GVLAB: Solve Visual Associations created by users (Fun!) - Solve carefully - it's a test (Increased pay)' \n" \
              " This is a batch with increased pay. Please solve carefully. If you dont understand - skip.\n" \
              " *** Solvers with high performance will receive an additional bonus. *** \n" \
              " Please let us know if something is unclear."
    # response = mturk.notify_workers(Subject=subject, MessageText=message,
    #                                 WorkerIds=testers_worker_ids)  # response['NotifyWorkersFailureStatuses']

    creators_df = get_annotator_df(create_hit_types_ids, annotator_type='creator')
    print_workers_stats(all_workers2details, creators_df, annotator_type='creator')


def print_workers_stats(all_workers2details, workers_df, annotator_type):
    if annotator_type == 'solver':
        print(f"Num solvers: {len(workers_df)}, average items solved by worker: {round(workers_df['# items'].mean(), 1)}, mean jaccard for worker: {round(workers_df['jaccard'].mean(), 3)}, std: {round(workers_df['jaccard'].std(), 3)}")
    else:
        print(f"Num creators: {len(workers_df)}, average items created: {round(workers_df['# items'].mean(), 1)}, mean fool-the-AI score: {round(workers_df['score_fooling_ai'].mean(), 3)}")
    solvers_personal_details = pd.DataFrame({k: v for k, v in all_workers2details.items() if k in workers_df.index}).T
    for c in solvers_personal_details:
        print(c)
        if c == 'ages':
            print(f"mean: {solvers_personal_details['ages'].mean()}, std: {solvers_personal_details['ages'].std()}")
        else:
            print(solvers_personal_details[c].value_counts())
        print()


def get_annotator_df(hit_types_ids, annotator_type):
    all_data = pd.DataFrame()
    for solve_hit_types_id in hit_types_ids:
        s_df = pd.read_csv(os.path.join('results', f'results_hit_type_id_{solve_hit_types_id}.csv'))
        all_data = pd.concat([all_data, s_df])
    solvers_data = {}
    for worker, worker_df in all_data.groupby("WorkerId"):
        if worker in solvers_data:
            raise Exception()
        if annotator_type == 'solver':
            ann_dict = {'# items': len(worker_df), 'jaccard': worker_df['jaccard'].mean()}
        else:
            score_fooling_ai = (worker_df['score_fooling_ai_1'].mean() + worker_df['score_fooling_ai_2'].mean()) / 2
            ann_dict = {'# items': len(worker_df) * 2, 'score_fooling_ai': score_fooling_ai}
        solvers_data[worker] = ann_dict
    solvers_df = pd.DataFrame(solvers_data).T
    return solvers_df


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