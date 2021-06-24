###### tags: `POLab`
# Efficiency Measure in Insurance Industry – A Network DEA Model
*2021/06/22*

#### ※*Reference*
*本篇主要參考於[高強教授](http://www.iim.ncku.edu.tw/files/11-1407-20368.php?Lang=zh-tw)在2008以及2009發表的Paper：*
1. *[Efficiency decomposition in two-stage data envelopment analysis: An application to non-life insurance companies in Taiwan](https://www.sciencedirect.com/science/article/abs/pii/S0377221707000112)*
2. *[Efficiency decomposition in network data envelopment analysis: A relational model](https://www.sciencedirect.com/science/article/pii/S0377221707010077)*

---

## Network DEA Model
After we got the basic concepts of the network data envelopment analysis(network-DEA), we might desire to solve different applications using it.

✿ If we want to review the network-DEA, please check [HERE](https://github.com/wurmen/DEA/blob/master/Network_DEA/network_dea.md)!

---

## Background and Motivation
Kao and Hwang (2008) —the first study that applies Network-DEA to the insurance field, which consists of 24 non-life insurance firms in Taiwan between 2001 and 2002. Subsequently, several scholars use the same dataset in Kao and Hwang (2008) to test new Network-DEA models.<br/><br/>
However, when it comes to efficiency measure in insurance industry nowadays. It’s difficult to collect similar data since <font color="red">the change in financial statement</font> is over 15 years. <br/>
Furthermore, network framework from Kao and Hwang (2008) should be update. <br/><br/>
As a result, we proposed a three stage network system which contains three processes, **premium acquisition**, **reinsurance allocation** and **profit generation**.<br/>

Insurance company will cede their reinsurance process after they gain insurance premuim, and then use reinsurance premium as well as insurance premium to generate profit, which include underwriting profit and investment profit. Chart of work flow is shown below.<br/>

![](https://i.imgur.com/Ne2WxoZ.png)

##### notations:
X<sup>1</sup>: Insurance expenses  
X<sup>2</sup>: Operation expenses  
&nbsp;&nbsp;&nbsp;&nbsp; X<sup>21</sup>: 50% of 𝑋2  
&nbsp;&nbsp;&nbsp;&nbsp; X<sup>22</sup>: 50% of 𝑋2  

Z<sup>1,2</sup>: Premiums ceded to reinsurers  
Z<sup>1,3</sup>: Premium income minus Z<sup>1,2</sup>
Z<sup>2,3</sup>: Reinsurance premiums  

Y<sup>1</sup>: Underwriting profit   
Y<sup>2</sup>: Investment profit  

P<sub>1</sub>: premium acquisition process  
P<sub>2</sub>: reinsurance allocation process  
P<sub>3</sub>: profit generation process  

---

## Data Collections
We can get datas from financial income statement which collected in [財團法人保險事業發展中心](https://www.tii.org.tw/tii/actuarial/actuarial1/report/index.html)
#### data calculation in income statement:
X<sup>1</sup> = 承保費用支出 + 佣金費用  
X<sup>2</sup> = 其他營業成本 + 財務成本 + 營業費用

Z<sup>1,2</sup> = 再保費支出  
Z<sup>1,3</sup> = 簽單保費收入 + 手續費收入 - 再保費支出  
Z<sup>2,3</sup> = 再保佣金收入 + 再保費收入

Y<sup>1</sup> = 繼續營業單位稅前純益（損益）- 營業外收入費用 - 淨投資損益  
Y<sup>2</sup> = 淨投資損益

---

## Methodology - network DEA model
*model framwork recall:*
![](https://i.imgur.com/Ne2WxoZ.png)

### CRS model

#### Notations
n: decision unit in nonlife companies
k: modeling decision unit in nonlife company
ε： non-Archimedean constant, in this case is 10<sup>-11</sup>
#### Decision variables:
v<sup>i</sup>: weights of inputs X<sup>1</sup>, i={1, 2, 21, 22} in this example  
u<sup>j</sup>: weights of outputs Y<sup>j</sup>, j={1, 2} in this example  
w<sup>r</sup>: weights of intermedian inputs and outputs Z<sup>r</sup>, i={(1, 2), (1, 3), (2, 3)} in this example  
#### Formulation:
![](https://github.com/wuyentung/ORA_final_project/blob/main/fig/crs%20model.png)

The blue <font color="blue">P<sub>1</sub></font> which i={1, 2, 3} denotes the constraint derived from network model

#### Effency estimation:
We can get effiency of each process by
![](https://github.com/wuyentung/ORA_final_project/blob/main/fig/crs%20eff%20p.png)
In order to represent this network system in the form of series and parallel structures for efficiency decomposition, dummy process <font color="red">d<sub>1</sub>, d<sub>2</sub></font> is introduced below.  
![](https://github.com/wuyentung/ORA_final_project/blob/main/fig/eff%20network.png)

Since efficiency of dummy process is always 1, we can decompose efficiency of each process by stage. See [this paper](https://www.sciencedirect.com/science/article/pii/S0377221707010077) for more clearily explanation.
![](https://github.com/wuyentung/ORA_final_project/blob/main/fig/crs%20eff%20s.png)
By using stage efficiency, there would be multipling relationship which
![](https://github.com/wuyentung/ORA_final_project/blob/main/fig/e.png)

### VRS input-oriented model
*similar to CRS model, only difference is adding multiplier variables*
#### Decision variables:
w<sup>i</sup><sub>0</sub>: multiplier variables of process 1 and 2, i={1, 2} in this example  
u<sup>j</sup><sub>0</sub>: multiplier variables of process 3, j={1} in this example  
#### Formulation:
![](https://i.imgur.com/6AsR7mE.png)
#### Effency estimation:
similar to CRS model, we can get effiency of each process by
![](https://i.imgur.com/G29Gdbv.png)
and we can use dummy process to get stage efficiency which is
![](https://i.imgur.com/3QIUVEp.png)
By using stage efficiency, there would also be multipling relationship which ![](https://i.imgur.com/cRsnRzW.png)

---
## Example and Application
### Data: 2019 Nonlife insurance company
unit: 1000 NTD
![](https://i.imgur.com/OvCpqsW.png)
### Implement of CRS model
##### ※ [source code](https://github.com/wurmen/DEA/blob/master/Network_DEA/network_dea_code.py) for complete model
after we colected data
#### Import gurobipy
```python
import gurobipy as gp
```
#### Model building
- assign some variables to store result
```python
E={}
val_p1,val_p2,val_p3,val_s1,val_s2={},{},{},{},{}
slack_p1,slack_p2,slack_p3={},{},{}
val_s3 = {}
I = 2
O = 2
MID = 3
sols = {}
```
- use for loop calculate efficiency for each DMU
```python
for k in dmu:
    P1,P2,P3={},{},{}
    v, u, w = {}, {}, {}
```
- model
```python
    m = gp.Model("network_DEA_CRS")
```
- adding decision variables
```python=
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
```
- objective function
```python
    m.setObjective(u[0] * Y1[k] + u[1] * Y2[k], gp.GRB.MAXIMIZE)

```
- adding constraint

```python
    m.addConstr((v[0] * X1[k] + v[1] * X2[k]) == 1)
    for j in dmu:
        # (w11Z12j+w12Z13j)−
        #   (v1X1j+v2X21j)≤0 
        P1[j] = m.addConstr((w[0] * Z1_2[j] + w[1] * Z1_3[j]) - (v[0] * X1[j] + v[1] * X2_1[j]) <= 0)
        # w2Z23j−(v2X22j+w11Z12j)≤0 
        P2[j] = m.addConstr((w[2] * Z2_3[j]) - (v[1] * X2_2[j] + w[0] * Z1_2[j]) <= 0)
        # (u1Y1j+u2Y2j−u0)−
        #   (w12Z13j+w2Z23j)≤0
        P3[j] = m.addConstr((u[0] * Y1[j] + u[1] * Y2[j]) - (w[1] * Z1_3[j] + w[2] * Z2_3[j]) <= 0)
```
- optimize
```python
    m.optimize()
```

#### Get solutions:
```python
    E[k] = m.objVal

    u_sol = m.getAttr('x', u)
    v_sol = m.getAttr('x', v)
    w_sol = m.getAttr('x', w)

    sols[k] = m.x
```
- process efficiency decomposition
```python
    # 計算各process的效率值
    val_p1[k] = safe_div((w_sol[0]*Z1_2[k] + w_sol[1]*Z1_3[k]), ((v_sol[0])*X1[k] + (v_sol[1])*X2_1[k]))
    val_p2[k] = safe_div((w_sol[2]*Z2_3[k]), ((v_sol[1])*X2_2[k] + (w_sol[0])*Z1_2[k]))
    val_p3[k] = safe_div((u_sol[0]*Y1[k] + u_sol[1]*Y2[k] ), (w_sol[1]*Z1_3[k] + w_sol[2]*Z2_3[k] ))
```
- stage efficiency decomposition
```python
    # 計算各stage的效率值
    val_s1[k] = safe_div((w_sol[0]*Z1_2[k] + w_sol[1]*Z1_3[k] + v_sol[1]*X2_2[k]), (v_sol[0]*X1[k] + (v_sol[1])*X2[k]))
    val_s2[k] = safe_div((w_sol[1]*Z1_3[k]  + w_sol[2]*Z2_3[k] ), (w_sol[0]*Z1_2[k] + w_sol[1]*Z1_3[k] + v_sol[1]*X2_2[k]))
    val_s3[k] = val_p3[k]
```
#### Result export
```python
## check solutions
sol_col = ["v_sol1", "v_sol2", "w_sol1", "w_sol2", "w_sol3", "u_sol1", "u_sol2" ]
sol_df = pd.DataFrame(columns=sol_col)
for k in dmu:
    sol_df = sol_df.append(pd.DataFrame(data=[sols[k]], columns=sol_col, index=[k]))

## check efficiency
col = ["eff_total", "eff_p1", "eff_p2", "eff_p3", "eff_s1", "eff_s2", "eff_s3"]
result_df = pd.DataFrame(columns=col)
for k in dmu:
    result_df = result_df.append(pd.DataFrame(data=[[E[k], val_p1[k], val_p2[k], val_p3[k], val_s1[k], val_s2[k], val_s3[k]]], columns=col, index=[k]))

result_df = result_df.append(pd.DataFrame(data=[[np.mean(result_df[i]) for i in col]], columns=col, index=["Avg."]))
result_df = result_df.append(pd.DataFrame(data=[[np.std(result_df[i]) for i in col]], columns=col, index=["Std."]))
```
- export
```python
with pd.ExcelWriter('result.xlsx') as writer:  
        result_df.to_excel(writer, sheet_name='CRS') 
        sol_df.to_excel(writer, sheet_name='CRS_sol') 
```
- 最後再用 excel 排序排名

### Result:
#### 1. process efficiency
![](https://i.imgur.com/cwoFLPD.png)

Generally, technical efficiency follows common sence, which 富邦 and 國泰世紀 hold top 2 place. While there would be some arithmetic situations makes **technical efficiency lower than 0**, eg, TE_p2 of 和泰, which make scale efficiency hard to be interpreted. Besides, since the efficeincy decomposition in scale efficiency could be greater than one in some case.

#### 2. stage efficiency
![](https://i.imgur.com/IAXHiOm.png)

When we decomposite efficiency by stage, we can avoid situation which make technical efficiency lower than 0, which is a **more reasonable result compare with process efficiency**. While decomposition in **scale efficiency could still greater than one** for some arithmetic evidence.

---

## Conclusion

* Contributions:
    1. Use dummy process to deal with complicated network system, to handle arithmetic problem in network-DEA VRS model
    1. Update network framework in insurance industry
    1. Update insurance data sets from 2002 to 2019
    
* Restrictions:
    1. Efficiency decomposition in scale efficiency can still greater than 1 for some arithmetic evidence
    1. Some final output was lower than one according to financial statement, there would be better way instead of adding all output of DMUs uniformly
    1. We cannot tell the whole efficiency simply based on financial statement

* Future work:
    1. Use penal data to evaluate two dimensional efficiency decomposition in insurance industry
    1. Trade off between underwriting profit and investment profit
    1. IFRSs 17 would change the financial statement in insurance industry. It would be a chance to renew mod


---

## Reference
* Chen K, Zhu J., 2019. Scale efficiency in two-stage network DEA. Journal of the Operational Research Society, 70, 101-110
* Kao, C., Hwang, S.N.,  2008. Efficiency decomposition in two-stage data envelopment analysis: An application to non-life insurance companies in Taiwan. European Journal of Operational Research, 185, 418-429
* Kao, C.,  2009. Efficiency decomposition in network data envelopment analysis: A relational model. European Journal of Operational Research, 192, 949-962
* Lee, C.-Y., Johnson, A.L., 2012. Two-dimensional efficiency decomposition to measure the demand effect in productivity analysis. European Journal of Operational Research, 216(3), 584-593
* Lee, H.-S., 2021, Efficiency decomposition of the network DEA in variable returns to scale: an additive dissection in losses. Omega, 100, 102212
* Vincenzo Patrizii, 2020. On network two stages variable returns to scale Dea models. Omega, 97, 102084