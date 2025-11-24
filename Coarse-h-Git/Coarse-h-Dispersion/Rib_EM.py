""" Replicating the results of
Compact Brillouin devices through hybrid integration on Silicon
Morrison et al.
https://doi.org/10.1364/OPTICA.4.000847
"""

import sys
import numpy as np
from pathlib import Path
import pandas as pd
import csv
import os
import scipy

import params
import starter
import csv_save_func

sys.path.append(str(Path('../../../../backend')))
import numbat
import materials
import modecalcs
import integration
from nbtypes import SI_GHz

# Naming conventions
# AC: acoustic
# EM: electromagnetic
# q_AC: acoustic wavenumber

# Geometric Parameters - all in nm.
wl_nm = 1550  # Wavelength of EM wave in vacuum
# Unit cell must be large to ensure fields are zero at boundary.
domain_x = 10 * wl_nm
domain_y = domain_x
# Waveguide widths.
rib_w = 2600
rib_h = 50
# Shape of the waveguide.
inc_shape = 'rib'

slab_w = params.slab_w()
slab_h = params.slab_h()

# Number of electromagnetic modes to solve for.
num_modes_EM_pump = params.num_modes_EM_pump()
num_modes_EM_Stokes = num_modes_EM_pump
# Number of acoustic modes to solve for.
num_modes_AC = params.num_modes_AC()
# The EM pump mode(s) for which to calculate interaction with AC modes.
# Can specify a mode number (zero has lowest propagation constant) or 'All'.
EM_mode_index_pump = 0
# The EM Stokes mode(s) for which to calculate interaction with AC modes.
EM_mode_index_Stokes = 0
# The AC mode(s) for which to calculate interaction with EM modes.
AC_mode_index = 'All'


'''
Stages so far for rib_h:
I NEED TO COMPLETE 50 --> 90!
[50, 90]
[100, 590]
[600, 610]
[620, 690]
[700, 900]

'''


while rib_h <= 90:
    output_folder = 'Rib_{}'.format(rib_h)
    os.makedirs(output_folder, exist_ok=True)
    
    AC_mode_data_prefix = "C:/Users/finnh/numbat/nb_releases/NumBAT/Honours-Proj/Winter-Holidays/Week 3/Coarse-h-Dispersion/{}/Rib_Field_data/AC_Mode_Data.csv".format(output_folder)
    os.makedirs(os.path.dirname(AC_mode_data_prefix), exist_ok=True)
    
    EM_mode_data_prefix = "C:/Users/finnh/numbat/nb_releases/NumBAT/Honours-Proj/Winter-Holidays/Week 3/Coarse-h-Dispersion/{}/Rib_Field_data/EM_Mode_Data.csv".format(output_folder)
    os.makedirs(os.path.dirname(EM_mode_data_prefix), exist_ok=True)
    
    
    
    with open(AC_mode_data_prefix, "a", newline='') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow([
            "mode number", "Angular-acoustic-frequency_q (1/micron)", "Lambda (microns)",
            "Acoustic frequency_q/2pi (1/micron)", "frequency (GHz)",
            "Phase velocity_vp (m/s)", "Group velocity_vg (m/s)",
            "f_x", "f_y", "f_t", "f_z",
            "r_0 (micron)", "w_x (micron)", "w_y (micron)", 
            "Masked_PE_Data", "Masked_MB_Data"
        ])
        f.close()
    
    
    with open(EM_mode_data_prefix, "a", newline='') as l:
        writer = csv.writer(l, delimiter=',')
        writer.writerow([
            "mode number", "Frequency_[omega/2pi] (THz)", "k (1/microns)",
            "n^~", "n_g",
            "f_x", "f_y", "f_t", "f_z",
            "r_0 (micron)", "w_x (micron)", "w_y (micron)"
        ])
        l.close()
    
    
    prefix, refine_fac = starter.read_args(rib_h, sys.argv)
    nbapp = numbat.NumBATApp(prefix, outdir=output_folder)
    print(f"This is for rib height: {rib_h}\n")
    
    # Create waveguide structure
    wguide = nbapp.make_structure(
        inc_shape=inc_shape,
        domain_x=domain_x,
        domain_y=domain_y,
        rib_w=rib_w,
        rib_h=rib_h,
        slab_w=slab_w,
        slab_h=slab_h,
        material_bkg=materials.make_material("Vacuum"),
        material_a=materials.make_material("Ge115As24Se645_2023_Govert"),
        material_b=materials.make_material("SiO2_2016_Smith"),
        lc_bkg=0.1, ## Meant to be 0.1
        lc_refine_1=10.0, ## Meant to be 10
        lc_refine_2=2.0 ## Meant to be 10
        ## plt_mesh=False
        ## check_mesh=False
    )
    
    wguide.plot_mesh(prefix)
    
    # Expected effective index of fundamental guided mode.
    n_eff = wguide.get_material('a').refindex_n - 0.1
    # Calculate the Electromagnetic modes of the pump field.
    sim_EM_pump = wguide.calc_EM_modes(num_modes_EM_pump, wl_nm, n_eff, suppress_slow_modes=True)
    csv_save_func.save_em_pump_to_csv(sim_EM_pump, output_folder)
    #npzfile = np.load('wguide_data.npz', allow_pickle=True)
    #sim_EM_pump = npzfile['sim_EM_pump'].tolist()
    
    
    # Calculate the Electromagnetic modes of the Stokes field.
    sim_EM_Stokes = sim_EM_pump.clone_as_backward_modes()
    csv_save_func.save_em_stokes_to_csv(sim_EM_Stokes, output_folder)
    #npzfile = np.load('wguide_data2.npz', allow_pickle=True)
    #sim_EM_Stokes = npzfile['sim_EM_Stokes'].tolist()
    
    sim_EM_pump.plot_modes(xlim_min=0.4, xlim_max=0.4, ## Was xlim_min=0.4, xlim_max=0.4
                           ylim_min=0.4, ylim_max=0.4, ## Was ylim_min=0.4, ylim_max=0.4
                           mode_indices=[EM_mode_index_pump], field_type='EM_E',
                           num_ticks=3, ticks=True, colorbar=True, 
                           quiver_points=40, n_points=1000, suffix = f'_{rib_h}')
    
    
    # Print the wavevectors of EM modes.
    v_kz = sim_EM_pump.kz_EM_all()
    print('\n k_z of EM modes \n', np.round(np.real(v_kz),4))
    
    # Calculate the EM effective index of the waveguide.
    print("\n n_eff = ", np.round(sim_EM_pump.neff_all(), 4))
    
    # Calculate acoustic wavenumber
    q_AC = np.real(v_kz[EM_mode_index_pump] - sim_EM_Stokes.kz_EM_all()[EM_mode_index_Stokes])
    print('\n AC wavenumber (1/m) = ', np.round(q_AC, 4))
    
    
    #q_AC= 2.*q_AC ## (????? IDK WHAT THIS IS/WHY THEY ARE REWRITING OVER IT)
    
    # Calculate acoustic modes
    shift_Hz = 6.0e9  ## Starting frequency for FEM search ## Meant to be 3e9
    sim_AC = wguide.calc_AC_modes(num_modes_AC, q_AC, EM_sim=sim_EM_pump, shift_Hz=shift_Hz)
    # #np.savez('wguide_data_AC', sim_AC=sim_AC)
    # npzfile = np.load('wguide_data_AC.npz')
    # sim_AC = npzfile['sim_AC'].tolist()
    
    sim_AC.plot_modes(num_ticks=3, xlim_min=0.4, xlim_max=0.4, suffix = f'_{rib_h}')
    
    # Print acoustic frequencies
    print('\n Freq of AC modes (GHz) \n', np.round(np.real(sim_AC.nu_AC_all())*1e-9, 4))
    
    set_Q_factor = params.set_Q_factor()  # Mechanical Q factor
    
    
    
    # Calculate interaction integrals and SBS gain for PE and MB effects combined,
    # as well as just for PE, and just for MB. Also calculate acoustic loss alpha.
    
    
    gain_box = integration.get_gains_and_qs(
        sim_EM_pump, sim_EM_Stokes, sim_AC, q_AC,
        EM_mode_index_pump=EM_mode_index_pump,
        EM_mode_index_Stokes=EM_mode_index_Stokes,
        AC_mode_index=AC_mode_index,
        fixed_Q=set_Q_factor
    )
    
    csv_save_func.save_ac_to_csv(sim_AC, gain_box, output_folder)
    
        
    SBS_gain_PE_ij = gain_box.gain_PE_all_by_em_modes(EM_mode_index_pump, EM_mode_index_Stokes)
    SBS_gain_MB_ij = gain_box.gain_MB_all_by_em_modes(EM_mode_index_pump, EM_mode_index_Stokes)
    SBS_gain_tot_ij = gain_box.gain_total_all_by_em_modes(EM_mode_index_pump, EM_mode_index_Stokes)
        
    # Print gain results
    print('\nGains by acoustic mode:')
    print('Ac. mode | Freq (GHz) | G_tot (1/mW) | G_PE (1/mW) | G_MB (1/mW)')
    v_nu = sim_AC.nu_AC_all()
    for (m, nu) in enumerate(v_nu):
        print(f'{m:7d} {np.real(nu)*1e-9:9.4f} {gain_box.gain_total(m):13.3e} '
                f'{gain_box.gain_PE(m):13.3e} {gain_box.gain_MB(m):13.3e}')
    
    
    # Plot gain spectrum
    freq_min = 3 * SI_GHz
    freq_max = 10 * SI_GHz
    
    gain_box.plot_spectra(freq_min=freq_min, freq_max=freq_max, logy=False, suffix = f'_{rib_h}')
    
    threshold = 1e-3
    masked_PE = np.where(np.abs(SBS_gain_PE_ij) > threshold, SBS_gain_PE_ij, 0)
    masked_MB = np.where(np.abs(SBS_gain_MB_ij) > threshold, SBS_gain_MB_ij, 0)
    masked_tot = np.where(np.abs(SBS_gain_tot_ij) > threshold, SBS_gain_tot_ij, 0)
    
    csv_save_func.save_masked_to_csv(masked_PE,masked_MB,masked_tot, output_folder)
    
    
    #def total_Q(sim_EM_pump, sim_EM_Stokes, sim_AC, EM_mode_index_pump, EM_mode_index_Stokes, getting_mode):
    #    Q_PE = integration.Q_PE(sim_EM_pump, sim_EM_Stokes, sim_AC, EM_mode_index_pump, EM_mode_index_Stokes, getting_mode)
    #    Q_MB = integration.Q_MB(sim_EM_pump, sim_EM_Stokes, sim_AC, EM_mode_index_pump, EM_mode_index_Stokes, getting_mode)
    #    Q_tot = Q_PE + Q_MB
    #    return Q_tot
    
    q = q_AC
    
    # Saving all AC mode data to csv file
    with open(AC_mode_data_prefix, "a", newline='') as f:  # Use "w" to overwrite any existing file
        writer = csv.writer(f, delimiter=',')
        
        # Loop through modes
        for getting_mode in range(num_modes_AC):
            md = sim_AC.get_mode(getting_mode)
            writer.writerow([getting_mode, abs(q)*1e-6, (2*np.pi) / q, q/(2*np.pi)*1e-6, 
                             abs(sim_AC.nu_AC(getting_mode)), abs(sim_AC.vp_AC(getting_mode)),
                             abs(sim_AC.vg_AC(getting_mode)), md.field_fracs()[0], md.field_fracs()[1], 
                             md.field_fracs()[2], md.field_fracs()[3], md.center_of_mass(), 
                             md.second_moment_widths()[0], md.second_moment_widths()[1],
                             masked_PE.data[getting_mode], masked_MB.data[getting_mode]])
    
        f.close()
    
    # Saving EM mode data to csv file
    with open(EM_mode_data_prefix, "a", newline='') as l:
        writer = csv.writer(l, delimiter=',')
        EM_md = sim_EM_pump.get_mode(EM_mode_index_pump)
        writer.writerow([str(EM_mode_index_pump), (scipy.constants.c/(wl_nm*1e-9))*1e-12, sim_EM_pump.kz_EM(EM_mode_index_pump)*1e-6,
                         sim_EM_pump.neff(EM_mode_index_pump), sim_EM_pump.ngroup_EM(EM_mode_index_pump),
                         EM_md.field_fracs()[0], EM_md.field_fracs()[1], EM_md.field_fracs()[2], EM_md.field_fracs()[3],
                         EM_md.center_of_mass(), EM_md.second_moment_widths()[0], EM_md.second_moment_widths()[1]
        ])
        l.close()
    
    print("\n Displaying gain results with negligible components masked out:")
    print("AC mode | Photoelastic (PE) | Moving boundary(MB) | Total")
    for (m, gpe, gmb, gt) in zip(range(num_modes_AC), masked_PE, masked_MB, masked_tot):
        print(f'{m:8d} {gpe:12.4f} {gmb:12.4f} {gt:12.4f}')
    
    
    print(nbapp.final_report())

    rib_h += 10