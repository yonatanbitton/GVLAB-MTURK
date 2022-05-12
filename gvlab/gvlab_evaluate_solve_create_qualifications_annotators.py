import json

import pandas as pd

user_collected_assocations_qualification_data_path = '/Users/yonatab/PycharmProjects/GVLAB-MTURK/gvlab/created_data/user_collected_associations_qualification.csv'
mean_jaccard_per_association_path = 'results/all_mean_user_jaccard_for_association_31UK836KROSS8RVV3KINI5EVNBTG3A.json'

def main():
    user_data = pd.read_csv(user_collected_assocations_qualification_data_path)
    mean_jaccard_per_association = json.load(open(mean_jaccard_per_association_path, 'r'))

    print("Done")



if __name__ == '__main__':
    main()