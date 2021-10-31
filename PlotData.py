import plotly
import plotly.express as px
import plotly.graph_objs as go
import json
import pandas as pd


class Plot:

    def __init__(self):
        pass

    def line_plot(self, df_exercise, color_column, title):

        print(df_exercise.dtypes)
        print(df_exercise)

        df_exercise = df_exercise.sort_values(by='Date', ascending=False)  # à modifier
        fig = px.line(
            df_exercise,
            x='Date',
            y='Charge',
            color=color_column,
            markers=True,
            width=900,
            height=500
        )
        fig.update_layout(
            title=title,
            yaxis_title="Charge (en Kg)",
        )
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


