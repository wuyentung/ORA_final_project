#%%
import pandas as pd
import numpy as np 
import solver
#%%
life = pd.read_excel("life_2019.xlsx", index_col=0)
DMU = [dmu for dmu in life.columns]
# DMU.remove("友邦人壽")
# DMU.remove("法國巴黎人壽")
# DMU.remove("安達人壽")

solver.solve(df=life, DMU=DMU)
#%%
