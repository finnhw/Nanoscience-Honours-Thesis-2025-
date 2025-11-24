import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from scipy.interpolate import griddata

# Create a dictionary to store all DataFrames
dfs = {}
i_width = 800
while i_width <= 2500:
    try:
        file_path = os.path.join(f'Rib_{i_width}', 'wguide_data_ac.csv')
        
        # Load the CSV file
        df = pd.read_csv(file_path)
        
        # Replace all 0 values with NaN
        df = df.replace(0, np.nan)
        
        # Store DataFrame in dictionary with key based on width
        dfs[f'df_{i_width}'] = df
        
    except Exception as e:
        print(f"Error loading Rib_{i_width}: {e}")
    
    # Increment by 20
    i_width += 20

print(f"\nLoaded {len(dfs)} DataFrames")
print(f"Available widths: {sorted(int(k.split('_')[1]) for k in dfs.keys())}")

# Lists to store data for plotting
widths = []
frequencies = []
gains = []

# Extract data for plotting
for width_key, df in dfs.items():
    width = int(width_key.split('_')[1])
    
    try:
        freq_col = df["Frequency (GHz)"]
        gain_col = df["G_total (1/mW)"]
        
        # Changed threshold to around 1 /Wm (which is 1e-3 /mW)
        # Adjust this value based on your data distribution
        mask = gain_col > 1e-3
        
        # For each frequency that meets the criteria, add a point
        for freq, gain in zip(freq_col[mask], gain_col[mask]):
            widths.append(width)
            frequencies.append(freq)
            gains.append(gain)
        
    except KeyError as e:
        print(f"Error with DataFrame {width_key}: {e}")
        if len(df.columns) >= 3:
            print(f"Available columns: {df.columns}")

# Convert to numpy arrays for easier manipulation
widths = np.array(widths)
frequencies = np.array(frequencies)
gains = np.array(gains)


if len(gains) > 0:
    # Use logarithmic scaling instead of linear normalization
    log_gains = np.log10(gains)
    min_log_gain = np.min(log_gains)
    max_log_gain = np.max(log_gains)
    
    # Normalize the log values to [0, 1] range
    normalized_gains = (log_gains - min_log_gain) / (max_log_gain - min_log_gain)
    
    # --- NEW FILTER: Only keep values where normalized gain >= 0.5 ---
    valid_mask = normalized_gains >= 0.5
    widths = widths[valid_mask]
    frequencies = frequencies[valid_mask]
    gains = gains[valid_mask]
    normalized_gains = normalized_gains[valid_mask]
    
    # Check if anything remains
    if len(gains) == 0:
        print("No data points with normalized gain ≥ 0.5.")
    else:
        # Updated colormap
        colors = [(0.05, 0.05, 0.2), (0.2, 0.0, 0.4), (0.6, 0.0, 0.3), (0.9, 0.3, 0.0), (1.0, 1.0, 0.2)]
        custom_cmap = LinearSegmentedColormap.from_list('high_contrast', colors)
        
        fig, ax = plt.subplots(figsize=(14, 10), facecolor='white')
        ax.set_facecolor('black')
        
        # Alpha values scaled with normalized gains
        alpha_values = np.power(normalized_gains, 0.5)
        alpha_values = 0.1 + 0.9 * alpha_values
        
        # Scatter plot (only for valid points)
        sc = ax.scatter(widths, frequencies, c=normalized_gains, cmap=custom_cmap,
                        alpha=alpha_values, s=25, edgecolors='none', vmin=0, vmax=1)
        
        ax.grid(True, linestyle='--', color='grey', alpha=0.5)
        ax.set_xlabel('Ge$_{11.5}$As$_{24}$Se$_{64.5}$ core thickness (nm) | width', fontsize=16)
        ax.set_ylabel('Frequency (GHz)', fontsize=16)
        ax.tick_params(axis='both', colors='black', labelsize=12)
        for spine in ax.spines.values():
            spine.set_color('black')
        
        cbar = plt.colorbar(sc)
        n_ticks = 6
        tick_positions = np.linspace(0, 1, n_ticks)
        tick_labels = [f'{pos:.1f}' for pos in tick_positions]
        cbar.set_ticks(tick_positions)
        cbar.set_ticklabels(tick_labels)
        cbar.set_label('Normalized SBS Gain', fontsize=14, color='black')
        plt.setp(cbar.ax.get_yticklabels(), color='black')
        
        ax.set_title('Frequencies vs. Finer Discrete Rib widths with SBS Gain Heat Map', fontsize=16, color='black')
        plt.tight_layout()
        plt.savefig("Contour_Plot_Norm_Limited.png", dpi=300, bbox_inches='tight', facecolor='white')
        plt.show()
        
        print(f"Total points plotted: {len(frequencies)}")
        print(f"Normalized gain range (after filtering): {min(normalized_gains):.6f} to {max(normalized_gains):.6f}")
else:
    print("No data points meet the criteria.")
