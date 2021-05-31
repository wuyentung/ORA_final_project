#%%
import gurobipy as gp
import pandas as pd
import numpy as np
import pandas as pd
#%%
life = pd.read_excel("life_2019.xlsx", index_col=0)

#%%
DMU = [dmu for dmu in life.columns]
# DMU.remove("友邦人壽")
# DMU.remove("法國巴黎人壽")
# DMU.remove("安達人壽")
#%%
def make_dict(par, DMU=DMU, y=False):
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
        if y:
            mini = - min(made.values())
            # if y:
            #     mini -= 1
            for key, value in made.items():
                made[key] = value + mini
        else:
            print("\n\n============\n\n")
            print("there is negative value in input side")
            print("\n\n============\n\n")
    return made
#%%
X1 = make_dict((np.array(life.iloc[[0]]).T + np.array(life.iloc[[1]]).T).tolist())
X2 = make_dict((((np.array(life.iloc[[2]]).T + np.array(life.iloc[[3]]).T + np.array(life.iloc[[4]]).T))).tolist())
X2_1 = make_dict((((np.array(life.iloc[[2]]).T + np.array(life.iloc[[3]]).T + np.array(life.iloc[[4]]).T))/2).tolist())
X2_2 = X2_1

Z1 = make_dict((np.array(life.iloc[[5]]).T + np.array(life.iloc[[6]]).T).tolist())
Z1_1 = make_dict((np.array(life.iloc[[7]]).T).tolist())
Z1_2 = make_dict((np.array(life.iloc[[5]]).T + np.array(life.iloc[[6]]).T - np.array(life.iloc[[7]]).T).tolist())
Z2 = make_dict((np.array(life.iloc[[8]]).T + np.array(life.iloc[[9]]).T).tolist())
#%%
Y1 = make_dict((np.array(life.iloc[[11]]).T).tolist(), y=True)
Y2 = make_dict((np.array(life.iloc[[10]]).T).tolist(), y=True)
#%%
E={}
val_p1,val_p2,val_p3,val_s1,val_s2={},{},{},{},{}
slack_p1,slack_p2,slack_p3={},{},{}
I = 3
O = 2
MID = 3
temp = {}
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
        # (u1Y1j+u2Y2j)−(v1X1j+v2X2j)≤0 
        m.addConstr(u[0] * Y1[j] + u[1] * Y2[j] - (v[0] * X1[j] + v[1] * X2[j]) <= 0)
        # w11Z11j+w12Z12j−(v1X1j+v2X21j)≤0 
        P1[j] = m.addConstr((w[0] * Z1_1[j] + w[1] * Z1_2[j]) - (v[0] * X1[j] + v[1] * X2_1[j]) <= 0)
        # w2Z2j−(v2X22j+w11Z11j)≤0
        P2[j] = m.addConstr(w[2] * Z2[j] - (v[1] * X2_2[j] + w[0] * Z1_1[j]) <= 0)
        # u1Y1j+u2Y2j−(w12Z12j+w2Z2j)≤0  
        P3[j] = m.addConstr(u[0] * Y1[j] + u[1] * Y2[j] - (w[1] * Z1_2[j] + w[2] * Z2[j]) <= 0)

    m.optimize()
    # m.write("temp.mst")
    # break
    E[k] = m.objVal

    print("\n\n\n=====\n\n\n")

    u_sol = m.getAttr('x', u)
    v_sol = m.getAttr('x', v)
    w_sol = m.getAttr('x', w)
    
    threshold = 0.000001
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
    val_p1[k] = (w_sol[0] * Z1_1[k] + w_sol[1] * Z1_2[k]) / np.max([(v_sol[0] * X1[k] + v_sol[1] * X2_1[k]), threshold]) 
    val_p2[k] = w_sol[2] * Z2[k] / np.max([(v_sol[1] * X2_2[k] + w_sol[0] * Z1_1[k]), threshold])
    val_p3[k] = (u_sol[0] * Y1[k] + u_sol[1] * Y2[k]) / np.max([(w_sol[1] * Z1_2[k] + w_sol[2] * Z2[k]), threshold])
    
    # 計算各stage的效率值
    val_s1[k] = (w_sol[1] * Z1_2[k] + w_sol[2] * Z2[k]) / np.max([(v_sol[0] * X1[k] + v_sol[1] * X2[k]), threshold])
    val_s2[k] = (u_sol[0] * Y1[k] + u_sol[1] * Y2[k]) / np.max([(w_sol[1] * Z1_2[k] + w_sol[2] * Z2[k]), threshold])

    temp[k] = u_sol
    #顯示各process的無效率值
    process1_slack=m.getAttr('slack',P1)
    slack_p1[k] = process1_slack[k]
    process2_slack=m.getAttr('slack',P2)
    slack_p2[k] = process2_slack[k]
    process3_slack=m.getAttr('slack',P3)
    slack_p3[k] = process3_slack[k]
    # break
#%%
for k in DMU:
    
    print("\n\n=====\n\n")
    print("\nThe efficiency of DMU %s:%4.4g"%(k,E[k]))
    print ('The efficiency of process 1 of DMU %s: %4.4g'%(k,val_p1[k]))
    print ('The efficiency of process 2 of DMU %s: %4.4g'%(k,val_p2[k]))
    print ('The efficiency of process 3 of DMU %s: %4.4g'%(k,val_p3[k]))
    print ('The efficiency of stage 1 of DMU %s: %4.4g'%(k,val_s1[k]))
    print ('The efficiency of stage 2 of DMU %s: %4.4g'%(k,val_s2[k]))
    print ('The inefficiency of process 1 of DMU %s: %4.4g'%(k,slack_p1[k]))
    print ('The inefficiency of process 2 of DMU %s: %4.4g'%(k,slack_p2[k]))
    print ('The inefficiency of process 3 of DMU %s: %4.4g'%(k,slack_p3[k]))


#%%
data_col = ["X1", "X2", "X2_1", "X2_2", "Z1", "Z1_1", "Z1_2", "Z2", "Y1", "Y2"]
#%%
data = pd.DataFrame(columns=data_col)
for k in DMU:
    data = data.append(pd.DataFrame(data=[[X1[k], X2[k], X2_1[k], X2_2[k], Z1[k], Z1_1[k], Z1_2[k], Z2[k], Y1[k], Y2[k]]], columns=data_col, index=[k]))
data
# data.to_excel("data_local.xlsx")
#%%
col = ["eff_total", "eff_p1", "eff_p2", "eff_p3", "eff_s1", "eff_s2", "ineff_p1", "ineff_p2", "ineff_p3"]
result_remove = pd.DataFrame(columns=col)
for k in DMU:
    result_remove = result_remove.append(pd.DataFrame(data=[[E[k], val_p1[k], val_p2[k], val_p3[k], val_s1[k], val_s2[k], slack_p1[k], slack_p2[k], slack_p3[k]]], columns=col, index=[k]))
result_remove.to_excel("CRS_Z1split.xlsx")
result_remove
#%%
