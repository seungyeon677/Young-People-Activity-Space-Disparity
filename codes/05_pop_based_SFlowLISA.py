import numpy as np
import pandas as pd

# Set display format for floating point numbers to maintain 5 decimal places
pd.options.display.float_format = '{:.5f}'.format

import warnings
warnings.filterwarnings(action='ignore')

# Define analysis target month (November 2022)
ym = ['202211']

# 1. Load Inverse Distance Weighting (IDW) Matrix
# This matrix represents geographical distances between administrative districts
p_array = np.array(pd.read_csv('./DistanceMatrix.csv', encoding = 'cp949'))

# 2. Load Processed Youth Movement Flow Data
# 'od' contains standardized population flows (Zyouth_P) for the Seoul Metropolitan Area
od = pd.read_csv('./서울인천경기_youthmove_weekday_202211.csv', encoding = 'cp949')

# Convert data columns to lists to optimize iteration performance (speeding up the 'for' loop)
O = list(od.loc[:, 'num_x'])     # Origin region ID
D = list(od.loc[:, 'num_y'])     # Destination region ID
Zpop = list(od.loc[:, 'Zyouth_P']) # Standardized youth population flow value
idx = od.index
print("Listing finished")

# 3. Calculate Spatial Lag for Flows using Distance-based Weights
# This step determines the 'Spatial Lag' by aggregating flows of neighboring OD pairs
youth_x = []
for i in range(len(idx)):
    middle_y = []
    for j in range(len(idx)):
        # Calculate spatial proximity between start nodes (dist_o) and end nodes (dist_d)
        dist_o = p_array[O[i]-1][O[j]-1]
        dist_d = p_array[D[i]-1][D[j]-1]
        
        # Avoid division by zero if there is no proximity
        if(dist_o + dist_d) == 0:
            continue

        # Apply Inverse Distance Weighting: Closer flows contribute more to the lag value
        zy = Zpop[j] * 1 / (dist_o + dist_d)
        middle_y.append(zy)
        
    # Sum the weighted values of neighbors to obtain the spatial lag for flow 'i'
    youth_x.append(sum(middle_y))
print("Flow spatial lag calculation finished")

# Store the calculated spatial lag in the dataframe
od['pop_lag'] = youth_x
od.to_csv('./DM_SIG_LAG_weekday_pop_0130.csv', encoding = 'cp949', index = False)

# 4. Compute Flow-LISA Statistic (Local Moran's I for Flows)
# Fl_pop represents the local spatial association score for each flow
od['Fl_pop'] = (od['Zyouth_P'] * od['pop_lag']) / od['Zyouth_P']**2

# Standardize the Flow-LISA scores to calculate significance (Z-score)
od['Fl_popsig'] = (od['Fl_pop'] - od['Fl_pop'].mean()) / od['Fl_pop'].std()
print("Significance calculation finished")

# 5. Classify Clusters based on Z-score and Lag values (LISA Quadrants)
# Categorize into HH (High-High), HL (High-Low), LH (Low-High), and LL (Low-Low)
od['value_P'] = 0
for i in idx:
    if (od['Zyouth_P'][i] >= 0):
        if (od['pop_lag'][i] >= 0):
            od['value_P'][i] = 'HH'
        else:
            od['value_P'][i] = 'HL'
    else:
        if (od['pop_lag'][i] >= 0):
            od['value_P'][i] = 'LH'
        else:
            od['value_P'][i] = 'LL'

# 6. Apply Statistical Significance Threshold
# Use a 99% confidence interval (Z-score threshold: +/- 2.58)
# Categorize non-significant results as 'NS'
od['value_P2'] = 0
for i in idx:
    if od['Fl_popsig'][i] <= -2.58:
        od['value_P2'][i] = od['value_P'][i]
    elif od['Fl_popsig'][i] >= 2.58:
        od['value_P2'][i] = od['value_P'][i]
    else:
        od['value_P2'][i] = 'NS'
print("Flow-LISA cluster categorization finished")

# Save final result including cluster categories for visualization (e.g., Mapping)
od.to_csv('./DM_SIG_Fl_weekday_pop_0130.csv', encoding = 'cp949', index = False)