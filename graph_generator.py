class GraphGenerator:
    def __init__(self, data):
        self.data = data
        self.remove_all_outliers()

    def generate_histogram(self, column, title, xlabel, ylabel, ax):
        ax.hist(self.data[column], bins=20, color='skyblue')
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

    def generate_pie_chart(self, column, title, ax):
        count = self.data[column].value_counts()
        ax.pie(count, labels=count.index, autopct='%1.1f%%', startangle=140)
        ax.set_title(title)

    def generate_line_graph(self, x_column, y_column, title, xlabel, ylabel, ax):
        if y_column is None:
            counts = self.data[x_column].value_counts().sort_index()
            ax.plot(counts.index, counts.values, marker='o', color='purple')
            ax.set_title(title)
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
        else:
            ax.plot(self.data[x_column], self.data[y_column], marker='o', color='purple')
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

    def generate_scatter_plot(self, x_column, y_column, title, xlabel, ylabel, ax):
        if y_column is None:
            y_column = self.data[x_column].value_counts().index
            counts = self.data[x_column].value_counts().sort_index()
            ax.scatter(counts.index, counts.values, color='orange')
        else:
            ax.scatter(self.data[x_column], self.data[y_column], color='orange')
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

    def generate_bar_graph(self, x_column, y_column, title, xlabel, ylabel, ax):
        if y_column is None:
            counts = self.data[x_column].value_counts()
            ax.bar(counts.index, counts.values, color='purple')
        else:
            ax.bar(self.data[x_column], self.data[y_column], color='purple')
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

    def generate_top_cities_bar_chart(self, column, ax):
        top_cities = self.data[column].value_counts().head(5)
        top_cities.plot(kind='bar', ax=ax, color='salmon')
        ax.set_title('Top 5 Cities with the Most Reports')
        ax.set_xlabel('City')
        ax.set_ylabel('Number of Reports')

    def remove_all_outliers(self):
        for column in self.data.select_dtypes(include='number').columns:
            Q1 = self.data[column].quantile(0.25)
            Q3 = self.data[column].quantile(0.75)
            IQR = Q3 - Q1

            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            self.data = self.data[(self.data[column] >= lower_bound) & (self.data[column] <= upper_bound)]




