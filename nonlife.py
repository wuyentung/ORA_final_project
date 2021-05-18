#%%
import gurobipy as gp
import pandas as pd
import numpy as np
#%%
nonlife = pd.read_excel("nonlife-insurance.xlsx", sheet_name="final_variables", index_col=0)
#%%
DMU = nonlife.columns

def make_dict(par, DMU=DMU):
    if len(par) != len(DMU):
        ValueError("shoule be same len")
    made = {}
    c = 0
    for dmu in DMU:
        made[dmu] = par[c][0]
        c+=1
    return made
#%%
X1 = make_dict((np.array(nonlife.iloc[[0]]).T + np.array(nonlife.iloc[[1]]).T).tolist())
X2_1 = make_dict((((np.array(nonlife.iloc[[2]]).T + np.array(nonlife.iloc[[3]]).T + np.array(nonlife.iloc[[4]]).T))/2).tolist())
X2_2 = X2_1

Z1 = make_dict((np.array(nonlife.iloc[[5]]).T + np.array(nonlife.iloc[[6]]).T).tolist())
Z1_1 = make_dict((np.array(nonlife.iloc[[7]]).T).tolist())
Z1_2 = make_dict((np.array(nonlife.iloc[[5]]).T + np.array(nonlife.iloc[[6]]).T - np.array(nonlife.iloc[[7]]).T).tolist())
Z2 = make_dict((np.array(nonlife.iloc[[8]]).T + np.array(nonlife.iloc[[9]]).T).tolist())
#%%
Y1 = make_dict((np.array(nonlife.iloc[[11]]).T).tolist())
Y2 = make_dict((np.array(nonlife.iloc[[10]]).T).tolist())
if min(Y1.values()) < 0:
    mini = - min(Y1.values())
    for key, value in Y1.items():
        Y1[key] = value + mini
#%%
E={}
val_p1,val_p2,val_p3,val_s1,val_s2={},{},{},{},{}
slack_p1,slack_p2,slack_p3={},{},{}
I = 3
O = 2
MID = 3
#%%
for k in DMU:
    P1,P2,P3={},{},{}
    v, u, w = {}, {}, {}

    m = gp.Model("network_DEA_CRS")

    for i in range(I):
        v[i]=m.addVar(vtype=gp.GRB.CONTINUOUS,name="v_%d"%i)

    for i in range(O):
        u[i]=m.addVar(vtype=gp.GRB.CONTINUOUS,name="u_%d"%i)

    for i in range(MID):
        w[i]=m.addVar(vtype=gp.GRB.CONTINUOUS,name="w_%d"%i)
    
    m.update()
    m.setObjective(u[0] * Y1[k] + u[1] * Y2[k] , gp.GRB.MAXIMIZE)

    m.addConstr(
        v[0] * X1[k] + 
        v[1] * X2_1[k] + 
        v[12 * X2_2[k] == 1
        )

    for j in DMU:
        m.addConstr(u[0] * Y1[j] + u[1] * Y2 - (v[0] * X1[j] + v[1] * X2_1[j] + v[2] * X2_2[j]) <= 0)
        P1[j] = m.addConstr(w[0] * Z1_1[j] + w[1] * Z1_2 - (v[0] * X1[j] + v[1] * X2_1[j]) <= 0)
        P2[j] = m.addConstr(w[0] * Z1_1[j] - (v[0] * proc2x1[j]+v[1] * proc2x2[j])<=0)
        P3[j]=m.addConstr(u[2]*proc3TotyO[j]-(v[0]*proc3x1[j]+v[1]*proc3x2[j]+u[0]*proc1yI[j]+u[1]*proc2yI[j]) <= 0)
