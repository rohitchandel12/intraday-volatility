#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 00:24:34 2019

@author: kunwu
"""

#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 23 10:55:37 2017
@author: wanjun
"""

#==============================================================================
#find peak points of time series
#peak points decided when two ma lines meet
#MA_length1, MA_length2: window length of two ma   lines
#last: last price of 1 period
#==============================================================================
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.offline as plt
import os
import time
#%%

class peak(object):
    def __init__(self,MA_length1,MA_length2):
        self.last=np.array([])
        self.n1=MA_length1
        self.n2=MA_length2
        self.n3=max(self.n1,self.n2)
        self.MA_1=[]
        self.MA_2=[]
        self.section_dict=[(0,'None')]
        self.diff=[0]*(self.n3-1)
        #index of effective peak points
        self.min_peak=[]
        self.max_peak=[]
        #index of all peak points
        self.min_peak_all=[]
        self.max_peak_all=[]
        
        self.min_now=[]
        self.max_now=[]
        self.latest_peak = "None"
        self.trend_inc=[]
        self.trend_dec=[]

    def find_peak(self,data):
        temp=data
        self.last=np.append(self.last,temp)
        self.current_wave=(self.last.max()/self.last.min()-1)
        
        if len(self.last)>=max(self.n1,self.n2):
            self.MA_1.append(self.last[-self.n1:].mean())
            self.MA_2.append(self.last[-self.n2:].mean())
            self.diff.append(self.MA_1[-1]-self.MA_2[-1])
        else:
            self.MA_1.append(self.last[-1])
            self.MA_2.append(self.last[-1])
           
        if len(self.last) <= self.n3:
            self.min_now.append(np.argmin(self.last.min()))
            self.max_now.append(np.argmax(self.last.max()))
            self.trend_inc.append(0)
            self.trend_dec.append(0)

        if len(self.last) > self.n3:
            if self.diff[-1]==0:
                self.diff[-1]=self.diff[-2]
            
            if self.diff[-1]>0 and self.diff[-1]*self.diff[-2]<0 and self.latest_peak != "min":
                self.section_dict.append((len(self.diff)-1,'min'))
                start=self.section_dict[-2][0]
                end=self.section_dict[-1][0]
                self.min_peak_all.append(start+np.argmin(self.last[start:end]))                   
                last_three = [self.last[self.max_now[-1]],self.last[start:end].min(),self.last[self.min_now[-1]]]
                if max(last_three)/min(last_three)<1+self.current_wave/10:
                    if len(self.max_peak)>0: del self.max_peak[-1]
                    if self.last[self.min_now[-1]]>self.last[start:end].min() and len(self.min_peak)>0:
                        self.min_peak[-1] = start+np.argmin(self.last[start:end])
                else:
                    self.min_peak.append(start+np.argmin(self.last[start:end]))
                self.latest_peak = "min"                       
                if len(self.min_peak)>0: self.min_now.append(self.min_peak[-1])
                else: self.min_now.append(self.min_now[-1])
                if len(self.max_peak)>0: self.max_now.append(self.max_peak[-1])
                else: self.max_now.append(self.max_now[-1])

                
            elif self.diff[-1]<0 and self.diff[-1]*self.diff[-2]<0 and self.latest_peak != "max" :
                self.section_dict.append((len(self.diff)-1,'max'))
                start=self.section_dict[-2][0]
                end=self.section_dict[-1][0]
                self.max_peak_all.append(start+np.argmax(self.last[start:end]))
                last_three = [self.last[self.max_now[-1]],self.last[start:end].max(),self.last[self.min_now[-1]]]
                if max(last_three)/min(last_three)<1.0016:     
                    if len(self.min_peak)>0: del self.min_peak[-1]
                    if self.last[self.max_now[-1]]<self.last[start:end].max() and len(self.max_peak)>0:
                        self.max_peak[-1] = start+np.argmax(self.last[start:end])
                else:
                    self.max_peak.append(start+np.argmax(self.last[start:end]))
                self.latest_peak = "max"                       
                if len(self.min_peak)>0: self.min_now.append(self.min_peak[-1])
                else: self.min_now.append(self.min_now[-1])
                if len(self.max_peak)>0: self.max_now.append(self.max_peak[-1])
                else: self.max_now.append(self.max_now[-1])
                
            else:
                self.min_now.append(self.min_now[-1])
                self.max_now.append(self.max_now[-1])

            if len(self.min_peak)>2:             
#                self.trend_inc.append((self.last[self.min_peak[-1]]-self.last[self.min_peak[-2]])/(self.last[self.min_peak[-2]])/((self.min_peak[-1]-self.min_peak[-2])))
                self.trend_inc.append((self.last[self.min_peak[-1]]-self.last[self.min_peak[-2]])/(self.last[self.min_peak[-2]]))                
            else: self.trend_inc.append(0)
            if len(self.max_peak)>2:
#                self.trend_dec.append((self.last[self.max_peak[-1]]-self.last[self.max_peak[-2]])/(self.last[self.max_peak[-2]])/((self.max_peak[-1]-self.max_peak[-2])))
                self.trend_dec.append((self.last[self.max_peak[-1]]-self.last[self.max_peak[-2]])/(self.last[self.max_peak[-2]]))
            else:self.trend_dec.append(0)

                
#%%
def main(stock_data,ma_1=5,ma_2=10):
    peak_data=peak(ma_1,ma_2)
    for index in range(len(stock_data)):
        minute_data=pd.DataFrame(stock_data.iloc[index]).T
        peak_data.find_peak(minute_data.close)
    return peak_data

#%%
if __name__=='__main__':
    
    path=os.path.join((os.getcwd())[:-9],'data')
    trade_list=os.listdir(path)
    
    #choose 1 dataset as an example
    object_stock=trade_list[10]
    temp_data=pd.read_csv(os.path.join(path,object_stock))
    temp_data.timestamp=temp_data.timestamp.apply(lambda x: time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(x)))
    temp_data.set_index('timestamp',inplace=True)
    temp_data=temp_data[temp_data.volume!=0]
    temp_data.dropna(how='any',inplace=True)
    peak_data=main(temp_data)
    data=peak_data.last
    arr_section=np.array(peak_data.section_dict[:])[:,0].astype('int')
    
    last_data=go.Scatter(x=list(range(len(data))),y=data,mode='lines',name='last_price')
    #build up compare data
    max_point=data.argmax()
    min_point=data.argmin()
    compare_index=[0,min(max_point,min_point),max(max_point,min_point),len(data)-1]
    compare_data=data[compare_index]
    compare_data=go.Scatter(x=compare_index,y=compare_data,mode='lines',name='simulate_price')
    peak_min_data=go.Scatter(x=peak_data.min_peak_all,y=data[peak_data.min_peak_all],mode='markers',name='peak_min',marker=dict(size=20,color='green'))
    peak_max_data=go.Scatter(x=peak_data.max_peak_all,y=data[peak_data.max_peak_all],mode='markers',name='peak_max',marker=dict(size=20,color='red'))
    #section=go.Scatter(x=arr_section,y=data[arr_section],mode='markers',name='section',marker=dict(size=20,color='black',symbol='cross'))
    layout=go.Layout(title=object_stock[:-4])
    #data_plot=[last_data,peak_min_data,peak_max_data,section]
    data_plot=[last_data,peak_min_data,peak_max_data,compare_data]
    fig=go.Figure(data=data_plot,layout=layout)
    plt.plot(fig)
    
    #compute extreme vol
    extreme_vol=pd.DataFrame(columns=['Parkinson','Garman_Klass','Rogers_Satchell','local_peak_vol'])
    for object_stock in trade_list:
        temp_data=pd.read_csv(os.path.join(path,object_stock))
        temp_data.timestamp=temp_data.timestamp.apply(lambda x: time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(x)))
        temp_data.set_index('timestamp',inplace=True)
        temp_data=temp_data[temp_data.volume!=0]
        temp_data.dropna(how='any',inplace=True)
        
        #parkinson ,Garman_Klass, Rogers_Satchell extreme vol
        part1=(np.log(temp_data.high/temp_data.low)**2).sum()
        extreme_vol.loc[object_stock[:-7],'Parkinson']=(part1/(4*len(temp_data.high)*np.log(2)))**0.5
        
        part1=(np.log((temp_data.high/temp_data.low).iloc[1:])**2).sum()
        part2=(2*np.log(2)-1)*(np.log((temp_data.close/temp_data.close.shift()).iloc[1:])**2).sum()
        extreme_vol.loc[object_stock[:-7],'Garman_Klass']=((part1/2-part2)/len(temp_data.high))**0.5
        
        extreme_vol.loc[object_stock[:-7],'Rogers_Satchell']=(((np.log(temp_data.high/temp_data.low)*np.log(temp_data.high/temp_data.open)+np.log(temp_data.low/temp_data.close)*np.log(temp_data.low/temp_data.open)).sum())/len(temp_data.high))**0.5

        #find local extreme data
        peak_data=main(temp_data)
        #combine all the local extreme index
        index_all=[0]+peak_data.min_peak+peak_data.max_peak+[len(peak_data.last)-1]
        index_all.sort()
        extreme_value=peak_data.last[index_all]
        extreme_vol.loc[object_stock[:-7],'local_peak_vol']=np.sqrt((np.diff(np.log(list(extreme_value)))**2).sum())
        
        
        
        
        
        
        
        
        