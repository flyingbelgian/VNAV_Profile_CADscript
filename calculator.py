import math

class Parameters:
    def __init__(self, constant, rule, var):
        self.constant = constant.value
        self.rule = rule.value
        self.var = var.value
        self.value = {}
        self.addCalcVariables()
        self.addHL()
        self.addTempCorr()
        self.addOAS()
        self.addLateralLimits()

    def addCalcVariables(self):
        '''Adds calculated reference values to the dictionary of parameters'''
        self.value['xFAP'] = (self.var['zFAP'] - self.var['zTHR'] - self.var['RDH']) / self.var['VPA_prom']
        self.value['TAS_conv'] = 171233 * math.pow(((288+self.var['temp_devISA'])-(0.006496*self.var['zAD'])),0.5) / math.pow(288-(0.006496*self.var['zAD']),2.628)
        self.value['TAS_final'] = self.var['IAS_final'] * self.value['TAS_conv']
        self.value['OCH'] = self.var['OCA'] - self.var['zTHR']

    def addHL(self):
        '''Adds calculated HL allowance to the dictionary of parameters'''
        HLadj_elev = 0
        if self.var['zAD'] > 900:
            HLadj_elev = 2 * self.var['zAD'] / 300 / 100
        HLadj_GP = 0
        if self.var['VPA_prom'] > 3.5:
            print("Non-Standard VPA")
        elif self.var['VPA_prom'] > 3.2:
            HLadj_GP = 5 * (self.var['VPA_prom'] - 3.2) * 10 / 100
        HLadj = (1+HLadj_elev) * (1+HLadj_GP)
        self.value['HL_calc'] = self.rule['HL_std'] * HLadj

    def addTempCorr(self):
        '''Adds calculated temperature correction to the dictionary of parameters'''
        deltatemp = self.var['temp_devISA']
        Lo = self.constant['Lo']
        hFAP = self.var['zFAP'] - self.var['zTHR']
        To = self.constant['To']
        hTHR = self.var['zTHR']
        temp_corr = (-deltatemp/Lo) * math.log(1 + Lo * hFAP / (To + Lo * hTHR))
        self.value['temp_corr'] = temp_corr

    def addOAS(self):
        '''Adds OAS parameters to the dictionary of parameters'''
        hFAP = self.var['zFAP'] - self.var['zTHR']
        ypsilon = 0.08 * self.constant['g']
        Hi = self.rule['H0']
        if self.var['zTHR'] > (10000 * self.constant['ft2m']):
            Hi = self.rule['H10000']
        elif self.var['zTHR'] > (5000 * self.constant['ft2m']):
            Hi = self.rule['H5000']
        self.value['VPA_min'] = (hFAP - self.value['temp_corr'] - self.var['RDH']) / self.value['xFAP']
        self.value['grad_FAS'] = (hFAP + self.value['temp_corr'] - Hi) * (self.var['VPA_prom'] / (hFAP - Hi))
        self.value['xFAS'] = ((Hi - self.var['RDH']) / self.var['VPA_prom']) + self.rule['ATT_FAF']
        # xSEC30 is point at which secondary surface height reaches 30m above ground plane
        self.value['xSEC30'] = self.value['xFAS'] - ((Hi - 30) / self.value['grad_FAS'])
        self.value['zFAF'] = (self.var['xFAF'] - self.value['xFAS']) * self.value['grad_FAS']
        xZ_adj = (self.value['HL_calc'] - self.var['RDH']) / self.var['VPA_prom'] \
                    - (self.rule['ATT_MAPt'] + 2*self.value['TAS_final']*math.sin(math.atan(self.var['VPA_prom'])) \
                    /ypsilon*(self.value['TAS_final']+self.var['wind_MA']))
        if self.var['zAD'] > 900 or math.degrees(math.atan(self.var['VPA_prom'])) > 3.2:
            self.value['xZ_calc'] = min(self.rule['xZ_std'], xZ_adj)
        else:
            self.value['xZ_calc'] = self.rule['xZ_std']
        self.value['xSOC'] = self.value['xZ_calc'] + ((self.value['OCH'] - self.value['HL_calc']) / self.var['VPA_prom'])

    def addLateralLimits(self):
        '''Adds calculated lateral limits for the start, finish and splays of the protection areas'''
        self.value['xFAF_start'] = self.var['xFAF'] + self.rule['ATT_FAF']
        self.value['xFAF_splay'] = self.var['xFAF'] - (self.rule['SW_FAF'] - self.rule['SW_MAPt'])/self.rule['splay_in']
        self.value['xMAPt_start'] = self.var['xMAPt'] + self.rule['ATT_MAPt']
        self.value['xMAPt_splay'] = self.value['xMAPt_start'] - (self.rule['SW_MA'] - self.rule['SW_MAPt'])/self.rule['splay_out']
        self.value['xVNAV_end'] = -self.var['xMATP']
        if self.var['xMATP'] == 0:
            self.value['xVNAV_end'] = -((self.var['zMATP'] - self.var['OCA'] + self.value['HL_calc']) / self.var['grad_MA']) + self.value['xSOC']
