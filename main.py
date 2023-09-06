


#______________________________________________________________________________________
import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc

import re

# New version. # We define the transformation that will take care of our columns
def apply_transformation(value):
    # For both types of columns (strings and strings which should represent Dates) we check if the value is Blank
    if pd.isna(value) or pd.isnull(value):
        return "N/A"

    # For strings, we check if it contains variations of "N/A", "#N/A", "n-a", etc.
    if isinstance(value, str) and re.fullmatch(r'^(n[/-]?a|N[/-]?A|#N[/-]?A)$', value, flags=re.IGNORECASE):
        return "N/A"

    # We check for dates:
    if isinstance(value, str) and re.search(r'(\d{1,2})[/-]\d{1,2}[-]\d{2,4}', value):
        try:
            # We try to convert the value to a datetime format. We use dayfirst=True to tell Pandas how to interpret date strings
            # We use errors='raise' so that if the value is not a valid date, pandas will raise a ValueError
            date_object = pd.to_datetime(value, dayfirst=True, errors='raise')
            return date_object.strftime('%d/%m/%Y')  # We convert to the format we want (DD/MM/YYYY)

        except ValueError:
            return "N/A"

    # At the end we return
    return value


file_path = 'Automation_Test.xlsx'
#_________________________________________________________________
#1) PRE AUD
# We read the Pre Aud Sheet (named Sheet1) of the Excel file
df = pd.read_excel('Automation_Test.xlsx', sheet_name='Sheet1')
print(df)


# We define a Function that reads an Excel file and a specific sheet of it, and applies the transformation
# (function) apply_transformation we created before
def read_and_transform(file_path, sheet_name=1):
    # We first read the file
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    # We then apply the transformation to the columns:
    columns_to_transform = ['Service Type', 'Region', 'Country', 'Business ID',
                            'Business CRM ID', 'Business Name', 'Assigned Date', 'Delivery Date', 'Person',
                            'Service Result']
    for col in columns_to_transform:
        df[col] = df[col].apply(apply_transformation)

    return df


# We read the Pre Aud Sheet (named Sheet1) of the Excel file
transformed_df = read_and_transform(file_path, sheet_name='Sheet1')
print(transformed_df)

#________________________________
# 2) AUD
# We read the Aud Sheet (named Sheet2) of the Excel file
aud_df = pd.read_excel('Automation_Test.xlsx', sheet_name='Sheet2')
print(aud_df)


# When we read it for th 1st time (without having done any transformation yet) the Dates columns have NaN for N/A or blank values

# We define a Function that reads an Excel file and a specific sheet of it, and applies the transformation
# (function) apply_transformation we created before
def aud_read_and_transform(file_path, sheet_name='Sheet 2'):
    # We first read the file
    aud_df = pd.read_excel(file_path, sheet_name=sheet_name)

    # We then apply the transformation to the columns:
    aud_columns_to_transform = ['A Type', 'Region', 'Country', 'Business ID', 'Business CRM ID', 'Business Name',
                                'Comb', 'C Start Date', 'C Expiry Date', 'Person', 'A Result']
    for col in aud_columns_to_transform:
        aud_df[col] = aud_df[col].apply(apply_transformation)

    return aud_df


aud_transformed_df = aud_read_and_transform(file_path, sheet_name='Sheet2')
print(aud_transformed_df)
# Now the the Dates columns have N/A instead of NaN for N/A or blank values

#----------------------------------

import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State

#_______________________________________________________________________________________________________________________________________

# PRE AUD and AUD

# 1) PRE AUD
# Assume the transformed_df is ready here.

# Replace "N/A" with NaN (NaT) in the 'Assigned Date' and 'Delivery Date' columns
transformed_df['Assigned Date'] = pd.to_datetime(transformed_df['Assigned Date'], errors='coerce')
transformed_df['Delivery Date'] = pd.to_datetime(transformed_df['Delivery Date'], errors='coerce')

# Create a new column 'N/A Delivery Date' to indicate if the row has 'N/A' in 'Delivery Date'
transformed_df['N/A Delivery Date'] = transformed_df['Delivery Date'].isna()

# Pre Aud: Create a color dictionary to map color based on the values of the Legend (G, R, Y, C)
pre_aud_color_dict = {
    'G': 'green',
    'R': 'red',
    'Y': 'yellow',
    'C': 'lightblue'
}

# 2) PRE AUD
# Assume the aud_transformed_df is ready here.

# We convert the 'C Start Date' and 'C Expiry Date' columns to datetime format and Replace "N/A" with NaN (NaT) in their columns
aud_transformed_df['C Start Date'] = pd.to_datetime(aud_transformed_df['C Start Date'], errors='coerce')
aud_transformed_df['C Expiry Date'] = pd.to_datetime(aud_transformed_df['C Expiry Date'], errors='coerce')

# Create a new column 'N/A C Start Date' to indicate if the row has 'N/A' in 'C Start Date'
aud_transformed_df['N/A C Start Date'] = aud_transformed_df['C Start Date'].isna()
aud_transformed_df['N/A C Expiry Date'] = aud_transformed_df['C Expiry Date'].isna()
# Aud: Create a color dictionary to map color based on the values of the Aud Legend (P, F, DE, PWC)
aud_color_dict = {
    'P': 'green',
    'F': 'red',
    'DE': 'yellow',
    'PWC': 'lightblue'
}

# Create the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP])

# Define the layout of the dashboard
app.layout = dbc.Container([ #Create a Container with all elements inside to set the padding(spacing)
    html.Div([ # Opens app.layout
        # Main Heading
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Img(src=app.get_asset_url('SAP_logo.png'),
                             id='logo-image',
                             style={
                                 "height": "45px",
                                 "width": "auto",
                                 "margin-bottom": "25px",
                             },
                    )
                ]),
            ]),
            dbc.Col([
                html.H1("Dashboard")
            ], style={'color': 'white', 'text-align':'center'}),
            dbc.Col([
                ])
        ]),
        # Pre Aud Heading
        dbc.Row([
            dbc.Col([
                html.H3("Pre Aud")
            ], style={'color': 'white'})
        ]),

        # Filter controls for Pre AUD section
        html.Div([ #Pre Aud filters group
            dbc.Row([
                dcc.Input(
                    id='date-placeholder',
                    type='text',
                    value='Select Delivery Dates',
                    style={
                        'color': 'lightgray',
                        'background-color': '#1f2c56'
                    }
                ),
            ]),
            dbc.Row([
                dcc.DatePickerRange(
                    id='date-filter',
                    start_date=pd.to_datetime(transformed_df['Delivery Date'], errors='ignore').min(),
                    end_date=pd.to_datetime(transformed_df['Delivery Date'], errors='ignore').max(),
                    display_format='DD/MM/YYYY',
                    style={
                            'color': 'white',
                            'background-color': '#1f2c56'
                    },

                ),
            ], className= 'date-range-picker'), #We use CSS

            # Dropdown for filtering based on Region
            dbc.Row([
                dcc.Dropdown(
                    id='region-filter',
                    options=[
                        {'label': region, 'value': region} for region in transformed_df['Region'].unique()
                    ],
                    multi=True,
                    placeholder='Select Region',

                ),
            ]),
            # Dropdown for filtering based on Country
            dbc.Row([
                dcc.Dropdown(
                    id='country-filter',
                    options=[
                        {'label': country, 'value': country} for country in transformed_df['Country'].unique()
                    ],
                    multi=True,
                    placeholder='Select Country'
                ),
            ]),
            # Dropdown for filtering based on Service Type
            dbc.Row([
                dcc.Dropdown(
                    id='service-type-filter',
                    options=[
                        {'label': service_type, 'value': service_type} for service_type in
                        transformed_df['Service Type'].unique()
                    ],
                    multi=True,
                    placeholder='Select Service Type'
                ),
            ]),
            # RadioItems for choosing whether to include or exclude rows with 'N/A' in the 'Delivery Date' column
            dbc.Row([
                dcc.RadioItems(
                    id='include-na-radio',
                    options=[
                        {'label': 'Include Rows with N/A in Delivery Date', 'value': 'include_na'},
                        {'label': 'Exclude Rows with N/A in Delivery Date', 'value': 'exclude_na'},
                    ],
                    value='exclude_na',  # Set the default value to exclude rows with N/A in Delivery Date
                )
            ], style={'color':'lightgrey'}), #We do not use CSS but style=
        ]), #Pre Aud filters group

        #Charts for Pre AUD section: 1 Row for both Charts (so Row, Col, Col)
        html.Div([ #Pre Aud Charts group
            dbc.Row([
                # 1st Chart
                dbc.Col([
                    dcc.Graph(id='service-result-pct-chart', className='chart-small')
                ], className="col-md-6 col-12"),
                # 2nd Chart
                dbc.Col([
                    dcc.Graph(id='service-type-count-chart', className='chart-small')
                ], className="col-md-6 col-12"),
            #dcc.Graph(id='service-result-pct-chart', className='chart-small'),
            #dcc.Graph(id='service-type-count-chart', className='chart-small')
            ]),
        ], className='pre-aud-chart-row'), #Pre Aud Charts group

        # Add space between the Pre Aud charts and the Aud section
        html.Div(style={'margin-bottom': '50px'}),

        # AUD SECTION
        # Aud Heading
        dbc.Row([
            dbc.Col([
                html.H3("Aud")
            ], style={'color': 'white'})
        ]),

        # Filter controls for AUD section
        html.Div([ # Aud DatePickerRange group
            dbc.Row([
                dbc.Col([
                    # Wrapper div for dcc.DatePickerRange
                    html.Div([
                        html.P("Select C Start Dates", style={'margin-bottom':'5px', 'color': 'lightgray'}),  # Text above the DatePickerRange
                        dcc.DatePickerRange(
                            id='start-date-filter',
                            # The names of the properties of the DatePickerRange are: start_date and end_date. Later in def update_charts() we will use:
                            # cert_start_date_start_date, cert_start_date_end_date etc..
                            start_date=aud_transformed_df['C Start Date'].min(),  # Set the start date as the minimum date in the data
                            end_date=aud_transformed_df['C Start Date'].max(),  # Set the end date as the maximum date in the data
                            display_format='DD/MM/YYYY'
                        ),
                    ], style={'display': 'inline-block', 'marginRight': '20px'}), # Adjust margin-right for spacing between components
                ]),
                dbc.Col([
                    # Wrapper div for dcc.DatePickerRange
                    html.Div([
                        html.P("Select C Expiry Dates", style={'margin-bottom':'5px', 'color':'lightgray'}),  # Text above the DatePickerRange"
                        dcc.DatePickerRange(
                            id='expiry-date-filter',
                            start_date=aud_transformed_df['C Expiry Date'].min(),  # Set the start date as the minimum date in the data
                            end_date=aud_transformed_df['C Expiry Date'].max(),  # Set the end date as the maximum date in the data
                            display_format='DD/MM/YYYY'
                        ),
                    ], style={'display': 'inline-block'}), # Adjust margin-right for spacing between components
                ]),
            ], className= 'date-range-picker'),
        ]), # Aud DatePickerRange group    #], className='date-picker-row'),

        # Rest of the components (dropdowns, radio items, and charts) remain unchanged.
        # Dropdown for filtering based on Aud Type
        html.Div([ # Aud Filters group
            dbc.Row([
                dcc.Dropdown(
                    id='aud-type-filter',
                    options=[
                        {'label': aud_type, 'value': aud_type} for aud_type in aud_transformed_df['A Type'].unique()
                    ],
                    multi=True,
                    placeholder='Select Aud Type'
                ),
            ]),
            # Dropdown for filtering based on Region
            dbc.Row([
                dcc.Dropdown(
                    id='aud_region-filter',
                    options=[
                        {'label': region, 'value': region} for region in aud_transformed_df['Region'].unique()
                    ],
                    multi=True,
                    placeholder='Select Region'
                ),
            ]),
            # Dropdown for filtering based on Country
            dbc.Row([
                dcc.Dropdown(
                    id='aud_country-filter',
                    options=[
                        {'label': country, 'value': country} for country in aud_transformed_df['Country'].unique()
                    ],
                    multi=True,
                    placeholder='Select Country'
                ),
            ]),
            # Dropdown for filtering based on Comb
            dbc.Row([
                dcc.Dropdown(
                    id='combined-filter',
                    options=[
                        {'label': comb, 'value': comb} for comb in aud_transformed_df['Comb'].unique()
                    ],
                    multi=False,  # It can't be Yes and No at the same time, but just one of them
                    placeholder='Select if Combined or Not'
                ),
            ]),
            # RadioItems for choosing whether to include or exclude rows with 'N/A' in the 'C Start Date' column
            dbc.Row([
                dcc.RadioItems(
                    id='start-date-na-radio',
                    options=[
                        {'label': 'Include Rows with N/A in C Start Date', 'value': 'include_na'},
                        {'label': 'Exclude Rows with N/A in C Start Date', 'value': 'exclude_na'},
                    ],
                    value='exclude_na',  # Set the default value to exclude rows with N/A in C Start Date
                ),
            ], style={'color':'lightgrey'}), #We do not use CSS but style=
        ]), # Aud Filters group #], className='filter-container'),  ########################

        # Charts for AUD section
        html.Div([ #Aud Charts group
            # 1st row of AUD charts (2 charts)
            dbc.Row([
                # 1st Chart
                dbc.Col([
                    dcc.Graph(id='aud-result-pct-chart', className='chart-container')
                ], className="col-md-6 col-12"),
                # 2nd Chart
                dbc.Col([
                    dcc.Graph(id='aud-type-count-chart', className='chart-container')
                ], className="col-md-6 col-12"),
            #dcc.Graph(id='service-result-pct-chart', className='chart-small'),
            #dcc.Graph(id='service-type-count-chart', className='chart-small')
            ]),
        # 2nd row of AUD charts (1 chart)
            dbc.Row([
                dcc.Graph(id='cert-expiry-date-chart', className='chart-container')
            ]),
        ]), #, className='aud-chart-group'), #Aud Charts group


    ]) #Closes app.layout
],  className='main-container') #Set fluid=True for a full-width container, adjust padding. style={'padding':'10px', 'background-color': '#192444'},
#Closes dbc.Container


# Callback for updating Pre AUD charts
@app.callback(
    [Output('service-result-pct-chart', 'figure'),
    Output('service-type-count-chart', 'figure')],
    [Input('date-filter', 'start_date'),
    Input('date-filter', 'end_date'),
    Input('region-filter', 'value'),
    Input('country-filter', 'value'),
    Input('service-type-filter', 'value'),
    Input('include-na-radio', 'value')]
)

# Define Update charts for Pre Aud
def update_charts(start_date, end_date, selected_regions, selected_countries, selected_service_types, include_na):
    # Filter the DataFrame based on the selected filters
    filtered_df = transformed_df.copy()

    if start_date and end_date:
        # We include also those rows with NaT values cause then they will be removed by the "Exclude N/A Rows" option (which is
        # selected by default)
        filtered_df = filtered_df[
            (filtered_df['Delivery Date'] >= start_date) & (filtered_df['Delivery Date'] <= end_date)
            | (pd.isna(filtered_df['Delivery Date']))
            ]

    if include_na == 'include_na':
        # We just make a copy of filtered_df which has the Delivery Date column containing also the NaT values from the lines
        # before cause we still did not enetered the else and we eill not enter
        filtered_df = filtered_df.copy()

    else:  # At the start we have this condition cause the RadioItems button is set to Exclude
        filtered_df = filtered_df.loc[~filtered_df['Delivery Date'].isna()]
        # Boolean indexing to select rows where the 'Delivery Date' column is not 'N/A'

    if selected_regions:
        filtered_df = filtered_df[filtered_df['Region'].isin(selected_regions)]
    if selected_countries:
        filtered_df = filtered_df[filtered_df['Country'].isin(selected_countries)]
    if selected_service_types:
        filtered_df = filtered_df[filtered_df['Service Type'].isin(selected_service_types)]

    # Calculate the percentage of Service Result by Region and Country: service_result_pct_df
    # First Calculate the total count for each region
    region_total_counts = filtered_df.groupby(['Region'])['Service Type'].count().reset_index()
    region_total_counts.rename(columns={'Service Type': 'Region Count'}, inplace=True)

    # Calculate the count of each Service Result within each Region
    service_result_counts = filtered_df.groupby(['Region', 'Service Result'])['Service Type'].count().reset_index()
    service_result_counts.rename(columns={'Service Type': 'Service Result Count'}, inplace=True)

    # Merge the two DataFrames to calculate the percentage
    service_result_pct_df = service_result_counts.merge(region_total_counts, on='Region')

    # Calculate the percentage based on the total count of services for all regions
    service_result_pct_df['Percentage'] = service_result_pct_df['Service Result Count'] / service_result_pct_df[
        'Region Count'].sum() * 100

    # Create the chart for Service Result by Region and Country
    fig1 = px.bar(service_result_pct_df, x='Region', y='Percentage', color='Service Result', barmode='group', color_discrete_map=pre_aud_color_dict, title='Service Result by Region and Country')
    # fig1 = go.Figure(
    #     data=[
    #         go.Bar(
    #             x=service_result_pct_df['Region'],
    #             y=service_result_pct_df['Percentage'],
    #             text=service_result_pct_df['Percentage'].apply(lambda x: f"{x:.2f}%"),
    #             hoverinfo='text',
    #             marker_color=service_result_pct_df['Service Result'].map(pre_aud_color_dict)
    #         )
    #     ]
    # )
    fig1.update_layout(
        title='Service Result by Region and Country',
        xaxis_title='Region', #We give the name of the x axis title (here is the same name of the column)
        yaxis_title='Percentage (%)',
        paper_bgcolor='#1f2c56',
        plot_bgcolor='#1f2c56',
        font_color='white',  # Setting font color to white

    )

    # Calculate the count of each Service Type within each Region
    service_type_counts = filtered_df.groupby(['Region', 'Service Type'])['Service Result'].count().reset_index()
    service_type_counts.rename(columns={'Service Result': 'Count'}, inplace=True)

    # Create the chart for Service Type by Region and Country
    fig2 = px.bar(service_type_counts, x='Region', y='Count', color='Service Type', title='Service Type by Region and Country')
    # fig2 = go.Figure(
    #     data=[
    #         go.Bar(
    #             x=service_type_counts['Region'],
    #             y=service_type_counts['Count'],
    #             text=service_type_counts['Count'],
    #             hoverinfo='text',
    #             marker_color=service_type_counts['Service Type'].map(pre_aud_color_dict)
    #         )
    #     ]
    # )
    fig2.update_layout(
        title='Service Type by Region and Country',
        xaxis_title='Region',
        yaxis_title='Count',
        paper_bgcolor='#1f2c56',
        plot_bgcolor='#1f2c56',
        font_color='white'
    )
    return fig1, fig2
    # Returned updated figures


# Callback for updating the 3 AUD charts
@app.callback(
    [Output('aud-result-pct-chart', 'figure'),
     Output('aud-type-count-chart', 'figure'),
     Output('cert-expiry-date-chart', 'figure')],
    [Input('start-date-filter', 'start_date'),
     Input('start-date-filter', 'end_date'),
     Input('expiry-date-filter', 'start_date'),
     Input('expiry-date-filter', 'end_date'),
     Input('aud-type-filter', 'value'),
     Input('aud_region-filter', 'value'),
     Input('aud_country-filter', 'value'),
     Input('combined-filter', 'value'),
     Input('start-date-na-radio', 'value')]
)
# Define Update charts for Aud
def update_charts(cert_start_date_start_date, cert_start_date_end_date, cert_expiry_date_start_date,
                  cert_expiry_date_end_date,
                  selected_aud_types, selected_regions, selected_countries, selected_combined, include_na):
    # Filter the DataFrame based on the selected filters
    aud_filtered_df = aud_transformed_df.copy()

    if cert_start_date_start_date and cert_start_date_end_date:  # Same as using: "if cert_start_date_start_date and cert_start_date_end_date is not None:"
        # We include also those rows with NaT values cause then they will be removed by the "Exclude N/A Rows" option (which is
        # selected by default)
        aud_filtered_df = aud_filtered_df[
            (aud_filtered_df['C Start Date'] >= cert_start_date_start_date) & (
                        aud_filtered_df['C Start Date'] <= cert_start_date_end_date)
            | (pd.isna(aud_filtered_df['C Start Date']))
            ]

    if cert_expiry_date_start_date and cert_expiry_date_end_date:
        # We include also those rows with NaT values cause then they will be removed by the "Exclude N/A Rows" option (which is
        # selected by default)
        aud_filtered_df = aud_filtered_df[
            (aud_filtered_df['C Expiry Date'] >= cert_expiry_date_start_date) & (
                        aud_filtered_df['C Expiry Date'] <= cert_expiry_date_end_date)
            | (pd.isna(aud_filtered_df['C Expiry Date']))
            ]

    if include_na == 'include_na':  # Same as using: "if include_na is not None:"
        # We just make a copy of filtered_df which has the C Start Date column containing also the NaT values from the lines
        # before cause we still did not enter the else and we will not enter
        aud_filtered_df = aud_filtered_df.copy()

    else:  # At the start we have this condition cause the RadioItems button is set to Exclude
        aud_filtered_df = aud_filtered_df.loc[~aud_filtered_df['C Start Date'].isna()]
        # Boolean indexing to select rows where the 'C Start Date' column is not 'N/A'

    if selected_aud_types:
        aud_filtered_df = aud_filtered_df[aud_filtered_df['A Type'].isin(selected_aud_types)]
    if selected_regions:
        aud_filtered_df = aud_filtered_df[aud_filtered_df['Region'].isin(selected_regions)]
    if selected_countries:
        aud_filtered_df = aud_filtered_df[aud_filtered_df['Country'].isin(selected_countries)]
    if selected_combined:
        # Convert selected_combined to lowercase (to match the column values)
        selected_combined = selected_combined.lower()
        aud_filtered_df = aud_filtered_df[aud_filtered_df['Comb'].str.lower() == selected_combined]
        # isin() requires a list. Here we have 2 options: or we wrap the value, the string (which can be Yes, No, N/A in a list)
        # and we use isin() or we simply use the string and check for an exact match with == without the need to wrap the value
        # in a list.

    # We create now all the Charts. For each chart we create a specific dataframe using the aud_filtered_df

    # 1st Chart: Calculate A Result counts using the filtered DataFrame
    aud_result_pct_df = aud_filtered_df.groupby('A Result').size().reset_index(name='Count')
    # Or the same with: service_result_count_df = service_type_count_df.groupby('A Result').size().reset_index(name='Count')

    # We count the total number of Aud to use it as the Denominator in the % calculation
    aud_result_pct_df['Total Aud'] = aud_result_pct_df['Count'].sum()

    # We calculate the % of that type of Aud
    aud_result_pct_df['Percentage %'] = round(aud_result_pct_df['Count'] / aud_result_pct_df['Total Aud'], 2)

    # Create the 1st chart for Aud (which is the 3rd Chart overall): Aud Result
    fig3 = px.bar(aud_result_pct_df, x='Percentage %', y='A Result', color='A Result',
                  color_discrete_map=aud_color_dict, title='Aud Result', orientation='h'
                  )

    #Format the X axis to have 2 decimal places and the '%' sign
    fig3.update_layout(
        xaxis_title='Percentage (%)',
        yaxis_title='A Result',
        paper_bgcolor='#1f2c56',  # Set chart background color
        plot_bgcolor='#1f2c56',  # Set chart plot area color
        font_color='white',  # Set font color to white
        xaxis_tickformat=".2%" #Format the X axis to have 2 decimal places and the '%' sign
    )

    # Calculate the maximum value for x-axis range
    max_x_range = max(aud_result_pct_df['Percentage %']) * 1.1  # Adding extra buffer (space)

    # Set the x-axis range to start from 0% and extend to the calculated maximum
    fig3.update_xaxes(range=[0, max_x_range])

    # Add annotations (% values) inside each bar (Better do in case fig fig.update_layout
    # for index, row in aud_result_pct_df.iterrows():
    # x_offset = 0.5  # Adjust this value to control the x-coordinate offset of the annotations
    # fig1.add_annotation(
    # x=row['Percentage %'] + x_offset,  # Count value
    # y=row['A Result'],  # Category (A Result)
    # text=f"{row['Percentage %']}%",  # Display the % with the "%" sign outside the bar
    # showarrow=False,
    # font=dict(size=12, color='black'), # Font settings for the annotation
    # )

    # 2nd Chart: Group by A Type and count the occurences for each A Type
    aud_type_count_df = aud_filtered_df['A Type'].groupby(aud_filtered_df['A Type']).size().reset_index(
        name='Count').sort_values(by='Count', ascending=False)

    # Create the 2nd chart
    fig4 = px.bar(aud_type_count_df, x='A Type', y='Count', title='A Type')
    fig4.update_layout(
        paper_bgcolor='#1f2c56',  # Set chart background color
        plot_bgcolor='#1f2c56',  # Set chart plot area color
        font_color='white',  # Set font color to white
    )

    # 3rd Chart: Cert Expiry Date Over Time (by Year and Quarter)
    # We already converted 'C Expiry Date' column to datetime format before using .dt cause the .dt accessor can only be used with datetime-like values
    # aud_filtered_df['C Expiry Date'] = pd.to_datetime(aud_filtered_df['C Expiry Date'], errors='coerce')

    # Group by Quarter counting the occurences for each Year Quarter
    cert_expiry_count_df = aud_filtered_df['C Expiry Date'].groupby(
        aud_filtered_df['C Expiry Date'].dt.to_period('Q')).size().reset_index(name='Count')

    # Convert the Periods to strings with custom formatting (e.g., "YYYY-Qx")
    cert_expiry_count_df['C Expiry Date'] = cert_expiry_count_df['C Expiry Date'].apply(
        lambda x: f"{x.year}-Q{x.quarter}")

    # In the end: we convert the Periods to strings (formatted as quarters) to make them JSON serializable otherwise WE CANNOT
    # PLOT them in Plotly
    cert_expiry_count_df['C Expiry Date'] = cert_expiry_count_df['C Expiry Date'].astype(str)

    # Create the 3rd chart
    fig5 = px.bar(cert_expiry_count_df, x='C Expiry Date', y='Count', title='Cert Expiry Date Over Time')
    fig5.update_layout(
        paper_bgcolor='#1f2c56',  # Set chart background color
        plot_bgcolor='#1f2c56',  # Set chart plot area color
        font_color='white',  # Set font color to white
    )
    return fig3, fig4, fig5
    # Returned updated figures



##########
#app.scripts.config.serve_locally = True
#app.css.config.serve_locally = True
#####

# Run the app. Here we did so that Dash app is configured to listen on 0.0.0.0 (all available network interfaces) rather than just 127.0.0.1 (localhost)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050, debug=True)






'''
#__________________
#We now style the layout
app.layout = html.Div([
    dbc.Row([
        dcc.DatePickerRange(id='date-filter')
    ]),
    dbc.Row([
        dcc.Dropdown(id='region-filter')
    ]),
    dbc.Row([
        dcc.Dropdown(id='country-filter')
    ]),
    dbc.Row([
        dcc.Dropdown(id='service-type-filter')
    ]),
    dbc.Row([
        dcc.RadioItems(id='include-na-radio')
    ]),

    # Aud 2 DatePickerRange
    dbc.Row([
        dbc.Col([
            dcc.DatePickerRange(id='start-date-filter')
        ]),
        dbc.Col([
            dcc.DatePickerRange(id='expiry-date-filter')
        ])
    ]),

    #Aud Dropdown Filters:
    dbc.Row([
        dcc.Dropdown(id='aud-type-filter')
    ]),
    dbc.Row([
        dcc.Dropdown(id='aud_region-filter')
    ]),
    dbc.Row([
        dcc.Dropdown(id='aud_country-filter')
    ]),
    dbc.Row([
        dcc.RadioItems(id='combined-filter')
    ]),
    dbc.Row([
        dcc.RadioItems(id='start-date-na-radio')
    ]),

    # Pre Aud Charts
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='service-result-pct-chart')
        ]),
        dbc.Col([
            dcc.Graph(id='service-type-count-chart')
        ])
    ]),

    # Audit Charts
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='aud-result-pct-chart')
        ]),
        dbc.Col([
            dcc.Graph(id='aud-type-count-chart')
        ])
    ]),
    dbc.Row([
        dcc.Graph(id='cert-expiry-date-chart')
    ])
])

##########
app.scripts.config.serve_locally = True
app.css.config.serve_locally = True
#####
# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port = 8050)
##############################################################################à
'''


















