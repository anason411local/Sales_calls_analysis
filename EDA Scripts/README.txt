================================================================================
OMC CALL DURATION - EDA ANALYSIS FILES
================================================================================

This folder contains Exploratory Data Analysis (EDA) for the TO_OMC_Duration 
column from the mergeed_for_test.csv dataset.

================================================================================
FILES IN THIS FOLDER
================================================================================

PYTHON SCRIPT:
--------------
omc_duration_eda.py
  - Main EDA script that generates all visualizations
  - Analyzes call duration distribution
  - Creates 3 comprehensive visualization files
  - Run with: python omc_duration_eda.py

VISUALIZATIONS (PNG FILES):
---------------------------
1. omc_duration_comprehensive_eda.png
   Contains 6 plots:
   - Histogram with Gaussian Distribution Overlay
   - Call Duration Distribution - Frequency Histogram
   - Box Plot with Violin Plot Overlay
   - Q-Q Plot - Normality Test
   - Cumulative Distribution Function (CDF)
   - Call Duration Distribution (in Minutes)

2. omc_duration_gaussian_analysis.png
   Contains 4 plots:
   - Gaussian Distribution Fit
   - Standardized Distribution (Z-Scores)
   - Residuals from Normal Distribution
   - Histogram vs KDE vs Normal Distribution

3. omc_duration_category_analysis.png
   Contains 4 sections:
   - Call Duration Categories Distribution (Bar Chart)
   - Call Duration Categories - Percentage Distribution (Pie Chart)
   - Distribution with Outliers Highlighted
   - Statistical Summary Table

DOCUMENTATION:
--------------
eda_insights_summary.txt
  - Comprehensive text summary of all findings
  - Statistical analysis results
  - Business insights and recommendations
  - Key metrics and interpretations

README.txt (this file)
  - Overview of folder contents
  - Quick reference guide

================================================================================
QUICK STATISTICS
================================================================================

Dataset: mergeed_for_test.csv
Column: TO_OMC_Duration (seconds)
Valid Records: 1,221 calls

Mean Duration:      483.29 seconds (8.05 minutes)
Median Duration:    293.00 seconds (4.88 minutes)
Std Deviation:      534.72 seconds
Range:              9 - 3,612 seconds (0.15 - 60.20 minutes)

Distribution: Right-skewed (most calls are shorter, with a long tail)
Outliers: 96 calls (7.9%) are unusually long (>22.3 minutes)

================================================================================
HOW TO USE
================================================================================

1. VIEW VISUALIZATIONS:
   - Open the PNG files to see beautiful matplotlib charts
   - All charts are high resolution (300 DPI)

2. READ INSIGHTS:
   - Open eda_insights_summary.txt for detailed analysis
   - Contains business recommendations and interpretations

3. RE-RUN ANALYSIS:
   - Execute: python omc_duration_eda.py
   - Will regenerate all visualizations
   - Useful if dataset is updated

4. MODIFY ANALYSIS:
   - Edit omc_duration_eda.py to customize
   - Add more visualizations or change parameters
   - Well-commented code for easy understanding

================================================================================
REQUIREMENTS
================================================================================

Python Packages:
- pandas
- numpy
- matplotlib
- seaborn
- scipy

Install with: pip install pandas numpy matplotlib seaborn scipy

================================================================================
KEY FINDINGS
================================================================================

1. Call Duration Distribution:
   - 33.4% of calls are under 3 minutes
   - 50.0% of calls are over 5 minutes
   - 26.3% of calls exceed 10 minutes

2. Distribution Shape:
   - Positively skewed (right-skewed)
   - Not perfectly normal/Gaussian
   - Heavy-tailed distribution

3. Typical Call:
   - Median: 4.88 minutes
   - Most calls: 3-10 minutes (40.9%)

4. Outliers:
   - 7.9% of calls are unusually long
   - May require investigation

================================================================================
CONTACT & SUPPORT
================================================================================

For questions or modifications, refer to:
- Main project README: d:\Sales_calls_analysis\README.md
- EDA script: omc_duration_eda.py (well-commented)
- Insights summary: eda_insights_summary.txt

================================================================================

