import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px

# Set page title
st.set_page_config(page_title="Circular Iligan", layout="wide")

# Display the main title
st.title("Circular Iligan")

# Load the data
@st.cache_data
def load_data():
    data = pd.read_csv("/Users/markryan/Desktop/smart_city/clean.csv")
    return data

df = load_data()

# Ensure latitude and longitude are numeric
df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
df = df.dropna(subset=['Latitude', 'Longitude'])

# Initialize session state for selected barangay if not already present
if 'selected_barangay' not in st.session_state:
    st.session_state.selected_barangay = df['Barangay'].unique()[0]

# Create two main columns
col1, col2 = st.columns([3, 1])  # Adjust the width of the columns as needed

with col1:
    # Create a map
    st.subheader("Map of Iligan Barangays")
    
    # Update the map with the selected barangay highlighted
    selected_barangay = st.session_state.selected_barangay
    
    # Base layer for all barangays
    base_layer = pdk.Layer(
        "ScatterplotLayer",
        df,
        get_position=['Longitude', 'Latitude'],
        get_color=[200, 30, 0, 160],
        get_radius=200,
        pickable=True
    )
    
    # Highlight layer for the selected barangay
    selected_data = df[df['Barangay'] == selected_barangay]
    highlight_layer = pdk.Layer(
        "ScatterplotLayer",
        selected_data,
        get_position=['Longitude', 'Latitude'],
        get_color=[0, 200, 0, 160],  # Highlight color
        get_radius=400,
        pickable=True
    )
    
    # Combine layers
    map_chart = pdk.Deck(
        layers=[base_layer, highlight_layer],
        initial_view_state=pdk.ViewState(
            latitude=df['Latitude'].mean(),
            longitude=df['Longitude'].mean(),
            zoom=11,
            pitch=0
        ),
        tooltip={"text": "{Barangay}\nTotal Waste 2019: {Total_2019}\nTotal Waste 2015: {Total_2015}"}
    )
    
    st.pydeck_chart(map_chart, use_container_width=True)
    
    # Create a new row for charts
    col1, col3 = st.columns([3, 2])  # Adjust the width of the columns as needed

    with col1:
        # Add a stacked bar chart
        st.subheader("Waste Types Comparison (2015 vs 2019)")

        # List of columns for 2015 and 2019 waste data
        columns_2015 = ['Recyclable_2015', 'Biodegradable_2015', 'Residual_2015', 'Special_2015']
        columns_2019 = ['Recyclable_2019', 'Biodegradable_2019', 'Residual_2019', 'Special_2019']

        # Clean and convert the columns to numeric, removing commas if present
        for col in columns_2015 + columns_2019:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')

        # Aggregate the waste data by type
        waste_2015 = df[columns_2015].sum()
        waste_2019 = df[columns_2019].sum()

        # Prepare the data in a DataFrame with years as columns
        waste_data = pd.DataFrame({
            'Waste Type': ['Recyclable', 'Biodegradable', 'Residual', 'Special'],
            '2015': [waste_2015[col] for col in columns_2015],
            '2019': [waste_2019[col] for col in columns_2019]
        })

        # Transpose and reset index to switch axes
        waste_data_transposed = waste_data.set_index('Waste Type').T.reset_index()
        waste_data_transposed.rename(columns={'index': 'Year'}, inplace=True)

        # Melt the data for Plotly compatibility
        waste_data_melted = waste_data_transposed.melt(id_vars='Year', var_name='Waste Type', value_name='Total Waste')

        # Create the stacked bar chart using Plotly
        fig = px.bar(waste_data_melted, 
                    x='Year', 
                    y='Total Waste', 
                    color='Waste Type', 
                    barmode='stack', 
                    title='Comparison of Waste Types in 2015 and 2019',
                    labels={'Total Waste': 'Total Waste (in tons)'},
                    text='Total Waste')  # Add text labels to the bars

        # Customize the chart
        fig.update_layout(xaxis_title='Year', 
                        yaxis_title='Total Waste (in tons)', 
                        barmode='stack',
                        height=400,  # Set the height to make the chart smaller
                        width=600)   # Set the width to make the chart smaller

        # Customize the text labels
        fig.update_traces(texttemplate='%{text:.2s}', textposition='inside')

        # Show the plot in Streamlit
        st.plotly_chart(fig, use_container_width=True)

    with col3:
        # Add a line chart for total waste comparison by barangay
        st.subheader("Total Waste Comparison by Barangay (2015 vs 2019)")

        # Clean and convert the relevant columns to numeric, removing commas if present
        df['Total_2015'] = pd.to_numeric(df['Total_2015'].astype(str).str.replace(',', ''), errors='coerce')
        df['Total_2019'] = pd.to_numeric(df['Total_2019'].astype(str).str.replace(',', ''), errors='coerce')

        # Prepare the data for plotting
        line_data = df[['Barangay', 'Total_2015', 'Total_2019']].melt(id_vars='Barangay', var_name='Year', value_name='Total Waste')

        # Create the smooth line chart using Plotly
        fig_line = px.line(line_data, 
                        x='Barangay', 
                        y='Total Waste', 
                        color='Year', 
                        markers=True,
                        line_shape='spline',  # Use 'spline' for smooth lines
                        title='Total Waste Comparison by Barangay for 2015 and 2019',
                        labels={'Total Waste': 'Total Waste (in tons)', 'Barangay': 'Barangay'})

        # Customize the chart
        fig_line.update_layout(xaxis_title='Barangay', 
                            yaxis_title='Total Waste (in tons)', 
                            legend_title='Year',
                            height=400,  # Set the height to make the chart smaller
                            width=600)   # Set the width to make the chart smaller

        # Show the plot in Streamlit
        st.plotly_chart(fig_line, use_container_width=True)

    # New line chart for waste generation by type
    with col1:
        # Add a line chart for waste generation by type
        st.subheader("Waste Generation by Type (2015 vs 2019)")

        # Prepare the data for plotting
        waste_types = ['Recyclable', 'Biodegradable', 'Residual', 'Special']
        line_data_by_type = pd.DataFrame({
            'Waste Type': waste_types,
            '2015': [df[f'{waste}_2015'].sum() for waste in waste_types],
            '2019': [df[f'{waste}_2019'].sum() for waste in waste_types]
        })

        # Melt the data for Plotly compatibility
        line_data_by_type_melted = line_data_by_type.melt(id_vars='Waste Type', var_name='Year', value_name='Total Waste')

        # Create the line chart using Plotly
        fig_line_by_type = px.line(line_data_by_type_melted, 
                                  x='Waste Type', 
                                  y='Total Waste', 
                                  color='Year', 
                                  markers=True,
                                  line_shape='spline',  # Use 'spline' for smooth lines
                                  title='Waste Generation by Type for 2015 and 2019',
                                  labels={'Total Waste': 'Total Waste (in tons)', 'Waste Type': 'Waste Type'})

        # Customize the chart
        fig_line_by_type.update_layout(xaxis_title='Waste Type', 
                                       yaxis_title='Total Waste (in tons)', 
                                       legend_title='Year',
                                       height=400,  # Set the height to make the chart smaller
                                       width=600)   # Set the width to make the chart smaller

        # Show the plot in Streamlit
        st.plotly_chart(fig_line_by_type, use_container_width=True)

with col2:
    # Display data table
    st.subheader("Barangay Data")
    st.dataframe(df, height=300)
    
    # Add a section for waste comparison
    st.subheader("Waste Comparison (2015 vs 2019)")

    # Select a barangay and store it in session state
    selected_barangay = st.selectbox(
        "Select a Barangay", 
        df['Barangay'].unique(), 
        index=df['Barangay'].unique().tolist().index(st.session_state.selected_barangay)
    )
    st.session_state.selected_barangay = selected_barangay
    
    # Filter data for the selected barangay
    barangay_data = df[df['Barangay'] == selected_barangay]
    
    # Prepare the data for comparison chart
    comparison_data = pd.DataFrame({
        'Waste Type': ['Recyclable', 'Biodegradable', 'Residual', 'Special'],
        '2015': [
            barangay_data['Recyclable_2015'].values[0],
            barangay_data['Biodegradable_2015'].values[0],
            barangay_data['Residual_2015'].values[0],
            barangay_data['Special_2015'].values[0]
        ],
        '2019': [
            barangay_data['Recyclable_2019'].values[0],
            barangay_data['Biodegradable_2019'].values[0],
            barangay_data['Residual_2019'].values[0],
            barangay_data['Special_2019'].values[0]
        ]
    })

    # Melt the data for Plotly compatibility
    comparison_data_melted = comparison_data.melt(id_vars='Waste Type', var_name='Year', value_name='Total Waste')

    # Create the bar chart for the selected barangay using Plotly
    fig_comparison = px.bar(comparison_data_melted, 
                           x='Waste Type', 
                           y='Total Waste', 
                           color='Year', 
                           barmode='group',
                           title=f'Waste Type Comparison for {selected_barangay} (2015 vs 2019)',
                           labels={'Total Waste': 'Total Waste (in tons)'})

    # Customize the chart
    fig_comparison.update_layout(xaxis_title='Waste Type', 
                                 yaxis_title='Total Waste (in tons)', 
                                 barmode='group',
                                 height=400,  # Set the height to make the chart smaller
                                 width=600)   # Set the width to make the chart smaller

    # Show the plot in Streamlit
    st.plotly_chart(fig_comparison, use_container_width=True)
