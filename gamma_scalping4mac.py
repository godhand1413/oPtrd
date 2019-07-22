import pyautogui
from pykeyboard import PyKeyboard
from requests import get
import pandas as pd
import numpy as np
import re,time

pd.set_option('display.unicode.east_asian_width', True)
np.set_printoptions(precision=4,suppress=True,formatter={'float': '{: 0.4f}'.format})
url = 'http://hq.sinajs.cn/list=CON_OP_10001902,CON_SO_10001902,sh510050'
k = PyKeyboard()
#持仓量，持仓价
ETF50_VOLUME = 44.52
ETF50_AVG = 2.948
OP_VOLUME = 47
OP_AVG = 0.3632
UNIT = 0.35

delta_unit = UNIT/OP_VOLUME
middle = ETF50_VOLUME/OP_VOLUME
lower = middle - delta_unit
upper = middle + delta_unit

z = True

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

def log(s):
    f = open('/Users/qiumin/Desktop/sina/log','a')
    f.write(s)
    f.close()
        
def etf_buy():
    k.tap_key('b')
    time.sleep(0.5)
    etf50.positionPrice=(etf50.total_cost+etf50.sell*UNIT)/(etf50.positionVolume+UNIT)
    etf50.positionVolume+=UNIT
    log('b,'+str(etf50.sell)+'\n')

def etf_sell():   
    k.tap_key('s')
    time.sleep(0.5)
    etf50.positionPrice=(etf50.total_cost-etf50.buy*UNIT)/(etf50.positionVolume-UNIT)
    etf50.positionVolume-=UNIT
    log('s,'+str(etf50.buy)+'\n')

if __name__ == '__main__':
    opt = Option(positionVolume=OP_VOLUME,positionPrice=OP_AVG)
    etf50 = Option(positionVolume=ETF50_VOLUME,positionPrice=ETF50_AVG)
    time.sleep(3)
    while(True):
        d = get_data(url)	
        data_loading(d)
        if(etf50.bid_ask>0.002):
            print('bid ask too big!')
            time.sleep(5)
            continue
        #switch
        if((opt.delta > middle) and (z == False)):
            pyautogui.press('f1')
            z = True
            print('switch to buy...')
        if((opt.delta < middle) and (z == True)):
            pyautogui.press('f2')
            z = False
            print('switch to sell...')
        #buy or sell
        if(opt.delta < lower):
            etf_sell()       
            middle = lower
            upper = middle
            lower -= delta_unit
            print('sell '+str(etf50.buy)+'\n')          
        if(opt.delta > upper):
            etf_buy()
            lower = middle
            middle = upper
            upper += delta_unit
            print('buy '+str(etf50.sell)+'\n')
        #浮盈
        x = etf50.profit
        y = opt.profit
        print('\n{:<9s}{:<9s}{:<9s}{:<9s}{:<9s}\n'\
              '{:<9.4f}{:<9.4f}{:<9.4f}{:<9.4f}{:<9.4f}\n'\
              '{:<9s}{:<9s}{:<9s}\n'\
              '{:<9.0f}{:<9.0f}{:<9.0f}'\
              .format('50etf','8_3300','delta','upper','lower',\
                      etf50.sell,opt.sell,opt.delta,upper,lower,\
                      '50etf','8_3300','sum',\
                      x,y,x+y))
        
        time.sleep(1)

    
