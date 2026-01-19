import pandas as pd

# Set display format for floating point numbers to 5 decimal places
pd.options.display.float_format = '{:.5f}'.format

## 1. Calculation of Coulter's Adjustment Coefficient (Ci)
# This coefficient quantifies the gap between actual supply and ideal supply 
# required to achieve spatial equity based on youth activity levels.

# Load the aggregated dataset containing housing supply and activity shares
df = pd.read_csv('./SIG_mpoppoppay+roomcount+size.csv', encoding = 'cp949')

### --- Scenario A: Short-term Population Mobility vs. Housing ---

# A-1. Adjustment for Unit Count based on Short-term Population
pop_Ci_count = []
for i in range(len(df)):
    # Formula: Actual Supply - (Activity Share * Total Supply)
    # A positive value indicates oversupply, while a negative value indicates a shortage.
    a = df.loc[i, 'Room_count'] - df.loc[i, 'POP/allPOP'] * df['Room_count'].sum()
    pop_Ci_count.append(a)
    
# A-2. Adjustment for Total Floor Area based on Short-term Population
pop_Ci_size = []
for i in range(len(df)):
    a = df.loc[i, 'Room_size'] - df.loc[i, 'POP/allPOP'] * df['Room_size'].sum()
    pop_Ci_size.append(a)
    
### --- Scenario B: Medium-term Population Mobility vs. Housing ---

# B-1. Adjustment for Unit Count based on Medium-term Population
mpop_Ci_count = []
for i in range(len(df)):
    a = df.loc[i, 'Room_count'] - df.loc[i, 'MPOP/allMPOP'] * df['Room_count'].sum()
    mpop_Ci_count.append(a)
    
# B-2. Adjustment for Total Floor Area based on Medium-term Population
mpop_Ci_size = []
for i in range(len(df)):
    a = df.loc[i, 'Room_size'] - df.loc[i, 'MPOP/allMPOP'] * df['Room_size'].sum()
    mpop_Ci_size.append(a)
    
### --- Scenario C: Short-term Consumption Pattern vs. Housing ---

# C-1. Adjustment for Unit Count based on Consumption (PAY)
pay_Ci_count = []
for i in range(len(df)):
    a = df.loc[i, 'Room_count'] - df.loc[i, 'PAY/allPAY'] * df['Room_count'].sum()
    pay_Ci_count.append(a)
    
# C-2. Adjustment for Total Floor Area based on Consumption (PAY)
pay_Ci_size = []
for i in range(len(df)):
    a = df.loc[i, 'Room_size'] - df.loc[i, 'PAY/allPAY'] * df['Room_size'].sum()
    pay_Ci_size.append(a)
    
# 2. Integrate the calculated coefficients into the main DataFrame
df['mpop_Ci_count'] = mpop_Ci_count
df['mpop_Ci_size'] = mpop_Ci_size

df['pop_Ci_count'] = pop_Ci_count
df['pop_Ci_size'] = pop_Ci_size

df['pay_Ci_count'] = pay_Ci_count
df['pay_Ci_size'] = pay_Ci_size

# 3. Export the final dataset with Coulter Adjustment Indices
# This output serves as the primary data for spatial policy recommendations.
df.to_csv('./SIG_mpoppoppay+Coulterindex.csv', encoding = 'cp949', index = False)