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
    Dist_FAPtoTHR = (values['Alt_FAP'] - values['Elev_THR'] - values['RDH']) / values['VPA_Prom']
    new_values['Dist_FAPtoTHR'] = Dist_FAPtoTHR
    TAS_Conversion = 171233 * math.pow(((288+values['Temp_ISA'])-(0.006496*values['Elev_AD'])),0.5) / math.pow(288-(0.006496*values['Elev_AD']),2.628)
    new_values['TAS_Conversion'] = TAS_Conversion
    new_values['TAS_Final_A'] = values['IAS_Final_A'] * TAS_Conversion
    new_values['TAS_Final_B'] = values['IAS_Final_B'] * TAS_Conversion
    new_values['TAS_Final_C'] = values['IAS_Final_C'] * TAS_Conversion
    new_values['TAS_Final_D'] = values['IAS_Final_D'] * TAS_Conversion
    new_values['OCH_A'] = values['OCA_A'] - values['Elev_THR']
    new_values['OCH_B'] = values['OCA_B'] - values['Elev_THR']
    new_values['OCH_C'] = values['OCA_C'] - values['Elev_THR']
    new_values['OCH_D'] = values['OCA_D'] - values['Elev_THR']
    return new_values

def addHL(values):
    '''Outputs a dictionary with calculated HL allowances to add to the dictionary of parameters'''
    new_values = {}
    HLadjelev = 0
    if values['Elev_AD'] > 900:
        HLadjelev = 2 * values['Elev_AD'] / 300 / 100
    HLadjGP = 0
    if values['VPA_Prom'] > 3.5:
        print("Non-Standard VPA")
    elif values['VPA_Prom'] > 3.2:
        HLadjGP = 5 * (values['VPA_Prom'] - 3.2) * 10 / 100
    HLadj = (1+HLadjelev) * (1+HLadjGP)
    new_values['HL_A_calc'] = values['HL_A_std'] * HLadj
    new_values['HL_B_calc'] = values['HL_B_std'] * HLadj
    new_values['HL_C_calc'] = values['HL_C_std'] * HLadj
    new_values['HL_D_calc'] = values['HL_D_std'] * HLadj
    return new_values

def addTempCorr(values):
    '''Outputs a dictionary with calculated temperature correction to add to the dictionary of parameters'''
    new_values = {}
    deltatemp = values['Temp_ISA']
    Lo = values['Lo']
    hFAP = values['Alt_FAP'] - values['Elev_THR']
    To = values['To']
    hTHR = values['Elev_THR']
    TempCorr = (-deltatemp/Lo) * math.log(1 + Lo * hFAP / (To + Lo * hTHR))
    new_values['TempCorr'] = TempCorr
    return new_values

def addOAS(values):
    '''Outputs a dictionary with OAS parameters to add to the dictionary of parameters'''
    new_values = {}
    hFAP = values['Alt_FAP'] - values['Elev_THR']
    ypsilon = 0.08 * values['g']
    Hi = values['H0']
    if values['Elev_THR'] > (10000 * values['ft2m']):
        Hi = values['H10000']
    elif values['Elev_THR'] > (5000 * values['ft2m']):
        Hi = values['H5000']
    VPA_Min = (hFAP - values['TempCorr'] - values['RDH']) / values['Dist_FAPtoTHR']
    new_values['VPA_Min'] = VPA_Min
    grad_FAS = (hFAP + values['TempCorr'] - Hi) * (values['VPA_Prom'] / (hFAP - Hi))
    new_values['grad_FAS'] = grad_FAS
    xFAS = ((Hi - values['RDH']) / values['VPA_Prom']) + values['ATT_FAF']
    new_values['xFAS'] = xFAS
    xSEC30 = xFAS - ((Hi - 30) / grad_FAS) #point at which secondary surface height reaches 30m above ground plane
    new_values['xSEC30'] = xSEC30
    altFAF = (values['Dist_FAFtoTHR'] - xFAS) * grad_FAS
    new_values['altFAF'] = altFAF    
    xZ_A_adj = (values['HL_A_calc'] - values['RDH']) / values['VPA_Prom'] \
                 - (values['ATT_MAPt'] + 2*values['TAS_Final_A']*math.sin(math.atan(values['VPA_Prom'])) \
                 /ypsilon*(values['TAS_Final_A']+values['MA_Wind']))
    xZ_B_adj = (values['HL_B_calc'] - values['RDH']) / values['VPA_Prom'] \
                 - (values['ATT_MAPt'] + 2*values['TAS_Final_B']*math.sin(math.atan(values['VPA_Prom'])) \
                 /ypsilon*(values['TAS_Final_B']+values['MA_Wind']))
    xZ_C_adj = (values['HL_C_calc'] - values['RDH']) / values['VPA_Prom'] \
                 - (values['ATT_MAPt'] + 2*values['TAS_Final_C']*math.sin(math.atan(values['VPA_Prom'])) \
                 /ypsilon*(values['TAS_Final_C']+values['MA_Wind']))
    xZ_D_adj = (values['HL_D_calc'] - values['RDH']) / values['VPA_Prom'] \
                 - (values['ATT_MAPt'] + 2*values['TAS_Final_D']*math.sin(math.atan(values['VPA_Prom'])) \
                 /ypsilon*(values['TAS_Final_D']+values['MA_Wind']))
    if values['Elev_AD'] > 900 or math.degrees(math.atan(values['VPA_Prom'])) > 3.2:
        new_values['xZ_A_calc'] = min(values['xZ_A_std'], xZ_A_adj)
        new_values['xZ_B_calc'] = min(values['xZ_B_std'], xZ_B_adj)
        new_values['xZ_C_calc'] = min(values['xZ_C_std'], xZ_C_adj)
        new_values['xZ_D_calc'] = min(values['xZ_D_std'], xZ_D_adj)
    else:
        new_values['xZ_A_calc'] = values['xZ_A_std']
        new_values['xZ_B_calc'] = values['xZ_B_std']
        new_values['xZ_C_calc'] = values['xZ_C_std']
        new_values['xZ_D_calc'] = values['xZ_D_std']
    new_values['xSOC_A'] = new_values['xZ_A_calc'] + ((values['OCH_A'] - values['HL_A_calc']) / values['VPA_Prom'])
    new_values['xSOC_B'] = new_values['xZ_B_calc'] + ((values['OCH_B'] - values['HL_B_calc']) / values['VPA_Prom'])
    new_values['xSOC_C'] = new_values['xZ_C_calc'] + ((values['OCH_C'] - values['HL_C_calc']) / values['VPA_Prom'])
    new_values['xSOC_D'] = new_values['xZ_D_calc'] + ((values['OCH_D'] - values['HL_D_calc']) / values['VPA_Prom'])
    return new_values

def addLateralLimits(values):
    '''Outputs a dictionary with calculated lateral limits for the start, finish and splays of the protection areas'''
    new_values = {}
    xFAF_start = values['Dist_FAFtoTHR'] + values['ATT_FAF']
    new_values['xFAF_start'] = xFAF_start
    xFAF_splay = values['Dist_FAFtoTHR'] - (values['SW_FAF'] - values['SW_MAPt'])/values['Splay_in']
    new_values['xFAF_splay'] = xFAF_splay
    xMAPt_start = values['Dist_MAPTtoTHR'] + values['ATT_MAPt']
    new_values['xMAPt_start'] = xMAPt_start
    xMAPt_splay = xMAPt_start - (values['SW_MA'] - values['SW_MAPt'])/values['Splay_out']
    new_values['xMAPt_splay'] = xMAPt_splay
    xVNAV_end_A = -values['Dist_THRtoMATP']
    xVNAV_end_B = -values['Dist_THRtoMATP']
    xVNAV_end_C = -values['Dist_THRtoMATP']
    xVNAV_end_D = -values['Dist_THRtoMATP']
    if values['Dist_THRtoMATP'] == 0:
        xVNAV_end_A = -((values['Alt_MAturn'] - values['OCA_A'] + values['HL_A_calc']) / values['Grad_MA']) + values['xSOC_A']
        xVNAV_end_B = -((values['Alt_MAturn'] - values['OCA_B'] + values['HL_B_calc']) / values['Grad_MA']) + values['xSOC_B']
        xVNAV_end_C = -((values['Alt_MAturn'] - values['OCA_C'] + values['HL_C_calc']) / values['Grad_MA']) + values['xSOC_C']
        xVNAV_end_D = -((values['Alt_MAturn'] - values['OCA_D'] + values['HL_D_calc']) / values['Grad_MA']) + values['xSOC_D']
    new_values['xVNAV_end_A'] = xVNAV_end_A
    new_values['xVNAV_end_B'] = xVNAV_end_B
    new_values['xVNAV_end_C'] = xVNAV_end_C
    new_values['xVNAV_end_D'] = xVNAV_end_D
    return new_values