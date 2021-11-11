import plotly
import plotly.express as px
import plotly.graph_objs as go
import json
import pandas as pd


class Plot:

    def __init__(self):
        pass

    def line_plot(self, df_exercise, color_column, title, x, y, text, yaxis_title, xaxis_title):

        fig = px.line(
            df_exercise,
            x=x,
            y=y,
            text=text,
            color=color_column,
            markers=True,
            width=900,
            height=500,
            line_shape='spline'
        )
        fig.update_layout(
            title=title,
            xaxis_title=xaxis_title,
            yaxis_title=yaxis_title,
        )
        fig.update_traces(
            textposition="bottom right"
        )
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    def hist_plot(self, function, x_axis, y_axis, label_name, title, xaxis_title, yaxis_title):

        fig = go.Figure()
        fig.add_trace(go.Histogram(histfunc=function, y=y_axis[0], x=x_axis, name=label_name[0]))
        fig.add_trace(go.Histogram(histfunc=function, y=y_axis[1], x=x_axis, name=label_name[1]))
        fig.add_trace(go.Histogram(histfunc=function, y=y_axis[2], x=x_axis, name=label_name[2]))

        fig.update_layout(
            title=title,
            xaxis_title=xaxis_title,
            yaxis_title=yaxis_title,
            width=600,
            height=500
        )

        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


