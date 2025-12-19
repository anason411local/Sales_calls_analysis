"""
Additional EDA for TO_OMC_Duration Column - Minute-Based Categories
Detailed analysis with granular minute breakdowns
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Set style for beautiful plots
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Load the data
print("Loading data...")
df = pd.read_csv(r'd:\Sales_calls_analysis\input_data\mergeed_for_test.csv')

# Clean and convert TO_OMC_Duration to numeric
print("Cleaning TO_OMC_Duration column...")
df['TO_OMC_Duration_Clean'] = pd.to_numeric(df['TO_OMC_Duration'], errors='coerce')

# Convert to minutes
df['Duration_Minutes'] = df['TO_OMC_Duration_Clean'] / 60

# Remove NaN values for analysis
duration_minutes = df['Duration_Minutes'].dropna()

print(f"\nTotal valid records: {len(duration_minutes)}")
print(f"Duration range: {duration_minutes.min():.2f} to {duration_minutes.max():.2f} minutes")

# Create granular minute categories
def categorize_minutes(minutes):
    if pd.isna(minutes):
        return 'Unknown'
    elif minutes < 1:
        return '<1 min'
    elif minutes < 1.5:
        return '<1.5 min'
    elif minutes < 2:
        return '<2 min'
    elif minutes < 2.5:
        return '<2.5 min'
    elif minutes < 3:
        return '<3 min'
    elif minutes < 3.5:
        return '<3.5 min'
    elif minutes < 4:
        return '<4 min'
    elif minutes < 4.5:
        return '<4.5 min'
    elif minutes < 5:
        return '<5 min'
    else:
        return '>5 min'

df['Minute_Category'] = df['Duration_Minutes'].apply(categorize_minutes)

# Get category counts
category_order = ['<1 min', '<1.5 min', '<2 min', '<2.5 min', '<3 min', 
                  '<3.5 min', '<4 min', '<4.5 min', '<5 min', '>5 min']
category_counts = df['Minute_Category'].value_counts().reindex(category_order, fill_value=0)

print("\n" + "="*80)
print("MINUTE-BASED CATEGORY DISTRIBUTION")
print("="*80)
for category, count in category_counts.items():
    percentage = (count / len(duration_minutes)) * 100
    print(f"{category:15s}: {count:4d} calls ({percentage:5.1f}%)")
print("="*80)

# ============================================================================
# CREATE VISUALIZATIONS
# ============================================================================

# Figure 1: Histogram and Pie Chart - Main View
fig1 = plt.figure(figsize=(20, 10))
fig1.suptitle('OMC Call Duration - Minute-Based Category Analysis', 
              fontsize=20, fontweight='bold', y=0.995)

# Define beautiful color palette
colors = ['#FF6B6B', '#FF8E53', '#FFA07A', '#FFB347', '#FFD700',
          '#98D8C8', '#4ECDC4', '#45B7D1', '#5DADE2', '#3498DB']

# 1. Histogram - Vertical Bars
ax1 = plt.subplot(2, 2, 1)
bars = ax1.bar(range(len(category_counts)), category_counts.values, 
               color=colors, edgecolor='black', linewidth=2, alpha=0.85)

ax1.set_xticks(range(len(category_counts)))
ax1.set_xticklabels(category_counts.index, rotation=45, ha='right', fontsize=11, fontweight='bold')
ax1.set_ylabel('Number of Calls', fontsize=13, fontweight='bold')
ax1.set_xlabel('Call Duration Categories', fontsize=13, fontweight='bold')
ax1.set_title('Call Duration Distribution by Minute Categories', 
              fontsize=15, fontweight='bold', pad=15)
ax1.grid(True, alpha=0.3, axis='y', linestyle='--')

# Add value labels on bars
for i, (bar, value) in enumerate(zip(bars, category_counts.values)):
    height = bar.get_height()
    percentage = (value / len(duration_minutes)) * 100
    ax1.text(bar.get_x() + bar.get_width()/2., height + 5,
             f'{int(value)}\n({percentage:.1f}%)',
             ha='center', va='bottom', fontsize=10, fontweight='bold')

# Add total line
ax1.axhline(y=category_counts.mean(), color='red', linestyle='--', 
            linewidth=2, alpha=0.7, label=f'Average: {category_counts.mean():.0f} calls')
ax1.legend(fontsize=11, loc='upper right')

# 2. Pie Chart - Percentage Distribution
ax2 = plt.subplot(2, 2, 2)
wedges, texts, autotexts = ax2.pie(category_counts.values, 
                                     labels=category_counts.index,
                                     autopct='%1.1f%%',
                                     startangle=90,
                                     colors=colors,
                                     explode=[0.05]*len(category_counts),
                                     shadow=True,
                                     textprops={'fontsize': 10, 'fontweight': 'bold'})

for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
    autotext.set_fontsize(11)

for text in texts:
    text.set_fontsize(10)
    text.set_fontweight('bold')

ax2.set_title('Call Duration - Percentage Distribution by Minutes', 
              fontsize=15, fontweight='bold', pad=15)

# 3. Horizontal Bar Chart (easier to read labels)
ax3 = plt.subplot(2, 2, 3)
y_pos = np.arange(len(category_counts))
bars_h = ax3.barh(y_pos, category_counts.values, color=colors, 
                   edgecolor='black', linewidth=2, alpha=0.85)

ax3.set_yticks(y_pos)
ax3.set_yticklabels(category_counts.index, fontsize=11, fontweight='bold')
ax3.set_xlabel('Number of Calls', fontsize=13, fontweight='bold')
ax3.set_title('Call Duration Categories - Horizontal View', 
              fontsize=15, fontweight='bold', pad=15)
ax3.grid(True, alpha=0.3, axis='x', linestyle='--')

# Add value labels on horizontal bars
for i, (bar, value) in enumerate(zip(bars_h, category_counts.values)):
    width = bar.get_width()
    percentage = (value / len(duration_minutes)) * 100
    ax3.text(width + 10, bar.get_y() + bar.get_height()/2.,
             f'{int(value)} ({percentage:.1f}%)',
             ha='left', va='center', fontsize=10, fontweight='bold')

# 4. Cumulative Distribution
ax4 = plt.subplot(2, 2, 4)
cumulative_counts = category_counts.cumsum()
cumulative_pct = (cumulative_counts / len(duration_minutes)) * 100

bars_cum = ax4.bar(range(len(cumulative_counts)), cumulative_counts.values,
                    color=colors, edgecolor='black', linewidth=2, alpha=0.7)

# Add line plot overlay
ax4_twin = ax4.twinx()
line = ax4_twin.plot(range(len(cumulative_pct)), cumulative_pct.values, 
                      color='red', marker='o', linewidth=3, markersize=8,
                      label='Cumulative %')

ax4.set_xticks(range(len(cumulative_counts)))
ax4.set_xticklabels(cumulative_counts.index, rotation=45, ha='right', 
                     fontsize=10, fontweight='bold')
ax4.set_ylabel('Cumulative Number of Calls', fontsize=12, fontweight='bold', color='steelblue')
ax4_twin.set_ylabel('Cumulative Percentage (%)', fontsize=12, fontweight='bold', color='red')
ax4.set_xlabel('Call Duration Categories', fontsize=13, fontweight='bold')
ax4.set_title('Cumulative Distribution by Minute Categories', 
              fontsize=15, fontweight='bold', pad=15)
ax4.grid(True, alpha=0.3, axis='y', linestyle='--')

# Add percentage labels on line
for i, (x, y) in enumerate(zip(range(len(cumulative_pct)), cumulative_pct.values)):
    ax4_twin.text(x, y + 2, f'{y:.1f}%', ha='center', va='bottom', 
                  fontsize=9, fontweight='bold', color='darkred')

ax4_twin.legend(loc='upper left', fontsize=11)

plt.tight_layout()
fig1.savefig(r'd:\Sales_calls_analysis\EDA Scripts\omc_duration_minutes_categories.png', 
            dpi=300, bbox_inches='tight')
plt.close(fig1)
print("\n[SUCCESS] Main minute-based categories plot saved: omc_duration_minutes_categories.png")

# ============================================================================
# Figure 2: Detailed Analysis
# ============================================================================

fig2 = plt.figure(figsize=(20, 10))
fig2.suptitle('OMC Call Duration - Detailed Minute-Based Analysis', 
              fontsize=20, fontweight='bold', y=0.995)

# 1. Stacked Percentage Bar
ax1 = plt.subplot(2, 2, 1)
percentages = (category_counts.values / len(duration_minutes)) * 100
bottom = 0
for i, (category, pct) in enumerate(zip(category_counts.index, percentages)):
    ax1.bar(0, pct, bottom=bottom, color=colors[i], 
            edgecolor='black', linewidth=2, label=category, width=0.6)
    # Add label in the middle of each segment
    ax1.text(0, bottom + pct/2, f'{category}\n{pct:.1f}%', 
             ha='center', va='center', fontsize=10, fontweight='bold', color='white')
    bottom += pct

ax1.set_xlim(-0.5, 0.5)
ax1.set_ylim(0, 100)
ax1.set_ylabel('Percentage (%)', fontsize=13, fontweight='bold')
ax1.set_title('Stacked Percentage Distribution', fontsize=15, fontweight='bold', pad=15)
ax1.set_xticks([])
ax1.grid(True, alpha=0.3, axis='y', linestyle='--')

# 2. Donut Chart
ax2 = plt.subplot(2, 2, 2)
wedges, texts, autotexts = ax2.pie(category_counts.values,
                                     labels=category_counts.index,
                                     autopct='%1.1f%%',
                                     startangle=90,
                                     colors=colors,
                                     pctdistance=0.85,
                                     textprops={'fontsize': 9, 'fontweight': 'bold'})

# Draw circle in center for donut effect
centre_circle = plt.Circle((0, 0), 0.70, fc='white')
ax2.add_artist(centre_circle)

# Add center text
ax2.text(0, 0, f'Total Calls\n{len(duration_minutes):,}', 
         ha='center', va='center', fontsize=16, fontweight='bold')

for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
    autotext.set_fontsize(10)

for text in texts:
    text.set_fontsize(9)
    text.set_fontweight('bold')

ax2.set_title('Donut Chart - Call Duration Distribution', 
              fontsize=15, fontweight='bold', pad=15)

# 3. Comparison Table
ax3 = plt.subplot(2, 2, 3)
ax3.axis('off')

table_data = [['Category', 'Count', 'Percentage', 'Cumulative %']]
cumulative = 0
for category, count in category_counts.items():
    pct = (count / len(duration_minutes)) * 100
    cumulative += pct
    table_data.append([
        category,
        f'{int(count):,}',
        f'{pct:.1f}%',
        f'{cumulative:.1f}%'
    ])

table = ax3.table(cellText=table_data, cellLoc='center', loc='center',
                  colWidths=[0.25, 0.25, 0.25, 0.25])
table.auto_set_font_size(False)
table.set_fontsize(11)
table.scale(1, 3)

# Style the header
for i in range(4):
    table[(0, i)].set_facecolor('#3498DB')
    table[(0, i)].set_text_props(weight='bold', color='white', fontsize=12)

# Alternate row colors and highlight >5 min
for i in range(1, len(table_data)):
    for j in range(4):
        if i % 2 == 0:
            table[(i, j)].set_facecolor('#F0F0F0')
        if table_data[i][0] == '>5 min':
            table[(i, j)].set_facecolor('#FFE5E5')
        table[(i, j)].set_text_props(fontsize=10, fontweight='bold')

ax3.set_title('Detailed Statistics Table', fontsize=15, fontweight='bold', pad=20)

# 4. Grouped Analysis
ax4 = plt.subplot(2, 2, 4)

# Group into broader categories for comparison
under_3_min = category_counts[['<1 min', '<1.5 min', '<2 min', '<2.5 min', '<3 min']].sum()
three_to_5_min = category_counts[['<3.5 min', '<4 min', '<4.5 min', '<5 min']].sum()
over_5_min = category_counts[['>5 min']].sum()

grouped_data = {
    'Under 3 Minutes': under_3_min,
    '3 to 5 Minutes': three_to_5_min,
    'Over 5 Minutes': over_5_min
}

grouped_colors = ['#FF6B6B', '#FFD700', '#4ECDC4']
bars_grouped = ax4.bar(grouped_data.keys(), grouped_data.values(),
                        color=grouped_colors, edgecolor='black', 
                        linewidth=2.5, alpha=0.85, width=0.6)

ax4.set_ylabel('Number of Calls', fontsize=13, fontweight='bold')
ax4.set_xlabel('Duration Groups', fontsize=13, fontweight='bold')
ax4.set_title('Grouped Duration Analysis', fontsize=15, fontweight='bold', pad=15)
ax4.grid(True, alpha=0.3, axis='y', linestyle='--')

# Add value labels
for bar, (key, value) in zip(bars_grouped, grouped_data.items()):
    height = bar.get_height()
    percentage = (value / len(duration_minutes)) * 100
    ax4.text(bar.get_x() + bar.get_width()/2., height + 10,
             f'{int(value)} calls\n({percentage:.1f}%)',
             ha='center', va='bottom', fontsize=12, fontweight='bold')

plt.tight_layout()
fig2.savefig(r'd:\Sales_calls_analysis\EDA Scripts\omc_duration_minutes_detailed.png', 
            dpi=300, bbox_inches='tight')
plt.close(fig2)
print("[SUCCESS] Detailed minute-based analysis plot saved: omc_duration_minutes_detailed.png")

# ============================================================================
# Figure 3: Large Standalone Charts
# ============================================================================

# Large Histogram
fig3, ax = plt.subplots(figsize=(16, 10))
bars = ax.bar(range(len(category_counts)), category_counts.values, 
              color=colors, edgecolor='black', linewidth=2.5, alpha=0.9)

ax.set_xticks(range(len(category_counts)))
ax.set_xticklabels(category_counts.index, rotation=0, ha='center', 
                    fontsize=14, fontweight='bold')
ax.set_ylabel('Number of Calls', fontsize=16, fontweight='bold')
ax.set_xlabel('Call Duration Categories (Minutes)', fontsize=16, fontweight='bold')
ax.set_title('OMC Call Duration Distribution - Minute-Based Categories\n(Histogram)', 
             fontsize=20, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3, axis='y', linestyle='--', linewidth=1.5)

# Add value labels on bars
for i, (bar, value) in enumerate(zip(bars, category_counts.values)):
    height = bar.get_height()
    percentage = (value / len(duration_minutes)) * 100
    ax.text(bar.get_x() + bar.get_width()/2., height + 8,
            f'{int(value)} calls',
            ha='center', va='bottom', fontsize=13, fontweight='bold')
    ax.text(bar.get_x() + bar.get_width()/2., height/2,
            f'{percentage:.1f}%',
            ha='center', va='center', fontsize=12, fontweight='bold', 
            color='white', bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))

# Add statistics box
stats_text = f'Total Calls: {len(duration_minutes):,}\n'
stats_text += f'Mean: {duration_minutes.mean():.2f} min\n'
stats_text += f'Median: {duration_minutes.median():.2f} min\n'
stats_text += f'Std Dev: {duration_minutes.std():.2f} min'
ax.text(0.98, 0.97, stats_text, transform=ax.transAxes,
        fontsize=13, verticalalignment='top', horizontalalignment='right',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
        fontweight='bold')

plt.tight_layout()
fig3.savefig(r'd:\Sales_calls_analysis\EDA Scripts\omc_duration_minutes_histogram_large.png', 
            dpi=300, bbox_inches='tight')
plt.close(fig3)
print("[SUCCESS] Large histogram saved: omc_duration_minutes_histogram_large.png")

# Large Pie Chart
fig4, ax = plt.subplots(figsize=(14, 14))
wedges, texts, autotexts = ax.pie(category_counts.values,
                                    labels=category_counts.index,
                                    autopct='%1.1f%%',
                                    startangle=90,
                                    colors=colors,
                                    explode=[0.08]*len(category_counts),
                                    shadow=True,
                                    textprops={'fontsize': 13, 'fontweight': 'bold'})

for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
    autotext.set_fontsize(14)

for text in texts:
    text.set_fontsize(13)
    text.set_fontweight('bold')

ax.set_title('OMC Call Duration Distribution - Minute-Based Categories\n(Pie Chart)', 
             fontsize=22, fontweight='bold', pad=30)

# Add legend with counts
legend_labels = [f'{cat}: {count} calls' for cat, count in category_counts.items()]
ax.legend(legend_labels, loc='center left', bbox_to_anchor=(1, 0, 0.5, 1),
          fontsize=12, title='Categories', title_fontsize=14)

plt.tight_layout()
fig4.savefig(r'd:\Sales_calls_analysis\EDA Scripts\omc_duration_minutes_piechart_large.png', 
            dpi=300, bbox_inches='tight')
plt.close(fig4)
print("[SUCCESS] Large pie chart saved: omc_duration_minutes_piechart_large.png")

print("\n" + "="*80)
print("MINUTE-BASED EDA COMPLETE!")
print("="*80)
print("\nGenerated Files:")
print("1. omc_duration_minutes_categories.png - Main 4-panel view")
print("2. omc_duration_minutes_detailed.png - Detailed analysis with table")
print("3. omc_duration_minutes_histogram_large.png - Large standalone histogram")
print("4. omc_duration_minutes_piechart_large.png - Large standalone pie chart")
print("\nAll plots saved in: d:\\Sales_calls_analysis\\EDA Scripts\\")
print("="*80)

