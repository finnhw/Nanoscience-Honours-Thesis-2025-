import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from scipy.interpolate import griddata

# Create a dictionary to store all DataFrames
dfs = {}
i_height = 50
while i_height <= 890:
    try:
        file_path = os.path.join('..', 'Coarse-h-Dispersion', f'Rib_{i_height}', 'wguide_data_ac.csv')
        
        # Load the CSV file
        df = pd.read_csv(file_path)
        
        # Replace all 0 values with NaN
        df = df.replace(0, np.nan)
        
        # Store DataFrame in dictionary with key based on height
        dfs[f'df_{i_height}'] = df
        
    except Exception as e:
        print(f"Error loading Rib_{i_height}: {e}")
    
    # Increment by 10
    i_height += 10

print(f"\nLoaded {len(dfs)} DataFrames")
print(f"Available heights: {sorted(int(k.split('_')[1]) for k in dfs.keys())}")

# Lists to store data for plotting
heights = []
frequencies = []
gains = []

# Extract data for plotting
for height_key, df in dfs.items():
    height = int(height_key.split('_')[1])
    
    try:
        freq_col = df["Frequency (GHz)"]
        gain_col = df["G_total (1/mW)"]
        
        # Changed threshold to around 1 /Wm (which is 1e-3 /mW)
        # Adjust this value based on your data distribution
        mask = gain_col > 1e-3
        
        # For each frequency that meets the criteria, add a point
        for freq, gain in zip(freq_col[mask], gain_col[mask]):
            heights.append(height)
            frequencies.append(freq)
            gains.append(gain)
        
    except KeyError as e:
        print(f"Error with DataFrame {height_key}: {e}")
        if len(df.columns) >= 3:
            print(f"Available columns: {df.columns}")

# Convert to numpy arrays for easier manipulation
heights = np.array(heights)
frequencies = np.array(frequencies)
gains = np.array(gains)

if len(gains) > 0:
    # Use logarithmic scaling instead of linear normalization
    # This preserves the relative differences better
    log_gains = np.log10(gains)
    min_log_gain = np.min(log_gains)
    max_log_gain = np.max(log_gains)
    
    # Normalize the log values to [0, 1] range
    normalized_gains = (log_gains - min_log_gain) / (max_log_gain - min_log_gain)
    
    # Alternative: If you prefer linear scaling with better contrast, use:
    # min_gain = np.min(gains)
    # max_gain = np.max(gains)
    # normalized_gains = (gains - min_gain) / (max_gain - min_gain)
    
    # Updated colormap: Dark navy (low) → purple → red → orange → yellow (high)
    colors = [(0.05, 0.05, 0.2), (0.2, 0.0, 0.4), (0.6, 0.0, 0.3), (0.9, 0.3, 0.0), (1.0, 1.0, 0.2)]
    custom_cmap = LinearSegmentedColormap.from_list('high_contrast', colors)
    
    # Create the figure with white background
    fig, ax = plt.subplots(figsize=(14, 10), facecolor='white')
    
    # Set only the plot area (axes) to black
    ax.set_facecolor('black')
    
    # Create alpha values that vary with gain (higher gain = more opaque)
    # Use a power function to make the contrast more dramatic
    alpha_values = np.power(normalized_gains, 0.5)  # Square root for smoother transition
    # Ensure minimum visibility and scale to reasonable range
    alpha_values = 0.1 + 0.9 * alpha_values  # Scale from 0.1 to 1.0
    
    # Scatter plot with variable alpha
    sc = ax.scatter(heights, frequencies, c=normalized_gains, cmap=custom_cmap,
                    alpha=alpha_values, s=25, edgecolors='none', vmin=0, vmax=1)
    
    # Grid in light grey
    ax.grid(True, linestyle='--', color='grey', alpha=0.5)
    
    # Axis labels in black (default for white background)
    ax.set_xlabel('Ge$_{11.5}$As$_{24}$Se$_{64.5}$ core thickness (nm) | Height', fontsize=16)
    ax.set_ylabel('Frequency (GHz)', fontsize=16)
    
    # Ticks and spines in black
    ax.tick_params(axis='both', colors='black', labelsize=12)
    for spine in ax.spines.values():
        spine.set_color('black')
    
    # Colorbar with normalized labeling
    cbar = plt.colorbar(sc)
    
    # Create normalized colorbar labels (0 to 1 range)
    n_ticks = 6
    tick_positions = np.linspace(0, 1, n_ticks)
    tick_labels = [f'{pos:.1f}' for pos in tick_positions]
    
    cbar.set_ticks(tick_positions)
    cbar.set_ticklabels(tick_labels)
    cbar.set_label('Normalized SBS Gain', fontsize=14, color='black')
    cbar.ax.yaxis.set_tick_params(color='black')
    plt.setp(cbar.ax.get_yticklabels(), color='black')
    
    # Optional title
    ax.set_title('Frequencies vs. Discrete Rib Heights with SBS Gain Heat Map', fontsize=16, color='black')
    
    plt.tight_layout()
    
    # Save with white background (facecolor)
    plt.savefig("Contour_Plot_Norm.png", dpi=300, bbox_inches='tight', facecolor='white')
    plt.show()
    
    # Print some statistics
    print(f"Total points plotted: {len(frequencies)}")
    print(f"Frequency range: {min(frequencies):.2f} to {max(frequencies):.2f} GHz")
    print(f"Gain range: {min(gains):.6e} to {max(gains):.6e} 1/mW")
    print(f"Log gain range: {min_log_gain:.3f} to {max_log_gain:.3f}")
    print(f"Normalized gain range: {min(normalized_gains):.6f} to {max(normalized_gains):.6f}")
    
    # Additional statistics to help understand the data distribution
    print(f"\nGain statistics:")
    print(f"Mean: {np.mean(gains):.6e}")
    print(f"Median: {np.median(gains):.6e}")
    print(f"Std: {np.std(gains):.6e}")
    
else:
    print("No data points meet the criteria.")
    print("Try lowering the threshold value.")