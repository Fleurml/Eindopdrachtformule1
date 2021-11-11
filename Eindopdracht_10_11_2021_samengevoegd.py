#!/usr/bin/env python
# coding: utf-8

# # F1

# ## Packages inladen

# In[1]:


import pandas as pd
import numpy as np
import folium
import plotly.express as px
import statsmodels.api as sm
import streamlit as st
from streamlit_folium import folium_static


# In[2]:


st.title('Formule1')


# In[3]:


st.write('Over de formule 1')


# ## Data inladen

# In[4]:


laptimes = pd.read_csv('lapTimes.csv')
# laptimes.head()


# In[5]:


drivers = pd.read_csv('drivers.csv')
# drivers.head()


# In[6]:


pitstops = pd.read_csv('pitStops.csv')
# pitstops.head()


# In[7]:


results = pd.read_csv('results.csv')
# results.head()


# In[8]:


circuits = pd.read_csv('circuits.csv')
# circuits.head()


# In[9]:


races = pd.read_csv('races.csv')
# races.head()


# ## Histogram maken

# In[10]:


laptimes['seconds'] = laptimes['milliseconds'] / 1000


# In[11]:


laptimes_names = laptimes.merge(drivers, how='left', on='driverId').iloc[:,:9]
#laptimes_names.head()


# In[12]:


laptimes_spanje_2016 = laptimes_names[laptimes_names['raceId'] == 952]
#laptimes_spanje_2016.head()


# In[13]:


#laptimes_spanje_2016['driverRef'].unique()


# In[14]:


fig1 = px.histogram(laptimes_spanje_2016, x='seconds',
                   nbins=500,
                   range_x=['85', '100'],
                   title='Ronde tijden race Spanje 2016',
                   opacity=0.8,
                   color_discrete_sequence=['indianred']
                   )
#fig1.show()


# In[15]:


st.plotly_chart(fig1)


# ## Scattered plot

# In[16]:


fig = px.scatter(laptimes_spanje_2016, 
                 x='lap', 
                 y='seconds', 
                 color='driverRef', 
                 hover_data=['driverId'],
                 marginal_y='histogram')

fig.update_layout(title= {'text':'Laptimes in seconds Spain 2016', 'x':0.39, 'y':0.95},
                  xaxis= {'title': {'text': 'Lap'}},
                  yaxis= {'title':{'text': 'Laptime (s)'}}, 
                  width=950, height=600, 
                  legend_title='Drivers', 
                  legend= dict( yanchor="top",
                              y=0.95,
                              xanchor="left",
                              x=1.01))

#fig.show()


# In[17]:


laptimes_spanje_2016_ZU = laptimes_spanje_2016[laptimes_spanje_2016['seconds'] <= 100]
#laptimes_spanje_2016_ZU.head()


# In[18]:


fig = px.scatter(laptimes_spanje_2016_ZU, 
                 x='lap', 
                 y='seconds', 
                 color='driverRef', 
                 hover_data=['driverId'],
                 marginal_y='histogram',  
                 trendline='ols', 
                 trendline_scope='overall')

fig.update_layout(title= {'text':'Laptimes in seconds Spain 2016', 'x':0.43, 'y':0.95},
                  xaxis= {'title': {'text': 'Lap'}},
                  yaxis= {'title':{'text': 'Laptime (s)'}, 'range':(86, 100)}, 
                  width=950, height=600, 
                  legend_title='Drivers', 
                  legend= dict( yanchor="top",
                              y=0.95,
                              xanchor="left",
                              x=1.01))

#fig.show()


# ## Regressiemodel

# In[19]:


X = sm.add_constant(laptimes_spanje_2016_ZU['lap'])
Y = laptimes_spanje_2016_ZU['seconds']
model = sm.OLS(Y, X).fit()
predictions = model.predict(X)
#model.summary()


# ## Histogram pitstop tijden

# In[20]:


pitstops['seconds'] = pitstops['milliseconds'] / 1000


# In[21]:


pitstops_names = pitstops.merge(drivers, how='left', on='driverId').iloc[:,:10]
#pitstops_names.head()


# In[22]:


pitstops_spanje_2016 = pitstops_names[pitstops_names['raceId'] == 952]
#pitstops_spanje_2016.head()


# In[23]:


fig = px.histogram(pitstops_spanje_2016, x='seconds',
                   nbins=500,
                   range_x=['20', '40'],
                   title='Pitstop tijden race Spanje 2016',
                   opacity=0.8,
                   color_discrete_sequence=['indianred']
                   )
#fig.show()


# ## Lijndiagram

# In[24]:


results['fastestLapTime'] = pd.to_datetime(results['fastestLapTime'], format='%M:%S.%f')
#results.head(6)


# In[25]:


results['fastest_seconds'] = 60*results.fastestLapTime.dt.minute + results.fastestLapTime.dt.second + 0.000001*results.fastestLapTime.dt.microsecond
results = results.sort_values('raceId')
#results


# In[26]:


results_new = results.merge(races, how='left', on='raceId')
results_new = results_new[['raceId', 'year', 'name', 'fastestLapTime', 'fastest_seconds']]
results_test = results_new


# In[27]:


results_test['test'] = results_test.groupby('raceId')['fastest_seconds'].transform('mean')
#results_test


# In[28]:


results_test = results_test.drop_duplicates(subset=['raceId', 'year', 'name', 'test'])
results_test = results_test.sort_values('raceId')
#results_test


# In[29]:


fig = px.line(results_test, 
              x = 'year', 
              y = 'test',
              color = 'name')
#fig.show()


# ## Kaart maken

# ### Dataset maken

# In[30]:


# Races met circuits samenvoegen
races_circuits = races.merge(circuits, on='circuitId')

# Gewenste kolommen selecteren
races_circuits1 = races_circuits.loc[:,('raceId', 'year', 'circuitId', 'name_x', 'circuitRef', 'location', 'country', 'lat', 'lng')]

# Resultaten toevoegen aan de races
circuits_winnaar1 = results.merge(races_circuits1, on='raceId')

# Gewenste kolommen selecteren
circuits_winnaar2 = circuits_winnaar1.loc[:,('raceId','driverId', 'position', 'year', 'circuitId', 'name_x', 'circuitRef', 'location', 'country', 'lat', 'lng')]

# Diversnames toevoegen aan de races
circuits_winnaar3 = circuits_winnaar2.merge(drivers, on='driverId')

# Gewenste kolommen selecteren
circuits_winnaar4 = circuits_winnaar3.loc[:,('raceId','driverId' ,'forename' ,'surname' ,'position', 'year', 'circuitId', 'name_x', 'circuitRef', 'location', 'country', 'lat', 'lng')]

# Winnaars selecteren
circuits_winnaar = circuits_winnaar4[circuits_winnaar4['position'] == 1.0]


# ### Kleurenpalet

# In[31]:


def color_producer(type):
    if type == 'Hamilton': 
        return 'aqua'
    elif type == 'Rosberg': 
        return 'lightgreen'
    elif type == 'Ricciardo': 
        return 'darkorange'
    elif type == 'Verstappen': 
        return 'darkblue'
    elif type == 'Vettel':
        return 'red'
    elif type == 'alonso':
        return 'black'
    elif type == 'R�_ikk̦nen':
        return 'darkred'
    elif type == 'Webber':
        return 'yellow'
    elif type == 'Button':
        return 'grey'
    elif type == 'Maldonado':
        return 'green'


# ###  Kaart

# In[32]:


def add_categorical_legend(folium_map, title, colors, labels):
    if len(colors) != len(labels):
        raise ValueError("colors and labels must have the same length.")

    color_by_label = dict(zip(labels, colors))
    
    legend_categories = ""     
    for label, color in color_by_label.items():
        legend_categories += f"<li><span style='background:{color}'></span>{label}</li>"
        
    legend_html = f"""
    <div id='maplegend' class='maplegend'>
      <div class='legend-title'>{title}</div>
      <div class='legend-scale'>
        <ul class='legend-labels'>
        {legend_categories}
        </ul>
      </div>
    </div>
    """
    script = f"""
        <script type="text/javascript">
        var oneTimeExecution = (function() {{
                    var executed = false;
                    return function() {{
                        if (!executed) {{
                             var checkExist = setInterval(function() {{
                                       if ((document.getElementsByClassName('leaflet-top leaflet-right').length) || (!executed)) {{
                                          document.getElementsByClassName('leaflet-top leaflet-right')[0].style.display = "flex"
                                          document.getElementsByClassName('leaflet-top leaflet-right')[0].style.flexDirection = "column"
                                          document.getElementsByClassName('leaflet-top leaflet-right')[0].innerHTML += `{legend_html}`;
                                          clearInterval(checkExist);
                                          executed = true;
                                       }}
                                    }}, 100);
                        }}
                    }};
                }})();
        oneTimeExecution()
        </script>
      """
   

    css = """

    <style type='text/css'>
      .maplegend {
        z-index:9999;
        float:right;
        background-color: rgba(255, 255, 255, 1);
        border-radius: 5px;
        border: 2px solid #bbb;
        padding: 10px;
        font-size:12px;
        positon: relative;
      }
      .maplegend .legend-title {
        text-align: left;
        margin-bottom: 5px;
        font-weight: bold;
        font-size: 90%;
        }
      .maplegend .legend-scale ul {
        margin: 0;
        margin-bottom: 5px;
        padding: 0;
        float: left;
        list-style: none;
        }
      .maplegend .legend-scale ul li {
        font-size: 80%;
        list-style: none;
        margin-left: 0;
        line-height: 18px;
        margin-bottom: 2px;
        }
      .maplegend ul.legend-labels li span {
        display: block;
        float: left;
        height: 16px;
        width: 30px;
        margin-right: 5px;
        margin-left: 0;
        border: 0px solid #ccc;
        }
      .maplegend .legend-source {
        font-size: 80%;
        color: #777;
        clear: both;
        }
      .maplegend a {
        color: #777;
        }
    </style>
    """

    folium_map.get_root().header.add_child(folium.Element(script + css))

    return folium_map


# In[33]:


m = folium.Map(tiles = 'cartodb positron')

jaar2010 = folium.FeatureGroup(name="2010", show=False).add_to(m)
jaar2011 = folium.FeatureGroup(name="2011", show=False).add_to(m)
jaar2012 = folium.FeatureGroup(name="2012", show=False).add_to(m)
jaar2013 = folium.FeatureGroup(name="2013", show=False).add_to(m)
jaar2014 = folium.FeatureGroup(name="2014", show=False).add_to(m)
jaar2015 = folium.FeatureGroup(name="2015", show=False).add_to(m)
jaar2016 = folium.FeatureGroup(name="2016", show=True).add_to(m)

for row in circuits_winnaar[circuits_winnaar['year'] == 2010].iterrows():
    row_values = row[1]
    jaar2010.add_child(folium.CircleMarker(location = [row_values['lat'], row_values['lng']],
                                 popup = row_values['surname'],
                                 radius = 5,
                                 color=color_producer(row_values['surname']),
                                 fill=True,
                                 fill_opacity=1,
                                 fill_color=color_producer(row_values['surname']))).add_to(m)

for row in circuits_winnaar[circuits_winnaar['year'] == 2011].iterrows():
    row_values = row[1]
    jaar2011.add_child(folium.CircleMarker(location = [row_values['lat'], row_values['lng']],
                                 popup = row_values['surname'],
                                 radius = 5,
                                 color=color_producer(row_values['surname']),
                                 fill=True,
                                 fill_opacity=1,
                                 fill_color=color_producer(row_values['surname']))).add_to(m)

for row in circuits_winnaar[circuits_winnaar['year'] == 2012].iterrows():
    row_values = row[1]
    jaar2012.add_child(folium.CircleMarker(location = [row_values['lat'], row_values['lng']],
                                 popup = row_values['surname'],
                                 radius = 5,
                                 color=color_producer(row_values['surname']),
                                 fill=True,
                                 fill_opacity=1,
                                 fill_color=color_producer(row_values['surname']))).add_to(m)

for row in circuits_winnaar[circuits_winnaar['year'] == 2013].iterrows():
    row_values = row[1]
    jaar2013.add_child(folium.CircleMarker(location = [row_values['lat'], row_values['lng']],
                                 popup = row_values['surname'],
                                 radius = 5,
                                 color=color_producer(row_values['surname']),
                                 fill=True,
                                 fill_opacity=1,
                                 fill_color=color_producer(row_values['surname']))).add_to(m)

for row in circuits_winnaar[circuits_winnaar['year'] == 2014].iterrows():
    row_values = row[1]
    jaar2014.add_child(folium.CircleMarker(location = [row_values['lat'], row_values['lng']],
                                 popup = row_values['surname'],
                                 radius = 5,
                                 color=color_producer(row_values['surname']),
                                 fill=True,
                                 fill_opacity=1,
                                 fill_color=color_producer(row_values['surname']))).add_to(m)

for row in circuits_winnaar[circuits_winnaar['year'] == 2015].iterrows():
    row_values = row[1]
    jaar2015.add_child(folium.CircleMarker(location = [row_values['lat'], row_values['lng']],
                                 popup = row_values['surname'],
                                 radius = 5,
                                 color=color_producer(row_values['surname']),
                                 fill=True,
                                 fill_opacity=1,
                                 fill_color=color_producer(row_values['surname']))).add_to(m)

for row in circuits_winnaar[circuits_winnaar['year'] == 2016].iterrows():
    row_values = row[1]
    jaar2016.add_child(folium.CircleMarker(location = [row_values['lat'], row_values['lng']],
                                 popup = row_values['surname'],
                                 radius = 5,
                                 color=color_producer(row_values['surname']),
                                 fill=True,
                                 fill_opacity=1,
                                 fill_color=color_producer(row_values['surname']))).add_to(m)
    

title_html = '''
<h3 align="center" style="font-size:20px"><b>Formule 1 2010-2016</b></h3>
'''
m.get_root().html.add_child(folium.Element(title_html))
    
add_categorical_legend(m, 'Winnaar van de race', 
                       colors = ['aqua', 'lightgreen', 'darkorange', 'darkblue', 'red', 'black', 'darkred', 'yellow', 'grey', 'green'], 
                       labels = ['Hamilton', 'Rosberg','Ricciardo','Verstappen', 'Vettel', 'Alonso', 'raikkonen', 'Webber', 'Button', 'Maldonado'])

folium.LayerControl(position='topleft', collapsed=False).add_to(m)

#m

folium_static(m)


# In[ ]:




