import numpy as np
import skfuzzy as fuzz
import matplotlib.pyplot as plt
import pymysql


conn = pymysql.connect(host='localhost', user='root', password='',db='bankdata')
b = conn.cursor()


x = ["bm", "aoe","campexe","csm","am"]
pw = [1,2,3,4,5]
a = 0
rpl:int = 0
srba:int = 0

try:
    while 1:
        inpuser = input("UserName:\t")
        if inpuser in x:
            index = x.index(inpuser)
            inppass = int(input("Password:\t"))
            if inppass == pw[index]:
                print("Successfully Logged in....!")
                break
            else:
                print("Incorrect Password...!")
                continue
        else:
            print("No username exists.")
        continue
except:
    print("Error logging in")
    
try:
    if inpuser == x[0]:#bank mangager
        srba = 0
        rpl =  0
    
    if inpuser == x[1]: #Account operating executive 
        srba = 6
        rpl =  5
    
    if inpuser == x[2]: # Campaign executive
        srba = 7
        rpl =  3
    
    if inpuser == x[3]: # customer service manager
        srba = 5
        rpl =  6

    if inpuser == x[4]: # Assistant manager
        srba = 3
        rpl =  9
except:
    print("Error setting up srba and rpl values")
# Generate universe variables
#   * Srba and Rpl on subjective ranges [0, 10]
#   * Lop has a range of [0, 12] in units of percentage points
x_srba = np.arange(0, 11, 1)
x_rpl = np.arange(0, 11, 1)
x_lop = np.arange(0, 13, 1)

# Generate fuzzy membership functions
srgba_notallow = fuzz.trimf(x_srba, [0,0,5])
srgba_allow = fuzz.trimf(x_srba, [5,10,10])

rpl_lo = fuzz.trimf(x_srba, [0, 0, 5])
rpl_md = fuzz.trimf(x_srba, [0, 5, 10])
rpl_hi = fuzz.trimf(x_srba, [5, 10, 10])

lop_lo = fuzz.trimf(x_lop, [0, 0, 4])
lop_md = fuzz.trimf(x_lop, [0, 6, 12])
lop_hi = fuzz.trimf(x_lop, [8, 12, 12])

fig, (ax1,ax2,ax3) = plt.subplots(nrows=3, figsize=(7, 8))

ax1.plot(x_rpl, rpl_lo, color='blue', linewidth=1.5, label='Low')
ax1.plot(x_rpl, rpl_md, color='green', linewidth=1.5, label='Medium')
ax1.plot(x_rpl, rpl_hi, color='red', linewidth=1.5, label='High')
ax1.set_title('RPL')
ax1.legend()

ax2.plot(x_srba, srgba_allow, color='blue', linewidth=1.5, label='Allow')
ax2.plot(x_srba, srgba_notallow, color='green', linewidth=1.5, label='Not allow')
ax2.set_title('SRBA')
ax2.legend()

ax3.plot(x_lop, lop_lo, color='blue', linewidth=1.5, label='Low')
ax3.plot(x_lop, lop_md, color='green', linewidth=1.5, label='Medium')
ax3.plot(x_lop, lop_hi, color='red', linewidth=1.5, label='High')
ax3.set_title('LOP')
ax3.legend()

for ax in (ax1, ax2, ax3):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()

plt.tight_layout()

# SRBA and Rpl Values are fed into interp_membership fuction 
#interp -- find the degree of membership  
srba_level_nallow = fuzz.interp_membership(x_srba, srgba_notallow, srba)
srba_level_allow = fuzz.interp_membership(x_srba, srgba_allow, srba)
#print("SRBA Dg: ",srba_level_allow)
rpl_level_lo = fuzz.interp_membership(x_rpl, rpl_lo, rpl)
rpl_level_md = fuzz.interp_membership(x_rpl, rpl_md, rpl)
rpl_level_hi = fuzz.interp_membership(x_rpl, rpl_hi, rpl)


# Now we take our rules and apply them. Rule 1 concerns bad srba OR rpl.
# The OR operator means we take the maximum of these two.
active_rule1 = np.fmax(srba_level_allow, rpl_level_lo)

# Now we apply this by clipping the top off the corresponding output
# membership function with `np.fmin`
lop_activation_lo = np.fmin(active_rule1, lop_lo)  # removed entirely to 0

# For rule 2 we connect acceptable rpl to medium rpl
lop_activation_md = np.fmin(rpl_level_md, lop_md)

# For rule 3 we connect high rpl OR high srba with high lop
active_rule3 = np.fmax(srba_level_nallow, rpl_level_hi)
lop_activation_hi = np.fmin(active_rule3, lop_hi)
#Return an array of zeros with the same shape and type as a given array
lop0 = np.zeros_like(x_lop)

# Aggregate all three output membership functions together
aggregated = np.fmax(lop_activation_lo,
                     np.fmax(lop_activation_md, lop_activation_hi))


# Calculate defuzzified result
lop = fuzz.defuzz(x_lop, aggregated, 'centroid')
lop_activation = fuzz.interp_membership(x_lop, aggregated, lop)  # for plot

print("LOP: ",lop_activation)
print("")

# Visualize this
fig, ax0 = plt.subplots(figsize=(8, 3))

ax0.plot(x_lop, lop_lo, color='blue', linewidth=0.5, linestyle='--', )
ax0.plot(x_lop, lop_md, color='green', linewidth=0.5, linestyle='--')
ax0.plot(x_lop, lop_hi, color='red', linewidth=0.5, linestyle='--')
ax0.fill_between(x_lop, lop0, aggregated, facecolor='', alpha=0.7)
ax0.plot([lop, lop], [0, lop_activation], color='black', linewidth=1.5, alpha=0.9)
ax0.set_title('Level of Privacy (Required)')

# Turn off top/right axes

plt.tight_layout()


sql= 'SELECT * from `cdata` LIMIT 30;'
b.execute(sql)

countrow = b.execute(sql)
#print("Number of rows:", countrow)
#doobdata = a.fetchone()
data = b.fetchall()

#print(doobdata)
#mean=1
noise = np.random.normal(lop_activation)
noise1 = 1.251
noise2 = 2.362
noise3 = 2.160
noise4 = 1.981

noise5 = 2.1608
noise6 = 1.9810
noise7 = 2.16076
noise8 = 1.98171 

print("Records fetched from the Database")
print("------------------------------------------------------------------------")
for rows in data:
    if 0.0 <= lop_activation <= 0.19:          #bm
        print("Age:",rows[0])
        print("Duration",rows[1])
        print("Campaign",rows[2])
        print("pdays",rows[3])
        print("previous",rows[4])
        print("emp_var_rate:",rows[5])
        print("cons_price_ind",rows[6])
        print("cons_conf_ind:",rows[7])
        print("euribor:",rows[8])
        print("nr_employee:",rows[9])
        print("")    
    if 0.2 <= lop_activation <= 0.39:         #am
        print("Age:",rows[0])
        print("Duration",rows[1])
        print("Campaign",rows[2]+noise2) #camp
        print("pdays",rows[3]+noise3) #pdays
        print("previous",rows[4])
        print("emp_var_rate:",rows[5])
        print("cons_price_ind",rows[6])
        print("cons_conf_ind:",rows[7])
        print("euribor",rows[8])
        print("nr_employee:",rows[9])
        print("")
    if 0.4 <= lop_activation <= 0.61:            
        print("Age:",rows[0])  #ce 
        print("Duration",rows[1])
        print("Campaign",rows[2])
        print("pdays",rows[3])
        print("previous",rows[4])
        print("emp_var_rate:",rows[5])
        print("cons_price_ind",rows[6])
        print("cons_conf_ind:",rows[7])
        print("euribor",rows[8]+noise4) #euribor
        print("nr_employee:",rows[9])
        print("")
    if 0.62 <= lop_activation <= 0.8:
        print("Age:",rows[0]) 
        print("Duration",rows[1])
        print("Campaign",rows[2])
        print("pdays",rows[3])
        print("previous",rows[4])
        print("emp_var_rate:",rows[5]+noise5)  #evr                  #csm 
        print("cons_price_ind",rows[6]+noise6)   #cpi
        print("cons_conf_ind:",rows[7]+noise5)   #cci
        print("euribor",rows[8]+noise6)  #e
        print("nr_employee:",rows[9]+noise5)
        print("")
                                                                    #ne 
    if 0.81 <= lop_activation <= 1:
        print("Age:",rows[0])   #aoe
        print("Duration:",rows[1])
        print("Campaign:",rows[2]) 
        print("pdays:",rows[3])
        print("previous:",rows[4])
        print("emp_var_rate:",rows[5])
        print("cons_price_ind:",rows[6]+noise7)  #cpi cci
        print("cons_conf_ind:",rows[7]+noise8)
        print("euribor",rows[8]) 
        print("nr_employee:",rows[9]) 
        print("")
b.close()