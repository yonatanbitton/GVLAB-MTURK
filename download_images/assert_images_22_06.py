import json
import cv2

import requests as requests
from tqdm import tqdm
from PIL import Image

image2url = json.load(open('download_images/image2url.json','r'))

working = {}
exceptions = {}
images_suffixes = ['.jpg','.jpeg','.png','.JPG','.JPEG','.PNG']

with open('download_images/fixed/working.txt', 'w') as f:
    for cand,url in tqdm(image2url.items(), total=len(image2url), desc='downloading images'):
        if any(url.endswith(x) for x in images_suffixes):
            fixed_url = url
        else:
            found_fix = False
            for suff in images_suffixes:
                if suff in url:
                    fixed_url = url[:url.index(suff) + len(suff)]
                    found_fix = True
                    f.write(f"{cand},{fixed_url}\n")
                    break
            if not found_fix:
                print(f"NOT FOUND FIX {cand} (Total {len(exceptions)})")
                exceptions[cand] = url
                continue
        try:
            image = Image.open(requests.get(fixed_url, stream=True).raw).convert("RGB")
            working[cand] = fixed_url
            # image.save(f'download_images/plots/{cand}.png')
        except:
            print(f"Exception {cand} (Total {len(exceptions)})")
            exceptions[cand] = url
        # cv2.imwrite(f'plots/{cand}.png',image)

json.dump(working, open('fixed/working.json','w'))
json.dump(exceptions, open('fixed/exceptions.json','w'))

print(f"Exceptions {len(exceptions)}")
print(exceptions)
