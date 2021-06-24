#%%
import pandas as pd
import numpy as np
#%%
pds = pd.read_excel("/Users/tungwu/Documents/GitHub/ORA_final_project/code/compare.xlsx", index_col=0, sheet_name=["life", "nonlife"])
#%%
pds["nonlife"]
#%%
