#%%
from gurobipy import *
#%%

DMU=['A']
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

X1 = make_dict(par=[[1]], DMU=DMU)
X2 = make_dict(par=[[2]], DMU=DMU)
X2_1 = make_dict(par=[[1]], DMU=DMU)
X2_2 = make_dict(par=[[1]], DMU=DMU)
Z1 = make_dict(par=[[10]], DMU=DMU)
Z1_1 = make_dict(par=[[5]], DMU=DMU)
Z1_2 = make_dict(par=[[5]], DMU=DMU)
Z2 = make_dict(par=[[10]], DMU=DMU)
Y1 = make_dict(par=[[20]], DMU=DMU)
Y2 = make_dict(par=[[20]], DMU=DMU)
#%%
DMU=['A', 'B', 'C', 'D', 'E']
X1 = make_dict(par=[[1], [2], [3], [4], [5]])
X2 = make_dict(par=[[2], [6], [8], [10], [12]])
X2_1 = make_dict(par=[[1], [3], [4], [5], [6]])
X2_2 = make_dict(par=[[1], [3], [4], [5], [6]])
Z1 = make_dict(par=[[10], [20], [30], [4], [5]])
Z1_1 = make_dict(par=[[5], [2], [3], [2], [2]])
Z1_2 = make_dict(par=[[5], [18], [27], [2], [3]])
Z2 = make_dict(par=[[10], [18], [27], [5], [4]])
Y1 = make_dict(par=[[20], [30], [27], [8], [7]])
Y2 = make_dict(par=[[20], [10], [57], [18], [17]])
DMU=['A', 'B','C','D','E']
E={}
val_p1,val_p2,val_p3,val_s1,val_s2={},{},{},{},{}
slack_p1,slack_p2,slack_p3={},{},{}

for k in DMU:

    I=2
    O=3

    DMU,Totx1,Totx2=multidict({("A"):[11,14],("B"):[7,7],("C"):[11,14],("D"):[14,14],("E"):[14,15]})
    DMU,proc1x1,proc1x2,proc1TotyO,proc1yO,proc1yI=multidict({("A"):[3,5,4,2,2],("B"):[2,3,2,1,1],("C"):[3,4,2,1,1],("D"):[4,6,3,2,1],("E"):[5,6,4,3,1]})
    DMU,proc2x1,proc2x2,proc2TotyO,proc2yO,proc2yI=multidict({("A"):[4,3,3,2,1],("B"):[2,1,2,1,1],("C"):[5,3,2,1,1],("D"):[5,5,4,3,1],("E"):[5,4,4,2,2]})
    DMU,proc3x1,proc3x2,proc3TotyO=multidict({("A"):[4,6,1],("B"):[3,3,1],("C"):[3,7,2],("D"):[5,3,1],("E"):[4,5,3]})
    
    P1,P2,P3={},{},{}
    v,u={},{}
    
    m=Model("network_DEA")
    
    for i in range(I):
        v[i]=m.addVar(vtype=GRB.CONTINUOUS,name="v_%d"%i)
    
    for i in range(O):
        u[i]=m.addVar(vtype=GRB.CONTINUOUS,name="u_%d"%i)
    
    m.update()
   

    m.setObjective(u[0]*proc1yO[k]+u[1]*proc2yO[k]+u[2]*proc3TotyO[k],GRB.MAXIMIZE)
            
    m.addConstr(v[0]*Totx1[k]+v[1]*Totx2[k]==1)
    for j in DMU:
        P1[j]=m.addConstr(u[0]*proc1TotyO[j]-(v[0]*proc1x1[j]+v[1]*proc1x2[j])<=0)
        P2[j]=m.addConstr(u[1]*proc2TotyO[j]-(v[0]*proc2x1[j]+v[1]*proc2x2[j])<=0)
        P3[j]=m.addConstr(u[2]*proc3TotyO[j]-(v[0]*proc3x1[j]+v[1]*proc3x2[j]+u[0]*proc1yI[j]+u[1]*proc2yI[j])<=0)
   
    m.optimize()
    E[k]="The efficiency of DMU %s:%4.4g"%(k,m.objVal)
    
    u_sol = m.getAttr('x', u)
    v_sol = m.getAttr('x',v)
    
    #?????????process????????????
    E1=u_sol[0]*proc1TotyO[k]/(v_sol[0]*proc1x1[k]+v_sol[1]*proc1x2[k]) 
    E2=u_sol[1]*proc2TotyO[k]/(v_sol[0]*proc2x1[k]+v_sol[1]*proc2x2[k])
    E3=u_sol[2]*proc3TotyO[k]/(v_sol[0]*proc3x1[k]+v_sol[1]*proc3x2[k]+u_sol[0]*proc1yI[k]+u_sol[1]*proc2yI[k])
    
    #?????????stage????????????
    stage1=(u_sol[0]*proc1TotyO[k]+u_sol[1]*proc2TotyO[k]+v_sol[0]*proc3x1[k]+v_sol[1]*proc3x2[k])/(v_sol[0]*Totx1[k]+v_sol[1]*Totx2[k])
    stage2=(u_sol[0]*proc1yO[k]+u_sol[1]*proc2yO[k]+u_sol[2]*proc3TotyO[k])/(u_sol[0]*proc1TotyO[k]+u_sol[1]*proc2TotyO[k]+v_sol[0]*proc3x1[k]+v_sol[1]*proc3x2[k])
    val_p1[k]='The efficiency of process 1 of DMU %s:%4.4g'%(k,E1)
    val_p2[k]='The efficiency of process 2 of DMU %s:%4.4g'%(k,E2)
    val_p3[k]='The efficiency of process 3 of DMU %s:%4.4g'%(k,E3)
    val_s1[k]='The efficiency of stage 1 of DMU %s:%4.4g'%(k,stage1)
    val_s2[k]='The efficiency of stage 2 of DMU %s:%4.4g'%(k,stage2)
    
    #?????????process???????????????
    process1_slack=m.getAttr('slack',P1)
    slack_p1[k]='The inefficiency of process 1 of DMU %s:%4.4g'%(k,process1_slack[k])
    process2_slack=m.getAttr('slack',P2)
    slack_p2[k]='The inefficiency of process 2 of DMU %s:%4.4g'%(k,process2_slack[k])
    process3_slack=m.getAttr('slack',P3)
    slack_p3[k]='The inefficiency of process 3 of DMU %s:%4.4g'%(k,process3_slack[k])

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
# import packages
import numpy as np
from pystoned import DEA
from pystoned import dataset as dataset
from pystoned.constant import RTS_VRS, ORIENT_IO, OPT_LOCAL, RTS_CRS
#%%
# import the data provided with Tim Coelli???s Frontier 4.1
data = dataset.load_Tim_Coelli_frontier()
#%%
X = data.x
# define and solve the DEA radial model
model = DEA.DEA(data.y, np.array(data.x), rts=RTS_CRS, orient=ORIENT_IO, yref=None, xref=None)
model.optimize(OPT_LOCAL)

# display the technical efficiency
model.display_theta()

# display the intensity variables
model.display_lamda()
#%%
#%%
