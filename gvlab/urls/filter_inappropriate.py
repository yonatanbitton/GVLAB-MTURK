import pandas as pd

if __name__ == '__main__':
    inappropriate_indices = pd.read_csv('EXTENDED_GVLAB_dataset_filtered_nsfw.csv')
    bad_ids = list(inappropriate_indices['ID'])
    urls = pd.read_csv('urls_create.csv')
    urls['real_id'] = urls['ID'].apply(lambda x: int(x.split('/')[-1]))
    urls_filtered = urls[~urls['real_id'].isin(bad_ids)]
    print(f"from {len(urls)} to {len(urls_filtered)}")
    urls_filtered.to_csv('urls_create.csv',index=False)
    print("Done")
