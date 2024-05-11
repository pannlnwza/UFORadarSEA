import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker
from data_processor import UFODataProcessor
import matplotlib
matplotlib.use('TkAgg')


class GraphGenerator:
    """
    A class to generate various types of graphs using matplotlib.
    """
    def __init__(self, data_processor: UFODataProcessor):
        """
        Initialize the GraphGenerator.
        """

        self.data_processor = data_processor
        self.data = self.data_processor.get_ufo_data()
        self.data = self.remove_all_outliers(self.data)

    def generate_histogram(self, attribute, xlabel, ylabel, title, color):
        """
        Generate a histogram.

        :param attribute: The attribute to plot.
        :param xlabel: The label for the x-axis.
        :param ylabel: The label for the y-axis.
        :param title: The title of the graph.
        :param color: The color of the bars.
        :return: The figure and axis objects.
        """
        fig, ax = plt.subplots()
        ax.hist(self.data[attribute], color=color)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        return fig, ax

    def generate_pie_chart(self, attribute, title, legend=False):
        """
        Generate a pie chart.

        :param attribute: The attribute to plot.
        :param title: The title of the graph.
        :param legend: Whether to display the legend (default is False).
        :return: The figure and axis objects.
        """
        def autopct_more_than_4(pct):
            return ('%1.f%%' % pct) if pct > 4 else ''
        fig, ax = plt.subplots()
        count = self.data[attribute].value_counts()
        ax.pie(count, labels=count.index, autopct=autopct_more_than_4, startangle=90)
        ax.set_title(title)
        if legend:
            ax.legend(labels=count.index, loc='best')
        return fig, ax

    def generate_line_graph(self, x_column, y_column, title, xlabel, ylabel, color):
        """
        Generate a line graph.

        :param x_column: The attribute for the x-axis.
        :param y_column: The attribute for the y-axis.
        :param title: The title of the graph.
        :param xlabel: The label for the x-axis.
        :param ylabel: The label for the y-axis.
        :param color: The color of the markers.
        :return: The figure and axis objects.
        """
        fig, ax = plt.subplots()
        if y_column is None:
            counts = self.data[x_column].value_counts().sort_index()
            ax.plot(counts.index, counts.values, marker='o', color=color)
            ax.set_title(title)
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
        else:
            ax.plot(self.data[x_column], self.data[y_column], marker='o', color=color)
            ax.set_title(title)
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
        return fig, ax

    def generate_scatter_plot(self, x_column, y_column, title, xlabel, ylabel, color):
        """
        Generate a scatter plot.

        :param x_column: The attribute for the x-axis.
        :param y_column: The attribute for the y-axis.
        :param title: The title of the graph.
        :param xlabel: The label for the x-axis.
        :param ylabel: The label for the y-axis.
        :param color: The color of the markers.
        :return: The figure and axis objects.
        """
        plt.tight_layout()
        fig, ax = plt.subplots()
        if y_column is None:
            y_column = self.data[x_column].value_counts().index
            counts = self.data[x_column].value_counts().sort_index()
            ax.scatter(counts.index, counts.values, c=color[0])
        else:
            ax.scatter(self.data[x_column], self.data[y_column], c=color[0])

        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        return fig, ax

    def generate_bar_graph(self, x_column, y_column, title, xlabel, ylabel, color):
        """
        Generate a bar graph.

        :param x_column: The attribute for the x-axis.
        :param y_column: The attribute for the y-axis.
        :param title: The title of the graph.
        :param xlabel: The label for the x-axis.
        :param ylabel: The label for the y-axis.
        :param color: The color of the bars.
        :return: The figure and axis objects.
        """
        fig, ax = plt.subplots()
        if y_column is None:
            counts = self.data[x_column].value_counts()
            ax.bar(counts.index, counts.values, color=color)
        else:
            ax.bar(self.data[x_column], self.data[y_column], color=color)
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        return fig, ax

    def generate_histogram1(self):
        """
        Generate a histogram of Length of encounter seconds.
        """
        fig, ax = plt.subplots(figsize=(4, 2), tight_layout=True)
        sns.histplot(data=self.data, x='length_of_encounter_seconds', kde=True, color='pink')
        ax.set_xlabel('Length of Encounter (seconds)')
        ax.set_ylabel('Frequency')
        ax.set_title('')
        return fig, ax

    def generate_histogram2(self):
        """
        Generate a histogram of most time of the day UFO sighting was found.
        """
        fig, ax = plt.subplots(figsize=(4, 2), tight_layout=True)
        sns.histplot(data=self.data, x='hour', kde=True, color='skyblue')
        ax.set_xlabel('Hour of the Day')
        ax.set_ylabel('Frequency')
        ax.set_title('')
        return fig, ax

    def generate_year_line(self):
        """
        Generate a line graph of Trends of sighting.
        """
        self.data['year_found'] = self.data['year_found'].astype(str)
        counts = self.data['year_found'].value_counts().sort_index()

        fig, ax = plt.subplots(figsize=(4, 3), tight_layout=True)
        sns.lineplot(data=counts, marker='o', ax=ax)

        ax.set_xlabel('Year')
        ax.set_ylabel('Frequency')
        ax.set_title('')
        ax.xaxis.set_major_locator(ticker.MultipleLocator(base=5))

        return fig, ax

    def generate_top_cities_bar_chart(self):
        """
        Generate a bar chart for the top 5 cities with the most reports.
        """
        # Count occurrences of each city
        city_counts = self.data['location'].value_counts()

        # Select the top 5 cities
        top_cities = city_counts.head(5)

        # Plot the bar chart
        fig, ax = plt.subplots(figsize=(4, 3), tight_layout=True)
        top_cities.plot(kind='bar', ax=ax, color='slateblue')

        # Set labels and title
        ax.set_xlabel('City')
        ax.set_ylabel('Number of Reports')
        ax.set_title('')
        ax.tick_params(rotation=20)
        return fig, ax

    def generate_pie_chart_ufo_shape(self):
        """
        Generate a pie chart for UFO shapes.
        :return: The figure and axis objects.
        """
        def autopct_more_than_4(pct):
            return ('%1.f%%' % pct) if pct > 4 else ''

        count = self.data['UFO_shape'].value_counts()
        percentages = 100 * count / count.sum()  # Calculate percentages
        labels_with_percentage = [f'{label} ({percentage:.0f}%)'
                                  for label, percentage in zip(count.index, percentages)]

        fig, ax = plt.subplots(figsize=(8.5, 3), tight_layout=True)
        with sns.axes_style('whitegrid'):
            wedges, _, autotexts = ax.pie(count, autopct=autopct_more_than_4, startangle=90)
            plt.legend(wedges, labels_with_percentage, loc='center right',
                       bbox_to_anchor=(2.2, 0.5), ncol=2)
            ax.set_title('')
        return fig, ax

    def generate_correlation_graph(self):
        """
        Generate a correlation graph for length_of_encounter_seconds and distance_to_nearest_airport_km.
        """
        fig, ax = plt.subplots()
        sns.regplot(data=self.data, x="distance_to_nearest_airport_km", y="length_of_encounter_seconds",
                    line_kws=dict(color="orange"))

        ax.set_title('')
        ax.set_xlabel('Length of Encounter (seconds)')
        ax.set_ylabel('Distance to the nearest Airport (kilometer)')
        return fig, ax

    @staticmethod
    def remove_all_outliers(data):
        """
        Remove outliers from the data.

        :param data: The DataFrame containing the data.
        :return: DataFrame without outliers.
        """
        for column in data.select_dtypes(include='number').columns:
            q1 = data[column].quantile(0.25)
            q3 = data[column].quantile(0.75)
            iqr = q3 - q1

            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr

            data = data[(data[column] >= lower_bound) & (data[column] <= upper_bound)]
        return data
