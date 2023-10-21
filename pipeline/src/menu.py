from ipywidgets import widgets, Vbox, HBox
import pandas as pd
import numpy as pd

style = {"description_width": "intiial"}

def setup_menu(
        widget_vehicle_type,
        widget_year,
        widget_vehicle_class,
        widget_make,
        widget_co2,
):
    """
    Setup the menu for the voila app
    
    Parameters
    ----------
    
    widget_vehicle_type : ipywidgets.Dropdown
        dropdown widget for vehicle type
    widget_year : ipywidgets.Combobox
        combobox widget for year
    widget_make : ipywidgets.Combobox
        combobox widget for make
    widget_vehicle_class : ipywidgets.SelectMultiple
        select multiple widget for vehcile class
    widget_co2 : ipywidgets.Intslider
        int slider widget for CO2 rating
        
    Returns
    -------
    tab : ipywidgets.Tab
        tab object containing the menu"""
    
    tab3 = Vbox(
        children=[
            HBox(children=[widget_vehicle_type, widget_year]),
            HBox(children=[widget_vehicle_class, widget_make]),
            HBox(children=[widget_co2]),

        ]
    )

    tab = widgets.Tab(children=[tab3])
    tab.set_title(0, "Choose parameters")

    return tab

def init_widgets(years, makes, classes, vehicle_type, style):
    """Initialize widgets
    
    Paramters
    ---------
    years : list
        list of years
    makes : list
        list of makes
    classes : list
        list of car classes
    vehicle_type : list
        list of vehicle types
    style : dict
        style dictionary for widgets
    
    Returns
    -------
    widget_vehicle_type : ipywidgets.Dropdown
        dropdown widget for vehicle type
    widget_year : ipywidgets.Combobox
        combobox widget for year
    widget_make : ipywidgets.Combobox
        combobox widget for make
    widget_vehicle_class : ipywidgets.SelectMultiple
        select multiple widget for vehcile class
    widget_co2 : ipywidgets.Intslider
        int slider widget for CO2 rating
    
    """
    widget_vehicle_type = widgets.Dropdown(
        options=vehicle_type,
        description="Vehicle type",
        value="fuel-only",
        style=style,
    )

    widget_year = widgets.Combobox(
        options=years,
        description="Model year",
        value="2023",
        style=style,
    )

    widget_make = widgets.Combobox(
        placeholder="Select of type a car brand",
        options=makes,
        value="acura",
        description="Car brand",
    )

    widget_vehicle_class = widgets.SelectMultiple(
        options=classes,
        description="Vehicle class",
        value=classes,
        style=style,
    )

    widget_co2 = widgets.IntSlider(
        value=5,
        min=0,
        max=10,
        step=1,
        description="CO2 rating >=",
        disabled=False,
        style=style,
    )

    return (
        widget_vehicle_type,
        widget_year,
        widget_make,
        widget_vehicle_class,
        widget_co2,
    )

def select_table(vehicle_type, year, vehicle_class, make, co2):
    """
    Select tabel based on vehicle class
    
    Parameters
    ----------
    vehicle_type : str
        Vehicle type (fuel only, hybrid, or electic)
    year : int
        Model year
    vehicle_class : list
        Vehicle class (compact, midsize, etc.)
    make : str
        Car manufacturer
    co2 : int
        CO2 rating
    
    Returns
    -------
    df : DataFrame
        Filtered DataFrame
    """
    query = f"""SELECT model_year,
                make,
                model,
                vehicle_class,
                vehicle_type
                co2_rating,
            FROM all_vehicles
            WHERE model_year = {year}
            AND vehicle_class IN {vehicle_class}
            AND vehicle_type = '{vehicle_type}'
            AND make = '{make}'
            AND co2_rating >= {co2}
            """
    return query

def clean_electric_car_range(electric_range):
    #todo: Add function body
    pass