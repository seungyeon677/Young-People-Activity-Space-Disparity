import numpy as np
import pandas as pd

# Set display format for floating point numbers to 5 decimal places
pd.options.display.float_format = '{:.5f}'.format

from tqdm.auto import tqdm
import warnings

# Ignore warning messages for a cleaner output
warnings.filterwarnings(action='ignore')

# 1. Load Administrative Code Mapping Data
# 'CODE_2023.01.01.csv' contains mapping between different administrative code systems
code = pd.read_csv('./CODE_2023.01.01.csv', encoding = 'cp949')
code['CODE_AD'] = code['CODE_AD'].astype(str)
code['CODE_AD2'] = code['CODE_AD'].str[:5] # Extract 5-digit district (SGG) level codes

# 2. Load Coordinate and Index Data for OD Pairs
# 'od_xy_num_0716.csv' contains spatial coordinates and numeric IDs for Origin-Destination pairs
od_xy = pd.read_csv('./od_xy_num_0716.csv', encoding = 'cp949')

# 3. Load Raw Credit Card Transaction Data (April 2022)
card = pd.read_csv('./KRILA_202204.csv', encoding = 'cp949')

# 4. Filter Data by Specific Criteria
# Filter for Weekends in April 2022, Youth Age Group (AGE_2), and exclude 'ETC' category
card2 = card[((card['TA_D'] == 20220402) | (card['TA_D'] == 20220403) | (card['TA_D'] == 20220409) | (card['TA_D'] == 202204010) | 
            (card['TA_D'] == 20220416) | (card['TA_D'] == 20220417) | (card['TA_D'] == 20220423) | (card['TA_D'] == 20220430)) & 
            ((card['AGE_CD'] == 'AGE_2') & (card['RY_CD'] != 'ETC'))]

# Convert region codes to string for prefix filtering
card2['CLNN_CTY_CD'] = card2['CLNN_CTY_CD'].astype(str)
card2['MCT_SSG_CD'] = card2['MCT_SSG_CD'].astype(str)

# 5. Filter for Seoul Metropolitan Area (SMA)
# Region codes starting with 11 (Seoul), 28 (Incheon), and 41 (Gyeonggi)
card3 = card2[((card2['CLNN_CTY_CD'].str.startswith('41')) | (card2['CLNN_CTY_CD'].str.startswith('28')) | (card2['CLNN_CTY_CD'].str.startswith('11'))) &
              ((card2['MCT_SSG_CD'].str.startswith('41')) | (card2['MCT_SSG_CD'].str.startswith('28')) | (card2['MCT_SSG_CD'].str.startswith('11')))].reset_index()

# Select relevant columns for aggregation
card_y = card3[['CLNN_CTY_CD', 'MCT_SSG_CD', 'RY_CD', 'TIME_CCD', 'SEX_CD', 'TAMT', 'CNT']]
c_o = card_y['CLNN_CTY_CD'].unique().tolist()
c_d = card_y['MCT_SSG_CD'].unique().tolist()

# 6. Manual Data Correction
# Specific handling for regional code '41670' (Yeoju-si) due to code system updates or inconsistencies
c_o = c_o[:82] + c_o[84:86]
c_o[82] = '41670'
c_d[30] = '41670'

# 7. Aggregate Consumption Flow (Total Transaction Amount) by OD Pair
c_od = []
for i in tqdm(range(len(c_o)), desc="Aggregating Origins"):
    for j in tqdm(range(len(c_d)), desc="Aggregating Destinations", leave=False):
        # Calculate the total transaction amount (TAMT) for each OD pair
        c_sum = card_y[(card_y['CLNN_CTY_CD'] == c_o[i]) & (card_y['MCT_SSG_CD'] == c_d[j])]['TAMT'].sum()
        
        # Map back to standard administrative codes using the master code table
        c_co = code[code['CODE_AD2'] == c_o[i]]['CODE'].tolist()[0]
        c_cd = code[code['CODE_AD2'] == c_d[j]]['CODE'].tolist()[0]
        c_od.append([c_co, c_cd, c_sum])
        
# Create a DataFrame for the aggregated consumption flows
col = ['O', 'D', 'PAY']
c_y = pd.DataFrame(c_od, columns = col)

# Create a unique key for merging with coordinate data
c_y['CODE'] = c_y['O'].astype(str) + c_y['D'].astype(str)

# 8. Filter Spatial Metadata for SMA
od_xy['O2'] = od_xy['O'].astype(str)
od_xy['D2'] = od_xy['D'].astype(str)
# Codes starting with 11(Seoul), 23/28(Incheon), 31/41(Gyeonggi) based on different datasets
od_xy = od_xy[((od_xy['O2'].str.startswith('11')) | (od_xy['O2'].str.startswith('23')) | (od_xy['O2'].str.startswith('31'))) &
              ((od_xy['D2'].str.startswith('11')) | (od_xy['D2'].str.startswith('23')) | (od_xy['D2'].str.startswith('31')))]

od_xy['CODE'] = od_xy['CODE'].astype(str)

# 9. Merge Aggregated Flows with Spatial Metadata
c_y2 = pd.merge(od_xy, c_y, how = 'left', on = 'CODE')
c_y2 = c_y2.iloc[:, [0, 1, 2, 3, 4, 5, 6, 7, 8, 11]]
c_y2.columns = ['O', 'D', 'O_x', 'O_y', 'D_x', 'D_y', 'num_x', 'num_y', 'CODE', 'PAY']

# 10. Statistical Normalization (Z-score)
# Standardize the transaction amount (PAY) for subsequent spatial association analysis (e.g., Flow-LISA)
c_y2['Zpay_P'] = (c_y2['PAY'] - c_y2['PAY'].mean()) / c_y2['PAY'].std()

# 11. Export the Final Processed Dataset
# Note: Input data is from April 2022, though the filename mentions November
c_y2.to_csv('./서울인천경기_youthpay_weekend_202204.csv', encoding = 'cp949', index = False)