'''
This is simply a function that streamlines all the parameters
being used and makes it easier to view/understand for each 
iteration of results produced.

With each run of varying code and its respective output, I can
just copy this file in as a notary document and easily see
what was being used for of the variables in the Rib code.
The variables that can be changed are:

Silica slab width: slab_w
Silica slab height: slab_h
Number of EM modes pumped: num_modes_EM_pump
Number of AC modes to solve: num_modes_AC
Q Factor: Q_factor

All the other variables in the Rib file are held constant.

'''

def slab_w(): ## Meant to be 14000
    global set_slab_w
    set_slab_w = 14000
    return set_slab_w

def slab_h(): ## Meant to be 1000
    global set_slab_h
    set_slab_h = 5000
    return set_slab_h

def num_modes_EM_pump(): ## Meant to be 25
    global set_num_modes_EM_pump
    set_num_modes_EM_pump = 30
    return set_num_modes_EM_pump

'''
* I belive that even though the paper suggests 500 to imporve resolution,
producing 150 AC mode caclulations in the interest of time as it takes 
around 1 hour to complete 500 AC mode calculations. All the relevant
frequencies occurs between modez 0 to 106. 

Hence, overshooting it to 150 modes is adequete for testing to achieve the
desired simulation result of figure 3 b).
'''

def num_modes_AC(): ## Meant to be 500*
    global set_num_modes_AC
    set_num_modes_AC = 500
    return set_num_modes_AC

def set_Q_factor(): ## Meant to be 200-500
    global Q_factor
    Q_factor = 200
    return Q_factor



###########################################################################################
###########################################################################################

# Call functions to initialise variable values
slab_w()
slab_h()
num_modes_EM_pump()
num_modes_AC()
set_Q_factor()


data = {
    'Variable': ['slab_w', 'slab_h', 'num_modes_EM_pump', 'num_modes_AC', 'set_Q_factor'],
    'Value': [set_slab_w, set_slab_h, set_num_modes_EM_pump, set_num_modes_AC, Q_factor]  
}

print(f"{'Variable':<20} | {'Value'}")
print("-" * 30)
for param, value in zip(data['Variable'], data['Value']):
    print(f"{param:<20} | {value}")

