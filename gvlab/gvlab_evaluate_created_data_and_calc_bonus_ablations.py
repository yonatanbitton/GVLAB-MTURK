import json

import pandas as pd

# from gvlab.send_gvlab_tasks import mturk, create_or_get_qualification
from gvlab.send_gvlab_tasks import mturk


def calc_bonus(score_fool_ai, score_solvable_by_humans):
    # Base payment 0.07$
    if score_solvable_by_humans < 0.8 or score_fool_ai < 50:
        return 0
    if 50 <= score_fool_ai < 60:
        return 0.03  # total - 0.08$ (+0.03$)
    elif 60 <= score_fool_ai < 67:
        return 0.07  # total - 0.12$ (+0.04$)
    elif 67 <= score_fool_ai < 80:
        # return 0.12  # total - 0.17$ (+0.05$)
        return 0.18  # total - 0.17$ (+0.05$)
    elif 80 <= score_fool_ai:
        # return 0.18  # total - 0.23$ (+0.06$)
        return 0.27  # total - 0.23$ (+0.06$)
    else:
        raise Exception(f"Unexpected scores: {score_fool_ai}, {score_solvable_by_humans}")


def get_score_by_cue_association(r):
    if r['cue'] == r['cue1']:
        return r['score_fooling_ai_1']
    elif r['cue'] == r['cue2']:
        return r['score_fooling_ai_2']
    else:
        Exception(f'Unknown Score')


def main(user_collected_assocations_path, mean_jaccard_per_association_path):
    user_data = pd.read_csv(user_collected_assocations_path)
    user_data['num_candidates'] = user_data['candidates'].apply(lambda x: len(json.loads(x)))
    mean_solvers_jaccard_per_association = {}
    for p in mean_jaccard_per_association_path:
        mean_solvers_jaccard_per_association = {**mean_solvers_jaccard_per_association, **json.load(open(p, 'r'))}
    # mean_solvers_jaccard_per_association = json.load(open(mean_jaccard_per_association_path, 'r'))
    mean_solvers_jaccard_per_association_index = {int(k.split("_")[-1]):v for k,v in mean_solvers_jaccard_per_association.items()}
    user_data['mean_solvers_jaccard'] = user_data['annotation_index'].apply(lambda x: mean_solvers_jaccard_per_association_index[x] if x in mean_solvers_jaccard_per_association_index else -1)

    ### SCORE
    user_data['score'] = user_data.apply(lambda r: get_score_by_cue_association(r), axis=1)

    user_data['bonus'] = user_data.apply(lambda r: calc_bonus(r['score'], r['mean_solvers_jaccard']), axis=1)

    user_data_not_null = user_data[user_data['mean_solvers_jaccard'] != -1]
    print(f"Not null proportion: {len(user_data_not_null)}/{len(user_data)}")

    all_scores_for_workers = []
    for worker, worker_df in user_data_not_null.groupby('WorkerId'):
        first_assignment_id = worker_df['AssignmentId'].iloc[0]
        num_associations = worker_df['num_associations'].mean()
        mean_solver_jaccard = int(worker_df['mean_solvers_jaccard'].mean() * 100)
        mean_human_vs_model_jaccard = int(worker_df['score'].mean())
        median_solver_jaccard = int(worker_df['mean_solvers_jaccard'].median() * 100)
        median_human_vs_model_jaccard = int(worker_df['score'].median())
        bonus_mean = worker_df['bonus'].mean()
        bonus_median = worker_df['bonus'].median()
        bonus_total = round(worker_df['bonus'].sum(), 2)
        worker_annotations_num = len(worker_df)
        proportion_solvable_by_humnans = int(len(worker_df[worker_df['mean_solvers_jaccard'] >= 0.8]) / len(worker_df) * 100)
        all_scores_for_workers.append({'worker': worker, 'worker_annotations_num': worker_annotations_num, 'bonus_total': bonus_total, 'score_fooling_ai': mean_human_vs_model_jaccard, 'score_solvable_by_humans': mean_solver_jaccard, 'num_associations': num_associations, 'median_solver_jaccard': median_solver_jaccard, 'median_human_vs_model_jaccard': median_human_vs_model_jaccard, 'bonus_mean': bonus_mean, 'bonus_median': bonus_median, 'proportion_solvable_by_humnans': proportion_solvable_by_humnans, 'first_assignment_id': first_assignment_id})
    all_scores_for_workers_df = pd.DataFrame(all_scores_for_workers).sort_values(by='bonus_mean')

    print("Scores TAHLES")
    print(f"Mean ann num for worker: {all_scores_for_workers_df['worker_annotations_num'].mean()}")
    print(all_scores_for_workers_df[['bonus_mean', 'score_fooling_ai', 'score_solvable_by_humans']].mean())
    print(f"Bonus Total: {all_scores_for_workers_df['bonus_total'].sum()}")

    """
    all_scores_for_workers_df[all_scores_for_workers_df['num_associations'] == 2].mean()
    all_scores_for_workers_df[all_scores_for_workers_df['num_associations'] == 3].mean()
    all_scores_for_workers_df[all_scores_for_workers_df['num_associations'] == 4].mean()
    """



    for r_idx, r in all_scores_for_workers_df.iterrows():
        SubjectBatchFinished = f"Create batch 100-500 have been finished - Your scores and bonuses. "
        worker_sentence = f"Good Job! You created {r['worker_annotations_num']} associations. " \
                          f"\n Your score for fooling the AI is {r['score_fooling_ai']}%, and score for solvable by humans is {r['score_solvable_by_humans']}%. " \
                          f"\n You receive a total bonus of {r['bonus_total']}$, average bonus of {round(r['bonus_mean'],2) * 2}$ per single HIT." \
                          f"\n {r['proportion_solvable_by_humnans']}% of your created associations were solved by solvers in an average score above 80%. " \
                          f"\n Please reach out if you have any questions." \
                          f"\n No more creates for now! Tell us if you want to do 'solves' - HITs will be available soon. Thanks! :)."
        print((r['worker'], r['first_assignment_id']))
        print(worker_sentence)
        # response = mturk.notify_workers(Subject=SubjectBatchFinished, MessageText=worker_sentence,
        #                                 WorkerIds=[r['worker']])  # response['NotifyWorkersFailureStatuses']

        print()

    # best_worker = user_data[user_data['WorkerId'] == 'A382S0KJMW3K9S']
    # best_worker_good_examples = best_worker.query('score == 100 and mean_solvers_jaccard == 1')
    # best_worker_good_examples_urls = best_worker_good_examples['annotation_index'].apply(lambda x: f"https://gvlab-dataset.github.io/mturk/solve/create/{x}")
    # for x in best_worker_good_examples_urls:
    #     print(x)


    # good_examples = user_data.query('score == 100 and mean_solvers_jaccard == 1')
    # good_examples_urls = good_examples['annotation_index'].apply(lambda x: f"https://gvlab-dataset.github.io/mturk/solve/create/{x}")
    # all_examples_string = ""
    # for x in good_examples_urls.sample(50):
    #     # print(x)
    #     all_examples_string += x + " \n "
    # examples_sentence = 'The average ‘fool-the-AI’ score is 47%, ‘solvable-by-humans’ score is 83.2%, and the average bonus per HIT is 0.12$.\n' \
    #                     'All of the examples here are `perfect`: fool-the-AI=100, solvable-by-humans=100 \n' \
    #                     'Enter this URLs and try to solve, you will receive instant feedback \n' \
    #                     'Learn from this example and try to improve for the next batch :) \n' \
    #                     ''
    # message = examples_sentence + all_examples_string
    # response = mturk.notify_workers(Subject=f'GVLAB great examples you created', MessageText=message,
    #                                                                 WorkerIds=list(all_scores_for_workers_df['worker']))  # response['NotifyWorkersFailureStatuses']
    # print(message)
    # print(response)

    min_score_fooling_ai = 35
    min_score_solvable_humans = 75
    proportion_fooling_ai = len(all_scores_for_workers_df[all_scores_for_workers_df['score_fooling_ai'] >= min_score_fooling_ai]) / len(all_scores_for_workers_df)
    proportion_solvable_by_humans = len(all_scores_for_workers_df[all_scores_for_workers_df['score_solvable_by_humans'] >= min_score_solvable_humans]) / len( all_scores_for_workers_df)
    passing_workers = all_scores_for_workers_df[all_scores_for_workers_df.apply(lambda x: x['score_fooling_ai'] >= min_score_fooling_ai and x['score_solvable_by_humans'] >= min_score_solvable_humans, axis=1)]
    amount_pass_joint_score = len(passing_workers)
    proportion_pass_joint_score = amount_pass_joint_score / len(all_scores_for_workers_df)
    print(f"proportion_fooling_ai: {proportion_fooling_ai}, proportion_solvable_by_humans: {proportion_solvable_by_humans}, proportion_pass_joint_score: {proportion_pass_joint_score}")

    # assign_qualification_and_notify(all_scores_for_workers_df, passing_workers)
    # notify_scores_explaination(passing_workers)
    # response = notify_batch(passing_workers)
    # print(response)
    print("Done")


def get_proportion_pass_joint_score(all_scores_for_workers_df, min_score_fooling_ai, min_score_solvable_humans):
    pass_joint = len(all_scores_for_workers_df[all_scores_for_workers_df.apply(lambda x: x['score_fooling_ai'] >= min_score_fooling_ai and x['score_solvable_by_humans'] >= min_score_solvable_humans, axis=1)])
    proportion = pass_joint / len(all_scores_for_workers_df)
    return proportion

if __name__ == '__main__':
    # game swow based
    # 0-100
    # user_collected_assocations_path = 'created_data/create_hit_type_id_3K3YEJM751RRJS8ZW8AYJ5Y3VVB5WP_indices_0_100.csv'
    # mean_jaccard_per_association_path = 'results/all_mean_user_jaccard_for_association_3PS3UFWQYLQKDK1X8G5P73OFYLZYRU.json'
    # 100-500
    # user_collected_assocations_path = 'created_data/create_hit_type_id_3HMIRIJYITY39Q6S35I504KLG4XRVE_indices_100_500.csv'
    # mean_jaccard_per_association_paths = ['results/all_mean_user_jaccard_for_association_3ES7ZYWJECSULNMPGJB6W8UQ8OKHC9.json', 'results/all_mean_user_jaccard_for_association_32A8IZJLQFI72Z2UI57PMZF56GCGHI.json'] # 100-300

    # game random
    # hit_type_id = '30AWZEBKT3DFB0EBAD1EFM7MVTVCAU' # solve-create random 0-100 - real
    # user_collected_assocations_path = 'created_data/create_hit_type_id_325VGVP4D3PCDRAZVOXKTZLWGGX0L7_random_indices_0_100.csv'
    # mean_jaccard_per_association_paths = ['results/all_mean_user_jaccard_for_association_30AWZEBKT3DFB0EBAD1EFM7MVTVCAU.json']

    # hit_type_id = '359956SLTZK0DLUYP1GZDVMJP6XRLX' # solve create 100-250 - real
    # user_collected_assocations_path = 'created_data/create_hit_type_id_36ENCJ709KV0KB7BIVKYZOALLH2KEA_random_indices_100_250.csv'
    # mean_jaccard_per_association_paths = ['results/all_mean_user_jaccard_for_association_359956SLTZK0DLUYP1GZDVMJP6XRLX.json']

    # create random 10-12 - 0-100
    # user_collected_assocations_path = 'created_data/create_hit_type_id_30WQ7ZZ0RU9SNPFM4Z1FUITI23JH9U_random_indices_0_100_candidates_10_12.csv'
    # mean_jaccard_per_association_paths = ['results/all_mean_user_jaccard_for_association_30AWZEBKT3DFB0EBAD1EFM7MVTVCAU.json']

    # create random 10-12 - 100-250
    # user_collected_assocations_path = 'created_data/create_hit_type_id_33KTOXRB2MHEDTK23QD1IIHZSACFRH_random_indices_100_250_candidates_10_12.csv'
    # mean_jaccard_per_association_paths = ['results/all_mean_user_jaccard_for_association_359956SLTZK0DLUYP1GZDVMJP6XRLX.json']

    user_collected_assocations_path = 'created_data/created_data_ablations.csv'
    mean_jaccard_per_association_paths = ['results/all_mean_user_jaccard_for_association_3ISL4H6O6I6UHIX9M1TRWKV5812IC6.json']

    main(user_collected_assocations_path, mean_jaccard_per_association_paths)