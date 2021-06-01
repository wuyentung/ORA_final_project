#%%
import gurobipy as gp
import pandas as pd
import numpy as np 
#%%
def pp():
    print(1)
#%%
def solve(df, DMU, NAME="temp"):
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
    X1 = make_dict((np.array(df.iloc[[0]]).T + np.array(df.iloc[[1]]).T).tolist())
    X2 = make_dict((((np.array(df.iloc[[2]]).T + np.array(df.iloc[[3]]).T + np.array(df.iloc[[4]]).T))).tolist())
    X2_1 = make_dict((((np.array(df.iloc[[2]]).T + np.array(df.iloc[[3]]).T + np.array(df.iloc[[4]]).T))/2).tolist())
    X2_2 = X2_1

    Z1 = make_dict((np.array(df.iloc[[5]]).T + np.array(df.iloc[[6]]).T).tolist())
    Z1_1 = make_dict((np.array(df.iloc[[7]]).T).tolist())
    Z1_2 = make_dict((np.array(df.iloc[[5]]).T + np.array(df.iloc[[6]]).T - np.array(df.iloc[[7]]).T).tolist())
    Z2 = make_dict((np.array(df.iloc[[8]]).T + np.array(df.iloc[[9]]).T).tolist())

    Y1 = make_dict((np.array(df.iloc[[11]]).T).tolist(), y=True)
    Y2 = make_dict((np.array(df.iloc[[10]]).T).tolist(), y=True)

    THRESHOLD = 0.00000000001
    
    def avoid0(val):
        if 0 == val:
            return THRESHOLD
        return val
    
    #######################
    #######################
    ######### CRS #########
    #######################
    #######################
    E={}
    val_p1,val_p2,val_p3,val_s1,val_s2={},{},{},{},{}
    slack_p1,slack_p2,slack_p3={},{},{}
    I = 2
    O = 2
    MID = 2
    sols = {}

    # DMU = nonlife.columns
    for k in DMU:
        P1,P2,P3={},{},{}
        v, u, w = {}, {}, {}

        m = gp.Model("network_DEA_CRS")

        for i in range(I):
            v[i]=m.addVar(vtype=gp.GRB.CONTINUOUS,name="v_%d"%i, 
                lb=THRESHOLD
                )

        for i in range(MID):
            w[i]=m.addVar(vtype=gp.GRB.CONTINUOUS,name="w_%d"%i, 
                lb=THRESHOLD
                )

        for i in range(O):
            u[i]=m.addVar(vtype=gp.GRB.CONTINUOUS,name="u_%d"%i, 
                lb=THRESHOLD
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
        E[k] = m.objVal

        print("\n====\n")

        u_sol = m.getAttr('x', u)
        v_sol = m.getAttr('x', v)
        w_sol = m.getAttr('x', w)
        
        sols[k] = m.x

        # 計算各process的效率值
        val_p1[k] = w_sol[0] * Z1[k] / (avoid0(v_sol[0]) * X1[k] + avoid0(v_sol[1]) * X2_1[k])
        val_p2[k] = w_sol[1] * Z2[k] / (avoid0(v_sol[1]) * X2_2[k] + avoid0(w_sol[0]) * Z1_1[k])
        val_p3[k] = (u_sol[0] * Y1[k] + u_sol[1] * Y2[k]) / (avoid0(w_sol[0]) * Z1_2[k] + avoid0(w_sol[1]) * Z2[k])
        
        # 計算各stage的效率值
        val_s1[k] = (w_sol[0] * Z1_2[k] + w_sol[1] * Z2[k]) / (avoid0(v_sol[0]) * X1[k] + avoid0(v_sol[1]) * X2[k])
        val_s2[k] = val_p3[k]
        
        #顯示各process的無效率值
        process1_slack=m.getAttr('slack',P1)
        slack_p1[k] = process1_slack[k]
        process2_slack=m.getAttr('slack',P2)
        slack_p2[k] = process2_slack[k]
        process3_slack=m.getAttr('slack',P3)
        slack_p3[k] = process3_slack[k]
    ## check solutions
    sol_col = ["v_sol1", "v_sol2", "w_sol1", "w_sol2", "u_sol1", "u_sol2"]
    sol_CRS = pd.DataFrame(columns=sol_col)
    for k in DMU:
        sol_CRS = sol_CRS.append(pd.DataFrame(data=[sols[k]], columns=sol_col, index=[k]))
        
    ## check efficiency
    RESULT_col = ["eff_total", "eff_p1", "eff_p2", "eff_p3", "eff_s1", "eff_s2", "ineff_p1", "ineff_p2", "ineff_p3"]
    result_CRS = pd.DataFrame(columns=RESULT_col)
    for k in DMU:
        result_CRS = result_CRS.append(pd.DataFrame(data=[[E[k], val_p1[k], val_p2[k], val_p3[k], val_s1[k], val_s2[k], slack_p1[k], slack_p2[k], slack_p3[k]]], columns=RESULT_col, index=[k]))
    result_CRS = result_CRS.append(pd.DataFrame(data=[[np.mean(result_CRS[i]) for i in RESULT_col]], columns=RESULT_col, index=["Avg."]))
    result_CRS = result_CRS.append(pd.DataFrame(data=[[np.std(result_CRS[i]) for i in RESULT_col]], columns=RESULT_col, index=["Std."]))
    ######################
    ######################
    #### CRS z1 split ####
    ######################
    ######################

    E={}
    val_p1,val_p2,val_p3,val_s1,val_s2={},{},{},{},{}
    slack_p1,slack_p2,slack_p3={},{},{}
    I = 2
    O = 2
    MID = 3
    sols = {}
    
    # DMU = nonlife.columns
    for k in DMU:
        P1,P2,P3={},{},{}
        v, u, w = {}, {}, {}
        m = gp.Model("network_DEA_CRS")

        for i in range(I):
            v[i]=m.addVar(vtype=gp.GRB.CONTINUOUS,name="v_%d"%i, 
                lb=THRESHOLD
                )

        for i in range(MID):
            w[i]=m.addVar(vtype=gp.GRB.CONTINUOUS,name="w_%d"%i, 
                lb=THRESHOLD
                )
        

        for i in range(O):
            u[i]=m.addVar(vtype=gp.GRB.CONTINUOUS,name="u_%d"%i, 
                lb=THRESHOLD
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

        print("\n====\n")

        u_sol = m.getAttr('x', u)
        v_sol = m.getAttr('x', v)
        w_sol = m.getAttr('x', w)
        
        sols[k] = m.x

        # 計算各process的效率值
        val_p1[k] = (w_sol[0] * Z1_1[k] + w_sol[1] * Z1_2[k]) / (v_sol[0] * X1[k] + v_sol[1] * X2_1[k])
        val_p2[k] = w_sol[2] * Z2[k] / (avoid0(v_sol[1]) * X2_2[k] + avoid0(w_sol[0]) * Z1_1[k])
        val_p3[k] = (u_sol[0] * Y1[k] + u_sol[1] * Y2[k]) / (avoid0(w_sol[1]) * Z1_2[k] + avoid0(w_sol[2]) * Z2[k])
        
        # 計算各stage的效率值
        val_s1[k] = (w_sol[1] * Z1_2[k] + w_sol[2] * Z2[k]) / (avoid0(v_sol[0]) * X1[k] + avoid0(v_sol[1]) * X2[k])
        val_s2[k] = val_p3[k]

        #顯示各process的無效率值
        process1_slack=m.getAttr('slack',P1)
        slack_p1[k] = process1_slack[k]
        process2_slack=m.getAttr('slack',P2)
        slack_p2[k] = process2_slack[k]
        process3_slack=m.getAttr('slack',P3)
        slack_p3[k] = process3_slack[k]
    ## check solutions
    sol_col = ["v_sol1", "v_sol2", "w_sol1", "w_sol2", "w_sol3", "u_sol1", "u_sol2"]
    sol_CRS_Z1split = pd.DataFrame(columns=sol_col)
    for k in DMU:
        sol_CRS_Z1split = sol_CRS_Z1split.append(pd.DataFrame(data=[sols[k]], columns=sol_col, index=[k]))
        
    ## check efficiency
    result_CRS_Z1split = pd.DataFrame(columns=RESULT_col)
    for k in DMU:
        result_CRS_Z1split = result_CRS_Z1split.append(pd.DataFrame(data=[[E[k], val_p1[k], val_p2[k], val_p3[k], val_s1[k], val_s2[k], slack_p1[k], slack_p2[k], slack_p3[k]]], columns=RESULT_col, index=[k]))
    result_CRS_Z1split = result_CRS_Z1split.append(pd.DataFrame(data=[[np.mean(result_CRS_Z1split[i]) for i in RESULT_col]], columns=RESULT_col, index=["Avg."]))
    result_CRS_Z1split = result_CRS_Z1split.append(pd.DataFrame(data=[[np.std(result_CRS_Z1split[i]) for i in RESULT_col]], columns=RESULT_col, index=["Std."]))
    #######################
    #######################
    ######### VRS #########
    #######################
    #######################
    E={}
    val_p1,val_p2,val_p3,val_s1,val_s2={},{},{},{},{}
    slack_p1,slack_p2,slack_p3={},{},{}
    I = 2
    O = 2
    MID = 2
    sols = {}

    # DMU = nonlife.columns
    for k in DMU:
        P1,P2,P3={},{},{}
        v, u, w = {}, {}, {}
        w_0, u_0 = {}, {}

        m = gp.Model("network_DEA_CRS")

        for i in range(I):
            v[i]=m.addVar(vtype=gp.GRB.CONTINUOUS,name="v_%d"%i, 
                lb=THRESHOLD
                )

        for i in range(MID):
            w[i] = m.addVar(vtype=gp.GRB.CONTINUOUS,name="w_%d"%i, 
                lb=THRESHOLD
                )

        for i in range(O):
            u[i]=m.addVar(vtype=gp.GRB.CONTINUOUS,name="u_%d"%i, 
                lb=THRESHOLD
                )

        for i in range(2):
            w_0[i] = m.addVar(vtype=gp.GRB.CONTINUOUS,name="w0_%d"%i,  
                )
        
        for i in range(1):
            u_0[i] = m.addVar(vtype=gp.GRB.CONTINUOUS,name="u0_%d"%i,  
                )
        
        m.update()

        m.setObjective(u[0] * Y1[k] + u[1] * Y2[k] - u_0[0], gp.GRB.MAXIMIZE)

        m.addConstr((v[0] * X1[k] + v[1] * X2[k]) == 1)
        for j in DMU:
            # (u1Y1j+u2Y2j−u0)−(v1X1j+v2X2j)≤0
            m.addConstr((u[0] * Y1[j] + u[1] * Y2[j] - u_0[0]) - (v[0] * X1[j] + v[1] * X2[j]) <= 0)
            # w1Z1j−w_0^1−(v1X1j+v2X21j)≤0
            P1[j] = m.addConstr((w[0] * Z1[j] - w_0[0]) - (v[0] * X1[j] + v[1] * X2_1[j]) <= 0)
            # w2Z2j−w_0^2−(v2X22j+w1Z11j−w_0^1 )≤0 
            P2[j] = m.addConstr((w[1] * Z2[j] - w_0[1]) - (v[1] * X2_2[j] + w[0] * Z1_1[j] - w_0[0]) <= 0)
            # u1Y1j+u2Y2j−u0−
            #   (w1Z12j+w2Z2j−w_0^1−w_0^2 )≤0 
            P3[j] = m.addConstr((u[0] * Y1[j] + u[1] * Y2[j] - u_0[0]) - (w[0] * Z1_2[j] - w_0[0] + w[1] * Z2[j] - w_0[1]) <= 0)
        m.optimize()
        # m.write("temp.mst")
        # break
        E[k] = m.objVal

        print("\n\n\n=====\n\n\n")

        u_sol = m.getAttr('x', u)
        v_sol = m.getAttr('x', v)
        w_sol = m.getAttr('x', w)
        
        w0_sol = m.getAttr('x', w_0)
        u0_sol = m.getAttr('x', u_0)

        sols[k] = m.x

        # 計算各process的效率值
        val_p1[k] = (w_sol[0] * Z1[k] - w0_sol[0]) / (avoid0(v_sol[0]) * X1[k] + avoid0(v_sol[1]) * X2_1[k])
        val_p2[k] = (w_sol[1] * Z2[k] - w0_sol[1]) / (avoid0(v_sol[1]) * X2_2[k] + avoid0(w_sol[0]) * Z1_1[k] - w0_sol[0])
        val_p3[k] = (u_sol[0] * Y1[k] + u_sol[1] * Y2[k] - u0_sol[0]) / (avoid0(w_sol[0]) * Z1_2[k] - avoid0(w0_sol[0]) + w_sol[1] * Z2[k] - w0_sol[1])
        
        # 計算各stage的效率值
        val_s1[k] = (w_sol[0] * Z1_2[k] - w0_sol[0] + w_sol[1] * Z2[k] - w0_sol[1]) / (avoid0(v_sol[0]) * X1[k] + avoid0(v_sol[1]) * X2[k])
        val_s2[k] = val_p3[k]
        
        #顯示各process的無效率值
        process1_slack=m.getAttr('slack',P1)
        slack_p1[k] = process1_slack[k]
        process2_slack=m.getAttr('slack',P2)
        slack_p2[k] = process2_slack[k]
        process3_slack=m.getAttr('slack',P3)
        slack_p3[k] = process3_slack[k]

    ## check solutions
    sol_col = ["v_sol1", "v_sol2", "w_sol1", "w_sol2", "u_sol1", "u_sol2", "w0_sol1", "w0_sol1", "u0_sol1"]
    sol_VRS = pd.DataFrame(columns=sol_col)
    for k in DMU:
        sol_VRS = sol_VRS.append(pd.DataFrame(data=[sols[k]], columns=sol_col, index=[k]))
        
    ## check efficiency
    result_VRS = pd.DataFrame(columns=RESULT_col)
    for k in DMU:
        result_VRS = result_VRS.append(pd.DataFrame(data=[[E[k], val_p1[k], val_p2[k], val_p3[k], val_s1[k], val_s2[k], slack_p1[k], slack_p2[k], slack_p3[k]]], columns=RESULT_col, index=[k]))
    result_VRS = result_VRS.append(pd.DataFrame(data=[[np.mean(result_VRS[i]) for i in RESULT_col]], columns=RESULT_col, index=["Avg."]))
    result_VRS = result_VRS.append(pd.DataFrame(data=[[np.std(result_VRS[i]) for i in RESULT_col]], columns=RESULT_col, index=["Std."]))

    ######################
    ######################
    #### VRS z1 split ####
    ######################
    ######################
    E={}
    val_p1,val_p2,val_p3,val_s1,val_s2={},{},{},{},{}
    slack_p1,slack_p2,slack_p3={},{},{}
    I = 2
    O = 2
    MID = 3
    sols = {}
    for k in DMU:
        P1,P2,P3={},{},{}
        v, u, w = {}, {}, {}
        w_0, u_0 = {}, {}


        m = gp.Model("network_DEA_VRS")

        for i in range(I):
            v[i]=m.addVar(vtype=gp.GRB.CONTINUOUS,name="v_%d"%i, 
                lb=THRESHOLD
                )

        for i in range(MID):
            w[i]=m.addVar(vtype=gp.GRB.CONTINUOUS,name="w_%d"%i, 
                lb=THRESHOLD 
                )

        for i in range(O):
            u[i]=m.addVar(vtype=gp.GRB.CONTINUOUS,name="u_%d"%i, 
                lb=THRESHOLD 
                )

        for i in range(2):
            w_0[i] = m.addVar(vtype=gp.GRB.CONTINUOUS,name="w0_%d"%i,
                )
        
        for i in range(1):
            u_0[i] = m.addVar(vtype=gp.GRB.CONTINUOUS,name="u0_%d"%i,
                )
        
        m.update()

        m.setObjective(u[0] * Y1[k] + u[1] * Y2[k] - u_0[0], gp.GRB.MAXIMIZE)

        m.addConstr((v[0] * X1[k] + v[1] * X2[k]) == 1)
        for j in DMU:
            # (u1Y1j+u2Y2j−u0)−(v1X1j+v2X2j)≤0 
            m.addConstr((u[0] * Y1[j] + u[1] * Y2[j] - u_0[0]) - (v[0] * X1[j] + v[1] * X2[j]) <= 0)
            # (w11Z11j+w12Z12j−w_0^1 )−
            #   (v1X1j+v2X21j)≤0 
            P1[j] = m.addConstr((w[0] * Z1_1[j] + w[1] * Z1_2[j] - w_0[0]) - (v[0] * X1[j] + v[1] * X2_1[j]) <= 0)
            # w2Z2j−w_0^2−(v2X22j+w11Z11j−w_0^1 )≤0 
            P2[j] = m.addConstr((w[2] * Z2[j] - w_0[1]) - (v[1] * X2_2[j] + w[0] * Z1_1[j] - w_0[0]) <= 0)
            # (u1Y1j+u2Y2j−u0)−
            #   (w12Z12j−w_0^1+w2Z2j−w_0^2 )≤0
            P3[j] = m.addConstr((u[0] * Y1[j] + u[1] * Y2[j] - u_0[0]) - (w[1] * Z1_2[j] - w_0[0] + w[2] * Z2[j] - w_0[1]) <= 0)
        m.optimize()
        E[k] = m.objVal

        print("\n=====\n")

        u_sol = m.getAttr('x', u)
        v_sol = m.getAttr('x', v)
        w_sol = m.getAttr('x', w)
        
        w0_sol = m.getAttr('x', w_0)
        u0_sol = m.getAttr('x', u_0)

        sols[k] = m.x

        # 計算各process的效率值
        val_p1[k] = (w_sol[0] * Z1_1[k] + w_sol[1] * Z1_2[k] - w0_sol[0]) / (avoid0(v_sol[0]) * X1[k] + avoid0(v_sol[1]) * X2_1[k])
        val_p2[k] = (w_sol[2] * Z2[k] - w0_sol[1]) / (avoid0(v_sol[1]) * X2_2[k] + avoid0(w_sol[0]) * Z1_1[k] - w0_sol[0])
        val_p3[k] = (u_sol[0] * Y1[k] + u_sol[1] * Y2[k] - u0_sol[0]) / (avoid0(w_sol[1]) * Z1_2[k] - w0_sol[0] + avoid0(w_sol[2]) * Z2[k] - w0_sol[1])
        
        # 計算各stage的效率值
        val_s1[k] = (w_sol[1] * Z1_2[k] - w0_sol[0] + w_sol[2] * Z2[k] - w0_sol[1]) / (avoid0(v_sol[0]) * X1[k] + avoid0(v_sol[1]) * X2[k])
        val_s2[k] = val_p3[k]


        #顯示各process的無效率值
        process1_slack=m.getAttr('slack',P1)
        slack_p1[k] = process1_slack[k]
        process2_slack=m.getAttr('slack',P2)
        slack_p2[k] = process2_slack[k]
        process3_slack=m.getAttr('slack',P3)
        slack_p3[k] = process3_slack[k]
    
    ## check solutions
    sol_col = ["v_sol1", "v_sol2", "w_sol1", "w_sol2", "w_sol3", "u_sol1", "u_sol2", "w0_sol1", "w0_sol1", "u0_sol1"]
    sol_VRS_Z1split = pd.DataFrame(columns=sol_col)
    for k in DMU:
        sol_VRS_Z1split = sol_VRS_Z1split.append(pd.DataFrame(data=[sols[k]], columns=sol_col, index=[k]))
        
    ## check efficiency
    result_VRS_Z1split = pd.DataFrame(columns=RESULT_col)
    for k in DMU:
        result_VRS_Z1split = result_VRS_Z1split.append(pd.DataFrame(data=[[E[k], val_p1[k], val_p2[k], val_p3[k], val_s1[k], val_s2[k], slack_p1[k], slack_p2[k], slack_p3[k]]], columns=RESULT_col, index=[k]))
    result_VRS_Z1split = result_VRS_Z1split.append(pd.DataFrame(data=[[np.mean(result_VRS_Z1split[i]) for i in RESULT_col]], columns=RESULT_col, index=["Avg."]))
    result_VRS_Z1split = result_VRS_Z1split.append(pd.DataFrame(data=[[np.std(result_VRS_Z1split[i]) for i in RESULT_col]], columns=RESULT_col, index=["Std."]))

    ######################
    ######################
    #### final output ####
    ######################
    ######################
    
    ## data used
    data_col = ["X1", "X2", "X2_1", "X2_2", "Z1", "Z1_1", "Z1_2", "Z2", "Y1", "Y2"]
    data = pd.DataFrame(columns=data_col)
    for k in DMU:
        data = data.append(pd.DataFrame(data=[[X1[k], X2[k], X2_1[k], X2_2[k], Z1[k], Z1_1[k], Z1_2[k], Z2[k], Y1[k], Y2[k]]], columns=data_col, index=[k]))
    data = data.append(pd.DataFrame(data=[[np.mean(data[i]) for i in data_col]], columns=data_col, index=["Avg."]))
    data = data.append(pd.DataFrame(data=[[np.std(data[i]) for i in data_col]], columns=data_col, index=["Std."]))
    with pd.ExcelWriter('/Users/tungwu/Documents/GitHub/ORA_final_project/result/%s_sol.xlsx' %NAME) as writer:  
        data.to_excel(writer, sheet_name="data")
        sol_CRS.to_excel(writer, sheet_name='CRS')
        sol_CRS_Z1split.to_excel(writer, sheet_name='CRS_Z1split')
        sol_VRS.to_excel(writer, sheet_name='VRS')
        sol_VRS_Z1split.to_excel(writer, sheet_name='VRS_Z1split')

    with pd.ExcelWriter('/Users/tungwu/Documents/GitHub/ORA_final_project/result/%s_result.xlsx' %NAME) as writer:  
        data.to_excel(writer, sheet_name="data")
        result_CRS.to_excel(writer, sheet_name='CRS')
        result_CRS_Z1split.to_excel(writer, sheet_name='CRS_Z1split')
        result_VRS.to_excel(writer, sheet_name='VRS')
        result_VRS_Z1split.to_excel(writer, sheet_name='VRS_Z1split')


#%%
if __name__ == "main":
    life = pd.read_excel("life_2019.xlsx", index_col=0)
    DMU = [dmu for dmu in life.columns]
    # DMU.remove("友邦人壽")
    # DMU.remove("法國巴黎人壽")
    # DMU.remove("安達人壽")

    solve(df=life, DMU=DMU)
    