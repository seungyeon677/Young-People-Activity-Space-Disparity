import pandas as pd
import geopandas as gpd
from geopandas.tools import sjoin

# 1. Load and Filter Administrative Boundary (SGG) Shapefile
# bnd_sigungu_00: National administrative boundary at the Sigungu level
shp = gpd.read_file('./bnd_sigungu_00_2022_2022_2Q.shp', encoding = 'cp949')
shp['SIGUNGU_CD'] = shp['SIGUNGU_CD'].astype(str)

# Filter for Seoul Metropolitan Area (SMA)
# Codes starting with 11(Seoul), 23(Incheon), and 31(Gyeonggi-do)
sig_shp = shp[(shp['SIGUNGU_CD'].str.startswith('11')) | (shp['SIGUNGU_CD'].str.startswith('23')) | (shp['SIGUNGU_CD'].str.startswith('31'))]
sig_shp.to_file('./SIG_sigungu_2022.shp', encoding = 'cp949')

# 2. Load and Preprocess Public Rental Housing (Happy House) Data
# Convert CRS to EPSG:5179 (Korea Central Belt) for accurate distance/spatial calculations
res = gpd.read_file('./행복주택_서울+인천+경기_v3_WGS.shp', encoding = 'cp949').set_crs(4326).to_crs(5179)
res['행정동코드'] = res['행정동코드'].astype(str)
res['CODE_AD2'] = res['행정동코드'].str[:5]

# Filter for Youth-targeted units only
# Exclude units for elderly (고령자), housing vulnerable (주거), and existing residents (기존)
res2 = res[~res['Room_who'].str.startswith('고령자') & ~res['Room_who'].str.startswith('주거') & ~res['Room_who'].str.startswith('기존')].reset_index()

# Calculate total floor area for each housing project
res2['Room_count'] = res2['Room_count'].astype(int)
res2['Room_size'] = res2['Room_size'].astype(int)
res2['Room_size2'] = res2['Room_size'] * res2['Room_count'] # Total Area = Unit Size * Number of Units

res2 = res2[['CODE_AD2', 'Room_count', 'Room_size2', 'X', 'Y', 'geometry']]

# 3. Spatial Join: Mapping Points (Housing) to Polygons (Districts)
point = gpd.read_file('./SIG_happyhouse.shp').set_crs(4326).to_crs(5179)
poly = gpd.read_file('./SIG_sigungu_2022.shp')

# Use 'sjoin' to identify which Sigungu polygon each housing point falls into
pointInPolys = sjoin(poly, point, how = 'left')
grouped = pointInPolys.groupby('index_right')

# Replace missing values (NaN) with 0 for districts without housing projects
pointInPolys = pointInPolys.fillna(0)

# 4. Aggregate Housing Statistics per District
sc = pointInPolys['SIGUNGU_CD'].unique()

hh = []
for i in range(len(sc)):
    # Sum up the total number of rooms and total floor area for each district
    b = pointInPolys[pointInPolys['SIGUNGU_CD'] == sc[i]]['Room_count'].sum()
    c = pointInPolys[pointInPolys['SIGUNGU_CD'] == sc[i]]['Room_size2'].sum()
    hh.append([sc[i], b, c])
    
# Create a summary DataFrame
h_df = pd.DataFrame(columns = ['CODE', 'Room_count', 'Room_size'], data = hh)

# 5. Export Final Aggregated Statistics
# This dataset represents the 'Supply' side in the youth housing mismatch analysis
h_df.to_csv('./SIG_happyhouse.csv', encoding = 'cp949', index = False)