import plotly.express as px


class Plot:

    def scatter_plot(self, df, x_data, y_data, color):
        fig = px.scatter(df, x=x_data, y=y_data, color=color)
        fig.show()
