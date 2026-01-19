import numpy as np
import pandas as pd

# Set float display format for better readability of statistical values
pd.options.display.float_format = '{:.5f}'.format

from tqdm.auto import tqdm
import warnings

# Suppress warnings to maintain a clean output console
warnings.filterwarnings(action='ignore')

# 1. Load Administrative Code Mapping Data
# code: Master mapping table for administrative region codes
code = pd.read_csv('./CODE_2023.01.01.csv', encoding = 'cp949')
code['CODE_AD'] = code['CODE_AD'].astype(str)
code['CODE_AD2'] = code['CODE_AD'].str[:5]  # Extract 5-digit district (SGG) level codes

# 2. Load Coordinate Data for OD (Origin-Destination) Pairs
# od_xy: Contains spatial coordinates and numeric IDs for each OD pair
od_xy = pd.read_csv('./od_xy_num_0716.csv', encoding = 'cp949')

# 3. Load Raw Floating Population Data (April 2022)
pop = pd.read_csv('./성연령최종파일_202204.csv', encoding = 'utf-8', sep = '|')

# Convert code columns to string for consistent prefix filtering
pop['home_GU_CODE'] = pop['home_GU_CODE'].astype(str)
pop['dst_HCODE'] = pop['dst_HCODE'].astype(str)

# 4. Filter for Weekday Patterns in the Seoul Metropolitan Area (SMA)
# Exclude weekends (Saturday and Sunday) to focus on daily activity patterns
pop = pop[(pop['DAY'] != '토') & (pop['DAY'] != '일')]

# Filter for movements where both Origin and Destination are within Seoul(11), Gyeonggi(41), or Incheon(28)
pop2 = pop[((pop['home_GU_CODE'].str.startswith('41')) | (pop['home_GU_CODE'].str.startswith('28')) | (pop['home_GU_CODE'].str.startswith('11'))) &
           ((pop['dst_HCODE'].str.startswith('41')) | (pop['dst_HCODE'].str.startswith('28')) | (pop['dst_HCODE'].str.startswith('11')))]

# 5. Extract Youth Population (20s and 30s)
# AGE '20G' and '30G' represent the target demographic group
pop_y = pop2[(pop2['AGE'] == '20G') | (pop2['AGE'] == '30G')].reset_index()
pop_y['dst_HCODE2'] = pop_y['dst_HCODE'].str[:5] # Standardize destination to 5-digit SGG level
pop_y2 = pop_y[['home_GU_CODE', 'dst_HCODE2', 'AGE', 'SEX', 'STD_YMD', 'DAY', 'type', 'POP']]

# 6. Aggregate Population Flows by OD Pair
y_o = pop_y2['home_GU_CODE'].unique()
y_d = pop_y2['dst_HCODE2'].unique()

y_od = []
# Nested loop to calculate the total flow for each unique OD combination
for i in tqdm(range(len(y_o))):
    for j in tqdm(range(len(y_d))):
        # Sum population for specific Origin (home_GU_CODE) and Destination (dst_HCODE2)
        y_sum = pop_y2[(pop_y2['home_GU_CODE'] == y_o[i]) & (pop_y2['dst_HCODE2'] == y_d[j])]['POP'].sum()
        
        # Convert administrative AD codes back to standard region IDs
        y_co = code[code['CODE_AD2'] == y_o[i]]['CODE'].tolist()[0]
        y_cd = code[code['CODE_AD2'] == y_d[j]]['CODE'].tolist()[0]
        y_od.append([y_co, y_cd, y_sum])
        
# Create a DataFrame for aggregated youth flows
col = ['O', 'D', 'POP']
p_y = pd.DataFrame(y_od, columns = col)

# 7. Final Data Integration and Normalization
p_y['O'] = p_y['O'].astype(str)
p_y['D'] = p_y['D'].astype(str)
p_y['CODE'] = p_y['O'] + p_y['D'] # Create a unique OD pair key

od_xy['CODE'] = od_xy['CODE'].astype(str)

# Merge with coordinate data for spatial analysis mapping
p_y2 = pd.merge(od_xy, p_y, left_on = 'CODE', right_on = 'CODE')

# Reorder and rename columns for clarity
p_y2 = p_y2.iloc[:, [0, 1, 2, 3, 4, 5, 6, 7, 8, 11]]
p_y2.columns = ['O', 'D', 'O_x', 'O_y', 'D_x', 'D_y', 'num_x', 'num_y', 'CODE', 'POP']

# Calculate Z-score for the population flow to identify statistical outliers and patterns
p_y2['Zpop_P'] = (p_y2['POP'] - p_y2['POP'].mean()) / p_y2['POP'].std()

# Export the processed dataset for Flow-LISA or other spatial association analysis
p_y2.to_csv('./SIG_pop_weekday_202204.csv', encoding = 'cp949', index = False)