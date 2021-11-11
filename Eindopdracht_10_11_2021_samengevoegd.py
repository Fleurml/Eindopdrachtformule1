#!/usr/bin/env python
# coding: utf-8

# # Formule1

# ## Packages inladen

# In[1]:


import pandas as pd
import numpy as np
import folium
import plotly.express as px
import statsmodels.api as sm
import streamlit as st
from streamlit_folium import folium_static


# ## Streamlit

# In[2]:


st.title('Formule 1: 1950-2016')


# In[3]:


st.markdown('Timon van Leeuwen (500782708) en Fleur Molenaar (500802473)')


# In[4]:


st.info('De gebruikte data komt van Kaggle. '
        'https://www.kaggle.com/cjgdev/formula-1-race-data-19502017?select=lapTimes.csv. ' 
        'We hebben gebruikt gemaakt van de datasets: circuits, drivers, lapTimes, pitStops, races en results.')


# In[5]:


Hist, Lijn, Spreid = st.columns(3)


# In[6]:


Kaart, Legenda, Regres = st.columns(3)


# ## Data inladen

# In[7]:


laptimes = pd.read_csv('lapTimes.csv')


# In[8]:


drivers = pd.read_csv('drivers.csv')


# In[9]:


pitstops = pd.read_csv('pitStops.csv')


# In[10]:


results = pd.read_csv('results.csv')


# In[11]:


circuits = pd.read_csv('circuits.csv')


# In[12]:


races = pd.read_csv('races.csv')


# ## Histogram rondetijden spanje 2016

# In[13]:


# milleseconde omzetten naar seconden
laptimes['seconds'] = laptimes['milliseconds'] / 1000


# In[14]:


# laptimes met drivers merge
laptimes_names = laptimes.merge(drivers, how='left', on='driverId').iloc[:,:9]


# In[15]:


# laptimes van spanje 2016 selecteren
laptimes_spanje_2016 = laptimes_names[laptimes_names['raceId'] == 952]


# In[16]:


#Histogram van laptimes spanje 2016
fig1 = px.histogram(laptimes_spanje_2016, x='seconds',
                   nbins=500,
                   range_x=['85', '100'],
                   opacity=0.8,
                   color_discrete_sequence=['indianred']
                   )

fig1.update_layout(title= {'text': 'Ronde tijden race Spanje 2016', 'x':0.39, 'y':0.95},
                  xaxis= {'title': {'text': 'Laptime (s)'}},
                  yaxis= {'title':{'text': 'Count'}}, 
                  width=600, height=350)
#fig1.show()


# In[17]:


# Streamlit Histogram
with Hist:
    st.plotly_chart(fig1)


# ## Scattered plot van de rondetijden per rondje

# ### Scattered plot van de rondetijden per rondje van alle waarden

# In[18]:


# Scattered plot van de rondetijden per rondje
fig2 = px.scatter(laptimes_spanje_2016, 
                 x='lap', 
                 y='seconds', 
                 color='driverRef', 
                 hover_data=['driverId'],
                 marginal_y='histogram')

fig2.update_layout(title= {'text':'Laptimes in seconds Spain 2016', 'x':0.39, 'y':0.95},
                  xaxis= {'title': {'text': 'Lap'}},
                  yaxis= {'title':{'text': 'Laptime (s)'}}, 
                  width=600, height=350, 
                  legend_title='Drivers', 
                  legend= dict( yanchor="top",
                              y=0.95,
                              xanchor="left",
                              x=1.01))

#fig2.show()


# ### Scattered plot van de rondetijden per rondje zonder eerste rondje en rondje met pitstop

# In[19]:


# Eerste rondje en rondes met pitstop eruit filteren
laptimes_spanje_2016_ZU = laptimes_spanje_2016[laptimes_spanje_2016['seconds'] <= 100]


# In[20]:


# Scattered plot van de rondetijden per rondje
fig3 = px.scatter(laptimes_spanje_2016_ZU, 
                 x='lap', 
                 y='seconds', 
                 color='driverRef', 
                 hover_data=['driverId'],
                 marginal_y='histogram',  
                 trendline='ols', 
                 trendline_scope='overall')

fig3.update_layout(title= {'text':'Laptimes in seconds Spain 2016', 'x':0.43, 'y':0.95},
                  xaxis= {'title': {'text': 'Lap'}},
                  yaxis= {'title':{'text': 'Laptime (s)'}, 'range':(86, 100)}, 
                  width=550, height=350, 
                  legend_title='Drivers', 
                  legend= dict( yanchor="top",
                              y=0.95,
                              xanchor="left",
                              x=1.01))

#fig3.show()


# In[21]:


# Streamlit spreidingsdiagram
with Spreid:
    st.plotly_chart(fig3)


# ## Regressiemodel

# In[22]:


# Lineair model
X = sm.add_constant(laptimes_spanje_2016_ZU['lap'])
Y = laptimes_spanje_2016_ZU['seconds']
model = sm.OLS(Y, X).fit()
predictions = model.predict(X)
model.summary()


# In[23]:


# Streamlit lineair model
with Regres:
    st.subheader('Regressiemodel')
    st.latex(r''' Y = Rondetijd, X = Ronde ''')
    st.latex(r''' Y = -0.0333X + 92.7113 ''')
    st.write('Per ronde die een coureur rijdt gaat de rondetijd met 0.03 seconden naar beneden. '
             'Het model heeft een R-squared van 0.140. Dit betekent dat het model voor 14% goed kan voorspellen. '
             'Dit is een redelijk laag getal, waarschijnlijk omdat het model op basis is van alle coureurs ' 
             'en niet alle coureurs dezelfde trend hebben. ' 
             'De P-waardes van de coëfficienenten zijn nul dat betekent dat er een statistisch significant verschil is. '
             'De gevonden coëfficienten zijn niet met toeval gevonden.')


# ## Lijndiagram

# ### Dataset maken

# In[24]:


results['fastestLapTime'] = pd.to_datetime(results['fastestLapTime'], format='%M:%S.%f')


# In[25]:


results['fastest_seconds'] = 60*results.fastestLapTime.dt.minute + results.fastestLapTime.dt.second + 0.000001*results.fastestLapTime.dt.microsecond
results = results.sort_values('raceId')


# In[26]:


results_new = results.merge(races, how='left', on='raceId')
results_new = results_new[['raceId', 'year', 'name', 'fastestLapTime', 'fastest_seconds']]
results_test = results_new


# In[27]:


results_new['Mean_sec'] = results_new.groupby('raceId')['fastest_seconds'].transform('mean')


# In[28]:


results_new = results_new.drop_duplicates(subset=['raceId', 'year', 'name', 'Mean_sec'])
results_new = results_new.sort_values('raceId')


# In[29]:


results_new = results_new.dropna()
results_new.groupby('name').count()
results_new = results_new.sort_values('year')


# ###  Lijndiagram van de gemiddelde rondetijd per jaar van de circuits

# In[30]:


# Lijndiagram van de gemiddelde rondetijd per jaar van de circuits
fig5 = px.line(results_new, 
              x = 'year', 
              y = 'Mean_sec',
              color = 'name')

fig5.update_layout(title= {'text':'Mean laptimes of circuits in seconds per year', 'x':0.43, 'y':0.95},
                  xaxis= {'title': {'text': 'Year'}},
                  yaxis= {'title':{'text': 'Laptime (s)'}, 'range':(70, 123)}, 
                  width=600, height=350, 
                  legend_title='Circuits', 
                  legend= dict( yanchor="top",
                              y=0.95,
                              xanchor="left",
                              x=1.01))

#fig5.show()


# In[31]:


# Streamlit lijndiagram
with Lijn:
    st.plotly_chart(fig5)


# ## Kaart maken

# ### Dataset maken

# In[32]:


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

# In[33]:


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

# In[34]:


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


# In[35]:


# Kaart maken
m = folium.Map(width=600,height=350, tiles = 'cartodb positron')

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
                       labels = ['Hamilton', 'Rosberg','Ricciardo','Verstappen', 'Vettel', 'Alonso', 'Raikkonen', 'Webber', 'Button', 'Maldonado'])



folium.LayerControl(position='topleft', collapsed=False).add_to(m)
m


# In[36]:


# Streamlit Kaart
with Kaart:
    st.subheader('Formule 1 2010-2016')
    folium_static(m)


# In[37]:


# Streamlit legenda
image = 'legenda.PNG'

with Legenda:
    st.image(image)


# In[38]:


# st.info('De gebruikte data komt van Kaggle.'
#         'https://www.kaggle.com/cjgdev/formula-1-race-data-19502017?select=lapTimes.csv ' 
#         'We hebben gebruikt gemaakt van de datasets: circuits, drivers, lapTimes, pitStops, races en results')

