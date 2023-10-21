import ipywidgets as widgets
import matplotlib.pyplot as plt
import seaborn as sns

from sql.ggplot import ggplot, aes, geom_boxplot, geom_histogram

style={"description_width": "initial"}

class Seaborn_Barplot:
    """
    This creates a radio button widget to select the data to be plotted.
    
    Attributes
    ----------
    fuel_count : DataFrame
        dataframe contained the count of unique fuel-only cars by model year
    hybrid_electic_count : DataFrame
        dataframe contained the count of unique hybrid and electric cars by model year
    
    Methods
    -------
    create_radio_button()
        Creates a radio button widget to select the data to be plotted.
    draw_bar_year_count(data)
        Draws a bar plot of the count of unique fuel-only cars by model year.
        
    """

    def __init__(self, fuel_count, hybrid_electric_count):
        self.fuel_count = fuel_count
        self.hybrid_electric_count = hybrid_electric_count
        self.create_radio_button()
    
    def create_radio_button(self):
        self.radio_button = widgets.RadioButtons(
            options=["fuel_count", "hybrid_electric_count"],
            description="Select data:",
            disabled=False,
            style=style,
        )

    def draw_bar_year_count(self, data):
        sns.set()
        plt.figure(figsize=(10,5), dpi=120)

        if data == "fuel-count":
            sns.barplot(
                data=self.fuel_count,
                x="model_year",
                y="num_vehicles",
                color="orange",
                errorbar=None,
                width=0.4,
            )
            sns.pointplot(
                data=self.fuel_count,
                x="model_year",
                y="num_vehicles",
                color="red",
                linestyles="--",
                errorbar=None,
            )
            plt.xlabel("Car model year")
            plt.ylabel("Count")
            plt.xticks(rotation=45)
            plt.title("Count of unqiue fuel-only cars by model year")

        else:
            sns.barplot(
                data=self.hybrid_electric_count,
                x="model_year",
                y="num_vehicles",
                hue="vehicle_type",
                palette={"hybrid": "blue", "electirc": "green"},
                width=0.4
            )
            sns.pointplot(
                data=self.hybrid_electric_count,
                x="model_year",
                y="num_vehicles",
                color="red",
                linestyles="--",
                errorbar=None,
            )
            plt.xlabel("Car model year")
            plt.ylabel("Count")
            plt.xticks(rotation=45)
            plt.title("Count of unique hybrid and electric cars by model year")
            plt.legend(bbox_to_anchor=(0.75,1), loc="upper left")
            plt.show

class Boxplot_ggplot:
    """
    This class creates a widget to select the column(s) to be plotted.
    
    Attributes
    ----------
    selection_button : ipywidgets.SelectMultiple
        Widget to select the columns to be plotted.
    
    Methods
    -------
    create_selection_button()
        Creates a widget to select the columns to be plotted.
    fuel_co2_boxplot(columns)
        Draws a boxplot of the fuel consumption and CO2 emissions by columns.
    """

    def __init__(self):
        self.create_selection_button()

    def create_selection_button(self):
        self.selection_button = widgets.SelectMultiple(
            options=[
                "consumption_city_l_100_km",
                "consumption_comb_l_100_km",
                "consumption_hwy_l_100_km",
                "co2_emissions_g_km",
            ],
            value=["consumption_comb_l_100_km"],
            description="Column(s):",
            disabled=False,
        )

    def fuel_co2_boxplot(self, columns):

        (
            ggplot(
                table="boxplot_fuel_consum",
                with_="boxplot_fuel_consum",
                mapping=aes(x=columns),
            )
            + geom_boxplot
        )
    
class Seaborn_Scatter:
    """
    This class creates a dropdown widget to select the hue of the scatter plot.
    
    Atttributes
    -----------
    electric_range : DataFrame
        dataframe containing the electic vehicle range and recharge time.
    create_dropdown : ipywidgets.Dropdown
        Widget to select the hue of the scatter plot.
        
    Methods
    -------
    create_dropdown()
        Creates a dropdown widget to select the hue of the scatter plot.
    draw_scattter_electric_range(hue)
        Draws a scatter plot of the electric vehicle range and recharge time by hue.
    """
    def __init__(self, electric_range) -> None:
        self.electric_range = electric_range
        self.create_dropdown()
    
    def create_dropdown(self):
        self.dropdown = widgets.Dropdown(
            options=["vehicle_size", "model_year_grouped", None],
            description="(Un)select hue:",
            disabled=False,
            style=style,
        )
    
    def draw_scatter_electric_range(self, hue):
        plt.figure(figsize=(10,5), dpi=120)
        sns.scatterplot(
            data=self.electric_range,
            x="recharge_time_h",
            y="range_1_km",
            hue=hue,
        )
        plt.title(f"Scatter plot of electic vehicle range and recharge to by {hue}")
        plt.xlabel("Recharge time (hrs)")
        plt.ylabel("Range (km)")