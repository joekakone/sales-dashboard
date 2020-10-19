# coding : utf-8

import pandas as pd
import numpy as np
from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.transform import cumsum
from bokeh.palettes import Category20c
from bokeh.models import ColumnDataSource, DataTable, TableColumn, HoverTool, LabelSet
from bokeh.models import WMTSTileSource

##### title ####
curdoc().title = 'Sales Dashboard'

##### KPIS #####
clients = 2070
revenue = 1305805
orders = 2095
average_order = 3380

# make variables available in html templates
curdoc().template_variables['clients'] = clients
curdoc().template_variables['revenue'] = revenue
curdoc().template_variables['orders'] = orders
curdoc().template_variables['average_order'] = average_order

##### Bokeh Plots ####

### Start Pie Chart ###
def gen_goal_data():
    goal = 1945000
    current = 1620500
    
    dt = pd.DataFrame({'item': ['Achieved', 'Rest'], 'part': [current, goal-current]})
    
    return dt

goaldata = gen_goal_data()

def PieChart(data, item_col, part_col):
    # transform
    data = data.copy()
    data['percent'] = data['part']/data['part'].sum() * 100
    data['percent']  = data['percent'].apply(lambda x: str(round(x, 2))+'%')
    data['angle'] = data['part']/data['part'].sum() * 2*3.14
    data['color'] = ['pink', 'gray']
    
    # hover
    tooltips = f"@{item_col}: @{part_col}"
    
    pie = figure(x_range=(-1, 1),
                 plot_width=250,
                 height=250,
                 toolbar_location=None,
                 tools="",
                 tooltips=tooltips,
                 name='piechart')
    
    # convert into ColumnDataSource
    source = ColumnDataSource(data)

    pie.annular_wedge(x=0,
                      y=1,
                      inner_radius=0.5,
                      outer_radius=0.8,
                      start_angle=cumsum('angle',include_zero=True),
                      end_angle=cumsum('angle'),
                      color='color',
                      alpha=0.7,
                      source=source)
    
    label = LabelSet(x=-.3,
                     y=1,
                     x_offset=0,
                     y_offset=0,
                     text=[data[data[item_col]=='Achieved']['percent'].values[0]],
                     text_baseline="middle",
                     text_font_size="24px")
    pie.add_layout(label)

    # others params
    pie.axis.axis_label = None
    pie.axis.visible = False
    pie.grid.grid_line_color = None

    return pie

piechart = PieChart(goaldata, 'item', 'part')

curdoc().add_root(piechart)
### End Pie Chart ###


### Start Line Plot ###
def gen_time_series():
    xticks = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    values = [1500, 1221, 1490, 1750, 1620, 1600, 1510]
    
    series = pd.DataFrame({'xtick': xticks, 'value': values})
    
    return series

series = gen_time_series()

def TimeSeriesPlot(data, xtick_col, value_col):
    plot = bar = figure(x_range=data[xtick_col],
                        plot_width=540,
                        height=250,
                        toolbar_location=None,
                        tools="",
                        name='line')
    
    # convert into ColumnDataSource
    source = ColumnDataSource(data)
    
    plot.vbar(x=xtick_col, top=value_col, width=.5, color='gray', alpha=0.7, source=source)
    
    plot.line(x=xtick_col, y=value_col, color='pink', line_width=3, source=source)
    
    plot.circle(x=xtick_col, y=value_col, line_color='pink', fill_color='white', size=10, source=source)
    
    label = LabelSet(x=xtick_col,
                     y=value_col,
                     x_offset=0,
                     y_offset=0,
                     text=value_col,
                     text_baseline="middle",
                     text_font_size="12px",
                     source=source)
    plot.add_layout(label)
    
    # others params
    plot.y_range.start = 0
    plot.xgrid.grid_line_color = None
    
    return plot

line = TimeSeriesPlot(series, 'xtick', 'value')

curdoc().add_root(line)
### End Line Plot ###


##### Charts #####
def gen_product_top5():
    products = {
        'product': ['Product A', 'Product B', 'Product C', 'Product D', 'Product E'],
        'sales': [12, 37, 25, 20, 22]
    }
    products = pd.DataFrame(products)

    products = products.sort_values(by='sales')
    
    return products

products = gen_product_top5()

def HBarChart(data, item_col, count_col):
    # hover
    tooltips = f"@{item_col}: @{count_col}"

    bar = figure(y_range=data[item_col],
                 plot_width=250,
                 height=250,
                 toolbar_location=None,
                 tools="",
                 tooltips=tooltips,
                 name='barchart')
    
    # convert into ColumnDataSource
    source = ColumnDataSource(data)

    bar.hbar(y=item_col, right=count_col, height=0.5, color='gray', alpha=0.7, source=source)

    # others params
    bar.x_range.start = 0
    bar.xaxis.visible = False
    bar.yaxis.axis_line_color = None
    bar.grid.grid_line_color = None
    
    return bar

barchart = HBarChart(products, 'product', 'sales')

curdoc().add_root(barchart)
### End Bar Chart ###


### Map Plot ###
def gen_geo_data():
    geodata = {
        'city': ['Cotonou', 'Porto-Novo', 'Ouidah'],
        'latitude': [6.366667, 6.497222, 6.366667],
        'longitude': [2.433333, 2.605, 2.083333]
    }
    geodata = pd.DataFrame(geodata)
    
    return geodata

geodata = gen_geo_data()

def MapPlot(data):
    def wgs84_to_web_mercator(df, lon="longitude", lat="latitude"):
        """Converts decimal longitude/latitude to Web Mercator format"""
        k = 6378137
        df["x"] = df[lon] * (k * np.pi/180.0)
        df["y"] = np.log(np.tan((90 + df[lat]) * np.pi/360.0)) * k
        return df
    
    data = wgs84_to_web_mercator(data)
    
    x_range = (data['x'].min()-10000, data['x'].max()+10000)
    y_range = (data['y'].min() ,data['y'].max())
    
    # convert into ColumnDataSource
    source = ColumnDataSource(data)
    
    mapplot = figure(plot_width=540,
                     plot_height=250,
                     x_range=x_range,
                     y_range=y_range,
                     x_axis_type="mercator",
                     y_axis_type="mercator",
                     toolbar_location=None,
                     tools='',
                     name='geoplot')

    # credits
    MAP_URL = 'http://a.basemaps.cartocdn.com/rastertiles/voyager/{Z}/{X}/{Y}.png'
    attribution = "Tiles by Carto, under CC BY 3.0. Data by OSM, under ODbL"
    mapplot.add_tile(WMTSTileSource(url=MAP_URL, attribution=attribution))

    mapplot.circle(x='x', y='y', fill_color='pink', size=20, fill_alpha=0.3, line_color=None, source=source)

    # hover
    mapplot.add_tools(HoverTool(tooltips=[
        ('City', '@city'),
        ('Latitude', "@latitude"),
        ('Longitude', "@longitude")
        ]))
    
    # others params
    mapplot.axis.visible = False
    
    return mapplot

mapplot = MapPlot(geodata)

curdoc().add_root(mapplot)
### End Map Plot ###


### Start Table ###
def gen_client_top10():
    clients = {
        'client': [
            'Sam Smith',
            'Sarah Guido',
            'Bruce Lee',
            'Elon Musk',
            'Claire Mathieu',
            'Gérard Berry',
            'Donald Trump',
            'Donnie Yen',
            'La Fouine',
            'Charles De Gaule'
        ],
        'orders': [1200, 3750, 2500, 2080, 2275, 750, 2000, 6200, 4500, 4850]
    }
    clients = pd.DataFrame(clients)

    clients = clients.sort_values(by='orders', ascending=False)
    
    return clients

clients = gen_client_top10()


def Table(data, name_col, value_col):
    # convert into ColumnDataSource
    source = ColumnDataSource(data)

    columns = [
        TableColumn(field=name_col, title="Client Name"),
        TableColumn(field=value_col, title="Orders ($)",)
    ]
    table = DataTable(source=source, columns=columns, height=240, width=530, name='table')
    
    return table

table = Table(clients, 'client', 'orders')

curdoc().add_root(table)
### End Table ###