#%%
import gurobipy as gp
import pandas as pd
import numpy as np
#%%
nonlife = pd.read_excel("nonlife-insurance.xlsx", sheet_name="final_variables", index_col=0)
#%%
DMU = [dmu for dmu in nonlife.columns]
DMU.remove("科法斯")
DMU.remove("裕利安宜")
DMU.remove("亞洲")
#%%
def make_dict(par, DMU=DMU):
    if len(par) != len(DMU):
        ValueError("shoule be same len")
    made = {}
    c = 0
    for dmu in DMU:
        # print(DMU)
        # print(par[c][0])
        made[dmu] = par[c][0]
        c+=1
    return made
#%%
X1 = make_dict((np.array(nonlife.iloc[[0]]).T + np.array(nonlife.iloc[[1]]).T).tolist())
X2 = make_dict((((np.array(nonlife.iloc[[2]]).T + np.array(nonlife.iloc[[3]]).T + np.array(nonlife.iloc[[4]]).T))).tolist())
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
# #%%
# DMU=['A', 'B', 'C', 'D', 'E']
# def make_dict(par, DMU=DMU):
#     if len(par) != len(DMU):
#         ValueError("shoule be same len")
#     made = {}
#     c = 0
#     for dmu in DMU:
#         # print(DMU)
#         # print(par[c][0])
#         made[dmu] = par[c][0]
#         c+=1
#     return made
# #%%
# X1 = make_dict(par=[[1], [1], [1], [1], [100]])
# # X2 = make_dict(par=[[4], [6], [8], [10], [12]])
# X2_1 = make_dict(par=[[2], [2], [2], [20], [400]])
# # X2_2 = make_dict(par=[[2], [3], [4], [5], [6]])
# Z1 = make_dict(par=[[300], [120], [10], [4], [1]])
# # Z1_1 = make_dict(par=[[1], [2], [3], [2], [2]])
# # Z1_2 = make_dict(par=[[9], [18], [27], [2], [3]])
# # Z2 = make_dict(par=[[12], [18], [27], [5], [4]])
# # Y1 = make_dict(par=[[22], [10], [27], [8], [7]])
# # Y2 = make_dict(par=[[20], [10], [57], [18], [17]])

#%%
E={}
val_p1,val_p2,val_p3,val_s1,val_s2={},{},{},{},{}
slack_p1,slack_p2,slack_p3={},{},{}
I = 3
O = 2
MID = 2
#%%
# DMU = nonlife.columns
for k in DMU:
    print(k)
    P1,P2,P3={},{},{}
    v, u, w = {}, {}, {}

    m = gp.Model("network_DEA_CRS")

    for i in range(I):
        v[i]=m.addVar(vtype=gp.GRB.CONTINUOUS,name="v_%d"%i, 
            # lb=0.0000000001
            )

    for i in range(O):
        u[i]=m.addVar(vtype=gp.GRB.CONTINUOUS,name="u_%d"%i, 
            # lb=0.000001
            )

    for i in range(MID):
        w[i]=m.addVar(vtype=gp.GRB.CONTINUOUS,name="w_%d"%i, 
            # lb=0.000001
            )
    
    m.update()

    m.setObjective(u[0] * Y1[k] + u[1] * Y2[k] , gp.GRB.MAXIMIZE)
    # m.setObjective((w[0] * Z1[k]) , gp.GRB.MAXIMIZE)
    # m.setObjective((w[1] * Z2[k]) , gp.GRB.MAXIMIZE)

    m.addConstr((w[0] * Z1_2[k] + w[1] * Z2[k]) == 1)
    # m.addConstr((v[0] * X1[k] + v[1] * X2_1[k]) == 1)
    # m.addConstr((w[0] * Z1_1[k] + v[1] * X2_2[k]) == 1)
    for j in DMU:
        # # (u1Y1j+u2Y2j)−(v1X1j+v2X2j)≤0  j=1,…,n
        # m.addConstr(u[0] * Y1[j] + u[1] * Y2[j] - (v[0] * X1[j] + v[1] * X2[j]) <= 0)
        # w1Z1j−(v1X1j+v2X21j)≤0  j=1,…,n
        # P1[j] = m.addConstr(u[0] * Y1[j] + u[1] * Y2[j] - (v[0] * X1[j] + v[1] * X2[j]) <= 0)
        P1[j] = m.addConstr(u[0] * Y1[j] + u[1] * Y2[j] - (w[0] * Z1_2[j] + w[1] * Z2[j]) <= 0)
        # P1[j] = m.addConstr(w[0] * Z1[j] - (v[0] * X1[j] + v[1] * X2_1[j]) <= 0)
        # P1[j] = m.addConstr(w[1] * Z2[j] - (w[0] * Z1_1[j] + v[1] * X2_2[j]) <= 0)

    m.optimize()
    E[k]="\nThe efficiency of DMU %s: %4.4g"%(k,m.objVal)

    u_sol = m.getAttr('x', u)
    v_sol = m.getAttr('x', v)
    w_sol = m.getAttr('x', w)
    
    print(E[k])
    print("\n", w_sol[0])
    print("\n", v_sol[0])
    print("\n", v_sol[1], "\n\n\n-----\n\n\n")
    # 計算各process的效率值
    # e = (u_sol[0] * Y1[k] + u_sol[1] * Y2[k]) / (v_sol[0] * X1[k] + v_sol[1] * X2[k])
    e = (u_sol[0] * Y1[k] + u_sol[1] * Y2[k]) / (w_sol[0] * Z1_2[k] + w_sol[1] * Z2[k])
    # e = (w_sol[0] * Z1[k]) / (v_sol[0] * X1[k] + v_sol[1] * X2_1[k])
    # e = (w_sol[1] * Z2[k]) / (w_sol[0] * Z1_1[k] + v_sol[1] * X2_2[k])
    

    val_p1[k] = 'The efficiency of DMU %s: %4.4g'%(k,e)
    
    #顯示各process的無效率值
    process1_slack = m.getAttr('slack',P1)
    slack_p1[k] = 'The inefficiency of process 1 of DMU %s:%4.4g'%(k,process1_slack[k])


for k in DMU:
    
    print("\n=====\n")
    print(E[k])
    print(val_p1[k])
    print(slack_p1[k])


#%%
from pystoned import DEA
from pystoned.constant import RTS_VRS, ORIENT_IO, OPT_LOCAL, RTS_CRS
#%%
x = np.array([[1, 2], [1, 2], [1, 2], [1, 20], [100, 400]])
y = np.array([[300], [120], [10], [4], [1]])
# define and solve the DEA radial model
model = DEA.DEA(y, np.array(x), rts=RTS_CRS, orient=ORIENT_IO, yref=None, xref=None)
model.optimize(OPT_LOCAL)

# display the technical efficiency
model.display_theta()

# display the intensity variables
model.display_lamda()
#%%
