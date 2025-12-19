"""
Comprehensive EDA for TO_OMC_Duration Column
Analyzing call duration distribution for OMC Department calls
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import norm, skew, kurtosis
import warnings
warnings.filterwarnings('ignore')

# Set style for beautiful plots
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Load the data
print("Loading data...")
df = pd.read_csv(r'd:\Sales_calls_analysis\input_data\mergeed_for_test.csv')

print(f"Total records: {len(df)}")
print(f"Columns: {len(df.columns)}")

# Clean and convert TO_OMC_Duration to numeric
print("\nCleaning TO_OMC_Duration column...")
# Replace non-numeric values with NaN
df['TO_OMC_Duration_Clean'] = pd.to_numeric(df['TO_OMC_Duration'], errors='coerce')

# Remove NaN values for analysis
duration_data = df['TO_OMC_Duration_Clean'].dropna()

print(f"\nOriginal records: {len(df)}")
print(f"Valid numeric duration records: {len(duration_data)}")
print(f"Invalid/Missing records: {len(df) - len(duration_data)}")

# Statistical Summary
print("\n" + "="*80)
print("STATISTICAL SUMMARY - TO_OMC_Duration (in seconds)")
print("="*80)
print(f"Count:           {len(duration_data):,}")
print(f"Mean:            {duration_data.mean():.2f} seconds ({duration_data.mean()/60:.2f} minutes)")
print(f"Median:          {duration_data.median():.2f} seconds ({duration_data.median()/60:.2f} minutes)")
print(f"Mode:            {duration_data.mode()[0]:.2f} seconds")
print(f"Std Deviation:   {duration_data.std():.2f} seconds")
print(f"Variance:        {duration_data.var():.2f}")
print(f"Min:             {duration_data.min():.2f} seconds ({duration_data.min()/60:.2f} minutes)")
print(f"Max:             {duration_data.max():.2f} seconds ({duration_data.max()/60:.2f} minutes)")
print(f"Range:           {duration_data.max() - duration_data.min():.2f} seconds")
print(f"Q1 (25%):        {duration_data.quantile(0.25):.2f} seconds")
print(f"Q2 (50%):        {duration_data.quantile(0.50):.2f} seconds")
print(f"Q3 (75%):        {duration_data.quantile(0.75):.2f} seconds")
print(f"IQR:             {duration_data.quantile(0.75) - duration_data.quantile(0.25):.2f} seconds")
print(f"Skewness:        {skew(duration_data):.4f}")
print(f"Kurtosis:        {kurtosis(duration_data):.4f}")

# Percentiles
print(f"\n90th Percentile: {duration_data.quantile(0.90):.2f} seconds ({duration_data.quantile(0.90)/60:.2f} minutes)")
print(f"95th Percentile: {duration_data.quantile(0.95):.2f} seconds ({duration_data.quantile(0.95)/60:.2f} minutes)")
print(f"99th Percentile: {duration_data.quantile(0.99):.2f} seconds ({duration_data.quantile(0.99)/60:.2f} minutes)")

# Create comprehensive visualization
fig = plt.figure(figsize=(20, 12))
fig.suptitle('OMC Call Duration Analysis - Comprehensive EDA', 
             fontsize=20, fontweight='bold', y=0.995)

# 1. Histogram with Gaussian (Normal) Distribution Overlay
ax1 = plt.subplot(2, 3, 1)
n, bins, patches = ax1.hist(duration_data, bins=50, density=True, alpha=0.7, 
                             color='steelblue', edgecolor='black', linewidth=1.2)

# Fit a normal distribution
mu, sigma = duration_data.mean(), duration_data.std()
x = np.linspace(duration_data.min(), duration_data.max(), 100)
ax1.plot(x, norm.pdf(x, mu, sigma), 'r-', linewidth=2.5, 
         label=f'Normal Distribution\nμ={mu:.1f}s, σ={sigma:.1f}s')

ax1.set_xlabel('Call Duration (seconds)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Probability Density', fontsize=12, fontweight='bold')
ax1.set_title('Histogram with Gaussian Distribution Overlay', fontsize=14, fontweight='bold', pad=10)
ax1.legend(loc='upper right', fontsize=10)
ax1.grid(True, alpha=0.3, linestyle='--')
ax1.axvline(mu, color='red', linestyle='--', linewidth=2, alpha=0.7, label=f'Mean: {mu:.1f}s')

# 2. Histogram with Frequency Count
ax2 = plt.subplot(2, 3, 2)
counts, bins, patches = ax2.hist(duration_data, bins=50, color='teal', 
                                  edgecolor='black', linewidth=1.2, alpha=0.8)

# Color the bars by height
cm = plt.cm.viridis
norm_colors = plt.Normalize(vmin=counts.min(), vmax=counts.max())
for count, patch in zip(counts, patches):
    patch.set_facecolor(cm(norm_colors(count)))

ax2.set_xlabel('Call Duration (seconds)', fontsize=12, fontweight='bold')
ax2.set_ylabel('Frequency', fontsize=12, fontweight='bold')
ax2.set_title('Call Duration Distribution - Frequency Histogram', fontsize=14, fontweight='bold', pad=10)
ax2.axvline(duration_data.mean(), color='red', linestyle='--', linewidth=2, 
            label=f'Mean: {duration_data.mean():.1f}s')
ax2.axvline(duration_data.median(), color='orange', linestyle='--', linewidth=2, 
            label=f'Median: {duration_data.median():.1f}s')
ax2.legend(loc='upper right', fontsize=10)
ax2.grid(True, alpha=0.3, linestyle='--')

# 3. Box Plot with Violin Plot
ax3 = plt.subplot(2, 3, 3)
parts = ax3.violinplot([duration_data], positions=[1], widths=0.7, 
                        showmeans=True, showmedians=True)
for pc in parts['bodies']:
    pc.set_facecolor('lightblue')
    pc.set_alpha(0.7)

bp = ax3.boxplot([duration_data], positions=[1], widths=0.3, patch_artist=True,
                  boxprops=dict(facecolor='lightcoral', alpha=0.7),
                  medianprops=dict(color='darkred', linewidth=2),
                  meanprops=dict(marker='D', markerfacecolor='green', markersize=8))

ax3.set_ylabel('Call Duration (seconds)', fontsize=12, fontweight='bold')
ax3.set_title('Box Plot with Violin Plot Overlay', fontsize=14, fontweight='bold', pad=10)
ax3.set_xticks([1])
ax3.set_xticklabels(['OMC Calls'])
ax3.grid(True, alpha=0.3, linestyle='--', axis='y')

# Add statistical annotations
textstr = f'Mean: {duration_data.mean():.1f}s\nMedian: {duration_data.median():.1f}s\nStd: {duration_data.std():.1f}s'
ax3.text(1.35, duration_data.max()*0.9, textstr, fontsize=10, 
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# 4. Q-Q Plot (Quantile-Quantile Plot)
ax4 = plt.subplot(2, 3, 4)
stats.probplot(duration_data, dist="norm", plot=ax4)
ax4.set_title('Q-Q Plot - Normality Test', fontsize=14, fontweight='bold', pad=10)
ax4.set_xlabel('Theoretical Quantiles', fontsize=12, fontweight='bold')
ax4.set_ylabel('Sample Quantiles', fontsize=12, fontweight='bold')
ax4.grid(True, alpha=0.3, linestyle='--')

# 5. Cumulative Distribution Function (CDF)
ax5 = plt.subplot(2, 3, 5)
sorted_data = np.sort(duration_data)
cumulative = np.arange(1, len(sorted_data) + 1) / len(sorted_data)
ax5.plot(sorted_data, cumulative, linewidth=2.5, color='darkgreen')
ax5.fill_between(sorted_data, cumulative, alpha=0.3, color='lightgreen')
ax5.set_xlabel('Call Duration (seconds)', fontsize=12, fontweight='bold')
ax5.set_ylabel('Cumulative Probability', fontsize=12, fontweight='bold')
ax5.set_title('Cumulative Distribution Function (CDF)', fontsize=14, fontweight='bold', pad=10)
ax5.grid(True, alpha=0.3, linestyle='--')

# Add percentile lines
for percentile in [0.25, 0.5, 0.75, 0.9]:
    value = duration_data.quantile(percentile)
    ax5.axvline(value, color='red', linestyle='--', alpha=0.5, linewidth=1)
    ax5.text(value, percentile, f'{int(percentile*100)}%', fontsize=9, 
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))

# 6. Duration in Minutes - Histogram
ax6 = plt.subplot(2, 3, 6)
duration_minutes = duration_data / 60
ax6.hist(duration_minutes, bins=40, color='purple', alpha=0.7, 
         edgecolor='black', linewidth=1.2)
ax6.set_xlabel('Call Duration (minutes)', fontsize=12, fontweight='bold')
ax6.set_ylabel('Frequency', fontsize=12, fontweight='bold')
ax6.set_title('Call Duration Distribution (in Minutes)', fontsize=14, fontweight='bold', pad=10)
ax6.axvline(duration_minutes.mean(), color='red', linestyle='--', linewidth=2, 
            label=f'Mean: {duration_minutes.mean():.2f} min')
ax6.axvline(duration_minutes.median(), color='orange', linestyle='--', linewidth=2, 
            label=f'Median: {duration_minutes.median():.2f} min')
ax6.legend(loc='upper right', fontsize=10)
ax6.grid(True, alpha=0.3, linestyle='--')

plt.tight_layout()
fig.savefig(r'd:\Sales_calls_analysis\EDA Scripts\omc_duration_comprehensive_eda.png', 
            dpi=300, bbox_inches='tight')
plt.close(fig)
print("\n[SUCCESS] Comprehensive EDA plot saved: omc_duration_comprehensive_eda.png")

# ============================================================================
# ADDITIONAL DETAILED PLOTS
# ============================================================================

# Figure 2: Detailed Gaussian Analysis
fig2 = plt.figure(figsize=(18, 10))
fig2.suptitle('OMC Call Duration - Detailed Gaussian Distribution Analysis', 
              fontsize=18, fontweight='bold', y=0.995)

# 1. Histogram with Multiple Distribution Fits
ax1 = plt.subplot(2, 2, 1)
ax1.hist(duration_data, bins=60, density=True, alpha=0.6, color='skyblue', 
         edgecolor='black', linewidth=1)

# Fit normal distribution
mu, sigma = duration_data.mean(), duration_data.std()
x = np.linspace(duration_data.min(), duration_data.max(), 200)
ax1.plot(x, norm.pdf(x, mu, sigma), 'r-', linewidth=3, 
         label=f'Normal: μ={mu:.1f}, σ={sigma:.1f}')

ax1.set_xlabel('Call Duration (seconds)', fontsize=11, fontweight='bold')
ax1.set_ylabel('Probability Density', fontsize=11, fontweight='bold')
ax1.set_title('Gaussian Distribution Fit', fontsize=13, fontweight='bold')
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3)

# 2. Standardized (Z-Score) Distribution
ax2 = plt.subplot(2, 2, 2)
z_scores = (duration_data - mu) / sigma
ax2.hist(z_scores, bins=50, density=True, alpha=0.6, color='lightcoral', 
         edgecolor='black', linewidth=1)

# Standard normal distribution
x_std = np.linspace(-4, 4, 200)
ax2.plot(x_std, norm.pdf(x_std, 0, 1), 'b-', linewidth=3, 
         label='Standard Normal (μ=0, σ=1)')

ax2.set_xlabel('Z-Score (Standardized)', fontsize=11, fontweight='bold')
ax2.set_ylabel('Probability Density', fontsize=11, fontweight='bold')
ax2.set_title('Standardized Distribution (Z-Scores)', fontsize=13, fontweight='bold')
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3)
ax2.axvline(0, color='red', linestyle='--', linewidth=2, alpha=0.5)

# 3. Residuals from Normal Distribution
ax3 = plt.subplot(2, 2, 3)
sorted_data = np.sort(duration_data)
theoretical_quantiles = norm.ppf(np.linspace(0.01, 0.99, len(sorted_data)), mu, sigma)
residuals = sorted_data - theoretical_quantiles

ax3.scatter(theoretical_quantiles, residuals, alpha=0.5, s=20, color='green')
ax3.axhline(0, color='red', linestyle='--', linewidth=2)
ax3.set_xlabel('Theoretical Quantiles', fontsize=11, fontweight='bold')
ax3.set_ylabel('Residuals', fontsize=11, fontweight='bold')
ax3.set_title('Residuals from Normal Distribution', fontsize=13, fontweight='bold')
ax3.grid(True, alpha=0.3)

# 4. Kernel Density Estimation (KDE) with Histogram
ax4 = plt.subplot(2, 2, 4)
ax4.hist(duration_data, bins=50, density=True, alpha=0.5, color='lightgreen', 
         edgecolor='black', linewidth=1, label='Histogram')

# KDE plot
from scipy.stats import gaussian_kde
kde = gaussian_kde(duration_data)
x_kde = np.linspace(duration_data.min(), duration_data.max(), 200)
ax4.plot(x_kde, kde(x_kde), 'b-', linewidth=3, label='KDE (Kernel Density)')

# Normal distribution
ax4.plot(x, norm.pdf(x, mu, sigma), 'r--', linewidth=2.5, 
         label='Normal Distribution')

ax4.set_xlabel('Call Duration (seconds)', fontsize=11, fontweight='bold')
ax4.set_ylabel('Density', fontsize=11, fontweight='bold')
ax4.set_title('Histogram vs KDE vs Normal Distribution', fontsize=13, fontweight='bold')
ax4.legend(fontsize=9)
ax4.grid(True, alpha=0.3)

plt.tight_layout()
fig2.savefig(r'd:\Sales_calls_analysis\EDA Scripts\omc_duration_gaussian_analysis.png', 
            dpi=300, bbox_inches='tight')
plt.close(fig2)
print("[SUCCESS] Gaussian analysis plot saved: omc_duration_gaussian_analysis.png")

# ============================================================================
# ADDITIONAL INSIGHTS PLOTS
# ============================================================================

# Figure 3: Duration Categories and Insights
fig3 = plt.figure(figsize=(18, 10))
fig3.suptitle('OMC Call Duration - Category Analysis & Insights', 
              fontsize=18, fontweight='bold', y=0.995)

# Create duration categories
def categorize_duration(seconds):
    if seconds < 60:
        return 'Very Short (<1 min)'
    elif seconds < 180:
        return 'Short (1-3 min)'
    elif seconds < 300:
        return 'Medium (3-5 min)'
    elif seconds < 600:
        return 'Long (5-10 min)'
    else:
        return 'Very Long (>10 min)'

df['Duration_Category'] = df['TO_OMC_Duration_Clean'].apply(categorize_duration)
category_counts = df['Duration_Category'].value_counts()

# 1. Bar Chart - Duration Categories
ax1 = plt.subplot(2, 2, 1)
categories_order = ['Very Short (<1 min)', 'Short (1-3 min)', 'Medium (3-5 min)', 
                    'Long (5-10 min)', 'Very Long (>10 min)']
category_counts_ordered = category_counts.reindex(categories_order, fill_value=0)
bars = ax1.bar(range(len(category_counts_ordered)), category_counts_ordered.values, 
               color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8'],
               edgecolor='black', linewidth=1.5)

ax1.set_xticks(range(len(category_counts_ordered)))
ax1.set_xticklabels(category_counts_ordered.index, rotation=45, ha='right', fontsize=9)
ax1.set_ylabel('Number of Calls', fontsize=11, fontweight='bold')
ax1.set_title('Call Duration Categories Distribution', fontsize=13, fontweight='bold')
ax1.grid(True, alpha=0.3, axis='y')

# Add value labels on bars
for i, (bar, value) in enumerate(zip(bars, category_counts_ordered.values)):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
             f'{int(value)}\n({value/len(duration_data)*100:.1f}%)',
             ha='center', va='bottom', fontsize=9, fontweight='bold')

# 2. Pie Chart - Duration Categories
ax2 = plt.subplot(2, 2, 2)
colors_pie = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
wedges, texts, autotexts = ax2.pie(category_counts_ordered.values, 
                                     labels=category_counts_ordered.index,
                                     autopct='%1.1f%%', startangle=90,
                                     colors=colors_pie,
                                     explode=[0.05]*len(category_counts_ordered),
                                     shadow=True)

for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
    autotext.set_fontsize(10)

for text in texts:
    text.set_fontsize(9)
    text.set_fontweight('bold')

ax2.set_title('Call Duration Categories - Percentage Distribution', 
              fontsize=13, fontweight='bold')

# 3. Histogram with Outliers Highlighted
ax3 = plt.subplot(2, 2, 3)
Q1 = duration_data.quantile(0.25)
Q3 = duration_data.quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

# Normal data
normal_data = duration_data[(duration_data >= lower_bound) & (duration_data <= upper_bound)]
outliers = duration_data[(duration_data < lower_bound) | (duration_data > upper_bound)]

ax3.hist(normal_data, bins=50, color='steelblue', alpha=0.7, 
         edgecolor='black', linewidth=1, label=f'Normal Data (n={len(normal_data)})')
ax3.hist(outliers, bins=20, color='red', alpha=0.7, 
         edgecolor='black', linewidth=1, label=f'Outliers (n={len(outliers)})')

ax3.set_xlabel('Call Duration (seconds)', fontsize=11, fontweight='bold')
ax3.set_ylabel('Frequency', fontsize=11, fontweight='bold')
ax3.set_title('Distribution with Outliers Highlighted', fontsize=13, fontweight='bold')
ax3.legend(fontsize=10)
ax3.grid(True, alpha=0.3)

# 4. Summary Statistics Table
ax4 = plt.subplot(2, 2, 4)
ax4.axis('off')

stats_data = [
    ['Metric', 'Value'],
    ['Total Calls', f'{len(duration_data):,}'],
    ['Mean Duration', f'{duration_data.mean():.1f}s ({duration_data.mean()/60:.2f} min)'],
    ['Median Duration', f'{duration_data.median():.1f}s ({duration_data.median()/60:.2f} min)'],
    ['Std Deviation', f'{duration_data.std():.1f}s'],
    ['Min Duration', f'{duration_data.min():.1f}s ({duration_data.min()/60:.2f} min)'],
    ['Max Duration', f'{duration_data.max():.1f}s ({duration_data.max()/60:.2f} min)'],
    ['25th Percentile', f'{Q1:.1f}s'],
    ['75th Percentile', f'{Q3:.1f}s'],
    ['IQR', f'{IQR:.1f}s'],
    ['Outliers Count', f'{len(outliers)} ({len(outliers)/len(duration_data)*100:.1f}%)'],
    ['Skewness', f'{skew(duration_data):.4f}'],
    ['Kurtosis', f'{kurtosis(duration_data):.4f}'],
]

table = ax4.table(cellText=stats_data, cellLoc='left', loc='center',
                  colWidths=[0.5, 0.5])
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 2.5)

# Style the header
for i in range(2):
    table[(0, i)].set_facecolor('#4ECDC4')
    table[(0, i)].set_text_props(weight='bold', color='white')

# Alternate row colors
for i in range(1, len(stats_data)):
    for j in range(2):
        if i % 2 == 0:
            table[(i, j)].set_facecolor('#F0F0F0')
        table[(i, j)].set_text_props(fontsize=9)

ax4.set_title('Statistical Summary Table', fontsize=13, fontweight='bold', pad=20)

plt.tight_layout()
fig3.savefig(r'd:\Sales_calls_analysis\EDA Scripts\omc_duration_category_analysis.png', 
            dpi=300, bbox_inches='tight')
plt.close(fig3)
print("[SUCCESS] Category analysis plot saved: omc_duration_category_analysis.png")

print("\n" + "="*80)
print("EDA COMPLETE!")
print("="*80)
print("\nGenerated Files:")
print("1. omc_duration_comprehensive_eda.png - Main comprehensive analysis")
print("2. omc_duration_gaussian_analysis.png - Detailed Gaussian distribution analysis")
print("3. omc_duration_category_analysis.png - Category breakdown and insights")
print("\nAll plots have been saved in: d:\\Sales_calls_analysis\\EDA Scripts\\")
print("="*80)

