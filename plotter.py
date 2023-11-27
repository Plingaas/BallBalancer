import plotly.express as px
import pandas as pd
import csv

def plot_interactive_data(filename):
    # Read CSV file into a pandas DataFrame
    df = pd.read_csv(filename)

    # Melt the DataFrame to have 'Variable' and 'Value' columns
    melted_df = pd.melt(df, id_vars=['Time'], var_name='Variable', value_name='Value')

    # Create an interactive plot
    fig = px.line(melted_df, x='Time', y='Value', color='Variable',
                  title='Interactive CSV Data Plot',
                  labels={'Value': 'Value', 'Variable': 'Variable'},
                  hover_name='Variable',
                  line_shape='linear')

    # Add checkboxes for hiding/showing lines
    fig.update_layout(
        updatemenus=[
            dict(
                type='buttons',
                showactive=True,
                buttons=[
                    dict(label='Show All',
                         method='relayout',
                         args=['visible', [True] * len(df.columns)]),
                    dict(label='Hide All',
                         method='relayout',
                         args=['visible', [False] * len(df.columns)])
                ]
            )
        ]
    )

    fig.show()

if __name__ == '__main__':
    csv_filename = 'log12.csv'  # Replace with your CSV file name
    plot_interactive_data(csv_filename)
