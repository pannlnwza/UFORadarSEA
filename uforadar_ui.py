import os
import datetime
import tkinter as tk
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from tkinter import ttk, messagebox
import pandas as pd
from tkintermapview import TkinterMapView
from graph_generator import GraphGenerator
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from data_processor import UFODataProcessor, Country
from PIL import Image, ImageTk
from button import CreateButton
from tkinter.filedialog import asksaveasfile


class MapPage(tk.Frame):
    """
    A frame for the map view page.
    """
    def __init__(self, parent):
        """
        Initialize MapPage.
        :param parent: Parent tkinter App.
        """
        super().__init__()
        self.parent = parent
        self.data = self.parent.data_processor.get_ufo_data()
        image = Image.open(os.path.join(os.getcwd(), 'images', 'marker_icon.png')).resize((40, 40))
        self.MARKER_ICON = ImageTk.PhotoImage(image)
        self.configure(bg='#F8F8FF')
        self.init_components()

    def init_components(self):
        """
        Initialize GUI components.
        """
        map_frame = ttk.Frame(self, borderwidth=2)
        map_frame.grid(row=0, column=0, rowspan=3, padx=5, pady=5, sticky=tk.NSEW)

        # Map view
        self.map_view = TkinterMapView(map_frame, width=600, height=500)
        self.map_view.pack(fill=tk.BOTH, expand=True)

        # Fit bounding box to Southeast Asia
        self.map_view.fit_bounding_box((28.73, 91.20), (-9.5, 128.52))

        # Add position markers for UFO sightings
        self.add_sighting_markers()

        title = tk.Label(self, text='UFORadarSEA', font=('Helvetica', 20, 'bold'), bg='#F8F8FF')
        title.grid(row=0, column=1, pady=5,sticky=tk.S)
        description = tk.Label(self, text='An interactive map to track UFO sightings.', bg='#F8F8FF')
        description.grid(row=1, column=1, pady=1, sticky=tk.N)

        # Filter frame
        self.create_filter_frame()

        # Configure grid weights
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)

    def create_filter_frame(self):
        """
        Create the filter frame.
        """
        self.filter_frame = tk.LabelFrame(self, text='Filter')
        self.filter_frame.grid(row=2, column=1, sticky=tk.NSEW)

        # Create a canvas for the radio buttons
        canvas = tk.Canvas(self.filter_frame, bg='white')
        canvas.grid(row=1, column=0, columnspan=3, sticky=tk.NSEW)

        # Add a scrollbar for the canvas
        scrollbar = ttk.Scrollbar(self.filter_frame, orient='vertical', command=canvas.yview)
        scrollbar.grid(row=1, column=3, sticky=tk.NS)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create a frame to contain the radio buttons
        radiobutton_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=radiobutton_frame, anchor=tk.NW)

        # Country filter
        country_label = tk.Label(radiobutton_frame, text='Country:')
        country_label.grid(row=0, column=0, sticky=tk.W)

        self.country_var = tk.StringVar()
        self.country_var.set('All')
        self.country_radios = []
        countries = self.data['country'].unique().tolist()
        for i, country in enumerate(countries):
            radio = ttk.Radiobutton(radiobutton_frame, text=country,
                                    variable=self.country_var, value=country)
            radio.grid(row=i + 1, column=0, sticky=tk.W, padx=10)
            self.country_radios.append(radio)

        # Year filter
        year_label = tk.Label(radiobutton_frame, text='Year:')
        year_label.grid(row=0, column=1, sticky=tk.W)

        self.year_var = tk.StringVar()
        self.year_var.set('All')
        years = ['1960-1970', '1971-1980', '1981-1990', '1991-2000', '2001-2010', '2011-2020', '2021-2030']
        for i, year in enumerate(years):
            radio = ttk.Radiobutton(radiobutton_frame, text=year,
                                    variable=self.year_var, value=year)
            radio.grid(row=i + 1, column=1, sticky=tk.W, padx=10)

        # Shape filter
        shape_label = tk.Label(radiobutton_frame, text='Shape:')
        shape_label.grid(row=0, column=2, sticky=tk.W)

        self.shape_var = tk.StringVar()
        self.shape_var.set('All')
        self.shape_radios = []
        shapes = self.data['UFO_shape'].unique().tolist()
        for i, shape in enumerate(shapes):
            radio = ttk.Radiobutton(radiobutton_frame, text=shape,
                                    variable=self.shape_var, value=shape)
            radio.grid(row=i + 1, column=2, sticky=tk.W, padx=10)
            self.shape_radios.append(radio)
        canvas.config(scrollregion=canvas.bbox('all'))

        self.apply_button = tk.Button(self.filter_frame, text='Apply Filter', command=self.apply_filter)
        self.apply_button.grid(row=5, column=0, columnspan=3, padx=5, pady=5, sticky=tk.W)
        self.clear_button = tk.Button(self.filter_frame, text='Clear Filter', command=self.clear_filter)
        self.clear_button.grid(row=5, column=0, columnspan=3, padx=5, pady=5, sticky=tk.E)

        # Results listbox
        self.results_listbox = tk.Listbox(self.filter_frame, height=5)
        self.results_listbox.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky=tk.NSEW)
        self.results_listbox.bind('<Double-Button-1>', self.show_result_details)

        self.progress = ttk.Progressbar(self.filter_frame, orient='horizontal', mode='indeterminate', length=275)
        self.progress.grid(row=3, column=0, columnspan=7, padx=10, pady=10, sticky=tk.W)

    def clear_filter(self):
        """
        Clear the applied filters.
        """
        selected_country = self.country_var.get()
        selected_year = self.year_var.get()
        selected_shape = self.shape_var.get()
        self.results_listbox.delete(0, tk.END)
        if selected_year != 'All' or selected_country != 'All' or selected_shape != 'All':
            self.country_var.set('All')
            self.year_var.set('All')
            self.shape_var.set('All')
            self.delete_markers()
            self.add_sighting_markers()
            self.map_view.fit_bounding_box((28.73, 91.20), (-9.5, 128.52))

    def apply_filter(self):
        """
        Apply the selected filters.
        """
        selected_country = self.country_var.get()
        selected_year = self.year_var.get()
        selected_shape = self.shape_var.get()
        filtered_data = self.data
        if selected_country != 'All':
            filtered_data = filtered_data[filtered_data['country'] == selected_country]
        if selected_year != 'All':
            start_year, end_year = map(int, selected_year.split('-'))
            filtered_data = filtered_data[(filtered_data['year_found'] >= start_year) &
                                          (filtered_data['year_found'] <= end_year)]
        if selected_shape != 'All':
            filtered_data = filtered_data[filtered_data['UFO_shape'] == selected_shape]

        if selected_year != 'All' or selected_country != 'All' or selected_shape != 'All':
            self.update_map_markers(filtered_data)
            self.update_results_list(filtered_data)

    def update_results_list(self, data: pd.DataFrame):
        """
        Update the list of filtered results.

        :param data: Filtered UFO sighting data.
        :type data: pandas.DataFrame
        """
        self.results_listbox.delete(0, tk.END)
        if data.empty:
            self.results_listbox.insert(tk.END, 'No result found.')
        else:
            for index, row in data.iterrows():
                self.results_listbox.insert(tk.END, f"Report No. {row['report_no']} - "
                                            f"{row['country']} - {row['year_found']} - {row['UFO_shape']}")

    def update_map_markers(self, filtered_data: pd.DataFrame):
        """
        Update map markers based on filtered data.

        :param filtered_data: Filtered UFO sighting data.
        :type filtered_data: pandas.DataFrame
        """
        self.delete_markers()
        for index, row in filtered_data.iterrows():
            latitude = float(row['latitude'])
            longitude = float(row['longitude'])
            shape = row['UFO_shape']
            self.map_view.set_marker(latitude, longitude, text=shape, icon=self.MARKER_ICON)

    def delete_markers(self):
        """
        Delete all map markers.
        """
        self.progress.start()
        label = tk.Label(self.filter_frame, text="Filtering might take some time. Please be patient. :)",
                         wraplength=200)
        label.grid(row=4, column=0)
        self.apply_button.configure(state='disabled')
        self.clear_button.configure(state='disabled')
        self.map_view.delete_all_marker()
        self.progress.stop()
        self.apply_button.configure(state='normal')
        self.clear_button.configure(state='normal')

    def add_sighting_markers(self):
        """
        Add map markers for all UFO sightings.
        """
        for index, row in self.data.iterrows():
            latitude = float(row['latitude'])
            longitude = float(row['longitude'])
            self.map_view.set_marker(latitude, longitude, icon=self.MARKER_ICON)

    def show_result_details(self, event):
        """
        Show detailed information about a selected result.
        """
        selected_index = self.results_listbox.curselection()
        selected_item = self.results_listbox.get(selected_index)
        if selected_item != 'No result found.':
            report_no, country, year, shape = selected_item.split(" - ")
            report_no = report_no.split(" ")[2]
            filtered_data = self.data[(self.data['report_no'] == int(report_no))]

            # Switch to the page with full information about the selected result
            self.show_full_information_page(filtered_data)
            self.full_info_frame.grid(row=0, column=1, rowspan=2, padx=5, pady=5, sticky=tk.NSEW)
            self.filter_frame.grid_forget()
            self.map_view.set_position(filtered_data.iloc[0]['latitude'], filtered_data.iloc[0]['longitude'])
            self.map_view.set_zoom(10)

    def show_full_information_page(self, filtered_data: pd.DataFrame):
        """
        Show full information about a selected UFO sighting.

        :param filtered_data: Filtered UFO sighting data.
        :type filtered_data: pandas.DataFrame
        """
        self.full_info_frame = ttk.LabelFrame(self, text='Full Information', padding='10')
        for index, row in filtered_data.iterrows():
            occurred_label = ttk.Label(self.full_info_frame, text=f"Occurred: {row['date_time_found']}")
            occurred_label.grid(row=0, column=0, sticky=tk.W)

            reported_label = ttk.Label(self.full_info_frame, text=f"Reported: {row['date_documented']}")
            reported_label.grid(row=1, column=0, sticky=tk.W)

            duration_label = ttk.Label(self.full_info_frame, text=f"Duration: "
                                       f"{row['length_of_encounter_seconds']} seconds")
            duration_label.grid(row=2, column=0, sticky=tk.W)

            location_label = ttk.Label(self.full_info_frame, text=f"Location: {row['location']}, {row['country']}")
            location_label.grid(row=3, column=0, sticky=tk.W)

            lat_label = ttk.Label(self.full_info_frame, text=f"Latitude: {row['latitude']}")
            lat_label.grid(row=4, column=0, sticky=tk.W)

            long_label = ttk.Label(self.full_info_frame, text=f"Longitude: {row['longitude']}")
            long_label.grid(row=5, column=0, sticky=tk.W)

            shape_label = ttk.Label(self.full_info_frame, text=f"Shape: {row['UFO_shape']}")
            shape_label.grid(row=7, column=0, sticky=tk.W)

            description_label = ttk.Label(self.full_info_frame, text=f"\nDescription:\n{row['description']}",
                                          wraplength=325)
            description_label.grid(row=9, column=0, sticky=tk.W)

        back_button = ttk.Button(self.full_info_frame, text='Back to Filter', command=self.back_to_filter_frame)
        back_button.grid(row=12, column=0, pady=5, sticky=tk.S)

    def back_to_filter_frame(self):
        """
        Go back to the filter frame.
        """
        self.full_info_frame.grid_forget()
        self.filter_frame.grid(row=2, column=1, sticky=tk.NSEW)


class GraphsPage(tk.Frame):
    """
    A frame for the graphs page.
    """
    def __init__(self, parent):
        """
        Initialize GraphsPage.

        :param parent: Parent tkinter App.
        """
        super().__init__()
        self.parent = parent
        self.graph_gen = GraphGenerator(self.parent.data_processor)
        self.configure(bg='#F8F8FF')
        self.init_components()

    def init_components(self):
        """
        Initialize GUI components.
        """
        # Histogram Frame
        histogram_frame = tk.LabelFrame(self, text='Distribution of Encounter Durations', bg='#F8F8FF')
        histogram_frame.grid(row=1, column=0, padx=10, pady=2)
        self.histogram_canvas = tk.Canvas(histogram_frame)
        self.histogram_canvas.pack(expand=True, fill=tk.BOTH, side=tk.TOP)

        histogram_frame2 = tk.LabelFrame(self, text='Distribution of Hour of the Day that Sighting was found',
                                         bg='#F8F8FF')
        histogram_frame2.grid(row=1, column=1, padx=10, pady=2)
        self.histogram_canvas2 = tk.Canvas(histogram_frame2)
        self.histogram_canvas2.pack(expand=True, fill=tk.BOTH, side=tk.TOP)

        # Pie Graph Frame
        pie_graph_frame = tk.LabelFrame(self, text='Pie Chart of different reported UFO shapes (UFO_shape).',
                                        bg='#F8F8FF')
        pie_graph_frame.grid(row=4, column=0, padx=10, pady=2, columnspan=2)
        self.pie_graph_canvas = tk.Canvas(pie_graph_frame)
        self.pie_graph_canvas.pack(expand=True, fill=tk.BOTH)

        # Bar Graph Frame
        bar_graph_frame = tk.LabelFrame(self, text='Top 5 Cities with the Most Reports', bg='#F8F8FF')
        bar_graph_frame.grid(row=2, column=1, padx=10, pady=2)
        self.bar_graph_canvas = tk.Canvas(bar_graph_frame)
        self.bar_graph_canvas.pack(expand=True, fill=tk.BOTH)

        # Line Graph Frame
        line_graph_frame = tk.LabelFrame(self, text='Trends of Sightings over time', bg='#F8F8FF')
        line_graph_frame.grid(row=2, column=0, padx=10, pady=2, sticky=tk.NSEW)
        self.line_graph_canvas = tk.Canvas(line_graph_frame)
        self.line_graph_canvas.pack(expand=True, fill=tk.BOTH)

        stats_button = CreateButton(self).button(img1='stats_2.png', img2='stats_1.png',
                                                 bg='#F8F8FF', command=self.statistic_popup)
        stats_button.grid(row=0, column=0, sticky=tk.W, padx=165, columnspan=2)
        self.create_and_display_graphs()

        # Configure grid weights
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)

    def create_and_display_graphs(self):
        """
        Create and display graphs.
        """
        fig_hist1, ax_hist1 = self.graph_gen.generate_histogram1()
        hist1_canvas = FigureCanvasTkAgg(fig_hist1, master=self.histogram_canvas)
        hist1_canvas.draw()
        hist1_canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)

        fig_hist2, ax_hist2 = self.graph_gen.generate_histogram2()
        hist2_canvas = FigureCanvasTkAgg(fig_hist2, master=self.histogram_canvas2)
        hist2_canvas.draw()
        hist2_canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)

        fig_pie, ax_pie = self.graph_gen.generate_pie_chart_ufo_shape()
        pie_canvas = FigureCanvasTkAgg(fig_pie, master=self.pie_graph_canvas)
        pie_canvas.draw()
        pie_canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)

        fig_bar, ax_bar = self.graph_gen.generate_top_cities_bar_chart()
        bar_canvas = FigureCanvasTkAgg(fig_bar, master=self.bar_graph_canvas)
        bar_canvas.draw()
        bar_canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)

        fig_line, ax_line = self.graph_gen.generate_year_line()
        line_canvas = FigureCanvasTkAgg(fig_line, master=self.line_graph_canvas)
        line_canvas.draw()
        line_canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)

    def statistic_popup(self):
        """
        Opens a popup window to display summary statistics for numerical attributes.
        """
        popup_window = tk.Toplevel(self)
        popup_window.title("Summary Statistic")

        popup_label = ttk.Label(popup_window, text="Choose a numerical attribute:")
        popup_label.pack()

        self.column_var = tk.StringVar()
        column_combobox = ttk.Combobox(popup_window, textvariable=self.column_var)
        column_combobox.pack()
        column_combobox['values'] = self.parent.data_processor.get_numerical_columns()

        column_combobox.bind("<<ComboboxSelected>>", self.display_statistics)

        self.statistics_label = ttk.Label(popup_window, text="")
        self.statistics_label.pack()

        scatter_plot_frame = tk.LabelFrame(popup_window,
                                           text='Correlation of Length of Encounter and Distance to nearest airport')
        scatter_plot_frame.pack()
        self.scatter_plot_canvas = tk.Canvas(scatter_plot_frame)
        self.scatter_plot_canvas.pack()
        fig_scatter, ax_scatter = self.graph_gen.generate_correlation_graph()
        fig_scatter.set_size_inches(5, 3.5)
        scatter_canvas = FigureCanvasTkAgg(fig_scatter, master=self.scatter_plot_canvas)
        scatter_canvas.draw()
        scatter_canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)
        plt.tight_layout()

    def display_statistics(self, event):
        """
        Displays summary statistics for the selected numerical attribute.
        """
        selected_column = self.column_var.get()
        if selected_column:
            self.statistics_label.config(text=self.parent.data_processor.calculate_statistics(selected_column))




class CreateYourOwnGraphPage(tk.Frame):
    """
    A frame for creating custom graphs based on UFO sighting data.
    """
    def __init__(self, parent):
        """
        Initialize the CreateYourOwnGraphPage.

        :param parent: The parent tkinter App.
        """
        super().__init__()
        self.parent = parent
        self.graph_gen = GraphGenerator(self.parent.data_processor)
        self.configure(bg='#F8F8FF')
        self.init_components()

    def init_components(self):
        """
        Initialize GUI components.
        """
        label = tk.Label(self, text='Create your own Graph!', font=('Helvetica', 15), bg='#F8F8FF')
        label.grid(row=0, column=0, pady=10, columnspan=2)

        self.graph_type_var = tk.StringVar()
        graph_type_label = tk.Label(self, text='Graph Type:', bg='#F8F8FF')
        graph_type_label.grid(row=1, column=0)
        graph_types = ['Bar Graph', 'Histogram', 'Pie Chart', 'Line Graph', 'Scatter Plot']
        self.graph_type_combobox = ttk.Combobox(self, textvariable=self.graph_type_var, values=graph_types)
        self.graph_type_combobox.bind('<<ComboboxSelected>>', self.graph_type_selected)
        self.graph_type_combobox.current(0)
        self.graph_type_combobox.grid(row=2, column=0)

        self.attribute_count_var = tk.StringVar()
        attribute_count_label = tk.Label(self, text='Attribute Count:', bg='#F8F8FF')
        attribute_count_label.grid(row=3, column=0)
        attribute_counts = ['1', '2']
        self.attribute_count_combobox = ttk.Combobox(self, textvariable=self.attribute_count_var,
                                                     values=attribute_counts)
        self.attribute_count_combobox.bind('<<ComboboxSelected>>', self.attribute_count_selected)
        self.attribute_count_combobox.grid(row=4, column=0)

        self.x_column_var = tk.StringVar()
        self.x_column_label = tk.Label(self, text='Attribute 1 (X-axis):', bg='#F8F8FF')
        columns = self.parent.data_processor.get_ufo_columns()
        self.x_column_combobox = ttk.Combobox(self, textvariable=self.x_column_var, values=columns)

        self.y_column_var = tk.StringVar()
        self.y_column_label = tk.Label(self, text='Attribute 2 (Y-axis):', bg='#F8F8FF')
        self.y_column_combobox = ttk.Combobox(self, textvariable=self.y_column_var, values=columns)

        self.color_var = tk.StringVar()
        self.color_label = tk.Label(self, text='Graph Color:', bg='#F8F8FF')
        self.color_combobox = ttk.Combobox(self, textvariable=self.color_var,
                                           values=['blue', 'green', 'red', 'yellow'])
        self.color_label.grid(row=1, column=1)
        self.color_combobox.grid(row=2, column=1)

        self.legend_var = tk.BooleanVar(value=True)  # Default to True
        self.legend_checkbutton = tk.Checkbutton(self, text='Show Legend', variable=self.legend_var, bg='#F8F8FF')

        create_button = tk.Button(self, text='Create Graph', command=self.error_handling)
        create_button.grid(row=4, column=1, rowspan=3, pady=10)

        export_button = CreateButton(self).button(img1='export_1.png', img2='export_2.png',
                                                  bg='#F8F8FF',command=self.export_graph)
        export_button.grid(row=20, column=0, sticky=tk.W, padx=170, columnspan=2)

        self.graph_canvas = tk.Canvas(self, bg='white', width=600, height=400)
        self.graph_canvas.grid(row=15, column=0, columnspan=2, sticky=tk.NSEW)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(7, weight=1)
        self.rowconfigure(12, weight=1)

    def create_graph(self):
        """
        Generate the selected graph based on user inputs.
        """
        attribute_count = self.attribute_count_var.get()
        graph_type = self.graph_type_var.get()
        x_column = self.x_column_var.get()
        y_column = self.y_column_var.get() if self.y_column_var.get() else None
        color = self.color_var.get()
        show_legend = self.legend_var.get()

        if attribute_count == "1":
            y_column = None

        if graph_type == 'Histogram':
            self.graph_gen.generate_histogram(attribute=x_column, xlabel=x_column, ylabel='Frequency',
                                              title=f'Histogram of {x_column}', color=color)
        elif graph_type == 'Pie Chart':
            self.graph_gen.generate_pie_chart(attribute=x_column, title=f'Pie Chart of {x_column}',
                                              legend=show_legend)
        elif graph_type == 'Line Graph':
            self.graph_gen.generate_line_graph(x_column=x_column, y_column=y_column,
                                               title=f'Line Graph of {x_column} and {y_column}'
                                               if y_column else f'Line Graph of {x_column}',
                                               xlabel=x_column, ylabel=y_column if y_column else 'Frequency',
                                               color=color)
        elif graph_type == 'Scatter Plot':
            self.graph_gen.generate_scatter_plot(x_column=x_column, y_column=y_column,
                                                 title=f'Scatter Plot of {x_column} and {y_column}'
                                                 if y_column else f'Scatter Plot of {x_column}',
                                                 xlabel=x_column, ylabel=y_column if y_column else 'Frequency',
                                                 color=color)
        elif graph_type == 'Bar Graph':
            self.graph_gen.generate_bar_graph(x_column=x_column, y_column=y_column,
                                              title=f'Bar Graph of {x_column} and {y_column}'
                                              if y_column else f'Bar Graph of {x_column}',
                                              xlabel=x_column, ylabel=y_column if y_column else 'Frequency',
                                              color=color)
        self.display_graph()

    def graph_type_selected(self, event):
        """
        Handle selection of graph type from combobox.
        """
        graph_type = self.graph_type_var.get()
        self.attribute_count_var.set("")
        self.reset_attributes()
        if graph_type in ['Histogram', 'Pie Chart']:
            self.attribute_count_var.set('1')
            self.attribute_count_combobox.configure(state='disabled')
            self.attribute_count_selected(None)
            self.y_column_combobox.grid_remove()
            self.y_column_label.grid_remove()
            if graph_type == 'Pie Chart':
                self.color_combobox.configure(state='disabled')
                self.color_var.set('-')
                self.legend_checkbutton.grid(row=3, column=1, pady=10)
        else:
            self.color_var.set('')
            self.attribute_count_combobox.configure(state='readonly')
            self.color_combobox.configure(state='readonly')
            self.attribute_count_combobox.configure(values=['1', '2'])
            self.legend_checkbutton.grid_forget()

    def reset_attributes(self):
        """
        Reset attribute selection widgets.
        """
        self.x_column_label.grid_forget()
        self.x_column_combobox.grid_forget()
        self.x_column_var.set('')
        self.y_column_label.grid_forget()
        self.y_column_combobox.grid_forget()
        self.y_column_var.set('')

    def attribute_count_selected(self, event):
        """
        Handle selection of attribute count from combobox.
        """
        attribute_count = int(self.attribute_count_var.get())
        if attribute_count == 1:
            self.y_column_label.grid_forget()
            self.y_column_combobox.grid_forget()
            self.x_column_label.grid(row=5, column=0)
            self.x_column_combobox.grid(row=6, column=0)
        elif attribute_count == 2:
            self.x_column_label.grid(row=5, column=0)
            self.x_column_combobox.grid(row=6, column=0)
            self.y_column_label.grid(row=7, column=0)
            self.y_column_combobox.grid(row=8, column=0)

    def error_handling(self):
        """
        Handle errors during graph creation.
        """
        graph_type = self.graph_type_var.get()
        attribute_count = self.attribute_count_var.get()
        color = self.color_var.get()
        x_column = self.x_column_var.get()
        y_column = self.y_column_var.get() if self.y_column_var.get() else None

        if not x_column or (attribute_count == '2' and not y_column):
            tk.messagebox.showerror('Error', 'Please fill in all the empty fields.')
            if not x_column:
                self.x_column_combobox.focus_set()
            else:
                self.y_column_combobox.focus_set()
        elif attribute_count == '':
            tk.messagebox.showerror('Error', 'Please fill in all the empty fields.')
            self.attribute_count_combobox.focus_set()
        elif graph_type == '':
            tk.messagebox.showerror('Error', 'Please fill in all the empty fields.')
            self.graph_type_combobox.focus_set()
        elif color == '':
            tk.messagebox.showerror('Error', 'Please fill in all the empty fields.')
            self.color_combobox.focus_set()
        else:
            self.create_graph()

    def display_graph(self):
        """
        Display the generated graph on the canvas.
        """
        self.graph_canvas.delete('all')
        self.fig = plt.gcf()
        self.fig.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_canvas)
        self.fig.canvas.draw()
        self.fig.canvas.get_tk_widget().grid(row=0, column=0, sticky=tk.NSEW)

    def export_graph(self):
        """
        Export the generated graph.
        """
        try:
            filename = asksaveasfile(initialfile='Untitled.png', defaultextension=".png",
                                     filetypes=[("Portable Graphics Format", "*.png")])
            if filename:
                # Save the current figure to the file
                self.fig.savefig(filename.name)
                messagebox.showinfo("Success", "Graph exported successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Error occurred while exporting the graph: {str(e)}")


class ReportPage(tk.Frame):
    """
    A frame for submitting UFO sighting reports.
    """
    def __init__(self, parent):
        """
        Initialize the ReportPage.

        :param parent: The parent tkinter App.
        """
        super().__init__()
        self.parent = parent
        self.data_processor = self.parent.data_processor
        self.configure(bg='#F8F8FF')
        self.init_components()

    def init_components(self):
        """
        Initialize GUI components.
        """
        date_label = tk.Label(self, text='Date and Time Found (MM/DD/YYYY HH:MM):',bg ='#F8F8FF')
        date_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        self.date_time_input = tk.StringVar()
        self.date_time_entry = ttk.Entry(self, textvariable=self.date_time_input)
        self.date_time_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)

        # Country
        country_label = tk.Label(self, text='Country:', bg='#F8F8FF')
        country_label.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        self.country_input = tk.StringVar()
        self.country_entry = ttk.Combobox(self, textvariable=self.country_input)
        self.country_entry.bind("<<ComboboxSelected>>", self.set_map_country)
        self.set_country_combobox_value()
        self.country_entry.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)

        # Location
        location_label = tk.Label(self, text='City/Location:', bg='#F8F8FF')
        location_label.grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        self.location_input = tk.StringVar()
        self.location_entry = ttk.Entry(self, textvariable=self.location_input)
        self.location_entry.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)

        # Latitude
        latitude_label = tk.Label(self, text='Latitude:', bg='#F8F8FF')
        latitude_label.grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
        self.lat_input = tk.StringVar()
        self.latitude_entry = tk.Entry(self, textvariable=self.lat_input, state='disabled')
        self.lat_input.set('Click on the map.')
        self.latitude_entry.grid(row=4, column=1, padx=10, pady=5, sticky=tk.W)

        # Longitude
        longitude_label = tk.Label(self, text='Longitude:', bg='#F8F8FF')
        longitude_label.grid(row=10, column=0, padx=10, pady=5, sticky=tk.W)
        self.long_input = tk.StringVar()
        self.longitude_entry = tk.Entry(self, textvariable=self.long_input, state='disabled')
        self.long_input.set('Click on the map.')
        self.longitude_entry.grid(row=10, column=1, padx=10, pady=5, sticky=tk.W)

        # UFO Shape
        ufo_shape_label = tk.Label(self, text='UFO Shape:', bg='#F8F8FF')
        ufo_shape_label.grid(row=11, column=0, padx=10, pady=5, sticky=tk.W)
        self.ufo_shape_input = tk.StringVar()
        self.ufo_shape_entry = tk.Entry(self, textvariable=self.ufo_shape_input)
        self.ufo_shape_entry.grid(row=11, column=1, padx=10, pady=5, sticky=tk.W)

        # Length of Encounter
        length_of_encounter_label = tk.Label(self, text='Length of Encounter (seconds):', bg='#F8F8FF')
        length_of_encounter_label.grid(row=12, column=0, padx=10, pady=5, sticky=tk.W)
        self.length_of_encounter_input = tk.StringVar()
        self.length_of_encounter_entry = tk.Entry(self, textvariable=self.length_of_encounter_input)
        self.length_of_encounter_entry.grid(row=12, column=1, padx=10, pady=5, sticky=tk.W)

        # Description
        description_label = tk.Label(self, text='Description:', bg='#F8F8FF')
        description_label.grid(row=13, column=0, padx=10, pady=5, sticky=tk.W)
        self.description_entry = tk.Text(self, height=5, width=30)
        self.description_entry.grid(row=13, column=1, padx=10, pady=5, sticky=tk.W)

        # Submit Button
        submit_button = CreateButton(self).button(img1='submit_1.png', img2='submit_2.png',
                                                  bg='#F8F8FF', command=self.submit_report)
        submit_button.grid(row=14, column=0, columnspan=2, padx=10, pady=10)

        self.create_map_frame()
        self.map_frame.grid(row=3, column=0, columnspan=2)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        for i in range(15):
            self.grid_rowconfigure(i, weight=1)

    def set_country_combobox_value(self):
        _list = []
        for country in Country:
            _list.append(country.value[0])
        self.country_entry['value'] = _list

    def set_map_country(self, event):
        country = self.country_input.get()
        lat = Country.find_val(country, 2)
        lon = Country.find_val(country, 3)
        self.map_view.set_position(lat, lon)
        self.map_view.set_zoom(4)

    def create_map_frame(self):
        """
        Create the frame for displaying the map.
        """
        self.map_frame = tk.LabelFrame(self, text='Select Location', bg='#F8F8FF')

        # Add the MapView widget to the map frame
        self.map_view = TkinterMapView(self.map_frame)
        self.map_view.fit_bounding_box((28.73, 91.20), (-9.5, 128.52))
        self.map_view.add_left_click_map_command(self.left_click_event)
        self.map_view.pack(expand=True, fill=tk.BOTH)

    def left_click_event(self, coordinates_tuple):
        """
        Handle left-click events on the map.

        :param coordinates_tuple: The coordinates of the click event.
        """
        self.lat_input.set(coordinates_tuple[0])
        self.long_input.set(coordinates_tuple[1])

    def validate_date(self, date_str) -> bool:
        """
        Validate the format of a date string.

        :param date_str: The date string to validate.
        :return: True if the date string has the correct format, False otherwise.
        """
        try:
            datetime.datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def submit_report(self):
        """
        Submit the UFO sighting report.
        """
        date_time_str = self.date_time_input.get()
        country = self.country_input.get()
        location = self.location_input.get()
        latitude = self.lat_input.get()
        longitude = self.long_input.get()
        ufo_shape = self.ufo_shape_input.get()
        length_of_encounter_seconds = self.length_of_encounter_input.get()
        description = self.description_entry.get('1.0', tk.END)
        if ("" or 'Click on the map.') in [date_time_str, country, location, latitude, longitude,
                                           ufo_shape, length_of_encounter_seconds, description]:
            tk.messagebox.showwarning('Error', 'Please fill in the empty fields.')
            return
        else:
            try:
                date_time = datetime.datetime.strptime(date_time_str, '%m/%d/%Y %H:%M')
            except ValueError:
                tk.messagebox.showerror('Error',
                                        'Invalid date and time format. '
                                        'Please enter in MM/DD/YYYY HH:MM format.')
                return
            try:
                length_of_encounter_seconds = float(length_of_encounter_seconds)
            except ValueError:
                tk.messagebox.showerror('Error',
                                        'The "Encounter Duration" must contain only numerical values.')
                return

        tk.messagebox.showinfo('Report submitted', 'Report submitted successfully!')
        self.data_processor.save_to_csv(date_time, country, location, latitude, longitude, ufo_shape,
                                        length_of_encounter_seconds, description)


class UFOApp(tk.Tk):
    """
    The main application window for UFORadarSEA.
    """
    def __init__(self, data_processor: UFODataProcessor):
        """
        Initialize the App.

        :param data_processor: An instance of UFODataProcessor for data processing.
        """
        super().__init__()
        image = Image.open(os.path.join(os.getcwd(), 'images', 'marker_icon.png')).resize((40, 40))
        self.icon = ImageTk.PhotoImage(image)
        self.wm_iconphoto(False, self.icon)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.title('UFORadarSEA')
        self.data_processor = data_processor
        self.configure(bg='#354662')
        self.init_components()

    def init_components(self):
        """
        Initialize GUI components.
        """
        self.main_menu = tk.Frame(self)
        self.main_canvas = tk.Canvas(self.main_menu, bg='#354662', width=800, height=450, borderwidth=0)
        self.main_canvas.pack(expand=True, fill=tk.BOTH)
        self.image = Image.open(os.path.join(os.getcwd(), 'images', 'main_bg.png'))
        self.main_bg = ImageTk.PhotoImage(self.image)
        self.main_canvas.create_image(0, 0, image=self.main_bg, anchor=tk.NW)

        self.view_map_button = CreateButton(self.main_menu).button(img1='map_2.png', img2='map_1.png',
                                                                   bg='#87919c',command=self.show_map_page)
        self.graphs_button = CreateButton(self.main_menu).button(img1='graphs_2.png', img2='graphs_1.png',
                                                                 bg='#d1cfc3', command=self.show_graphs_page)
        self.file_report_button = CreateButton(self.main_menu).button(img1='report_2.png', img2='report_1.png',
                                                                      bg='#c7c5b8',command=self.show_report_page)
        self.button1_canvas = self.main_canvas.create_window(335, 200,
                                                             anchor=tk.NW,
                                                             window=self.view_map_button)

        self.button2_canvas = self.main_canvas.create_window(335, 275,
                                                             anchor=tk.NW,
                                                             window=self.graphs_button)

        self.button3_canvas = self.main_canvas.create_window(335, 350,
                                                             anchor=tk.NW,
                                                             window=self.file_report_button)
        self.back_button = CreateButton(self).button(img1='back_2.png', img2='back_1.png',
                                                     bg='#F8F8FF', command=self.show_main_menu)

        self.main_menu.pack(expand=True)

        self.map_page = MapPage(self)
        self.report_page = ReportPage(self)
        self.graphs_page = GraphsPage(self)
        self.user_create_graph_page = CreateYourOwnGraphPage(self)

        self.main_menu.grid_rowconfigure(0, weight=1)
        self.main_menu.grid_rowconfigure(1, weight=1)
        self.main_canvas.grid_columnconfigure(0, weight=1)
        self.main_canvas.grid_columnconfigure(1, weight=1)
        self.main_canvas.grid_columnconfigure(2, weight=1)

    def show_map_page(self):
        """
        Switch to the map page.
        """
        self.map_page.pack(expand=True, fill=tk.BOTH)
        self.main_menu.pack_forget()
        self.configure(bg='#F8F8FF')
        self.back_button.pack(anchor=tk.W, expand=True)

    def show_report_page(self):
        """
        Switch to the report page.
        """
        self.report_page = ReportPage(self)
        self.report_page.pack(expand=True, fill=tk.BOTH)
        self.main_menu.pack_forget()
        self.configure(bg='#F8F8FF')
        self.back_button.pack(anchor=tk.W, expand=True)

    def show_graphs_page(self):
        """
        Switch to the graphs page.
        """
        self.graphs_page = GraphsPage(self)
        self.graphs_page.pack(expand=True, fill=tk.BOTH)
        self.main_menu.pack_forget()
        self.user_create_graph_page.pack_forget()
        self.configure(bg='#F8F8FF')
        self.back_button.pack(anchor=tk.W, expand=True)
        create_graph_button = CreateButton(self.graphs_page).button(img1='create_graph2.png',
                                                                    img2='create_graph1.png',
                                                                    bg='#F8F8FF',
                                                                    command=self.show_user_create_graph_page)
        create_graph_button.grid(row=0, column=0, sticky=tk.W)

    def show_main_menu(self):
        """
        Switch to the main menu.
        """
        if not self.main_menu.winfo_ismapped():  # Check if main menu is not already mapped
            self.main_menu.pack(expand=True)
            self.configure(bg='#354662')
            matplotlib.pyplot.close('all')
        self.map_page.pack_forget()
        self.graphs_page.pack_forget()
        self.report_page.pack_forget()
        self.back_button.pack_forget()

    def show_user_create_graph_page(self):
        """
        Switch to the custom graph creation page.
        """
        self.graphs_page.pack_forget()
        self.back_button.pack_forget()
        self.user_create_graph_page.pack(expand=True, fill=tk.BOTH)
        self.back_to_graph = CreateButton(self.user_create_graph_page).button(img1='back_graph_1.png',
                                                                              img2='back_graph_2.png',
                                                                              bg='#F8F8FF',
                                                                              command=self.show_graphs_page)
        self.back_to_graph.grid(row=20, column=0, sticky=tk.W)

    def on_close(self):
        matplotlib.pyplot.close('all')
        self.quit()

    def run(self):
        """
        Run the application.
        """
        self.mainloop()
