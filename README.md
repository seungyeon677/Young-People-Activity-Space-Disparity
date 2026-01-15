# Young-People-Activity-Space-Disparity

Unveiling Spatial Disparities between Public Rental Housing and Young People’s Daily Activity Spaces

This repository contains the source code and methodology used in the research published in the *Journal of the Korean Geographical Society*.

## 📑 Publication Information
* **Title:** 청년인구 일상 활동 영역과 행복주택 입지의 공간적 불일치에 관한 연구 (Unveiling Spatial Disparities between Public Rental Housing and Young People’s Daily Activity Spaces)
* **Authors:** Lee, S., Hwang, T., Do Lee, W., & Hwang, C. S.
* **Journal:** *Journal of the Korean Geographical Society*, 59 (4), 196-209. (2024)
* **DOI:** [Link to Journal/DOI if available]

## 🔍 Research Overview
This study explores the geographic relationship between **"Happy Housing"** (South Korea's representative public rental housing for youth) and the actual **Daily Activity Spaces** of the young population. 

We utilize large-scale mobility data, including:
* **Mobile Floating Population Data:** To track hourly and monthly population movements.
* **Credit Card Transaction Data:** To analyze consumption-based activity patterns.

### Methodology: Flow-LISA
To identify spatial associations, we employed **Flow-LISA (Local Indicators of Spatial Association for Flows)**. This allowed us to detect clusters where housing supply and actual human activity either align (High-High) or show significant mismatch.

## 🛠 Project Structure
* `/data`: Sample datasets and administrative boundary files (Shapefiles).
* `/notebooks`: Jupyter notebooks for KNN sensitivity analysis and visualization.
