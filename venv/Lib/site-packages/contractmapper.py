import pandas as pd
import plotly.graph_objects as go
import os


def format_dates(df):
    # Clean and convert dates
    df['date'] = pd.to_datetime(df['date'].str.replace(r'\.\d+', '', regex=True), errors='coerce')
    return df


def plot_games(df):
    df = format_dates(df)

    # Create figure
    fig = go.Figure()

    # Define the time periods
    time_periods = {
        'Day': df['date'].dt.date,  # Use date only for daily counts
        'Week': df['date'].dt.to_period('W').dt.start_time,
        'Month': df['date'].dt.to_period('M').dt.start_time
    }

    # Calculate total games for each playgroup
    total_games = df['playgroup_name'].value_counts()

    # Sort playgroups by total games
    sorted_playgroups = total_games.index.tolist()

    # Create traces for each playgroup and each time period
    for playgroup in sorted_playgroups:
        for period, x_data in time_periods.items():
            playgroup_data = df[df['playgroup_name'] == playgroup]

            # Aggregate counts based on the time period
            if period == 'Day':
                # Count games per day for the specific playgroup
                playgroup_counts = playgroup_data.groupby(x_data).size()
            else:
                # Count games per week/month for the specific playgroup
                playgroup_counts = playgroup_data.groupby(x_data).size()

            fig.add_trace(go.Scatter(
                x=playgroup_counts.index,
                y=playgroup_counts.values,
                mode='lines+markers',
                name=f'{playgroup} ({period})',
                visible=True if period == 'Week' else 'legendonly',  # Default visibility for Week
                hoverinfo='text',
                text=playgroup_counts.values,
                legendgroup=playgroup  # Group by playgroup for legend organization
            ))

    # Update layout with dropdown menu
    fig.update_layout(
        title='Games Played by Playgroup',
        xaxis_title='Date',
        yaxis_title='Number of Games',
        xaxis=dict(type='date'),
        showlegend=True,
        legend=dict(title='Playgroups'),
        updatemenus=[
            {
                'buttons': [
                    {
                        'label': 'Days',
                        'method': 'update',
                        'args': [{'visible': [True if 'Day' in trace.name else False for trace in fig.data]}]
                    },
                    {
                        'label': 'Weeks',
                        'method': 'update',
                        'args': [{'visible': [True if 'Week' in trace.name else False for trace in fig.data]}]
                    },
                    {
                        'label': 'Months',
                        'method': 'update',
                        'args': [{'visible': [True if 'Month' in trace.name else False for trace in fig.data]}]
                    }
                ],
                'direction': 'down',
                'showactive': True,
            }
        ]
    )

    # Save the figure as an HTML file
    output_file = 'static/games_over_time.html'
    fig.write_html(output_file)

    # Print the location of the HTML file
    print('Test1')
    print(f"Plot saved as: {os.path.abspath(output_file)}")

    # Show figure
    fig.show()


# Example usage with plays2.csv
df = pd.read_csv('plays2.csv')
plot_games(df)
