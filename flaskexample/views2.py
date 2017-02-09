from flask import Flask, render_template, json, request
import numpy as np
import warnings
warnings.filterwarnings('ignore')
import matplotlib
import json
import random
import pandas as pd
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.ioff()
from flaskexample import app

from threading import Lock
lock = Lock()
import datetime
import mpld3
from mpld3 import plugins
warnings.filterwarnings('ignore')

colors = {
    'Black': '#000000',
    'Red':   '#FF0000',
    'Green': '#00FF00',
    'Blue':  '#0000FF',
}


def getitem(obj, item, default):
    if item not in obj:
        return default
    else:
        return obj[item]

    
    



# get database 

combined_data = pd.DataFrame.from_csv('./combined_data.csv')




# Setting up matplotlib sytles using BMH
s = json.load(open("./flaskexample/static/bmh_matplotlibrc.json"))
matplotlib.rcParams.update(s)

css = """
table
{
  border-collapse: collapse;
}
th
{
  color: #ffffff;
  background-color: #000000;
}
td
{
  background-color: #cccccc;
}
table, th, td
{
  font-family:Arial, Helvetica, sans-serif;
  border: 1px solid black;
  text-align: right;
}
"""

    
    
def draw_fig(data):
    """Returns html equivalent of matplotlib figure

    Parameters
    ----------
    fig_type: string, type of figure
            one of following:
                    * line
                    * bar

    Returns
    --------
    d3 representation of figure
    """
    fig_type1=data["plot_type"]
    fig_type2=data["plot_type2"]
    location=data["location"]
    view=data["view"]
    location=float(location)
    
    
    if location!=16:
        query_results=combined_data[combined_data['location']==location]
    else:
        query_results=combined_data.copy()
        
    if location ==16:
        query_results=query_results.groupby(query_results.index).mean()
    print query_results['location'].unique()
        
    print view
    if view=='dayofweek':
        query_results=query_results.groupby(query_results.index.dayofweek).mean()
    elif view == 'month':
        query_results=query_results.groupby(query_results.index.month).mean()        
    elif view == 'all':
        query_results=query_results.asfreq('1d')
        
    x=query_results.index
    if len(x)==0:
        return ""
   
    #df = pd.DataFrame(index=range(x.shape[0]))
    #df['x'] = x
    with lock:
        
        
        fig, ax_all = plt.subplots(nrows=2, sharex=True, figsize=(8, 4))
        
        for i,fig_type in enumerate([fig_type1, fig_type2]):
            ax=ax_all[i]
            if fig_type == "Pollution":
                target = 'value'
                ax.set_ylabel('PM2.5 Pollution (ppm)',fontsize=17)
            elif fig_type == "Traffic":
                ax.set_ylabel('Traffic Score',fontsize=17)
                target ='local_traffic'
                # plugins.connect(fig, plugins.LineLabelTooltip(lines[0]))

            elif fig_type == "Temperature":
                ax.set_ylabel('Temperature  (C)',fontsize=17)
                target='TempAvg'

            elif fig_type == "Wind":
                ax.set_ylabel('Wind Velocity',fontsize=17)
                target='Wind_v'

            elif fig_type == "Heating":
                ax.set_ylabel('Heating Oil Consumption',fontsize=17)
                target='Consumption_Oil'

            elif fig_type == "scatter":
                N = query_results['TempMax'].count()
                query_results['TempMax'].plot(ax=ax1)
                scatter = ax1.scatter(query_results.index,
                                     query_results['TempMax'],
                                     c='r',
                                     s=50,
                                     alpha=0.3,
                                     cmap=plt.cm.jet)
                ax1.grid(color='white', linestyle='solid')

                labels = ['point {0}'.format(i + 1) for i in range(N)]
                tooltip = mpld3.plugins.PointLabelTooltip(scatter, labels=labels)
                mpld3.plugins.connect(fig, tooltip)

            elif fig_type == "Reduction":
                ax.set_ylabel('Pollution Reduction',fontsize=17)
                target='reduction'

            query_results[target].plot(ax=ax)
            scatter_out=query_results.dropna()
            scatter = ax.scatter(scatter_out.index,
                                     scatter_out[target],
                                     c='r',
                                     s=200,
                                     alpha=0,
                                     cmap=plt.cm.jet)
            ax.grid(color='white', linestyle='solid')
            labels = ['value: {0}'.format(np.round(i)) for i in scatter_out[target].as_matrix()]
            tooltip = mpld3.plugins.PointLabelTooltip(scatter, labels=labels)
            mpld3.plugins.connect(fig, tooltip)            
            ax.yaxis.labelpad = 10 


        if view=='dayofweek':
            ax.set_xlabel('Day of Week',fontsize=17)
        elif view == 'month':
            ax.set_xlabel('Month of Year',fontsize=17)
        elif view == 'all':
            ax.set_xlabel('Time',fontsize=17)

    return mpld3.fig_to_html(fig,figid='fig')


@app.route('/')
def home():
    print 'home'
    return render_template('index_mpld3.html')

@app.route('/about')
def aboutme():
    return render_template("aboutme.html")


@app.route('/query', methods=['POST'])
def query():
    print request.data
    data = json.loads(request.data)
    print data
    print type(data["location"])
    return draw_fig(data)
