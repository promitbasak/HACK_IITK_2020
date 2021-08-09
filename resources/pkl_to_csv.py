import pandas as pd
import os
import json

pkl_list = [f for f in os.listdir() if f.endswith(".pkl")]
for pkl in pkl_list:
    if type(pd.read_pickle(pkl)) in [pd.DataFrame, pd.Series]:
        pd.read_pickle(pkl).to_csv(pkl[:-4]+".csv", index=False)
    else:
        json.dump(pd.read_pickle(pkl), open(pkl[:-4]+".json", "w"))
        
    
