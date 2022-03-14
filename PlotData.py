import plotly
import plotly.express as px
import plotly.graph_objs as go
import json
import pandas as pd


class Plot:

    def __init__(self):
        pass

    def area_plot(self, df_exercise, color_column, title, x, y, text, text_color, yaxis_title, xaxis_title, y_range, line_color, line_group):

        fig = px.area(
            df_exercise,
            x=x,
            y=y,
            text=text,
            color=color_column,
            markers=True,
            width=900,
            height=500,
            line_shape='spline',
            line_group=line_group,
        )

        fig.update_layout(
            title=title,
            titlefont=dict(
                size=14,
                color='#a4acbc'
            ),
            xaxis_title=xaxis_title,
            yaxis_title=yaxis_title,
            yaxis=dict(
                titlefont=dict(
                    size=12,
                )
            ),
            paper_bgcolor='#071d49',
            plot_bgcolor='#071d49',
            font=dict(color='#fff'),
            width=600,
            height=300,
        )

        fig.update_xaxes(showgrid=False, gridcolor='#25385f')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#25385f', range=y_range)

        fig.update_traces(
            textposition="top left",
            textfont=dict(
                size=11,
                color=text_color,
            ),
            line_color=line_color,
        )
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    def area_plot_with_scale(self, df_exercise, reps_range, color_column, title, x, y, yaxis_title, xaxis_title, y_range, color_discrete_sequence, legend_order='normal', text=None):

        fig = px.area(
            df_exercise,
            x=x,
            y=y,
            color=color_column,
            text=text,
            color_discrete_sequence=color_discrete_sequence,
            markers=True,
            width=900,
            height=500,
            line_shape='spline',
            category_orders={"Répétitions": reps_range}
        )

        fig.update_layout(
            title=title,
            titlefont=dict(
                size=14,
                color='#a4acbc'
            ),
            xaxis_title=xaxis_title,
            yaxis_title=yaxis_title,
            yaxis=dict(
                titlefont=dict(
                    size=12,
                )
            ),
            paper_bgcolor='#071d49',
            plot_bgcolor='#071d49',
            font=dict(color='#fff'),
            legend={'traceorder': legend_order},
            width=600,
            height=300,
        )

        fig.update_xaxes(showgrid=False, gridcolor='#25385f')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#25385f', range=y_range)

        fig.update_traces(
            textposition="top left",
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

    def pie_chart(self, df_data, values, names, color_discrete_sequence, title, legend_pos_y=0.5, legend_pos_x=1.25,
                  margin_l=0, margin_r=200, margin_b=65, margin_t=65):

        fig = px.pie(
            df_data,
            values=values,
            names=names,
            hole=.5,
            color_discrete_sequence=color_discrete_sequence
        )

        fig.update_layout(
            width=600,
            height=275,
            title=title,
            titlefont=dict(
                size=14,
                color='#a4acbc'
            ),
            paper_bgcolor='#071d49',
            margin=go.layout.Margin(
                l=margin_l,  # left margin
                r=margin_r,  # right margin
                b=margin_b,  # bottom margin
                t=margin_t,  # top margin
            ),
            legend=dict(
                orientation="v",
                yanchor="bottom",
                y=legend_pos_y,
                xanchor="right",
                x=legend_pos_x,
                font=dict(
                    size=13,
                    color="white"
                ),
            ),
        )

        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    def separated_hist_chart(self, df, title, color_discrete_sequence, legend_title=None, xaxis_title=None, yaxis_title=None, y_range=None):

        fig = px.histogram(
            df,
            x='Repetitions',
            y='Exercise',
            orientation='h',
            histfunc='avg',
            color='Exercise',
            height=300,
            width=600,
            color_discrete_sequence=color_discrete_sequence
        )

        fig.update_layout(
            title=title,
            titlefont=dict(
                size=14,
                color='#a4acbc'
            ),
            xaxis_title=xaxis_title,
            yaxis_title=yaxis_title,
            yaxis=dict(
                titlefont=dict(
                    size=12,
                )
            ),
            paper_bgcolor='#071d49',
            plot_bgcolor='#071d49',
            font=dict(color='#fff'),
            legend=dict(
                title=legend_title,
            ),
            bargap=0.4
        )

        fig.update_xaxes(showgrid=False, gridcolor='#25385f')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#25385f', categoryorder='total ascending', range=y_range)

        # for data in fig.data:
        #     data["width"] = 0.30

        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    def bubble_chart(self, data_df, x, y, title, size, color, hover_name, legend_title, yaxis_title=None, xaxis_title=None):

        fig = px.scatter(
            data_df,
            width=600,
            height=300,
            x=x,
            y=y,
            size=size,
            color=color,
            #color_continuous_scale='Inferno',
            hover_name=hover_name,

        )

        fig.update_layout(
            title=title,
            titlefont=dict(
                size=14,
                color='#a4acbc'
            ),
            xaxis_title=xaxis_title,
            yaxis_title=yaxis_title,
            yaxis=dict(
                titlefont=dict(
                    size=12,
                )
            ),
            paper_bgcolor='#071d49',
            plot_bgcolor='#071d49',
            font=dict(color='#fff'),
            legend=dict(
                title=legend_title,
            ),
        )

        fig.update_xaxes(showgrid=False, gridcolor='#25385f')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#25385f')

        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)






