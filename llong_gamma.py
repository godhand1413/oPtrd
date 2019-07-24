from requests import get
import pandas as pd
import numpy as np
import re,time

pd.set_option('display.unicode.east_asian_width', True)
np.set_printoptions(precision=4,suppress=True,formatter={'float': '{: 0.4f}'.format})
url = 'http://hq.sinajs.cn/list=CON_OP_10001902,CON_SO_10001902,sh510050'
#持仓量，持仓价
ETF50_VOLUME = 44.17
ETF50_AVG = 2.951
OP_VOLUME = 47
OP_AVG = 0.3632
UNIT = 0.05

delta_unit = UNIT/OP_VOLUME
pDelta = ETF50_VOLUME/OP_VOLUME

#标的
class Option(object):
        def __init__(self,positionVolume,positionPrice,code=None,\
                     buy=None,b_volume=None,sell=None,s_volume=None,delta=None):               
                self.code = code
                self.buy = buy
                self.b_volume = b_volume
                self.sell = sell
                self.s_volume = s_volume
                self.delta = delta
                self.positionPrice = positionPrice
                self.positionVolume = positionVolume
        @property               
        def bid_ask(self):
                return self.sell - self.buy
        @property
        def total_cost(self):
                return self.positionVolume*self.positionPrice
        @property
        def profit(self):
                return (self.buy - self.positionPrice)*self.positionVolume*10000

def get_data(url):
    d = get(url).text
    d = re.findall(r"\"(.+)\"",d)
    d = pd.DataFrame(d)
    d = d[0].str.split(',',expand=True)
    return np.array(d)

def data_loading(d):
        #买一量，买一价，卖一量，卖一价
        opt.b_volume,opt.buy,opt.s_volume,opt.sell = d[0,[0,1,4,3]].astype(float)
        opt.delta = -float(d[1,5])
        etf50.b_volume,etf50.buy,etf50.s_volume,etf50.sell = d[2,[10,11,20,21]].astype(float)
        
if __name__ == '__main__':
    opt = Option(positionVolume=OP_VOLUME,positionPrice=OP_AVG)
    etf50 = Option(positionVolume=ETF50_VOLUME,positionPrice=ETF50_AVG)
    time.sleep(3)
    while(True):
        d = get_data(url)   
        data_loading(d)
        #buy or sell
        x = int((opt.delta - pDelta)/delta_unit)
        if(x > 0):
            print('buy --> {:<9d}'.format(x))
        else:
            print('sell --> {:<9d}'.format(-x))
        time.sleep(1)

    
