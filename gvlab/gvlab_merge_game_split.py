import json
import numpy as np
import pandas as pd

# from gvlab.send_gvlab_tasks import mturk, create_or_get_qualification
from gvlab.gvlab_evaluate_created_data_and_calc_bonus import calc_bonus
from gvlab.send_gvlab_tasks import mturk


def get_score_by_cue_association(r):
    if r['cue'] == r['cue1']:
        return r['score_fooling_ai_1']
    elif r['cue'] == r['cue2']:
        return r['score_fooling_ai_2']
    else:
        Exception(f'Unknown Score')


def get_worker_temploral_index(x, workers_submit_times, idx):
    worker_submit_time_list = workers_submit_times[x['WorkerId']]
    worker_temploral_index = worker_submit_time_list.index(x['SubmitTime'])
    if idx % 2 != 0:
        worker_temploral_index += 1
    return worker_temploral_index


def main(user_collected_assocations_paths, mean_jaccard_per_association_path, std_jaccard_per_association_paths):
    user_data = pd.DataFrame()
    for p in user_collected_assocations_paths:
        curr_data = pd.read_csv(p)
        print(f"curr_data: {len(curr_data)}")
        user_data = pd.concat([user_data, curr_data])
    user_data['num_candidates'] = user_data['candidates'].apply(lambda x: len(json.loads(x)))
    add_solvers_jaccard_mean(mean_jaccard_per_association_path, user_data)
    add_solvers_jaccard_std(std_jaccard_per_association_paths, user_data)

    ### SCORE
    user_data['score'] = user_data.apply(lambda r: get_score_by_cue_association(r), axis=1)
    user_data['score_fool_the_ai'] = user_data['score']

    user_data_not_null_mean = user_data[user_data['solvers_jaccard_mean'] != -1]
    print(f"Not null proportion - user_data_not_null_mean: {len(user_data_not_null_mean)}/{len(user_data)}")

    user_data_not_null_std = user_data_not_null_mean[user_data_not_null_mean['solvers_jaccard_std'] != -1]
    print(f"Not null proportion - user_data_not_null_mean: {len(user_data_not_null_std)}/{len(user_data_not_null_mean)}")

    user_data = user_data_not_null_std

    # get_worker_scores()
    # get_temporal_charts(user_data)
    # get_temporal_correlations(user_data)

    relevant_columns = ['HITId', 'id', 'candidates', 'cue', 'associations', 'score_fool_the_ai', 'num_associations', 'annotation_index', 'num_candidates', 'solvers_jaccard_mean', 'solvers_jaccard_std']
    game_data = user_data[relevant_columns]
    print(f"game_data: {len(game_data)}, solvers_jaccard_mean: {round(game_data['solvers_jaccard_mean'].mean(), 2)}, score_fool_the_ai: {round(game_data['score_fool_the_ai'].mean(), 2)}")

    game_data_above_threshold = game_data[game_data['solvers_jaccard_mean'] > 0.8]
    print(f"game_data_above_threshold: {len(game_data_above_threshold)}, solvers_jaccard_mean: {round(game_data_above_threshold['solvers_jaccard_mean'].mean(), 2)}, score_fool_the_ai: {round(game_data_above_threshold['score_fool_the_ai'].mean(), 2)}")
    game_data_above_threshold.to_csv('test_sets/gvlab_game_split.csv')
    print("Done")


def get_temporal_correlations(user_data):
    all_correlations = []
    for worker, worker_df in user_data.groupby('WorkerId'):
        correlation_temporal_index_and_bonus = round(
            worker_df['worker_annotation_temporal_index'].corr(worker_df['bonus']), 2)
        correlation_temporal_index_and_fool_the_ai = round(
            worker_df['worker_annotation_temporal_index'].corr(worker_df['score_fool_the_ai']), 2)
        correlation_temporal_index_and_solvable_by_humans = round(
            worker_df['worker_annotation_temporal_index'].corr(worker_df['solvers_jaccard_mean']), 2)
        all_correlations.append({'worker': worker, 'bonus': correlation_temporal_index_and_bonus,
                                 'fool-the-ai': correlation_temporal_index_and_fool_the_ai,
                                 'solvable-by-humans': correlation_temporal_index_and_solvable_by_humans})
        worker_df_sorted = worker_df.sort_values(by='worker_annotation_temporal_index')
        # worker_df.set_index('worker_annotation_temporal_index')['bonus'].plot.line()
    all_correlations = pd.DataFrame(all_correlations).set_index('worker')
    print(f'all_correlations: {all_correlations}')
    print(all_correlations.mean())


def get_temporal_charts(user_data):
    workers_submit_times = {}
    for worker, worker_df in user_data.groupby('WorkerId'):
        worker_submit_time = list(worker_df['SubmitTime'])
        workers_submit_times[worker] = worker_submit_time
    user_data['score_fool_the_ai'] = user_data['score']
    worker_annotation_temporal_index_lst = []
    for idx, (r_idx, r) in enumerate(user_data.iterrows()):
        worker_annotation_temporal_index_lst.append(get_worker_temploral_index(r, workers_submit_times, idx))
    user_data['worker_annotation_temporal_index'] = worker_annotation_temporal_index_lst
    user_data['bonus'] = user_data.apply(lambda r: calc_bonus(r['score'], r['solvers_jaccard_mean']), axis=1)
    workers_accumulative_data = []
    for i in range(max(worker_annotation_temporal_index_lst)):
        workers_in_ith_annotation = user_data[user_data['worker_annotation_temporal_index'] == i]
        bonus_mean = workers_in_ith_annotation['bonus'].mean()
        score_fool_the_ai_mean = workers_in_ith_annotation['score_fool_the_ai'].mean()
        solvers_jaccard_mean_mean = workers_in_ith_annotation['solvers_jaccard_mean'].mean()
        data_i = {'annotation_temporal_index': i, 'num_workers': len(workers_in_ith_annotation),
                  'bonus_mean': bonus_mean, 'score_fool_the_ai_mean': score_fool_the_ai_mean,
                  'solvers_jaccard_mean_mean': solvers_jaccard_mean_mean}
        workers_accumulative_data.append(data_i)
    workers_accumulative_data_df = pd.DataFrame(workers_accumulative_data)
    workers_accumulative_data_df = workers_accumulative_data_df.set_index('annotation_temporal_index')
    # import matplotlib.pyplot as plt
    # workers_accumulative_data_df['bonus_mean'].plot.line()
    # plt.ylabel('average bonus')
    # plt.suptitle('bonus as a factor of annotation index')
    #
    # workers_accumulative_data_df['score_fool_the_ai_mean'].plot.line()
    # plt.ylabel('average fool-the-AI score')
    # plt.suptitle('fool-the-AI score as a factor of annotation index')
    #
    # workers_accumulative_data_df['solvers_jaccard_mean_mean'].plot.line()
    # plt.ylabel('average solvable-by-humans score')
    # plt.suptitle('solvable-by-humans score as a factor of annotation index')


def get_worker_scores():
    pass
    # all_scores_for_workers = []
    # for worker, worker_df in user_data.groupby('WorkerId'):
    #     first_assignment_id = worker_df['AssignmentId'].iloc[0]
    #     num_associations = worker_df['num_associations'].mean()
    #     mean_solver_jaccard = int(worker_df['solvers_jaccard_mean'].mean() * 100)
    #     mean_human_vs_model_jaccard = int(worker_df['score'].mean())
    #     worker_annotations_num = len(worker_df)
    #     proportion_solvable_by_humans = int(len(worker_df[worker_df['solvers_jaccard_mean'] >= 0.8]) / len(worker_df) * 100)
    #     all_scores_for_workers.append({'worker': worker, 'worker_annotations_num': worker_annotations_num, 'score_fooling_ai': mean_human_vs_model_jaccard, 'score_solvable_by_humans': mean_solver_jaccard, 'num_associations': num_associations, 'proportion_solvable_by_humnans': proportion_solvable_by_humans, 'first_assignment_id': first_assignment_id})
    # all_scores_for_workers_df = pd.DataFrame(all_scores_for_workers)
    # get_user_agreement(user_data)


def get_user_agreement(user_data):
    df_by_id = user_data.groupby('id')
    all_user_agreements = []
    all_mean_user_jaccard_for_association = {}
    all_std_user_jaccard_for_association = {}
    all_items = []
    for id, df_by_id in df_by_id:
        user1_preds = set(sorted(df_by_id['user_predictions'].iloc[0]))
        user2_preds = set(sorted(df_by_id['user_predictions'].iloc[1]))
        user3_preds = set(sorted(df_by_id['user_predictions'].iloc[2]))
        user_agreement_jaccard = len(user1_preds & user2_preds & user3_preds) / len(
            user1_preds | user2_preds | user3_preds)
        all_user_agreements.append(user_agreement_jaccard)

        user1_jaccard = df_by_id['jaccard'].iloc[0]
        user2_jaccard = df_by_id['jaccard'].iloc[1]
        user3_jaccard = df_by_id['jaccard'].iloc[2]
        mean_user_jaccard = round(np.mean([user1_jaccard, user2_jaccard, user3_jaccard]), 2)
        all_mean_user_jaccard_for_association[id] = mean_user_jaccard
        std_user_jaccard = round(np.std([user1_jaccard, user2_jaccard, user3_jaccard]), 2)
        all_std_user_jaccard_for_association[id] = std_user_jaccard

        for c in ['labels', 'candidates']:
            assert df_by_id[c].iloc[0] == df_by_id[c].iloc[1] == df_by_id[c].iloc[2]

        game_rows = user_data[user_data['ID'] == id]
        assert len(game_rows) == 1
        game_row = game_rows.iloc[0].to_dict()
        game_row['solvers_jaccard_mean'] = mean_user_jaccard
        game_row['solvers_jaccard_std'] = std_user_jaccard
        all_items.append(game_row)

    print(f"user agreement: {int(np.mean(all_user_agreements) * 100)}")
    print(f'mean jaccard for association: {round(np.mean(list(all_mean_user_jaccard_for_association.values())) * 100, 2)}')
    print(f'mean jaccard STD for association: {round(np.mean(list(all_std_user_jaccard_for_association.values())) * 100, 2)}')

    # swow_with_jaccard_items_df = pd.DataFrame(swow_with_jaccard_items)
    #
    # bad_ids = []
    # for idx, item in enumerate(swow_with_jaccard_items_df[['ID', 'candidates_connectivity_data']].values):
    #     try:
    #         json.loads(item[1].replace("'", '"'))
    #     except Exception:
    #         print((item[0]))
    #         bad_ids.append(item[0])
    #
    # swow_with_jaccard_items_df = swow_with_jaccard_items_df[~swow_with_jaccard_items_df['ID'].isin(bad_ids)]
    # swow_with_jaccard_items_df_above_threshold = swow_with_jaccard_items_df[swow_with_jaccard_items_df['solvers_jaccard_mean'] > 0.8].sample(1000)
    # relevant_columns = ['ID', 'cue', 'associations', 'num_associations', 'cue_weight', 'associations_mean_weight', 'candidates', 'candidates_connectivity_data', 'candidates_connectivity_score', 'solvers_jaccard_mean', 'solvers_jaccard_std']
    # swow_with_jaccard_items_df_above_threshold = swow_with_jaccard_items_df_above_threshold[relevant_columns]
    # swow_with_jaccard_items_df_above_threshold['candidates_connectivity_data'] = swow_with_jaccard_items_df_above_threshold['candidates_connectivity_data'].apply(lambda x: json.dumps(json.loads(x.replace("'",'"'))))

    # print(f'Writing swow_with_jaccard_items_df_above_threshold at length {len(swow_with_jaccard_items_df_above_threshold)} to test_sets/gvlab_swow_split.csv')
    # swow_with_jaccard_items_df_above_threshold.to_csv('test_sets/gvlab_swow_split.csv',index=False)
    return all_mean_user_jaccard_for_association, all_std_user_jaccard_for_association

def add_solvers_jaccard_mean(mean_jaccard_per_association_path, user_data):
    mean_solvers_jaccard_per_association = {}
    for p in mean_jaccard_per_association_path:
        mean_solvers_jaccard_per_association = {**mean_solvers_jaccard_per_association, **json.load(open(p, 'r'))}
    mean_solvers_jaccard_per_association_index = {int(k.split("_")[-1]): v for k, v in
                                                  mean_solvers_jaccard_per_association.items()}
    user_data['solvers_jaccard_mean'] = user_data['annotation_index'].apply(
        lambda x: mean_solvers_jaccard_per_association_index[
            x] if x in mean_solvers_jaccard_per_association_index else -1)

def add_solvers_jaccard_std(std_jaccard_per_association_path, user_data):
    std_solvers_jaccard_per_association = {}
    for p in std_jaccard_per_association_path:
        std_solvers_jaccard_per_association = {**std_solvers_jaccard_per_association, **json.load(open(p, 'r'))}
    std_solvers_jaccard_per_association_index = {int(k.split("_")[-1]): v for k, v in
                                                  std_solvers_jaccard_per_association.items()}
    user_data['solvers_jaccard_std'] = user_data['annotation_index'].apply(
        lambda x: std_solvers_jaccard_per_association_index[
            x] if x in std_solvers_jaccard_per_association_index else -1)


def get_proportion_pass_joint_score(all_scores_for_workers_df, min_score_fooling_ai, min_score_solvable_humans):
    pass_joint = len(all_scores_for_workers_df[all_scores_for_workers_df.apply(lambda x: x['score_fooling_ai'] >= min_score_fooling_ai and x['score_solvable_by_humans'] >= min_score_solvable_humans, axis=1)])
    proportion = pass_joint / len(all_scores_for_workers_df)
    return proportion

if __name__ == '__main__':
    hit_types_ids_swow_images = ['3PS3UFWQYLQKDK1X8G5P73OFYLZYRU', '3ES7ZYWJECSULNMPGJB6W8UQ8OKHC9', '32A8IZJLQFI72Z2UI57PMZF56GCGHI'] # solve-create 0-100 - real # solve-create 100-300 - real # solve-create 300-500 - real
    hit_types_ids_random_images = ['30AWZEBKT3DFB0EBAD1EFM7MVTVCAU', '359956SLTZK0DLUYP1GZDVMJP6XRLX']
    user_collected_assocations_paths = ['created_data/create_hit_type_id_3K3YEJM751RRJS8ZW8AYJ5Y3VVB5WP_indices_0_100.csv', 'created_data/create_hit_type_id_3HMIRIJYITY39Q6S35I504KLG4XRVE_indices_100_500.csv', 'created_data/create_hit_type_id_325VGVP4D3PCDRAZVOXKTZLWGGX0L7_random_indices_0_100.csv', 'created_data/create_hit_type_id_36ENCJ709KV0KB7BIVKYZOALLH2KEA_random_indices_100_250.csv']
    mean_jaccard_per_association_paths_swow = [f"results/all_mean_user_jaccard_for_association_{h}.json" for h in hit_types_ids_swow_images]
    std_jaccard_per_association_paths_swow = [f"results/all_std_user_jaccard_for_association_{h}.json" for h in hit_types_ids_swow_images]
    mean_jaccard_per_association_paths_random = [f"results/all_mean_user_jaccard_for_association_{h}.json" for h in hit_types_ids_random_images]
    std_jaccard_per_association_paths_random = [f"results/all_std_user_jaccard_for_association_{h}.json" for h in hit_types_ids_random_images]
    mean_jaccard_per_association_paths = mean_jaccard_per_association_paths_swow + mean_jaccard_per_association_paths_random
    std_jaccard_per_association_paths = std_jaccard_per_association_paths_swow + std_jaccard_per_association_paths_random
    main(user_collected_assocations_paths, mean_jaccard_per_association_paths, std_jaccard_per_association_paths)