import pandas as pd

# Set float display format to 5 decimal places for precise inequality index values
pd.options.display.float_format = '{:.5f}'.format

## 1. Calculation of Coulter's Inequity Index
# This index measures the spatial disparity between supply (Housing) and demand/activity (Population/Spending).

# Load aggregated data containing housing supply, population mobility, and consumption statistics
df = pd.read_csv('./SIG_mpoppoppay+roomcount+size.csv', encoding = 'cp949')

### --- Scenario A: Short-term Population Mobility vs. Housing ---

# A-1. Supply (Unit Count) vs. Demand (Short-term Population)
upper_a = []
down_b = []
for i in range(len(df)):
    # Numerator part: Squared difference between the share of housing units and the share of population
    a = (df.loc[i, 'Room_count']/df['Room_count'].sum() - df.loc[i, 'POP/allPOP'])**2
    # Denominator part: Squared share of the population
    b = df.loc[i, 'POP/allPOP']**2
    upper_a.append(a)
    down_b.append(b)
    
# Calculate the final Coulter Index for unit counts (Short-term Pop)
pop_CI_count = (100 * sum(upper_a)**(1/2)) / ((sum(down_b) - 2*min(down_b) + 1)**(1/2))

# A-2. Supply (Total Floor Area) vs. Demand (Short-term Population)
upper_a = []
down_b = []
for i in range(len(df)):
    a = (df.loc[i, 'Room_size']/df['Room_size'].sum() - df.loc[i, 'POP/allPOP'])**2
    b = df.loc[i, 'POP/allPOP']**2
    upper_a.append(a)
    down_b.append(b)
    
# Calculate the final Coulter Index for housing size (Short-term Pop)
pop_CI_size = (100 * sum(upper_a)**(1/2)) / ((sum(down_b) - 2*min(down_b) + 1)**(1/2))


### --- Scenario B: Medium-term Population Mobility vs. Housing ---

# B-1. Supply (Unit Count) vs. Demand (Medium-term Population)
upper_a = []
down_b = []
for i in range(len(df)):
    a = (df.loc[i, 'Room_count']/df['Room_count'].sum() - df.loc[i, 'MPOP/allMPOP'])**2
    b = df.loc[i, 'MPOP/allMPOP']**2
    upper_a.append(a)
    down_b.append(b)

# Calculate the final Coulter Index for unit counts (Medium-term Pop)
pop_CI_count = (100 * sum(upper_a)**(1/2)) / ((sum(down_b) - 2*min(down_b) + 1)**(1/2))

# B-2. Supply (Total Floor Area) vs. Demand (Medium-term Population)
upper_a = []
down_b = []
for i in range(len(df)):
    a = (df.loc[i, 'Room_size']/df['Room_size'].sum() - df.loc[i, 'MPOP/allMPOP'])**2
    b = df.loc[i, 'MPOP/allMPOP']**2
    upper_a.append(a)
    down_b.append(b)
    
# Calculate the final Coulter Index for housing size (Medium-term Pop)
pop_CI_size = (100 * sum(upper_a)**(1/2)) / ((sum(down_b) - 2*min(down_b) + 1)**(1/2))


### --- Scenario C: Short-term Consumption Pattern vs. Housing ---

# C-1. Supply (Unit Count) vs