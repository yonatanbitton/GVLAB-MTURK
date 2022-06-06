import pandas as pd
import json

def main():
    df = pd.read_csv('/Users/yonatab/Downloads/10_12_split_big_objects_no_names.csv')
    df = df[~df['direct_visual'].isna()]
    print(f"Total of {len(df)} annotated data")
    print(df['direct_visual'].value_counts())

    results = json.load(open('results/all_mean_user_jaccard_for_association_30AWZEBKT3DFB0EBAD1EFM7MVTVCAU.json'))
    df['% humans'] = df['annotation_index'].apply(lambda x: results[f"solve_create_{x}"])

    for direct_visual_label, direct_visual_label_df in df.groupby('direct_visual'):
        model_performance = round(direct_visual_label_df['score'].apply(lambda x: 100 - x).mean(), 1)
        print(f"direct_visual_label: {direct_visual_label}, items: {len(direct_visual_label_df)}, model_performance: {model_performance}")

    print("Done")

if __name__ == '__main__':
    main()