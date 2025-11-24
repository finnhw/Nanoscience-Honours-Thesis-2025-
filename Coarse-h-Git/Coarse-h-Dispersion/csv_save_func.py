import os
import numpy as np
import pandas as pd

# For wguide_data (electromagnetic pump modes)
def save_em_pump_to_csv(sim_EM_pump, folder):
    os.makedirs(folder, exist_ok=True)
    # Extract relevant data
    kz_values = np.real(sim_EM_pump.kz_EM_all())
    neff_values = np.real(sim_EM_pump.neff_all())
    
    # Create DataFrame
    em_pump_df = pd.DataFrame({
        'Mode_Index': np.arange(len(kz_values)),
        'kz_EM (1/m)': kz_values,
        'n_eff': neff_values
    })

    # CSV file path
    filename = 'wguide_data_pump.csv'
    file_path_save = os.path.join(folder, filename)
    
    # Save
    em_pump_df.to_csv(file_path_save, index=False)
    
    #npz_filename = 'wguide_data.npz'
    #npz_path = os.path.join(folder, npz_filename)
    #np.savez(npz_path, sim_EM_pump=sim_EM_pump)
    
    print(f"Saved EM pump data to {file_path_save}")

def save_em_stokes_to_csv(sim_EM_Stokes, folder):
    os.makedirs(folder, exist_ok=True)
    # Extract relevant data
    kz_values = np.real(sim_EM_Stokes.kz_EM_all())
    neff_values = np.real(sim_EM_Stokes.neff_all())
    
    # Create DataFrame
    em_stokes_df = pd.DataFrame({
        'Mode_Index': np.arange(len(kz_values)),
        'kz_EM_Stokes (1/m)': kz_values,
        'n_eff_Stokes': neff_values
    })
    
    # CSV file path
    filename = 'wguide_data_stokes.csv'
    file_path_save = os.path.join(folder, filename)
    
    # Save to CSV
    em_stokes_df.to_csv(file_path_save, index=False)
    print(f"Saved EM Stokes data to {file_path_save}")
    
    # Save simulation object using numpy with specific filename
    #npz_filename = 'wguide_data2.npz'
    #npz_path = os.path.join(folder, npz_filename)
    #np.savez(npz_path, sim_EM_Stokes=sim_EM_Stokes)
    
    #print(f"Saved EM Stokes simulation object to {npz_path}")

def save_ac_to_csv(sim_AC, gain, folder):
    os.makedirs(folder, exist_ok=True)
    # Extract relevant data
    frequencies = np.real(sim_AC.nu_AC_all()) * 1e-9  # Convert to GHz
    
    # Create a dataframe with mode frequencies
    ac_df = pd.DataFrame({
        'Mode_Index': np.arange(len(frequencies)),
        'Frequency (GHz)': frequencies
    })
    
    # Add gain data if available
    if gain is not None:
        ac_df['G_total (1/mW)'] = [gain.gain_total(m) for m in range(len(frequencies))]
        ac_df['G_PE (1/mW)'] = [gain.gain_PE(m) for m in range(len(frequencies))]
        ac_df['G_MB (1/mW)'] = [gain.gain_MB(m) for m in range(len(frequencies))]
    
    # CSV file path
    filename = 'wguide_data_ac.csv'
    file_path_save = os.path.join(folder, filename)
    
    # Save to CSV
    ac_df.to_csv(file_path_save, index=False)
    print(f"Saved AC data to {file_path_save}")
    
    # Note: No npz file saving for this function as not specified in requirements

def save_masked_to_csv(masked_PE, masked_MB, masked_tot, folder):
    os.makedirs(folder, exist_ok=True)
    ## Data entered into this def should naturally be arrays 
    masked_df = pd.DataFrame({
        'AC_Mode': np.arange(len(masked_PE)),  # Create sequence from 0 to len-1
        'Photoelastic (PE)': masked_PE,
        'Moving boundary(MB)': masked_MB,
        'Total': masked_tot
    })
    
    # CSV file path
    filename = 'masked_data.csv'
    file_path_save = os.path.join(folder, filename)
    
    # Save to CSV
    masked_df.to_csv(file_path_save, index=False)
    
    # Save arrays using numpy
    #npz_filename = 'masked_data.npz'
    #npz_path = os.path.join(folder, npz_filename)
    #np.savez(npz_path, masked_PE=masked_PE, masked_MB=masked_MB, masked_tot=masked_tot)
    
    print(f"Saved masked data to {file_path_save}")
    #print(f"Saved masked arrays to {npz_path}")
