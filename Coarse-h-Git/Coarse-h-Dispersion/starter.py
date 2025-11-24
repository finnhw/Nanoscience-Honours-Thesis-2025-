# startup arg parser for all literature examples

def read_args(enum, argv, sub='', refine=5):

    prefix = 'Rib_EM_{0:02d}'.format(enum)
    prefix +=sub

    if len(argv)>1 and argv[1]=='fast=1':  # choose between faster or more accurate calculation
        refine_fac=1
        #prefix = 'f'+prefix
        s_fmode = ' - fast mode'
    elif len(argv)>1 and argv[1]=='fast=2':
        refine_fac=2
        s_fmode = ' - fast mode (2x)'
    else:
        s_fmode = ''
        refine_fac=refine

    

    print('\n\n\n')
    print('-------------------------------------------------')
    print('\nCommencing NumBAT Rib_EM Honours Calculation')
    return prefix, refine_fac

