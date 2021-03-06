# conding=utf-8
from WindPy import w
from datetime import datetime,timedelta
import pandas as pd
import numpy as np
import os,sys

#class tradedata:
#    def __init__(self,tradecode,rt_date,rt_time,rt_last,rt_last_vol,rt_oi_change,rt_nature):
#        self.name = tradecode
#        self.date = rt_date
#        self.time = rt_time
#        self.price = rt_last
#        self.pos = rt_last_vol
#        self.change = rt_oi_change
#        self.nature = rt_nature

# 获取实时交易数据
#def ReadTradeInfo(codelist):
#    naturedict = {1:'空开',2:'空平',3:'空换',4:'多开',5:'多平',6:'多换',7:'双开',8:'双平'}
#    tradedata = {}
#    code = ','.join(codelist)
#    tradeinfo = w.wsq(code, "rt_date,rt_time,rt_last,rt_last_vol,rt_oi_change,rt_nature").Data
#    for i in range(len(codelist)):
#        tradecode = codelist[i]
#        rt_date = str(tradeinfo[0][i]).split('.')[0]
#        rt_timeorigin = str(tradeinfo[1][i]).split('.')[0]
#        rt_time = ("%s:%s:%s") % (rt_timeorigin[:-4],rt_timeorigin[-4:-2],rt_timeorigin[-2:])
#        rt_last = tradeinfo[2][i]
#        rt_last_vol = tradeinfo[3][i]
#        rt_oi_change = tradeinfo[4][i]
#        rt_nature = naturedict[int(tradeinfo[5][i])]
#        tradedata[i] = [rt_date,rt_time,rt_last,rt_last_vol,rt_oi_change,rt_nature]
#    return tradedata

def report_progress(progress, total, start, end):
    ratio = progress / float(total)
    percentage = round(ratio * 100)
    length = 80
    percentnums = round(length*ratio)
    sec = (end-start).seconds
    buf = '\r[%s%s] %d%% (%d Seconds)' % (('#'*percentnums),('-'*(length-percentnums)), percentage,sec)
    sys.stdout.write(buf)
    sys.stdout.flush()
def report_progress_done():
    sys.stdout.write('\n')

# 从csv文件读取以往交易数据
def ReadTradeInfo(code):
    #nowmon = datetime.now().strftime('%Y%m')
    #获取各品种以往数据的文件名
    allfiles = os.listdir()
    codefiles = []
    oldtradeinfo = pd.DataFrame
    for item in allfiles:
        if (item.split('.')[-1] == 'csv'):
                if code in item:
                    codefiles.append(item)
    codefiles = sorted(codefiles)
    # 读取各品种以往数据
    datalist = []
    for j in range(len(codefiles)):
        data = pd.read_csv(codefiles[j],encoding='gb2312',dtype={'code':str,'rt_date':str,'rt_time':str,'rt_last':np.int32,'rt_last_vol':np.int32,'rt_oi_change':np.int32,'rt_nature':np.int32})
        datalist.append(data)
    if datalist:
        oldtradeinfo = pd.concat(datalist,ignore_index=True) #合并为一个dataframe
    return (oldtradeinfo)

### 根据code名称获取csv文件列表，并区分以往文件和实时文件
def get_files(code):
    now = datetime.now().strftime('%Y%m%d')
    allfiles = os.listdir()
    codefiles = []
    livefile = ''
    index = -2
    for item in allfiles:
        if (item.split('.')[-1] == 'csv'):
                if code in item:
                    codefiles.append(item)
    oldfiles = sorted(codefiles)
    for i in range(len(oldfiles)):
        if now in oldfiles[i]:
            index = i
    if index == -2:
        index = -1
    livefile = oldfiles[index]
    oldfiles.remove(livefile)
    return (oldfiles,livefile)

def get_filelist(code):
    allfiles = os.listdir()
    codefiles = []
    for item in allfiles:
        if (item.split('.')[-1] == 'csv'):
                if code in item:
                    codefiles.append(item)
    codefiles = sorted(codefiles)
    print('文件列表: %s' % (', '.join(codefiles)))
    return codefiles

def get_yesterday(dfdate):
    today = datetime.strptime(dfdate,'%Y%m%d')
    yesterday = (today - timedelta(days=1)).strftime('%Y%m%d')
    return yesterday

def read_files(datafiles):
    dflist = []
    dfs = pd.DataFrame
    if len(datafiles) > 0:
        for i in range(len(datafiles)):
            dfdate = datafiles[i].split('_')[1].split('.')[0]
            yesterday = get_yesterday(dfdate)
            df = pd.read_csv(datafiles[i], encoding='gb2312', usecols= (0,1,3,5,6),
                               dtype={'时间': str, '价格': np.int32, '现手': np.int32, '增仓': np.int32,
                                      '性质': str})
            print('读取文件%r,共%d行:' % (datafiles[i], len(df.index)))
            start = datetime.now()
            for index, row in df.iterrows():
                if datetime.strptime(row.时间,'%H:%M:%S') > datetime.strptime('20:00:00','%H:%M:%S'):
                    df.iloc[index,0] = yesterday + '_' + row.时间
                else:
                    df.iloc[index, 0] = dfdate + '_' + row.时间
                end = datetime.now()
                report_progress(index, len(df.index),start, end)
            report_progress_done()
            dflist.append(df)
            #end = datetime.now()
            #print('已读取文件%r,共%d行，用时%d秒' % (datafiles[i],len(df.index),(end-start).seconds))
            del df
        if len(dflist) > 0:
            dfs = pd.concat(dflist, ignore_index=True)
    return  dfs


def read_old_files(oldfiles):
    dflist = []
    olddf = pd.DataFrame
    if len(oldfiles) > 0:
        for i in range(len(oldfiles)):
            df = pd.read_csv(oldfiles[i], encoding='gb2312',
                               dtype={'code': str, 'rt_date': str, 'rt_time': str, 'rt_last': np.int32,
                                      'rt_last_vol': np.int32, 'rt_oi_change': np.int32, 'rt_nature': np.int32})
            dflist.append(df)
        if len(dflist) > 0:
            olddf = pd.concat(dflist, ignore_index=True)
    return olddf

def read_live_file(livefile,num):
    templine = []
    for i in range(1, num + 1):
        templine.append(i)
    livedf = pd.read_csv(livefile, encoding='gb2312',skiprows=tuple(templine),
                               dtype={'code': str, 'rt_date': str, 'rt_time': str, 'rt_last': np.int32,
                                      'rt_last_vol': np.int32, 'rt_oi_change': np.int32, 'rt_nature': np.int32})
    return livedf