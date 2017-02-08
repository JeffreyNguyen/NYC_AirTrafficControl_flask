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


pie_fracs = [20, 30, 40, 10]
pie_labels = ["A", "B", "C", "D"]






labels = []
#N=100
#for i in range(N):
    #label = df.ix[[i], :].T
    #label.columns = ['Row {0}'.format(i)]
    # .to_html() is unicode; so make leading 'u' go away with str()
    #labels.append(str(label.to_html()))
    
    
    
    
    
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
    fig_type=data["plot_type"]
    location=data["location"]
    view=data["view"]
    location=float(location)
    
    
    if location!=16:
        query_results=combined_data[combined_data['location']==location]
    else:
        query_results=combined_data.copy()
        
    if location ==16:
        query_results=query_results.groupby(query_results.index).mean()
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
        fig, (ax0, ax1) = plt.subplots(nrows=2, sharex=True, figsize=(8, 4))
        y = query_results['value'].plot(ax=ax0)
        ax0.set_xlabel('Time')
        ax0.set_ylabel('PM2.5 (ppm)')
        if fig_type == "Pollution":
            y = query_results['value'].plot(ax=ax1)
        elif fig_type == "Traffic":
            ax1.set_ylabel('Traffic Score')
            lines = query_results['local_traffic'].plot(ax=ax1)
            # plugins.connect(fig, plugins.LineLabelTooltip(lines[0]))

        elif fig_type == "Temperature":
            ax1.set_ylabel('Maximum Temperature  (C)')
            #print query_results['TempMax']
            y = query_results['TempMax'].plot(ax=ax1)
            #points=ax1.scatter(query_results.index,query_results['TempMax'],
            #           c='r',
            #           s=50,
            #           alpha=0,
            #           cmap=plt.cm.jet)
            
            #labels=query_results['TempMax'].values.astype(str)
            #tooltip = plugins.PointHTMLTooltip(points, labels=labels,
            #                       voffset=10, hoffset=10, css=css)
            
            #plugins.connect(fig, tooltip)
            
        elif fig_type == "Wind":
            ax1.set_ylabel('Wind Velocity')
            y = query_results['Wind_v'].plot(ax=ax1)
        elif fig_type == "Heating":
            ax1.set_ylabel('Heating Oil Consumption')
            y = query_results['Consumption_Oil'].plot(ax=ax1)
            
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
            ax1.set_ylabel('Pollution Reduction')
            y = query_results['reduction'].plot(ax=ax1);
        elif fig_type == "area":
            ax.plot(x, y)
            ax.fill_between(x, 0, y, alpha=0.2)
            
    if view=='dayofweek':
        ax1.set_xlabel('Day of Week')
    elif view == 'month':
        ax1.set_xlabel('Month of Year')
    elif view == 'all':
        # start=datetime.datetime(year=2011,month=9,day=1);
        end=datetime.datetime(year=2013,month=1,day=1);
        # plt.xlim(start,end)            
        # ax1.set_xlabel('Time')

        #plugins.connect(fig, plugins.MousePosition(fontsize=14))
        
    #fig.autofmt_xdate()
    return mpld3.fig_to_html(fig,figid='fig')

#app = Flask(__name__)

def polynomial():
    """ Very simple embedding of a polynomial chart
    """

    # Grab the inputs arguments from the URL
    args = request.args

    # Get all the form arguments in the url with defaults
    color = colors[getitem(args, 'color', 'Black')]
    _from = int(getitem(args, '_from', 0))
    to = int(getitem(args, 'to', 10))

    # Create a polynomial line graph with those arguments
    x = list(range(_from, to + 1))
    fig = figure(title="Polynomial")
    fig.line(x, [i ** 2 for i in x], color=color, line_width=2)

    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    script, div = components(fig)
    return render_template('index_mpld3.html',script=script, div=div)




@app.route('/')
def home():
    print 'home'
    return render_template('index_mpld3.html')


@app.route('/query', methods=['POST'])
def query():
    print request.data
    data = json.loads(request.data)
    print data
    print type(data["location"])
    return draw_fig(data)
    #return polynomial()

#if __name__ == '__main__':
#app.run(debug=True, host='0.0.0.0')
