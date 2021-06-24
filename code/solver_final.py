#%%
import gurobipy as gp
import pandas as pd
import numpy as np 

#%%
'''
    version of solver:
    Z1 split with CRS and VRS
    3 stages with dummy
    since VRS in life insurance is weird, we use dummy to get inefficiency of each stage
'''
#%%
def safe_div(upper, lower):
    if 0 == lower:
        return 1
    return upper/lower

#%%
def crs_solver(dmu, X1, X2, X2_1, X2_2, Z1_2, Z1_3, Z2_3, Y1, Y2, THRESHOLD=0.00000000001):
    E={}
    val_p1,val_p2,val_p3,val_s1,val_s2={},{},{},{},{}
    slack_p1,slack_p2,slack_p3={},{},{}
    val_s3 = {}
    I = 2
    O = 2
    MID = 3
    sols = {}
    for k in dmu:
        P1,P2,P3={},{},{}
        v, u, w = {}, {}, {}
        # w_0, u_0 = {}, {}

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
        
        m.update()

        m.setObjective(u[0] * Y1[k] + u[1] * Y2[k], gp.GRB.MAXIMIZE)

        m.addConstr((v[0] * X1[k] + v[1] * X2[k]) == 1)
        for j in dmu:
            # (u1Y1j+u2Y2j−u0)−(v1X1j+v2X2j)≤0 
            m.addConstr((u[0] * Y1[j] + u[1] * Y2[j]) - (v[0] * X1[j] + v[1] * X2[j]) <= 0)
            # (w11Z12j+w12Z13j)−
            #   (v1X1j+v2X21j)≤0 
            P1[j] = m.addConstr((w[0] * Z1_2[j] + w[1] * Z1_3[j]) - (v[0] * X1[j] + v[1] * X2_1[j]) <= 0)
            # w2Z23j−(v2X22j+w11Z12j)≤0 
            P2[j] = m.addConstr((w[2] * Z2_3[j]) - (v[1] * X2_2[j] + w[0] * Z1_2[j]) <= 0)
            # (u1Y1j+u2Y2j−u0)−
            #   (w12Z13j+w2Z23j)≤0
            P3[j] = m.addConstr((u[0] * Y1[j] + u[1] * Y2[j]) - (w[1] * Z1_3[j] + w[2] * Z2_3[j]) <= 0)
        m.optimize()
        # m.write("VRS_Z1split.lp")
        # m.write("VRS_Z1split.mps")
        E[k] = m.objVal

        print("\n\n\n=====\n\n\n")

        u_sol = m.getAttr('x', u)
        v_sol = m.getAttr('x', v)
        w_sol = m.getAttr('x', w)

        sols[k] = m.x

        # 計算各process的效率值
        val_p1[k] = safe_div((w_sol[0]*Z1_2[k] + w_sol[1]*Z1_3[k]), ((v_sol[0])*X1[k] + (v_sol[1])*X2_1[k]))
        val_p2[k] = safe_div((w_sol[2]*Z2_3[k]), ((v_sol[1])*X2_2[k] + (w_sol[0])*Z1_2[k]))
        val_p3[k] = safe_div((u_sol[0]*Y1[k] + u_sol[1]*Y2[k] ), (w_sol[1]*Z1_3[k] + w_sol[2]*Z2_3[k] ))
        
        # 計算各stage的效率值
        val_s1[k] = safe_div((w_sol[0]*Z1_2[k] + w_sol[1]*Z1_3[k] + v_sol[1]*X2_2[k]), (v_sol[0]*X1[k] + (v_sol[1])*X2[k]))
        val_s2[k] = safe_div((w_sol[1]*Z1_3[k]  + w_sol[2]*Z2_3[k] ), (w_sol[0]*Z1_2[k] + w_sol[1]*Z1_3[k] + v_sol[1]*X2_2[k]))
        val_s3[k] = val_p3[k]


        #顯示各process的無效率值
        process1_slack=m.getAttr('slack',P1)
        slack_p1[k] = process1_slack[k]
        process2_slack=m.getAttr('slack',P2)
        slack_p2[k] = process2_slack[k]
        process3_slack=m.getAttr('slack',P3)
        slack_p3[k] = process3_slack[k]

    ## check solutions
    sol_col = ["v_sol1", "v_sol2", "w_sol1", "w_sol2", "w_sol3", "u_sol1", "u_sol2" ]
    sol_df = pd.DataFrame(columns=sol_col)
    for k in dmu:
        sol_df = sol_df.append(pd.DataFrame(data=[sols[k]], columns=sol_col, index=[k]))

    ## check efficiency
    col = ["eff_total", "eff_p1", "eff_p2", "eff_p3", "eff_s1", "eff_s2", "eff_s3", "ineff_p1", "ineff_p2", "ineff_p3"]
    result_df = pd.DataFrame(columns=col)
    for k in dmu:
        result_df = result_df.append(pd.DataFrame(data=[[E[k], val_p1[k], val_p2[k], val_p3[k], val_s1[k], val_s2[k], val_s3[k], slack_p1[k], slack_p2[k], slack_p3[k]]], columns=col, index=[k]))

    result_df = result_df.append(pd.DataFrame(data=[[np.mean(result_df[i]) for i in col]], columns=col, index=["Avg."]))
    result_df = result_df.append(pd.DataFrame(data=[[np.std(result_df[i]) for i in col]], columns=col, index=["Std."]))
    del X1, X2, X2_1, X2_2, Z1_2, Z1_3, Z2_3, Y1, Y2, k
    return sol_df, result_df
#%%
def vrs_solver(dmu, X1, X2, X2_1, X2_2, Z1_2, Z1_3, Z2_3, Y1, Y2, THRESHOLD=0.00000000001):
    E={}
    val_p1,val_p2,val_p3,val_s1,val_s2={},{},{},{},{}
    slack_p1,slack_p2,slack_p3={},{},{}
    val_s3 = {}
    I = 2
    O = 2
    MID = 3
    sols = {}
    for k in dmu:
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
        for j in dmu:
            # (u1Y1j+u2Y2j−u0)−(v1X1j+v2X2j)≤0 
            m.addConstr((u[0] * Y1[j] + u[1] * Y2[j] - u_0[0]) - (v[0] * X1[j] + v[1] * X2[j]) <= 0)
            # (w11Z12j+w12Z13j−w_0^1 )−
            #   (v1X1j+v2X21j)≤0 
            P1[j] = m.addConstr((w[0] * Z1_2[j] + w[1] * Z1_3[j] - w_0[0]) - (v[0] * X1[j] + v[1] * X2_1[j]) <= 0)
            # w2Z23j−w_0^2−(v2X22j+w11Z12j−w_0^1 )≤0 
            P2[j] = m.addConstr((w[2] * Z2_3[j] - w_0[1]) - (v[1] * X2_2[j] + w[0] * Z1_2[j] - w_0[0]) <= 0)
            # (u1Y1j+u2Y2j−u0)−
            #   (w12Z13j−w_0^1+w2Z23j−w_0^2 )≤0
            P3[j] = m.addConstr((u[0] * Y1[j] + u[1] * Y2[j] - u_0[0]) - (w[1] * Z1_3[j] - w_0[0] + w[2] * Z2_3[j] - w_0[1]) <= 0)
        m.optimize()
        
        E[k] = m.objVal

        print("\n\n\n=====\n\n\n")

        u_sol = m.getAttr('x', u)
        v_sol = m.getAttr('x', v)
        w_sol = m.getAttr('x', w)
        
        w0_sol = m.getAttr('x', w_0)
        u0_sol = m.getAttr('x', u_0)

        sols[k] = m.x

        # 計算各process的效率值
        val_p1[k] = safe_div((w_sol[0]*Z1_2[k] + w_sol[1]*Z1_3[k] - w0_sol[0]), ((v_sol[0])*X1[k] + (v_sol[1])*X2_1[k]))
        val_p2[k] = safe_div((w_sol[2]*Z2_3[k] - w0_sol[1]), ((v_sol[1])*X2_2[k] + (w_sol[0])*Z1_2[k] - w0_sol[0]))
        val_p3[k] = safe_div((u_sol[0]*Y1[k] + u_sol[1]*Y2[k] - u0_sol[0]), (w_sol[1]*Z1_3[k] - w0_sol[0] + w_sol[2]*Z2_3[k] - w0_sol[1]))
        
        # 計算各stage的效率值
        val_s1[k] = safe_div((w_sol[0]*Z1_2[k] + w_sol[1]*Z1_3[k] - w0_sol[0] + v_sol[1]*X2_2[k]), (v_sol[0]*X1[k] + (v_sol[1])*X2[k]))
        val_s2[k] = safe_div((w_sol[1]*Z1_3[k] - w0_sol[0] + w_sol[2]*Z2_3[k] - w0_sol[1]), (w_sol[0]*Z1_2[k] + w_sol[1]*Z1_3[k] - w0_sol[0] + v_sol[1]*X2_2[k]))
        val_s3[k] = val_p3[k]


        #顯示各process的無效率值
        process1_slack=m.getAttr('slack',P1)
        slack_p1[k] = process1_slack[k]
        process2_slack=m.getAttr('slack',P2)
        slack_p2[k] = process2_slack[k]
        process3_slack=m.getAttr('slack',P3)
        slack_p3[k] = process3_slack[k]

    ## check solutions
    sol_col = ["v_sol1", "v_sol2", "w_sol1", "w_sol2", "w_sol3", "u_sol1", "u_sol2", "w0_sol1", "w0_sol", "u0_sol1"]
    sol_df = pd.DataFrame(columns=sol_col)
    for k in dmu:
        sol_df = sol_df.append(pd.DataFrame(data=[sols[k]], columns=sol_col, index=[k]))

    ## check efficiency
    col = ["eff_total", "eff_p1", "eff_p2", "eff_p3", "eff_s1", "eff_s2", "eff_s3", "ineff_p1", "ineff_p2", "ineff_p3"]
    result_df = pd.DataFrame(columns=col)
    for k in dmu:
        result_df = result_df.append(pd.DataFrame(data=[[E[k], val_p1[k], val_p2[k], val_p3[k], val_s1[k], val_s2[k], val_s3[k], slack_p1[k], slack_p2[k], slack_p3[k]]], columns=col, index=[k]))

    result_df = result_df.append(pd.DataFrame(data=[[np.mean(result_df[i]) for i in col]], columns=col, index=["Avg."]))
    result_df = result_df.append(pd.DataFrame(data=[[np.std(result_df[i]) for i in col]], columns=col, index=["Std."]))
    del X1, X2, X2_1, X2_2, Z1_2, Z1_3, Z2_3, Y1, Y2, k
    return sol_df, result_df
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
    Z1_2 = make_dict((np.array(df.iloc[[7]]).T).tolist())
    Z1_3 = make_dict((np.array(df.iloc[[5]]).T + np.array(df.iloc[[6]]).T - np.array(df.iloc[[7]]).T).tolist())
    Z2_3 = make_dict((np.array(df.iloc[[8]]).T + np.array(df.iloc[[9]]).T).tolist())

    Y1 = make_dict((np.array(df.iloc[[11]]).T).tolist(), y=True)
    Y2 = make_dict((np.array(df.iloc[[10]]).T).tolist(), y=True)

    ## data used
    data_col = ["X1", "X2", "X2_1", "X2_2", "Z1", "Z1_1", "Z1_2", "Z2", "Y1", "Y2"]
    data = pd.DataFrame(columns=data_col)
    for k in DMU:
        data = data.append(pd.DataFrame(data=[[X1[k], X2[k], X2_1[k], X2_2[k], Z1[k], Z1_2[k], Z1_3[k], Z2_3[k], Y1[k], Y2[k]]], columns=data_col, index=[k]))
    data = data.append(pd.DataFrame(data=[[np.mean(data[i]) for i in data_col]], columns=data_col, index=["Avg."]))
    data = data.append(pd.DataFrame(data=[[np.std(data[i]) for i in data_col]], columns=data_col, index=["Std."]))
    # data
    # data.to_excel("data_%s.xlsx" % NAME)
    
    sol_CRS, result_CRS = crs_solver(DMU, X1, X2, X2_1, X2_2, Z1_2, Z1_3, Z2_3, Y1, Y2)
    sol_VRS, result_VRS = vrs_solver(DMU, X1, X2, X2_1, X2_2, Z1_2, Z1_3, Z2_3, Y1, Y2)
    
    ######################
    ######################
    #### final output ####
    ######################
    ######################
    
    
    with pd.ExcelWriter('/Users/tungwu/Documents/GitHub/ORA_final_project/final_output/%s.xlsx' % NAME) as writer:  
        data.to_excel(writer, sheet_name="data") 
        result_CRS.to_excel(writer, sheet_name='CRS') 
        result_VRS.to_excel(writer, sheet_name='VRS')
        sol_CRS.to_excel(writer, sheet_name='CRS_sol') 
        sol_VRS.to_excel(writer, sheet_name='VRS_sol')
    del X1, X2, X2_1, X2_2, Z1, Z1_2, Z1_3, Z2_3, Y1, Y2, k



    
#%%
# life = pd.read_excel("/Users/tungwu/Documents/GitHub/ORA_final_project/data/life_2019.xlsx", index_col=0)
# life_dmu = [dmu for dmu in life.columns]
# # DMU.remove("友邦人壽")
# # DMU.remove("法國巴黎人壽")
# # DMU.remove("安達人壽")

# solve(df=life, DMU=life_dmu, NAME="life_2019")

# #%%
# nonlife = pd.read_excel("/Users/tungwu/Documents/GitHub/ORA_final_project/data/nonlife_2019.xlsx", sheet_name="final_variables", index_col=0)

# nonlife_dmu = [dmu for dmu in nonlife.columns]
# nonlife_dmu.remove("科法斯")
# nonlife_dmu.remove("裕利安宜")
# nonlife_dmu.remove("法國巴黎")
# nonlife_dmu.remove("安達")
# nonlife_dmu.remove("美國國際")
# nonlife_dmu.remove("亞洲")

# solve(df=nonlife, DMU=nonlife_dmu)
#%%
