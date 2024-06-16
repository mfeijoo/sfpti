import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from glob import glob
import os


st.title('Blue Physics Proton Analysis')


filenames = glob('*.csv')

dates = []

for filename in filenames:
    with open (filename) as filenow:
        datenow = filenow.readline()[11:]
        dates.append(datenow)

dffiles = pd.DataFrame({'file':filenames, 'date':dates}) 
i_list = dffiles.index[dffiles.date.str.contains('000')].tolist()
dffiles.drop(i_list, inplace = True)
dffiles['realdate'] = pd.to_datetime(dffiles.date)
dffiles.sort_values(by='realdate', inplace = True, ascending=False)
dffiles.reset_index(inplace = True, drop = True)
st.write('List of Files')
st.dataframe(dffiles.loc[:,['file', 'date']])

filenow = st.selectbox('Select File to Analyze', dffiles.file)

#Take a quick look at the raw data
@st.cache_data
def read_dataframe(file):
    #confirm the rows to skip
    file0 = open(file)
    firstlines = file0.readlines()[:20]
    file0.close()
    rank = firstlines[2][6]
    if rank == '0':
        capacitor = 10/1000
    else:
        capacitor = 30/1000
    for n, line in enumerate(firstlines):
        if line.startswith('number,time'):
            lines_to_skip = n
    #then read the data frame
    df = pd.read_csv(file, skiprows = lines_to_skip)
    return df, capacitor

dforig, capacitor = read_dataframe(filenow)
df = dforig.loc[:, ['number', 'time', 'temp', 'ch0', 'ch1']]
st.dataframe(df)

inttime = df.time.diff().mean() * 1000000
st.write('Average integration time: %.2f microseconds' %inttime)

last_time = df.iloc[-1,1]
zeros = df.loc[(df.time < 1) | (df.time > last_time -1), 'ch0':].mean()
dfzeros = df.loc[:, 'ch0':] - zeros
dfzeros.columns = ['ch0z', 'ch1z']
dfz = pd.concat([df, dfzeros], axis = 1)
dfz0 = dfz.loc[:, ['time', 'ch0z']]
dfz0.columns = ['time', 'signal']
dfz0['ch'] = 'ch0z'
dfz1 = dfz.loc[:, ['time', 'ch1z']]
dfz1.columns = ['time', 'signal']
dfz1['ch'] = 'ch1z'
dfztp = pd.concat([dfz0, dfz1])
fig1 = px.line(dfztp, x='time', y='signal', color = 'ch', markers = True)
fig1.update_traces(marker=dict(size=4))
fig1.update_xaxes(title = 'time (s)')
fig1.update_yaxes(title = 'Voltage (V)')
st.plotly_chart(fig1)

