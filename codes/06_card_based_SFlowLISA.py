import numpy as np
import pandas as pd

# Set float display format to 5 decimal places for statistical precision
pd.options.display.float_format = '{:.5f}'.format

import warnings
warnings.filterwarnings(action='ignore')

# Define analysis target month (November 2022)
ym = ['202211']

# 1. Load Inverse Distance Matrix
# This matrix represents the geographical distance between administrative units
p_array = np.array(pd.read_csv('./DistanceMatrix.csv', encoding = 'cp949'))

# 2. Load Processed Youth Consumption Flow Data
# The dataset contains standardized youth spending flows (Zyouth_P) in the SMA
od = pd.read_csv('./서울인천경기_youthpay_weekday_202211.csv', encoding = 'cp949')

# Convert columns to lists to optimize the nested loop performance
O = list(od.loc[:, 'num_x'])      # Numeric ID for Origin
D = list(od.loc[:, 'num_y'])      # Numeric ID for Destination
Zyouth = list(od.loc[:, 'Zyouth_P']) # Standardized consumption value
idx = od.index
print("Data listing finished")

# 3. Calculate Spatial Lag for Flows (Flow-based Spatial Lag)
# This measures the influence of neighboring flows using Inverse Distance Weighting (IDW)
youth_x = []
for i in range(len(idx)):
    middle_y = []
    for j in range(len(idx)):
        # Proximity between Origin nodes and Destination nodes respectively
        dist_o = p_array[O[i]-1][O[j]-1]
        dist_d = p_array[D[i]-1][D[j]-1]
        
        # Skip if there is no proximity (avoid division by zero)
        if(dist_o + dist_d) == 0:
            continue

        # Apply IDW: Neighbors with shorter distances have higher weights
        zy = Zyouth[j] * 1 / (dist_o + dist_d)
        middle_y.append(zy)
    
    # Aggregate weighted neighboring flows to obtain the spatial lag for flow 'i'
    youth_x.append(sum(middle_y))
print("Youth flow lag calculation finished")

# Store spatial lag results
od['youth_lag'] = youth_x
od.to_csv('./DM_SIG_LAG_weekday_pay_0130.csv', encoding = 'cp949', index = False)

# 4. Calculate Flow-LISA Statistic
# Compute the local spatial association indicator for flows
od['Fl_youth'] = (od['Zyouth_P'] * od['youth_lag']) / od['Zyouth_P']**2

# Standardize Flow-LISA scores to identify statistical significance (Z-score)
od['Fl_youthsig'] = (od['Fl_youth'] - od['Fl_youth'].mean()) / od['Fl_youth'].std()
print("Significance calculation finished")

# 5. Classify Clusters based on LISA Quadrants
# Categorize flows into HH (High-High), HL (High-Low), LH (Low-High), and LL (Low-Low)
od['value_Y'] = 0
for i in idx:
    if (od['Zyouth_P'][i] >= 0):
        if (od['youth_lag'][i] >= 0):
            od['value_Y'][i] = 'HH'
        else:
            od['value_Y'][i] = 'HL'
    else:
        if (od['youth_lag'][i] >= 0):
            od['value_Y'][i] = 'LH'
        else:
            od['value_Y'][i] = 'LL'

# 6. Significance Filtering (Z-score Threshold)
# Apply a threshold of 2.58 (99% confidence level) to identify significant clusters
# Flows below the threshold are marked as 'NS' (Non-Significant)
od['value_Y2'] = 0
for i in idx:
    if od['Fl_youthsig'][i] <= -2.58:
        od['value_Y2'][i] = od['value_Y'][i]
    elif od['Fl_youthsig'][i] >= 2.58:
        od['value_Y2'][i] = od['value_Y'][i]
    else:
        od['value_Y2'][i] = 'NS'
print("Flow-LISA categorization finished")

# Export final result for spatial mapping and visualization
od.to_csv('./DM_SIG_Fl_weekday_pay_0130.csv', encoding = 'cp949', index = False)