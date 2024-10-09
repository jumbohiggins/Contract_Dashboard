import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Load your CSV data
df = pd.read_csv('plays2.csv', parse_dates=['date'])
df['date'] = pd.to_datetime(df['date'], format='mixed')

# Create a Dash app
app = dash.Dash(__name__)

# Define layout
app.layout = html.Div([
    html.H1("Playgroup Statistics Dashboard"),

    # Dropdown for playgroups
    dcc.Dropdown(
        id='playgroup-dropdown',
        options=[
            {'label': group, 'value': group} for group in df['playgroup_name'].value_counts().index
        ],
        value=df['playgroup_name'].value_counts().index[0],  # Default to the first playgroup
        clearable=False
    ),

    # Dropdown for time period
    dcc.Dropdown(
        id='time-frame-dropdown',
        options=[
            {'label': 'Daily', 'value': 'D'},
            {'label': 'Weekly', 'value': 'W'},
            {'label': 'Monthly', 'value': 'M'}
        ],
        value='D',  # Default to Daily
        clearable=False
    ),

    # Graphs for the selected playgroup
    dcc.Graph(id='games-over-time'),
    dcc.Graph(id='deaths-over-time'),
    dcc.Graph(id='victories-over-time'),
    dcc.Graph(id='losses-over-time'),
    dcc.Graph(id='contract-levels'),

    # Statistics panels
    html.Div(id='stat-panels', style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'})
])


# Function to filter data for the last month
def filter_last_month(df):
    last_month_start = pd.Timestamp.now(tz='UTC') - pd.Timedelta(days=30)
    return df[df['date'] >= last_month_start]


# Define callbacks
@app.callback(
    [Output('games-over-time', 'figure'),
     Output('deaths-over-time', 'figure'),
     Output('victories-over-time', 'figure'),
     Output('losses-over-time', 'figure'),
     Output('contract-levels', 'figure'),
     Output('stat-panels', 'children')],
    Input('playgroup-dropdown', 'value'),
    Input('time-frame-dropdown', 'value')
)
def update_graphs(selected_playgroup, time_frame):
    # Filter dataframe for the selected playgroup
    filtered_df = df[df['playgroup_name'] == selected_playgroup]

    # Calculate stats based on the last month's data
    last_month_df = filter_last_month(filtered_df)

    total_wins = last_month_df['num_victories'].sum()
    total_losses = last_month_df['num_losses'].sum()
    avg_deaths = last_month_df['num_deaths'].mean()

    # Calculate average games played over the last month
    avg_games_weekly = last_month_df.resample('W-Mon', on='date').size().mean() if not last_month_df.empty else 0
    avg_games_monthly = last_month_df.resample('M', on='date').size().mean() if not last_month_df.empty else 0

    # Update win/loss ratio for clarity
    if total_losses > 0:
        win_loss_ratio = f"{total_wins} Wins : {total_losses} Losses"
    else:
        win_loss_ratio = f"{total_wins} Wins : 0 Losses (No losses recorded)"

    # Most common and least common level of contract run
    most_common_level = last_month_df['level'].mode()[0] if not last_month_df['level'].empty else 'N/A'
    least_common_level = last_month_df['level'].value_counts().idxmin() if not last_month_df['level'].empty else 'N/A'

    # Create stat panels
    stat_panels = html.Div([
        html.Div(f"Average Games Played Weekly (Last Month): {avg_games_weekly:.2f}", className='stat-panel'),
        html.Div(f"Average Games Played Monthly (Last Month): {avg_games_monthly:.2f}", className='stat-panel'),
        html.Div(f"Average Deaths (Last Month): {avg_deaths:.2f}", className='stat-panel'),
        html.Div(f"Win/Loss Ratio (Last Month): {win_loss_ratio}", className='stat-panel'),
        html.Div(f"Most Common Level (Last Month): {most_common_level}", className='stat-panel'),
        html.Div(f"Least Common Level (Last Month): {least_common_level}", className='stat-panel')
    ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'margin': '20px'})

    # Resample data based on the selected time frame for graphs
    if time_frame == 'D':
        games_resampled = filtered_df.resample('D', on='date').sum()
    elif time_frame == 'W':
        games_resampled = filtered_df.resample('W-Mon', on='date').sum()
    else:  # Monthly
        games_resampled = filtered_df.resample('M', on='date').sum()

    # Generate graphs based on the resampled DataFrame
    games_over_time = px.line(games_resampled, x=games_resampled.index, y='num_victories', title='Games Over Time')
    deaths_over_time = px.line(games_resampled, x=games_resampled.index, y='num_deaths', title='Deaths Over Time')
    victories_over_time = px.line(games_resampled, x=games_resampled.index, y='num_victories',
                                  title='Victories Over Time')
    losses_over_time = px.line(games_resampled, x=games_resampled.index, y='num_losses', title='Losses Over Time')

    # Contract levels based on last month data
    contract_levels = px.histogram(last_month_df, x='level', title='Contract Levels, Last Month')

    return games_over_time, deaths_over_time, victories_over_time, losses_over_time, contract_levels, stat_panels


# Add styles for the stat panels
app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/brPBPO.css'
})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Use the port provided by Render
    app.run(host='0.0.0.0', port=port)
