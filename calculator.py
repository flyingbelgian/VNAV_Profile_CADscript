import input
import math

def getSource():
    '''Reads the constants.csv and variables.csv into a dictionary of parameters. Converts variables ft, deg, NM and kt where necessary'''
    #start library with all values by loading constants
    values = input.Constants("constants.csv").values
    #get variables and convert to SI prior to adding to library
    variable_source = input.Variables("variables.csv")
    for item in variable_source.values:
        if item[2] == 'ft':
            values[item[0]] = float(item[1])*values['ft2m']
        elif item[2] == 'deg':
            values[item[0]] = math.tan(math.radians(float(item[1])))
        elif item[2] == 'NM':
            values[item[0]] = float(item[1])*values['NM2m']
        elif item[2] == 'kt':
            values[item[0]] = float(item[1])*values['kt2ms']
        else:
            values[item[0]] = float(item[1])
    return values

def addCalcVariables(values):
    '''Outputs a dictionary with calculated reference values to add to the dictionary of parameters'''
    new_values = {}
    xFAP = (values['zFAP'] - values['zTHR'] - values['RDH']) / values['VPA_prom']
    new_values['xFAP'] = xFAP
    TAS_conv = 171233 * math.pow(((288+values['temp_devISA'])-(0.006496*values['zAD'])),0.5) / math.pow(288-(0.006496*values['zAD']),2.628)
    new_values['TAS_conversion'] = TAS_conv
    new_values['TAS_final_A'] = values['IAS_final_A'] * TAS_conv
    new_values['TAS_final_B'] = values['IAS_final_B'] * TAS_conv
    new_values['TAS_final_C'] = values['IAS_final_C'] * TAS_conv
    new_values['TAS_final_D'] = values['IAS_final_D'] * TAS_conv
    new_values['OCH_A'] = values['OCA_A'] - values['zTHR']
    new_values['OCH_B'] = values['OCA_B'] - values['zTHR']
    new_values['OCH_C'] = values['OCA_C'] - values['zTHR']
    new_values['OCH_D'] = values['OCA_D'] - values['zTHR']
    return new_values

def addHL(values):
    '''Outputs a dictionary with calculated HL allowances to add to the dictionary of parameters'''
    new_values = {}
    HLadj_elev = 0
    if values['zAD'] > 900:
        HLadj_elev = 2 * values['zAD'] / 300 / 100
    HLadj_GP = 0
    if values['VPA_prom'] > 3.5:
        print("Non-Standard VPA")
    elif values['VPA_prom'] > 3.2:
        HLadj_GP = 5 * (values['VPA_prom'] - 3.2) * 10 / 100
    HLadj = (1+HLadj_elev) * (1+HLadj_GP)
    new_values['HL_A_calc'] = values['HL_A_std'] * HLadj
    new_values['HL_B_calc'] = values['HL_B_std'] * HLadj
    new_values['HL_C_calc'] = values['HL_C_std'] * HLadj
    new_values['HL_D_calc'] = values['HL_D_std'] * HLadj
    return new_values

def addTempCorr(values):
    '''Outputs a dictionary with calculated temperature correction to add to the dictionary of parameters'''
    new_values = {}
    deltatemp = values['temp_devISA']
    Lo = values['Lo']
    hFAP = values['zFAP'] - values['zTHR']
    To = values['To']
    hTHR = values['zTHR']
    temp_corr = (-deltatemp/Lo) * math.log(1 + Lo * hFAP / (To + Lo * hTHR))
    new_values['temp_corr'] = temp_corr
    return new_values

def addOAS(values):
    '''Outputs a dictionary with OAS parameters to add to the dictionary of parameters'''
    new_values = {}
    hFAP = values['zFAP'] - values['zTHR']
    ypsilon = 0.08 * values['g']
    Hi = values['H0']
    if values['zTHR'] > (10000 * values['ft2m']):
        Hi = values['H10000']
    elif values['zTHR'] > (5000 * values['ft2m']):
        Hi = values['H5000']
    VPA_min = (hFAP - values['temp_corr'] - values['RDH']) / values['xFAP']
    new_values['VPA_min'] = VPA_min
    grad_FAS = (hFAP + values['temp_corr'] - Hi) * (values['VPA_prom'] / (hFAP - Hi))
    new_values['grad_FAS'] = grad_FAS
    xFAS = ((Hi - values['RDH']) / values['VPA_prom']) + values['ATT_FAF']
    new_values['xFAS'] = xFAS
    xSEC30 = xFAS - ((Hi - 30) / grad_FAS) #point at which secondary surface height reaches 30m above ground plane
    new_values['xSEC30'] = xSEC30
    altFAF = (values['xFAF'] - xFAS) * grad_FAS
    new_values['zFAF'] = altFAF    
    xZ_A_adj = (values['HL_A_calc'] - values['RDH']) / values['VPA_prom'] \
                 - (values['ATT_MAPt'] + 2*values['TAS_final_A']*math.sin(math.atan(values['VPA_prom'])) \
                 /ypsilon*(values['TAS_final_A']+values['wind_MA']))
    xZ_B_adj = (values['HL_B_calc'] - values['RDH']) / values['VPA_prom'] \
                 - (values['ATT_MAPt'] + 2*values['TAS_final_B']*math.sin(math.atan(values['VPA_prom'])) \
                 /ypsilon*(values['TAS_final_B']+values['wind_MA']))
    xZ_C_adj = (values['HL_C_calc'] - values['RDH']) / values['VPA_prom'] \
                 - (values['ATT_MAPt'] + 2*values['TAS_final_C']*math.sin(math.atan(values['VPA_prom'])) \
                 /ypsilon*(values['TAS_final_C']+values['wind_MA']))
    xZ_D_adj = (values['HL_D_calc'] - values['RDH']) / values['VPA_prom'] \
                 - (values['ATT_MAPt'] + 2*values['TAS_final_D']*math.sin(math.atan(values['VPA_prom'])) \
                 /ypsilon*(values['TAS_final_D']+values['wind_MA']))
    if values['zAD'] > 900 or math.degrees(math.atan(values['VPA_prom'])) > 3.2:
        new_values['xZ_A_calc'] = min(values['xZ_A_std'], xZ_A_adj)
        new_values['xZ_B_calc'] = min(values['xZ_B_std'], xZ_B_adj)
        new_values['xZ_C_calc'] = min(values['xZ_C_std'], xZ_C_adj)
        new_values['xZ_D_calc'] = min(values['xZ_D_std'], xZ_D_adj)
    else:
        new_values['xZ_A_calc'] = values['xZ_A_std']
        new_values['xZ_B_calc'] = values['xZ_B_std']
        new_values['xZ_C_calc'] = values['xZ_C_std']
        new_values['xZ_D_calc'] = values['xZ_D_std']
    new_values['xSOC_A'] = new_values['xZ_A_calc'] + ((values['OCH_A'] - values['HL_A_calc']) / values['VPA_prom'])
    new_values['xSOC_B'] = new_values['xZ_B_calc'] + ((values['OCH_B'] - values['HL_B_calc']) / values['VPA_prom'])
    new_values['xSOC_C'] = new_values['xZ_C_calc'] + ((values['OCH_C'] - values['HL_C_calc']) / values['VPA_prom'])
    new_values['xSOC_D'] = new_values['xZ_D_calc'] + ((values['OCH_D'] - values['HL_D_calc']) / values['VPA_prom'])
    return new_values

def addLateralLimits(values):
    '''Outputs a dictionary with calculated lateral limits for the start, finish and splays of the protection areas'''
    new_values = {}
    xFAF_start = values['xFAF'] + values['ATT_FAF']
    new_values['xFAF_start'] = xFAF_start
    xFAF_splay = values['xFAF'] - (values['SW_FAF'] - values['SW_MAPt'])/values['splay_in']
    new_values['xFAF_splay'] = xFAF_splay
    xMAPt_start = values['xMAPt'] + values['ATT_MAPt']
    new_values['xMAPt_start'] = xMAPt_start
    xMAPt_splay = xMAPt_start - (values['SW_MA'] - values['SW_MAPt'])/values['splay_out']
    new_values['xMAPt_splay'] = xMAPt_splay
    xVNAV_end_A = -values['xMATP']
    xVNAV_end_B = -values['xMATP']
    xVNAV_end_C = -values['xMATP']
    xVNAV_end_D = -values['xMATP']
    if values['xMATP'] == 0:
        xVNAV_end_A = -((values['zMATP'] - values['OCA_A'] + values['HL_A_calc']) / values['grad_MA']) + values['xSOC_A']
        xVNAV_end_B = -((values['zMATP'] - values['OCA_B'] + values['HL_B_calc']) / values['grad_MA']) + values['xSOC_B']
        xVNAV_end_C = -((values['zMATP'] - values['OCA_C'] + values['HL_C_calc']) / values['grad_MA']) + values['xSOC_C']
        xVNAV_end_D = -((values['zMATP'] - values['OCA_D'] + values['HL_D_calc']) / values['grad_MA']) + values['xSOC_D']
    new_values['xVNAV_end_A'] = xVNAV_end_A
    new_values['xVNAV_end_B'] = xVNAV_end_B
    new_values['xVNAV_end_C'] = xVNAV_end_C
    new_values['xVNAV_end_D'] = xVNAV_end_D
    return new_values