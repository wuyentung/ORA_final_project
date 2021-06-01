#%%
import pandas as pd
import numpy as np 
import solver
#%%
life = pd.read_excel("/Users/tungwu/Documents/GitHub/ORA_final_project/data/life_2019.xlsx", index_col=0)
DMU = [dmu for dmu in life.columns]
# DMU.remove("友邦人壽")
# DMU.remove("法國巴黎人壽")
# DMU.remove("安達人壽")

solver.solve(df=life, DMU=DMU, NAME="life_2019")
#%%
nonlife = pd.read_excel("/Users/tungwu/Documents/GitHub/ORA_final_project/data/nonlife_2019.xlsx", index_col=0)
DMU = [dmu for dmu in nonlife.columns]
DMU.remove("科法斯")
DMU.remove("裕利安宜")
DMU.remove("法國巴黎")
DMU.remove("安達")
DMU.remove("美國國際")
DMU.remove("亞洲")
solver.solve(df=nonlife, DMU=DMU, NAME="nonlife_2019")
#%%
solver.pp()
#%%
temp = pd.read_excel("/Users/tungwu/Documents/GitHub/ORA_final_project/result/nonlife_2019_result.xlsx", index_col=0)
#%%
