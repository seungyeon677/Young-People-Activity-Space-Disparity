import pandas as pd

# 1. Load Monthly Resident Population Data (November 2022)
# The dataset contains population counts by age; 'thousands' is used to parse numbers with commas
df = pd.read_csv('./202211_연령별인구현황_월간.csv', encoding = 'cp949', thousands = ',')

# Extract administrative region codes from the '행정구역' column (Format: Area Name (Code))
df['CODE_AD'] = df['행정구역'].str.split('(').str[1].str.split(')').str[0]

# 2. Filter for Youth Population (Ages 20 to 39)
# Select specific columns representing ages from 20 to 39 based on the Korean age counting system or standard
df2 = df[['CODE_AD', 
           '2022년11월_계_20세', '2022년11월_계_21세', '2022년11월_계_22세', '2022년11월_계_23세', '2022년11월_계_24세',
           '2022년11월_계_25세', '2022년11월_계_26세', '2022년11월_계_27세', '2022년11월_계_28세', '2022년11월_계_29세', 
           '2022년11월_계_30세', '2022년11월_계_31세', '2022년11월_계_32세', '2022년11월_계_33세', '2022년11월_계_34세', 
           '2022년11월_계_35세', '2022년11월_계_36세', '2022년11월_계_37세', '2022년11월_계_38세', '2022년11월_계_39세']]

# Standardize to 5-digit District (SGG) codes
df2['CODE_AD2'] = df2['CODE_AD'].str[:5]

# Calculate total Resident Population (RPOP) for the defined youth age group
df2['RPOP'] = df2.iloc[:, 1:22].sum(axis = 1)

# 3. Spatial Filtering for Seoul Metropolitan Area (SMA)
# Keep data only for Seoul(11), Incheon(28), and Gyeonggi-do(41)
df3 = df2[['CODE_AD2', 'RPOP']]
df3 = df3[(df3['CODE_AD2'].str.startswith('11')) | (df3['CODE_AD2'].str.startswith('28')) | (df3['CODE_AD2'].str.startswith('41'))]

# 4. Load Master Regional Codes for Mapping
# f_mpop: Migration flow data to identify the unique region codes used in the study
f_mpop = pd.read_csv('./SIG_mpop_weekday_202211.csv', encoding = 'cp949')
c = f_mpop['O'].unique()

# code: Conversion table between administrative codes and numeric analysis IDs
code = pd.read_csv('./CODE_2023.01.01.csv', encoding = 'cp949')
code['CODE_AD'] = code['CODE_AD'].astype(str)
code['CODE_AD2'] = code['CODE_AD'].str[:5]

# 5. Map Resident Population to Study Analysis Codes
rpop = []
for i in range(len(c)):
    # Match the study's region ID (c[i]) to the administrative code (AD2)
    # Then retrieve the corresponding Resident Population (RPOP)
    try:
        a = code[code['CODE'] == c[i]]['CODE_AD2'].tolist()[0]
        b = df3[df3['CODE_AD2'] == a]['RPOP'].tolist()[0]
        rpop.append([c[i], b])
    except IndexError:
        # Handle cases where code mapping might be missing
        continue
    
# Create a DataFrame for the finalized resident population dataset
r_df = pd.DataFrame(columns = ['CODE', 'RPOP'], data = rpop)

# 6. Export Processed Resident Population Data
# This file will be used to calculate spatial mismatch or housing demand
r_df.to_csv('./SIG_rpop_202211.csv', encoding = 'cp949', index = False)