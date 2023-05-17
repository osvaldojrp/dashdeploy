import plotly.express as px
import pandas as pd
import dash
from dash import dcc
from dash import html
from trase.tools.aws.aws_helpers import read_geojson

gdf = read_geojson(
    "spatial/risk_benchmark/country_level_risk/beef/out/global_beef_deforestation_risk_categorization_first_stage"
    ".geojson",
    sep=";",
    keep_default_na=True)


gdf['Cumulative contribution (%)'] = gdf['Cumulative contribution (%)'].fillna(100)

gdf['risk category (detailed)'] = gdf['risk category (detailed)'] \
    .replace({'DCF country - not a major producer': 'Negligible risk: not major producer',
              'At risk of absolute deforestation': 'At-risk: commoditity deforestation',
              'At risk of relative deforestation': 'At-risk: high footprint',
              'At risk of ecosystem conversion': 'At-risk: ecosystem conversion',
              'DCF country - low ecosystem conversion': 'Negligible risk: low ecosystem conversion'}, regex=True)

# Create the Dash app
app = dash.Dash(__name__)

# Define the layout of the Dash app
app.layout = html.Div(
    style={'fontFamily': 'DM Sans Medium'},
    children=[
        html.H1("Global cattle deforestation risk"),  # Title for the map
        dcc.Graph(
            id='choropleth-graph',
            style={'height': '80vh'}
        ),
        dcc.RadioItems(
            id='radio-items',
            options=[
                {'label': 'Aggregated risk categories', 'value': 'risk-categories'},
                {'label': 'Detailed risk categories', 'value': 'detailed-risk-categories'}
            ],
            value='risk-categories',
            labelStyle={'display': 'inline-block'}
        ),
        html.Div(
            style={'margin': '20px'},
            children=[
                html.H3("Contribuiton to the glogal cattle deforestation"),  # Title for the slider
                dcc.Slider(
                    id='slider',
                    min=0,
                    max=gdf['Cumulative contribution (%)'].max(),
                    value=100.001,
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ]
        )
    ]
)


# Callback function to update the displayed figure based on the slider value
@app.callback(
    dash.dependencies.Output('choropleth-graph', 'figure'),
    [dash.dependencies.Input('slider', 'value'),
     dash.dependencies.Input('radio-items', 'value')]
)
def update_figure(slider_value, selected_option):
    filtered_df = gdf[gdf['Cumulative contribution (%)'] < slider_value]
    if selected_option == 'risk-categories':
        hover_df = pd.DataFrame({
            'ISO-3': filtered_df['ISO3'],
            'Country': filtered_df['Country'],
            'Risk category': filtered_df['risk category (aggregated)'],
            'Contribution to global deforestation (%)': filtered_df['Cumulative contribution (%)'],
            '2014-2018 Cattle deforestation (ha)': filtered_df['Average pasture deforestation (2014-2018) - ha'],
            '2014-2018 Cattle production (ton.)': filtered_df['Average cattle production (2014-2018) - tonnes']
        })

        fig = px.choropleth(
            data_frame=hover_df,
            locations='ISO-3',
            locationmode="ISO-3",
            color='Risk category',
            color_discrete_map={'DCF country': '#BBFFEC',
                                'at-risk country': '#FF6A5F',
                                'no data': '#E2EAE7'},
            geojson=filtered_df.geometry,
            featureidkey="properties.NAME",
            projection="robinson",
            hover_data=['Country', 'Contribution to global deforestation (%)',
                        '2014-2018 Cattle deforestation (ha)', '2014-2018 Cattle production (ton.)'],
        )

        fig.update_layout(
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            geo=dict(showframe=False, showcoastlines=False, showocean=False, showland=True),
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                itemclick='toggleothers',
                font=dict(
                    family="DM Sans",
                    size=14,
                    color="#839A8C"
                ),
                title='Aggregated risk categories',
                title_font={"size": 14, "color": '#839A8C', "family": "DM Sans Medium"}  # Update legend title font
            )
        )

        fig.update_traces(
            marker_line_width=1,
            marker_line_color='white'
        )

        return fig

    elif selected_option == 'detailed-risk-categories':
        hover_df = pd.DataFrame({
            'ISO-3': filtered_df['ISO3'],
            'Country': filtered_df['Country'],
            'Risk category': filtered_df['risk category (detailed)'],
            'Contribution to global deforestation (%)': filtered_df['Cumulative contribution (%)'],
            '2014-2018 Cattle deforestation (ha)': filtered_df['Average pasture deforestation (2014-2018) - ha'],
            '2014-2018 Cattle production (ton.)': filtered_df['Average cattle production (2014-2018) - tonnes']
        })

        fig = px.choropleth(
            data_frame=hover_df,
            locations='ISO-3',
            locationmode="ISO-3",
            color='Risk category',
            color_discrete_map={'At-risk: commoditity deforestation': '#E27227',
                                'At-risk: ecosystem conversion': '#E9EF00',
                                'At-risk: high footprint': '#EB60C2',
                                'Negligible risk: low ecosystem conversion': '#658270',
                                'Negligible risk: not major producer': '#849A8E',
                                'no data': '#E2EAE7'},
            geojson=filtered_df.geometry,
            featureidkey="properties.NAME",
            projection="robinson",
            hover_data=['Country', 'Contribution to global deforestation (%)',
                        '2014-2018 Cattle deforestation (ha)', '2014-2018 Cattle production (ton.)'],
        )

        fig.update_layout(
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            geo=dict(showframe=False, showcoastlines=False, showocean=False, showland=True),
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                itemclick='toggleothers',
                font=dict(
                    family="DM Sans",
                    size=14,
                    color="#839A8C"
                ),
                title='Detailed risk categories',
                title_font={"size": 14, "color": '#839A8C', "family": "DM Sans Medium"}  # Update legend title font
            )
        )

        fig.update_traces(
            marker_line_width=1,
            marker_line_color='white'
        )

        return fig


# Run the Dash application
if __name__ == '__main__':
    app.run_server(debug=True)