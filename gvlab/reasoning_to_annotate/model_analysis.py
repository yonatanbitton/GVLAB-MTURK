import pandas as pd
import json
import numpy as np
concreteness_df = pd.read_excel('/Users/yonatab/Documents/PhD/Masking Project/loss_conf_data/Concreteness_ratings_Brysbaert_et_al_BRM.xlsx')
concreteness_for_word = dict(concreteness_df[['Word', 'Conc.M']].values)

def main():
    path = '/Users/yonatab/Downloads/10_12_tagged (1).csv'
    df = pd.read_csv(path)
    # df = pd.read_csv('/Users/yonatab/Downloads/10_12_split_big_objects_no_names.csv')
    df = df[~df['direct_visual'].isna()]
    print(f"Total of {len(df)} annotated data")
    print(df['direct_visual'].value_counts())


    df['cue_concreteness'] = df['cue'].apply(lambda x: concreteness_for_word[x] if x in concreteness_for_word else -1)

    get_human_performance(df)

    print("START")
    df['annotation'] = df.apply(lambda r: get_label(r), axis=1)
    items = []
    for annotation, annotation_df in df.groupby('annotation'):
        # avg_fool_ai = round(annotation_df['score'].mean(), 1)
        only_with_human_above_60 = annotation_df[annotation_df['% humans'] >= 0.60]
        print(f"annotation: {annotation}, only_with_human_above_60: {len(only_with_human_above_60)/len(annotation_df)}")
        human_performance = round(only_with_human_above_60['% humans'].mean() * 100, 1)
        avg_human_score = 100 - round(annotation_df['score'].mean(), 1)
        num_items = len(annotation_df)
        items.append({'annotation': annotation, 'avg_human_score': avg_human_score, 'num_items': num_items, 'human_performance': human_performance})
    items_df = pd.DataFrame(items)
    print(items_df)
    print("END")
    exit()



    model_analysis_scores = []
    for direct_visual_label, direct_visual_label_df in df.groupby('direct_visual'):
        model_performance = round(direct_visual_label_df['score'].apply(lambda x: 100 - x).mean(), 1)
        # human_performance = round(direct_visual_label_df[direct_visual_label_df['% humans'] >= 0.60]['% humans'].mean() * 100, 1)
        # human_performance = round(
        #     direct_visual_label_df['% humans'].mean() * 100, 1)
        print(f"direct_visual_label: {direct_visual_label}, items: {len(direct_visual_label_df)}, model_performance: {model_performance}")
        model_analysis_scores.append({'direct_visual_label': direct_visual_label, '# items': len(direct_visual_label_df), '% model': model_performance, '% humans': human_performance})

    model_analysis_scores_df = pd.DataFrame(model_analysis_scores)
    print(model_analysis_scores_df)

    print("Done")


def get_human_performance(df):
    # results = json.load(open('results/all_mean_user_jaccard_for_association_30AWZEBKT3DFB0EBAD1EFM7MVTVCAU.json'))
    results = pd.read_csv('results/results_hit_type_id_31IV7WI13C89M2DA19OYI2OGG715HS.csv')
    results['candidates'] = results['candidates'].apply(lambda x: json.loads(x.replace("'", '"')))
    df['candidates'] = df['candidates'].apply(lambda x: json.loads(x.replace("'", '"')))
    human_performances = []
    for r_idx, r in df.iterrows():
        found = []
        for res_idx, res_r in results.iterrows():
            cand_no_jpg = [x.split(".")[0] for x in res_r['candidates']]
            if set(cand_no_jpg) == set(r['candidates']):
                found.append(res_r['jaccard'])
        # if len(found) == 3:
        #     print("Got pred")
        human_performances.append(np.mean(found))
    print("human_performances")
    # df['% humans'] = df['annotation_index'].apply(lambda x: results[f"solve_create_{x}"] if x in results else None)
    df['% humans'] = human_performances

def get_label(r):
    if r['direct_visual'] == 1:
        return 'direct_visual'
    # elif r['visual_non_direct'] == 1:
    #     return 'visual_non_direct'
    # elif r['direct_visual'] == 0 and r['visual_non_direct'] == 0:
    #     return 'non_visual'
    elif r['visual_non_direct'] == 1:
        return 'not_visually_salient'
    elif r['direct_visual'] == 0 and r['visual_non_direct'] == 0:
        return 'not_visually_salient'
    else:
        return None

if __name__ == '__main__':
    main()