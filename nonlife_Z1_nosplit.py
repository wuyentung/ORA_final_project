#%%
import gurobipy as gp
import pandas as pd
import numpy as np
import pandas as pd
#%%
nonlife = pd.read_excel("nonlife-insurance.xlsx", sheet_name="final_variables", index_col=0)
#%%
DMU = [dmu for dmu in nonlife.columns]
# DMU.remove("科法斯")
# DMU.remove("裕利安宜")
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
    if min(made.values()) < 0:
        mini = - min(made.values()) +1
        for key, value in made.items():
            made[key] = value + mini
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
# if min(made.values()) < 0:
#     mini = - min(made.values())
#     for key, value in made.items():
#         made[key] = value + mini
#%%
# data = pd.DataFrame([X1, X2, X2_1, X2_2, Z1, Z1_1, Z1_2, Z2, Y1, Y2], index=["X1", "X2", "X2_1", "X2_2", "Z1", "Z1_1", "Z1_2", "Z2", "Y1", "Y2"])
# #%%
# DMU=['A', 'B', 'C', 'D', 'E']
# #%%
# X1 = make_dict(par=[[1], [2], [3], [4], [5]])
# X2 = make_dict(par=[[4], [6], [8], [10], [12]])
# X2_1 = make_dict(par=[[2], [3], [4], [5], [6]])
# X2_2 = make_dict(par=[[2], [3], [4], [5], [6]])
# Z1 = make_dict(par=[[10], [20], [30], [4], [5]])
# Z1_1 = make_dict(par=[[1], [2], [3], [2], [2]])
# Z1_2 = make_dict(par=[[9], [18], [27], [2], [3]])
# Z2 = make_dict(par=[[12], [18], [27], [5], [4]])
# Y1 = make_dict(par=[[22], [30], [27], [8], [7]])
# Y2 = make_dict(par=[[20], [10], [57], [18], [17]])

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
    P1,P2,P3={},{},{}
    v, u, w = {}, {}, {}

    m = gp.Model("network_DEA_CRS")

    for i in range(I):
        v[i]=m.addVar(vtype=gp.GRB.CONTINUOUS,name="v_%d"%i, 
            # lb=0.000001
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

    m.addConstr((v[0] * X1[k] + v[1] * X2[k]) == 1)
    for j in DMU:
        # (u1Y1j+u2Y2j)−(v1X1j+v2X2j)≤0  j=1,…,n
        m.addConstr(u[0] * Y1[j] + u[1] * Y2[j] - (v[0] * X1[j] + v[1] * X2[j]) <= 0)
        # w1Z1j−(v1X1j+v2X21j)≤0  j=1,…,n
        P1[j] = m.addConstr(w[0] * Z1[j] - (v[0] * X1[j] + v[1] * X2_1[j]) <= 0)
        # w2Z2j−(v2X22j+w1Z11j)≤0  j=1,…,n
        P2[j] = m.addConstr(w[1] * Z2[j] - (v[1] * X2_2[j] + w[0] * Z1_1[j]) <= 0)
        # u1Y1j+u2Y2j−(w1Z12j+w2Z2j)≤0  j=1,…,n
        P3[j] = m.addConstr(u[0] * Y1[j] + u[1] * Y2[j] - (w[0] * Z1_2[j] + w[1] * Z2[j]) <= 0)

    m.optimize()
    # m.write("temp.mst")
    # break
    E[k]="\nThe efficiency of DMU %s:%4.4g"%(k,m.objVal)

    print("\n\n\n=====\n\n\n")

    u_sol = m.getAttr('x', u)
    v_sol = m.getAttr('x', v)
    w_sol = m.getAttr('x', w)
    
    threshold = 0.0000001
    # for i in range(I):
    #     if v_sol[i] < threshold:
    #         v_sol[i] = threshold
    # for i in range(O):
    #     if u_sol[i] < threshold:
    #         u_sol[i] = threshold
    # for i in range(MID):
    #     if w_sol[i] < threshold:
    #         w_sol[i] = threshold

    # 計算各process的效率值
    e1 = w_sol[0] * Z1[k] / np.max([(v_sol[0] * X1[k] + v_sol[1] * X2_1[k]), threshold]) 
    e2 = w_sol[1] * Z2[k] / np.max([(v_sol[1] * X2_2[k] + w_sol[0] * Z1_1[k]), threshold])
    e3 = (u_sol[0] * Y1[k] + u_sol[1] * Y2[k]) / np.max([(w_sol[0] * Z1_2[k] + w_sol[1] * Z2[k]), threshold])
    
    # 計算各stage的效率值
    stage1 = (w_sol[0] * Z1_2[k] + w_sol[1] * Z2[k]) / np.max([(v_sol[0] * X1[k] + v_sol[1] * X2[k]), threshold])
    stage2 = (u_sol[0] * Y1[k] + u_sol[1] * Y2[k]) / np.max([(w_sol[0] * Z1_2[k] + w_sol[1] * Z2[k]), threshold])

    val_p1[k]='The efficiency of process 1 of DMU %s: %4.4g'%(k,e1)
    val_p2[k]='The efficiency of process 2 of DMU %s: %4.4g'%(k,e2)
    val_p3[k]='The efficiency of process 3 of DMU %s: %4.4g'%(k,e3)
    val_s1[k]='The efficiency of stage 1 of DMU %s: %4.4g'%(k,stage1)
    val_s2[k]='The efficiency of stage 2 of DMU %s: %4.4g'%(k,stage2)
    
    #顯示各process的無效率值
    process1_slack=m.getAttr('slack',P1)
    slack_p1[k]='The inefficiency of process 1 of DMU %s: %4.4g'%(k,process1_slack[k])
    process2_slack=m.getAttr('slack',P2)
    slack_p2[k]='The inefficiency of process 2 of DMU %s: %4.4g'%(k,process2_slack[k])
    process3_slack=m.getAttr('slack',P3)
    slack_p3[k]='The inefficiency of process 3 of DMU %s: %4.4g'%(k,process3_slack[k])
    # break
#%%
for k in DMU:
    
    print("\n\n=====\n\n")
    print (E[k])
    print (val_p1[k])
    print (val_p2[k])
    print (val_p3[k])
    print (val_s1[k])
    print (val_s2[k])
    print (slack_p1[k])
    print (slack_p2[k])
    print (slack_p3[k])


#%%
