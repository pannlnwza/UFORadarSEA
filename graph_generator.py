import matplotlib.pyplot as plt
import pandas as pd


class GraphGenerator:
    """
    A class to generate various types of graphs using matplotlib.
    """
    def __init__(self, data: pd.DataFrame):
        """
        Initialize the GraphGenerator.

        :param data: The DataFrame containing the data.
        :type data: pd.Dataframe
        """
        self.data = data
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
        fig, ax = plt.subplots(figsize=(5, 3), tight_layout=True)
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
        fig, ax = plt.subplots(figsize=(10, 2), tight_layout=True)
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
        fig, ax = plt.subplots(figsize=(5, 3), tight_layout=True)
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
        fig, ax = plt.subplots(figsize=(5, 3), tight_layout=True)
        if y_column is None:
            counts = self.data[x_column].value_counts()
            ax.bar(counts.index, counts.values, color=color)
        else:
            ax.bar(self.data[x_column], self.data[y_column], color=color)
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        return fig, ax

    def generate_top_cities_bar_chart(self, column):
        """
        Generate a bar chart for the top 5 cities with the most reports.

        :param column: The column containing city data.
        :return: The figure and axis objects.
        """
        fig, ax = plt.subplots(figsize=(5, 3), tight_layout=True)
        top_cities = self.data[column].value_counts().head(5)
        top_cities.plot(kind='bar', color='salmon')
        ax.set_title('')
        ax.set_xlabel('City')
        ax.set_ylabel('Number of Reports')
        plt.xticks(rotation=15)
        return fig, ax

    def generate_pie_chart_ufo_shape(self, column, title):
        """
        Generate a pie chart for UFO shapes.

        :param column: The column containing UFO shape data.
        :param title: The title of the pie chart.
        :return: The figure and axis objects.
        """
        def autopct_more_than_4(pct):
            return ('%1.f%%' % pct) if pct > 4 else ''

        count = self.data[column].value_counts()
        percentages = 100 * count / count.sum()  # Calculate percentages
        labels_with_percentage = [f'{label} ({percentage:.0f}%)'
                                  for label, percentage in zip(count.index, percentages)]

        fig, ax = plt.subplots(figsize=(10, 3.5), tight_layout=True)
        wedges, _, autotexts = ax.pie(count, autopct=autopct_more_than_4, startangle=90)
        plt.legend(wedges, labels_with_percentage, loc='center right',
                   bbox_to_anchor=(2.15, 0.5), ncol=2)
        ax.set_title(title)
        return fig, ax

    @staticmethod
    def remove_all_outliers(data):
        """
        Remove outliers from the data.

        :param data: The DataFrame containing the data.
        :return: DataFrame without outliers.
        """
        for column in data.select_dtypes(include='number').columns:
            Q1 = data[column].quantile(0.25)
            Q3 = data[column].quantile(0.75)
            IQR = Q3 - Q1

            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            data = data[(data[column] >= lower_bound) & (data[column] <= upper_bound)]
        return data
