# -*- coding: utf-8 -*-
"""
Created on Wed Nov 28 18:04:51 2018

@author: sz08641
"""
import getpass
import pandas as pd
import numpy as np
import datetime as dt
import time
import xlsxwriter as xlsw
import warnings
import itertools
import matplotlib.pyplot as plt
import seaborn as sns
import uuid  # for randoms id
import os
#import difflib
from opt_val import BSM_call_value, BSM_put_value
from greeks import BSM_delta,BSM_gamma, BSM_vega, BSM_theta, BSM_delta_put,BSM_theta_put

warnings.simplefilter(action='ignore', category=FutureWarning)

now = dt.datetime.now()
datum = dt.date.today()
#sugar Pi

factor = 22.04622 #factor cent/lb raw sugar to usd/t

"""
Starting with class coding
"""

class Scenario:
    
    """ predefined market variation levels 
    s:          name of scenario
    user:       user of tool
    datum:      date of scenario
    now:        date and time of scenario
    chg:        percentage change on scenario 
    start:      level of change to start from current e.g. -10 means 10% below but
                positive values are also allowed)
    end:        level of change to end analysis e.g. +50 means 50% over original level
                negative values are also allow
    changes:    list with % variation to be used in the scenario
    
    """
    num_sce=0
    chg = round(0.05,2)
    down = round(0.90,2)
    high = round(1.10,2)
    variation = [1.00]
    instances = {}
    changes=[]
    #__refs__ = defaultdict(list)
    def __init__(self,name_sce):
        Scenario.num_sce+=1
        self.scid=uuid.uuid1()
        self.name_sce = name_sce
        self.datum = datum.strftime('%d-%m-%Y')
        self.now = now.strftime('%d-%m-%Y %H:%M')
        self.user = getpass.getuser() # name of user 
        
        
        self.instances[self.num_sce]={}
        self.create_data()
        self.changes = self.change_mkt()      
 
       
     
    def create_data(self):
        self.instances[self.num_sce]['id']=self.scid
        self.instances[self.num_sce]['scenario']=self.name_sce
        self.instances[self.num_sce]['datum']=self.datum
        self.instances[self.num_sce]['user']=self.user
        self.instances[self.num_sce]['df_in']=[]
        self.instances[self.num_sce]['df_out']=[]
        self.instances[self.num_sce]['Option']={}
        return self.instances
        
    def change_mkt(self):
        nchg = np.append(self.variation,np.arange(self.down,self.high+self.chg,self.chg))
        self.changes = np.unique(nchg)
        self.instances[self.num_sce]['changes']=[round((self.down-1)*100,2),round((self.high-1)*100,2),round((self.chg)*100,2)]
        return self.changes
    
    def apply_var(self,ndown,nhigh,nchg):
        self.changes=self.variation
        self.down = ndown/100+1
        self.high = nhigh/100+1
        self.chg = nchg/100
        self.changes = self.change_mkt()
        self.instances[self.num_sce]['changes']=[round(ndown,2),round(nhigh,2),round(nchg,2)]
        return self.changes
    # this gives the possibility to change the market variation 
    # for the whole class
#    @classmethod
#    def set_var(cls, ndown, nhigh,nchg):
#        #cls.changes=cls.variation
#        cls.down = ndown/100+1
#        cls.high = nhigh/100+1
#        cls.chg = nchg/100
#        cls.changes = cls.change_mkt(cls)
#        cls.instances[cls.num_sce]['changes']=[round(ndown,2),round(nhigh,2),round(nchg,2)]
#        return cls.changes

    
class DataFrame(Scenario): #to call the data from source file
    df_dict={'in':{},'out':{}}#Dict for source data frame
    versions = ['xls','xlsx'] 
    levels = {}        #to put market values categorized by market
   
    def __init__(self,name_sce,file_name,df=None,cols=None):
        super().__init__(name_sce)
        self.file_name=file_name
        self.name_sce=name_sce
        self.df_in=self.Add_Source_name()
        self.df_out=self.Add_Out_name()
        if df== None:
            self.df=self.reading()
        else:
            self.df=df
         
        if cols==None:
            self.cols=self.get_cols()
        else:
            self.cols=cols
     
        self.start = self.df.value
        self.market=self.df.market
        self.currency=self.df.currency
        self.unit=self.df.unit
        self.measure=self.df.measure
        self.type=self.df.type
       
     
    def Add_Source_name(self):
        self.df_dict['in']['df_'+str(self.num_sce)]=[]
        return self.df_dict['in']['df_'+str(self.num_sce)]
      
    def Add_Out_name(self):
        self.df_dict['out']['df_'+str(self.num_sce)]=[]
        return self.df_dict['in']['df_'+str(self.num_sce)]
      
    def reading(self):
        if self.file_name.split('.')[-1] in self.versions:
            self.df_dict['in']['df_'+str(self.num_sce)].append(pd.read_excel(self.file_name,encoding="cp1252"))
            self.df_in.append(pd.read_excel(self.file_name,encoding="cp1252"))
            self.instances[self.num_sce]['df_in']=self.df_dict['in']['df_'+str(self.num_sce)][0]
            
        else:
            self.df_dict['in']['df_'+str(self.num_sce)].append(pd.read_csv(self.file_name,sep=' |,|;|:|-',encoding="cp1252", engine='python'))#only one separatar comma
            self.df_in.append(pd.read_csv(self.file_name,sep=' |,|;|:|-',encoding="cp1252", engine='python'))
            self.instances[self.num_sce]['df_in']=self.df_dict['in']['df_'+str(self.num_sce)][0]
        return self.df_dict['in']['df_'+str(self.num_sce)][0]
    
    
    
    def get_cols(self):
        self.cols=self.df.columns.values
        return self.cols
    
    
#    """ to check if the data has the european, ny markets"""
#    def matching_mkt(self):
#        for mkt in self.df.market():
#            x = difflib.SequenceMatcher(None,mkt,'eu')
#            print(x.ratio())
#        pass
#    
    def add_mkts(self):
        if 'market' in self.df.columns.values:
            for market in self.df.market:
                self.levels[market]=[]
           
        else:
            print ('you need a columns named \'market\' to your source file')
                
        return self.levels.keys()
    
    def save_df(self): # to add values to the instance dictionary
         self.instances[self.num_sce]['start_data']=self.df
         return self.instances
     
    def calc_levels(self):
        for i in range(0,len(self.df.value)):
            for changes in self.changes:
                self.levels[self.df.market[i]].append(round(self.df.value[i]*changes,2))
            
        return self.instances


    def Out_DataFrame (self):
        
        self.dfOut=pd.DataFrame.from_dict(self.levels)
        
        self.instances[self.num_sce]['levels']=self.dfOut
        return self.dfOut
    
    

    def Final_Frame(self):
        self.df_dict['out']['df_'+str(self.num_sce)]=[]
        keys, values = zip(*self.levels.items())
        self.df2=pd.DataFrame.from_dict([dict(zip(keys,v)) for v in itertools.product(*values)])
        self.df_dict['out']['df_'+str(self.num_sce)].append(self.df2)
        self.instances[self.num_sce]['df_out']=self.df_dict['out']['df_'+str(self.num_sce)][0]
        return self.df2
    
    
    
    def Opt_Val(self,opt_id,date_expiry,sigma,strike):
        self.opt_id=opt_id
        self.date_expiry=date_expiry
        dexpiry=dt.datetime.strptime(self.date_expiry, "%Y-%m-%d").date() 
        dte=dexpiry - datum
        self.T=dte.days/365
        self.sigma =sigma
        self.strike=strike
        self.r=0.0
        self.instances[self.num_sce]['Option'][self.opt_id]={'Expiry':[],'Sigma':[],'Strike':[],'Rate':[],'T':[]}
        self.instances[self.num_sce]['Option'][self.opt_id]['Expiry'].append(self.date_expiry)
        self.instances[self.num_sce]['Option'][self.opt_id]['Sigma'].append(self.sigma)
        self.instances[self.num_sce]['Option'][self.opt_id]['Strike'].append(self.strike)
        self.instances[self.num_sce]['Option'][self.opt_id]['Rate'].append(self.r)
        self.instances[self.num_sce]['Option'][self.opt_id]['T'].append(self.T)
        return self.instances[self.num_sce]['Option']

    def Indexing(self):
         self.instances[self.num_sce]['levels']['% MKT Change']=self.changes*100-100
         self.instances[self.num_sce]['levels'] =self.instances[self.num_sce]['levels'].set_index('% MKT Change')
         
         return self.instances
        
""" TO NAME THE SCENARIO """
name_sce = input('Please enter name of scenario: ')
time.sleep(1)

       
""" TO ACCESS THE SOURCE FILE"""
extension=['xlsx','xls','csv','txt'] 
files = []
for i in os.listdir():
    if i.split('.')[-1] in extension:
       files = np.append(files,i)
files = np.unique(files)
for c, v in enumerate(files):
    print(c,v)
time.sleep(1)
print('')
file_num=int(input('Please indicate the number of file to be used as source: '))
time.sleep(1)


print('The base scenario considers current level +/- 10 % with a step of 5%')
time.sleep(2)
answer = input('Do you want to keep these levels for the base scenario? yes/no: ')
if answer == 'yes':
  file_name =files[file_num]
  s1= DataFrame(name_sce,file_name)
  s1.add_mkts()
  s1.calc_levels()
  df1= s1.Out_DataFrame()
  s1.Indexing()
  df2=s1.Final_Frame()
   
else:
   ndown = float(input('Please indicate the down level from current  (example -5): ').replace(",","."))
   nhigh = float(input('Please indicate the high level from current (example +5): ').replace(",","."))
   nchg = float(input('Please indicate the % of change by step (example +1): ').replace(",","."))
   print("")
   time.sleep(1)
   
   file_name =files[file_num]
   s1= DataFrame(name_sce,file_name)
   print('The new levels for variation are: \n '+str(s1.apply_var(ndown,nhigh,nchg))) # aplying new levels to be checked is changing all levels
   s1.add_mkts()
   print('')
   print('Your scenario will have the following market changes from current: ')
   time.sleep(1)
  # print(str(s1.set_var(ndown,nhigh,nchg))) # aplying new levels to be checked is changing all levels
   s1.calc_levels()
   df1= s1.Out_DataFrame()
   s1.Indexing()
   df2=s1.Final_Frame()
   time.sleep(1)

 

print('')
print('The following markets will be your input: ')
for k in s1.df.market:
    time.sleep(1)
    print(k)
    time.sleep(1)
time.sleep(1)
print('')
time.sleep(1)  
for k,v in s1.levels.items():
    print(f'The market levels for {k} are: ')
    print(str(v).strip('[]'))
    print("")
    
    time.sleep(2)

time.sleep(2)

""" CREATING NEW COLS (This needs to be automatized)"""
df2['Europe_USD/t']=df2['Europe']*df2['Forex']
df2['NY_USD/t']=df2['New York']*factor
df2['white_prem USD/t']=df2['London']-df2['NY_USD/t']


ans2= input('Do you want to calculate option premiums? yes/no: ')
if ans2 =='yes':
    date_expiry =input("What is the expiry date of your option(s) (YYYY-MM-DD): ")
    time.sleep(2)
    sigma=float(input("What is the implied volatility e.g. 0.28 : ").replace(",","."))
    time.sleep(2)
    dum = input("Do you want to check different strike prices? yes/no: ")
    if dum=="yes":
        strikes=[]
        i = 1 # to follow the number of strikes
        time.sleep(1)
        print("Please write your strike levels, press ENTER after each level or write 'end' when finish.")
        a = input("Strike "+ str(i) +" : ")
        while a != "end":
            a = float(str(a).replace(",", "."))
            if a not in strikes:
                strikes.append(a)
                i=i+1              
            else:
                    print("This strike level is already in the list")
                     
        
            a = input("Strike "+ str(i) + " : ")

        print("")
        strikes.sort()
        
#    strike=float(input("What is the strike price e.g. 13.50 : ").replace(",","."))
    print('')
    time.sleep(2)
    for opt_id in range(0,len(strikes)):
        s1.Opt_Val(opt_id,date_expiry,sigma,strikes[opt_id])
        df2['STRIKE_'+str(strikes[opt_id])]=strikes[opt_id]
    Call_prem=[]
    Put_prem=[]
    delta_c=[]
    gamma_c=[]
    vega_c=[]
    theta_c=[]
    
    delta_p=[]
    gamma_p=[]
    vega_p=[]
    theta_p=[]
  
    for strike in strikes:
        for i in range(0,len(df2['New York'])):
            Call_prem.append(BSM_call_value(df2['New York'][i], 
                                            s1.instances[s1.num_sce]['Option'][s1.opt_id]['Strike'][0],
                                            s1.instances[s1.num_sce]['Option'][s1.opt_id]['T'][0],
                                            s1.instances[s1.num_sce]['Option'][s1.opt_id]['Rate'][0],
                                            s1.instances[s1.num_sce]['Option'][s1.opt_id]['Sigma'][0]))
            delta_c.append(BSM_delta(df2['New York'][i], 
                                     s1.instances[s1.num_sce]['Option'][s1.opt_id]['Strike'][0],
                                            s1.instances[s1.num_sce]['Option'][s1.opt_id]['T'][0],
                                            s1.instances[s1.num_sce]['Option'][s1.opt_id]['Rate'][0],
                                            s1.instances[s1.num_sce]['Option'][s1.opt_id]['Sigma'][0]))
            gamma_c.append(BSM_gamma(df2['New York'][i],
                                     s1.instances[s1.num_sce]['Option'][s1.opt_id]['Strike'][0],
                                            s1.instances[s1.num_sce]['Option'][s1.opt_id]['T'][0],
                                            s1.instances[s1.num_sce]['Option'][s1.opt_id]['Rate'][0],
                                            s1.instances[s1.num_sce]['Option'][s1.opt_id]['Sigma'][0]))
                                     
            vega_c.append(BSM_vega(df2['New York'][i],
                                   s1.instances[s1.num_sce]['Option'][s1.opt_id]['Strike'][0],
                                            s1.instances[s1.num_sce]['Option'][s1.opt_id]['T'][0],
                                            s1.instances[s1.num_sce]['Option'][s1.opt_id]['Rate'][0],
                                            s1.instances[s1.num_sce]['Option'][s1.opt_id]['Sigma'][0]))
                                  
            theta_c.append(BSM_theta(df2['New York'][i],
                                     s1.instances[s1.num_sce]['Option'][s1.opt_id]['Strike'][0],
                                            s1.instances[s1.num_sce]['Option'][s1.opt_id]['T'][0],
                                            s1.instances[s1.num_sce]['Option'][s1.opt_id]['Rate'][0],
                                            s1.instances[s1.num_sce]['Option'][s1.opt_id]['Sigma'][0]))
                                    
    for strike in strikes:    
        for i in range(0,len(df2['New York'])):    
            Put_prem.append(BSM_put_value(df2['New York'][i], 
                                          s1.instances[s1.num_sce]['Option'][s1.opt_id]['Strike'][0],
                                                s1.instances[s1.num_sce]['Option'][s1.opt_id]['T'][0],
                                                s1.instances[s1.num_sce]['Option'][s1.opt_id]['Rate'][0],
                                                s1.instances[s1.num_sce]['Option'][s1.opt_id]['Sigma'][0]))
            delta_p.append(BSM_delta_put(df2['New York'][i],
                                         s1.instances[s1.num_sce]['Option'][s1.opt_id]['Strike'][0],
                                                s1.instances[s1.num_sce]['Option'][s1.opt_id]['T'][0],
                                                s1.instances[s1.num_sce]['Option'][s1.opt_id]['Rate'][0],
                                                s1.instances[s1.num_sce]['Option'][s1.opt_id]['Sigma'][0]))
            gamma_p.append(BSM_gamma(df2['New York'][i],
                                     s1.instances[s1.num_sce]['Option'][s1.opt_id]['Strike'][0],
                                                s1.instances[s1.num_sce]['Option'][s1.opt_id]['T'][0],
                                                s1.instances[s1.num_sce]['Option'][s1.opt_id]['Rate'][0],
                                                s1.instances[s1.num_sce]['Option'][s1.opt_id]['Sigma'][0]))
            vega_p.append(BSM_vega(df2['New York'][i],
                                   s1.instances[s1.num_sce]['Option'][s1.opt_id]['Strike'][0],
                                                s1.instances[s1.num_sce]['Option'][s1.opt_id]['T'][0],
                                                s1.instances[s1.num_sce]['Option'][s1.opt_id]['Rate'][0],
                                                s1.instances[s1.num_sce]['Option'][s1.opt_id]['Sigma'][0]))
            theta_p.append(BSM_theta_put(df2['New York'][i],
                                         s1.instances[s1.num_sce]['Option'][s1.opt_id]['Strike'][0],
                                                s1.instances[s1.num_sce]['Option'][s1.opt_id]['T'][0],
                                                s1.instances[s1.num_sce]['Option'][s1.opt_id]['Rate'][0],
                                                s1.instances[s1.num_sce]['Option'][s1.opt_id]['Sigma'][0]))
        
    df2['OPTION_CALL']=Call_prem
    df2['Delta_Call']=delta_c
    df2['Gamma_Call']=gamma_c
    df2['Vega_Call']=vega_c
    df2['Theta_Call']=theta_c
    
    df2['OPTION_PUT']=Put_prem
    df2['Delta_Put']=delta_p
    df2['Gamma_Put']=gamma_p
    df2['Vega_Put']=vega_p
    df2['Theta_Put']=theta_p



print('The first Values of the new Data Frame are:\n ')
time.sleep(1)
print(df2.head())
time.sleep(1)
print("")
print("")

print("Here you find the statistics for each column in your data frame:")
for name in df2.columns.values:
    time.sleep(1)
    print(df2[name].describe())
    print("-----------")
    time.sleep(1)
    print("")



##""" TO SAVE IN EXCEL """     
writer = pd.ExcelWriter("Output "+s1.user+" "+ str(datum) +".xlsx",engine ="xlsxwriter")

for i in range(1,len(Scenario.instances.keys())+1):
    Scenario.instances[i]['df_out'].to_excel(writer, sheet_name =Scenario.instances[i]['scenario'])
    Scenario.instances[i]['levels'].to_excel(writer,sheet_name ="Input "+Scenario.instances[i]['scenario'])

writer.save()
writer.close()        
    
    

 

""" TO PRINT CHANGES OF MARKETS BY SCENARIO """
for i in Scenario.instances.keys():
    print('The changes from current levels for scenario ' +Scenario.instances[i]['scenario']+' are: ')
    print(str(Scenario.instances[i]['changes'][0])+ " % as lowest variation level from current")
    print(str(Scenario.instances[i]['changes'][1])+ " % as highest variation levels from current")
    print(str(Scenario.instances[i]['changes'][2])+ " % change between each level")