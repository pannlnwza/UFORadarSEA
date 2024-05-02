import tkinter as tk
import matplotlib.pyplot as plt
import tkinter.messagebox
from tkinter import ttk
from tkintermapview import TkinterMapView
from graph_generator import GraphGenerator
from tkcalendar import DateEntry
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from uforadar_dataprocessor import UFODataProcessor


class MapPage(tk.Frame):
    def __init__(self, parent, data_processor: UFODataProcessor):
        super().__init__(parent)
        self.parent = parent
        self.data_processor = data_processor
        self.data = self.data_processor.get_ufo_data()
        self.init_components()

    def init_components(self):
        map_frame = ttk.Frame(self, borderwidth=2, relief="groove")
        map_frame.grid(row=0, column=0, rowspan=2, padx=5, pady=5, sticky="nsew")

        # Map view
        self.map_view = TkinterMapView(map_frame, width=600, height=500)
        self.map_view.pack(fill=tk.BOTH, expand=True)

        # Fit bounding box to Southeast Asia
        self.map_view.fit_bounding_box((28.73, 91.20), (-9.5, 128.52))

        # Add position markers for UFO sightings
        self.add_sighting_markers()

        title = tk.Label(self, text='UFORadarSEA')
        title.grid(row=0, column=1)
        # Filter frame
        self.filter_frame()

        # Configure grid weights
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

    def filter_frame(self):
        filter_frame = ttk.LabelFrame(self, text="Filter", padding="10")
        filter_frame.grid(row=1, column=1, padx=5, pady=5, sticky=tk.NSEW)

        # Create a canvas for the radiobuttons
        canvas = tk.Canvas(filter_frame)
        canvas.grid(row=1, column=0, columnspan=3, sticky=tk.NSEW)

        # Add a scrollbar for the canvas
        scrollbar = ttk.Scrollbar(filter_frame, orient="vertical", command=canvas.yview)
        scrollbar.grid(row=1, column=3, sticky="ns")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create a frame to contain the radiobuttons
        radiobutton_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=radiobutton_frame, anchor=tk.NW)

        # Country filter
        country_label = ttk.Label(radiobutton_frame, text="Country:")
        country_label.grid(row=0, column=0, sticky=tk.W)

        self.country_var = tk.StringVar()
        self.country_var.set("All")
        self.country_radios = []
        countries = self.get_unique_values('country')  # Get unique country values from dataset
        for i, country in enumerate(countries):
            radio = ttk.Radiobutton(radiobutton_frame, text=country, variable=self.country_var, value=country)
            radio.grid(row=i + 1, column=0, sticky="w")
            self.country_radios.append(radio)

        # Year filter
        year_label = ttk.Label(radiobutton_frame, text="Year:")
        year_label.grid(row=0, column=1, sticky="w")

        self.year_var = tk.StringVar()
        self.year_var.set("All")
        years = ['1960-1970', '1971-1980', '1981-1990', '1991-2000', '2001-2010', '2011-2020', 'After 2021']
        for i, year in enumerate(years):
            radio = ttk.Radiobutton(radiobutton_frame, text=year, variable=self.year_var, value=year)
            radio.grid(row=i + 1, column=1, sticky="w")

        # Shape filter
        shape_label = ttk.Label(radiobutton_frame, text="Shape:")
        shape_label.grid(row=0, column=2, sticky="w")

        self.shape_var = tk.StringVar()
        self.shape_var.set("All")
        self.shape_radios = []
        shapes = self.get_unique_values('UFO_shape')  # Get unique shape values from dataset
        for i, shape in enumerate(shapes):
            radio = ttk.Radiobutton(radiobutton_frame, text=shape, variable=self.shape_var, value=shape)
            radio.grid(row=i + 1, column=2, sticky="w")
            self.shape_radios.append(radio)

        # Update the canvas scroll region
        radiobutton_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

        apply_button = ttk.Button(filter_frame, text="Apply Filter", command=self.apply_filter)
        apply_button.grid(row=5, column=0, columnspan=3, padx=5, pady=5, sticky=tk.W)
        clear_button = ttk.Button(filter_frame, text="Clear Filter", command=self.clear_filter)
        clear_button.grid(row=5, column=0, columnspan=3, padx=5, pady=5, sticky=tk.E)

        # Results listbox
        self.results_listbox = tk.Listbox(filter_frame, height=5)
        self.results_listbox.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")
        self.results_listbox.bind("<Button-1>", self.show_result_details)

    def clear_filter(self):
        self.country_var.set('All')
        self.year_var.set('All')
        self.shape_var.set('All')
        self.add_sighting_markers()
        self.map_view.fit_bounding_box((28.73, 91.20), (-9.5, 128.52))

    def apply_filter(self):
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

        self.update_results_list(filtered_data)
        self.update_map_markers(filtered_data)

    def update_results_list(self, data):
        # Clear the current items in the listbox
        self.results_listbox.delete(0, tk.END)

        # Insert new items based on the filtered data
        for index, row in data.iterrows():
            self.results_listbox.insert(tk.END, f"Report No. {row['report_no']} - {row['country']} - {row['year_found']} - {row['UFO_shape']}")

    def update_map_markers(self, filtered_data):
        # Clear existing markers
        self.map_view.delete_all_marker()

        # Add new markers based on filtered data
        for index, row in filtered_data.iterrows():
            latitude = float(row['latitude'])
            longitude = float(row['longitude'])
            shape = row['UFO_shape']
            self.map_view.set_marker(latitude, longitude, text=shape)

    def add_sighting_markers(self):
        for index, row in self.data.iterrows():
            latitude = float(row['latitude'])
            longitude = float(row['longitude'])
            shape = row['UFO_shape']
            self.map_view.set_marker(latitude, longitude, text=shape)

    def show_result_details(self, event):
        # Get the selected item from the results listbox
        selected_index = self.results_listbox.curselection()
        if selected_index:
            selected_item = self.results_listbox.get(selected_index)

            # Split the selected item to get relevant information
            report_no, country, year, shape = selected_item.split(" - ")
            report_no = report_no.split(" ")[2]
            # Get the filtered data for the selected item
            filtered_data = self.data[(self.data['report_no'] == int(report_no))]
            print(filtered_data.iloc[0]['latitude'])
            # Switch to the page with full information about the selected result
            self.show_full_information_page(filtered_data)

            # Update map marker to show the selected result marker and zoom to it
            self.update_map_markers(filtered_data)

            self.map_view.set_position(filtered_data.iloc[0]['latitude'], filtered_data.iloc[0]['longitude'])
            self.map_view.set_zoom(10)

    def show_full_information_page(self, filtered_data):
        # Create a new frame to display full information about the selected result
        full_info_frame = ttk.LabelFrame(self, text="Full Information", padding="10")
        full_info_frame.grid(row=1, column=1, padx=5, pady=5, sticky=tk.NSEW)

        # Add information labels/buttons/etc. to display full information
        # For example:
        for index, row in filtered_data.iterrows():
            # Add occurred and reported dates
            occurred_label = ttk.Label(full_info_frame, text=f"Occurred: {row['date_time_found']}")
            occurred_label.grid(row=0, column=0, sticky=tk.W)
            reported_label = ttk.Label(full_info_frame, text=f"Reported: {row['date_documented']}")
            reported_label.grid(row=1, column=0, sticky=tk.W)
            # Add duration and number of observers
            duration_label = ttk.Label(full_info_frame, text=f"Duration: {row['length_of_encounter_seconds']} seconds")
            duration_label.grid(row=2, column=0, sticky=tk.W)
            # Add location details
            location_label = ttk.Label(full_info_frame, text=f"Location: {row['location']}, {row['country']}")
            location_label.grid(row=3, column=0, sticky=tk.W)
            lat_label = ttk.Label(full_info_frame, text=f"Latitude: {row['latitude']}")
            lat_label.grid(row=4, column=0, sticky=tk.W)
            long_label = ttk.Label(full_info_frame, text=f"Longitude: {row['longitude']}")
            long_label.grid(row=5, column=0, sticky=tk.W)
            # Add shape, color, estimated size, etc.
            shape_label = ttk.Label(full_info_frame, text=f"Shape: {row['UFO_shape']}")
            shape_label.grid(row=7, column=0, sticky=tk.W)
            # Add description
            description_label = ttk.Label(full_info_frame, text=f"\nDescription:\n{row['description']}", wraplength=325)
            description_label.grid(row=9, column=0, sticky=tk.W)

        # Add a button to go back to the filter frame
        back_button = ttk.Button(full_info_frame, text="Back to Filter", command=self.back_to_filter_frame)
        back_button.grid(row=12, column=0, pady=5, sticky=tk.S)

    def back_to_filter_frame(self):
        # Remove the full information frame and display the filter frame again
        self.filter_frame()

    def get_unique_values(self, column):
        return self.data[column].unique().tolist()


class GraphsPage(tk.Frame):
    def __init__(self, parent, data_processor: UFODataProcessor):
        super().__init__(parent)
        self.parent = parent
        self.data_processor = data_processor
        self.data = self.data_processor.get_ufo_data()
        self.graph_gen = GraphGenerator(self.data)
        self.init_components()

    def init_components(self):
        self.create_and_display_graphs()


    def create_and_display_graphs(self):
        fig, axs = plt.subplots(nrows=3, ncols=2, figsize=(14,10))

        self.graph_gen.generate_histogram('length_of_encounter_seconds','Distribution of Encounter Durations',
                                          'Duration (seconds)', 'Frequency', axs[0, 0])
        self.graph_gen.generate_histogram('hour', 'Frequency of Sightings by Hour of the Day',
                                          'Hour of the Day', 'Frequency', axs[0, 1])

        self.graph_gen.generate_top_cities_bar_chart('location', axs[1, 0])

        self.graph_gen.generate_pie_chart('UFO_shape','Frequency Distribution of UFO Shapes', axs[1, 1])

        self.graph_gen.generate_line_graph(x_column='year_found', y_column=None,
                                           title='Trend Analysis of UFO Sightings Over the Years',
                                           xlabel='Year', ylabel='Number of Sightings', ax=axs[2, 0])

        self.graph_gen.generate_scatter_plot('length_of_encounter_seconds', 'distance_to_nearest_airport_km',
                                             'Encounter Duration vs. Distance to Nearest Airport',
                                             'Encounter Duration (seconds)', 'Distance to Nearest Airport (km)',
                                             axs[2, 1])

        plt.tight_layout()
        self.user_create_graph_page = CreateYourOwnGraphPage(self, self.data_processor)
        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=tk.NSEW)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)



class CreateYourOwnGraphPage(tk.Frame):
    def __init__(self, parent, data_processor: UFODataProcessor):
        super().__init__(parent)
        self.parent = parent
        self.data_processor = data_processor
        self.data = self.data_processor.get_ufo_data()
        self.graph_gen = GraphGenerator(self.data)
        self.init_components()

    def init_components(self):
        label = tk.Label(self, text='Create you own Graph!')
        label.grid(row=0, column=0)

        self.graph_type_var = tk.StringVar()
        graph_type_label = ttk.Label(self, text="Graph Type:")
        graph_type_label.grid(row=1, column=0)
        graph_types = ['Histogram', 'Pie Chart', 'Bar Graph', 'Line Graph', 'Scatter Plot']
        self.graph_type_combobox = ttk.Combobox(self, textvariable=self.graph_type_var, values=graph_types)
        self.graph_type_combobox.bind("<<ComboboxSelected>>", self.graph_type_selected)

        self.x_column_var = tk.StringVar()
        self.x_column_label = ttk.Label(self, text="X Axis:")
        columns = list(self.data.columns)
        self.x_column_combobox = ttk.Combobox(self, textvariable=self.x_column_var, values=columns)

        self.y_column_var = tk.StringVar()
        self.y_column_label = ttk.Label(self, text="Y Axis:")
        self.y_column_combobox = ttk.Combobox(self, textvariable=self.y_column_var, values=columns)



        self.graph_canvas = tk.Canvas(self, bg='white', width=600, height=400)
        self.graph_canvas.grid(row=8, column=0, sticky=tk.NSEW)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(7, weight=1)

        self.display_components()

    def display_components(self):
        self.graph_type_combobox.grid(row=2, column=0)

        self.x_column_label.grid(row=3, column=0)
        self.x_column_combobox.grid(row=4, column=0)

        self.y_column_label.grid(row=5, column=0)
        self.y_column_combobox.grid(row=6, column=0)

        create_button = tk.Button(self, text="Create Graph", command=self.create_graph)
        create_button.grid(row=7, column=0)

        self.rowconfigure(8, weight=1)

    def create_graph(self):
        graph_type = self.graph_type_var.get()
        x_column = self.x_column_var.get()
        y_column = self.y_column_var.get() if self.y_column_var.get() else None

        plt.figure(figsize=(6, 4))

        if graph_type == 'Histogram':
            self.graph_gen.generate_histogram(x_column, f'Histogram of {x_column}', x_column, 'Frequency', plt.gca())
        elif graph_type == 'Pie Chart':
            self.graph_gen.generate_pie_chart(x_column, f'Pie Chart of {x_column}', plt.gca())
        elif graph_type == 'Line Graph':
            self.graph_gen.generate_line_graph(x_column=x_column, y_column=y_column,
                                               title=f'Line Graph of {x_column} and {y_column}' if y_column else f'Line Graph of {x_column}',
                                               xlabel=x_column, ylabel=y_column if y_column else 'Frequency',
                                               ax=plt.gca())
        elif graph_type == 'Scatter Plot':
            self.graph_gen.generate_scatter_plot(x_column=x_column, y_column=y_column,
                                                 title=f'Scatter Plot of {x_column} vs {y_column}' if y_column else f'Scatter Plot of {x_column}',
                                                 xlabel=x_column, ylabel=y_column if y_column else 'Frequency',
                                                 ax=plt.gca())
        elif graph_type == 'Bar Graph':
            self.graph_gen.generate_bar_graph(x_column=x_column, y_column=y_column,
                                                  title=f'Bar Graph of {x_column} and {y_column}' if y_column else f'Bar Graph of {x_column}',
                                                  xlabel=x_column, ylabel=y_column if y_column else 'Frequency', ax=plt.gca())
        self.display_graph()

    def graph_type_selected(self, event):
        graph_type = self.graph_type_var.get()
        if graph_type in ['Histogram', 'Pie Chart']:
            self.x_column_label.configure(text='Attribute:')
            self.y_column_combobox.grid_remove()
            self.y_column_label.grid_remove()
        else:
            self.x_column_label.configure(text='X Axis:')
            self.y_column_combobox.grid()
            self.y_column_label.grid()

    def display_graph(self):
        self.graph_canvas.delete('all')
        self.fig = plt.gcf()
        self.fig.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_canvas)
        self.fig.canvas.draw()
        self.fig.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")


class ReportPage(tk.Frame):
    def __init__(self, parent, data_processor: UFODataProcessor):
        super().__init__(parent)
        self.parent = parent
        self.init_components()

    def init_components(self):
        date_label = ttk.Label(self, text="Date and Time Found:")
        date_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        self.date_entry = DateEntry(self, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.date_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)

        # Country
        country_label = ttk.Label(self, text="Country:")
        country_label.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        self.country_input = tk.StringVar()
        self.country_entry = ttk.Entry(self, textvariable=self.country_input)
        self.country_entry.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)

        # Location
        location_label = ttk.Label(self, text="City:")
        location_label.grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        self.location_input = tk.StringVar()
        self.location_entry = ttk.Entry(self, textvariable=self.location_input)
        self.location_entry.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)

        # Latitude
        latitude_label = tk.Label(self, text="Latitude:")
        latitude_label.grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
        self.lat_input = tk.StringVar()
        self.latitude_entry = tk.Entry(self, textvariable=self.lat_input, state='disabled')
        self.lat_input.set('Click on the map.')
        self.latitude_entry.grid(row=4, column=1, padx=10, pady=5, sticky=tk.W)

        # Longitude
        longitude_label = tk.Label(self, text="Longitude:")
        longitude_label.grid(row=10, column=0, padx=10, pady=5, sticky=tk.W)
        self.long_input = tk.StringVar()
        self.longitude_entry = tk.Entry(self, textvariable=self.long_input, state='disabled')
        self.long_input.set('Click on the map.')
        self.longitude_entry.grid(row=10, column=1, padx=10, pady=5, sticky=tk.W)

        # UFO Shape
        ufo_shape_label = tk.Label(self, text="UFO Shape:")
        ufo_shape_label.grid(row=11, column=0, padx=10, pady=5, sticky=tk.W)
        self.ufo_shape_entry = tk.Entry(self)
        self.ufo_shape_entry.grid(row=11, column=1, padx=10, pady=5, sticky=tk.W)

        # Length of Encounter
        length_of_encounter_label = tk.Label(self, text="Length of Encounter (seconds):")
        length_of_encounter_label.grid(row=12, column=0, padx=10, pady=5, sticky=tk.W)
        self.length_of_encounter_entry = tk.Entry(self)
        self.length_of_encounter_entry.grid(row=12, column=1, padx=10, pady=5, sticky=tk.W)

        # Description
        description_label = tk.Label(self, text="Description:")
        description_label.grid(row=13, column=0, padx=10, pady=5, sticky=tk.W)
        self.description_entry = tk.Text(self, height=5, width=30)
        self.description_entry.grid(row=13, column=1, padx=10, pady=5, sticky=tk.W)

        # Submit Button
        submit_button = tk.Button(self, text="Submit", command=self.submit_report)
        submit_button.grid(row=14, column=0, columnspan=2, padx=10, pady=10)

        self.create_map_frame()
        self.map_frame.grid(row=3, column=0, columnspan=2)

    def create_map_frame(self):
        self.map_frame = tk.LabelFrame(self, text="Select Location")

        # Add the MapView widget to the map frame
        self.map_view = TkinterMapView(self.map_frame)
        self.map_view.fit_bounding_box((28.73, 91.20), (-9.5, 128.52))
        self.map_view.add_left_click_map_command(self.left_click_event)
        self.map_view.pack(expand=True, fill="both")

    def left_click_event(self, coordinates_tuple):
        self.lat_input.set(coordinates_tuple[0])
        self.long_input.set(coordinates_tuple[1])



    def submit_report(self):
        date_time_found = self.date_entry.get_date()
        country = self.country_entry.get()
        location = self.location_entry.get()
        latitude = self.latitude_entry.get()
        longitude = self.longitude_entry.get()
        ufo_shape = self.ufo_shape_entry.get()
        length_of_encounter_seconds = self.length_of_encounter_entry.get()
        description = self.description_entry.get("1.0", tk.END)

        # Process the report data here (e.g., save to file, send to database, etc.)
        # Replace this with your desired action
        print(date_time_found, country, location, latitude, longitude, ufo_shape, length_of_encounter_seconds, description)
        tk.messagebox.showinfo('Report submitted', 'Report submitted successfully!')


class App(tk.Tk):
    def __init__(self, data_processor: UFODataProcessor):
        super().__init__()
        self.title('UFORadarSEA')
        self.data_processor = data_processor
        self.init_components()

    def init_components(self):
        self.main_menu = tk.Frame(self)
        title_label = ttk.Label(self.main_menu, text="UFORadarSEA", font=("Helvetica", 24), padding=(0, 20))
        title_label.grid(row=0, column=0, columnspan=3)
        view_map_button = tk.Button(self.main_menu, text="View Map", height=2, width=7, command=self.show_map_page)
        view_map_button.grid(row=1, column=0, padx=5, pady=10)

        graphs_button = tk.Button(self.main_menu, text="Graphs", height=2, width=7, command=self.show_graphs_page)
        graphs_button.grid(row=1, column=1, padx=5, pady=10)

        file_report_button = tk.Button(self.main_menu, text="File a Report", height=2, width=7,  command=self.show_report_page)
        file_report_button.grid(row=1, column=2, padx=5, pady=10)
        self.main_menu.pack(expand=True)

        self.map_page = MapPage(self, self.data_processor)
        self.report_page = ReportPage(self, self.data_processor)
        self.graphs_page = GraphsPage(self, self.data_processor)
        self.user_create_graph_page = CreateYourOwnGraphPage(self, self.data_processor)


    def show_map_page(self):
        self.map_page.pack(expand=True, fill=tk.BOTH)
        self.main_menu.pack_forget()
        self.back_button = tk.Button(self.map_page, text='Back to Main Menu', command=self.show_main_menu)
        self.back_button.grid(row=2, column=0, sticky=tk.W)

    def show_report_page(self):
        self.report_page.pack(expand=True, fill=tk.BOTH)
        self.main_menu.pack_forget()
        self.back_button = tk.Button(self.report_page, text='Back to Main Menu', command=self.show_main_menu)
        self.back_button.grid(row=14, column=0, sticky=tk.W)

    def show_graphs_page(self):
        self.graphs_page.pack(expand=True, fill=tk.BOTH)
        self.main_menu.pack_forget()
        self.user_create_graph_page.pack_forget()
        self.back_button = tk.Button(self.graphs_page, text='Back to Main Menu', command=self.show_main_menu)
        self.back_button.grid(row=1, column=0, sticky=tk.W)
        create_graph_button = tk.Button(self.graphs_page, text='Create your own graph!', command=self.show_user_create_graph_page)
        create_graph_button.grid(row=1, column=0, padx=150, sticky=tk.W)

    def show_main_menu(self):
        self.map_page.pack_forget()
        self.report_page.pack_forget()
        self.graphs_page.pack_forget()
        self.main_menu.pack(expand=True)

    def show_user_create_graph_page(self):
        self.graphs_page.pack_forget()
        self.user_create_graph_page.pack(expand=True, fill=tk.BOTH)
        self.back_button = tk.Button(self.user_create_graph_page, text='Back to Graphs', command=self.show_graphs_page)
        self.back_button.grid(row=9, column=0, sticky=tk.W)


    def run(self):
        self.mainloop()

