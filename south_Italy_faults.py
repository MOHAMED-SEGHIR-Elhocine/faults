# -*- coding: utf-8 -*-
import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd
# import json # No longer needed
import numpy as np
from branca.colormap import LinearColormap
import plotly.express as px
# import plotly.graph_objects as go # No longer needed unless adding more complex plotly charts
from folium.plugins import HeatMap # Ensure HeatMap is imported

# ===== App Configuration =====
st.set_page_config(
    page_title="Italian Fault Systems Explorer",
    page_icon="🌋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== Custom CSS =====
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 1.5rem;
        color: #1E3A8A; /* Dark Blue */
    }
    .subheader {
        font-size: 1.5rem;
        font-weight: 600;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
        color: #1E3A8A; /* Dark Blue */
    }
    .info-box {
        background-color: #EBF8FF; /* Light Blue background */
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #3182CE; /* Blue left border */
        margin-bottom: 1rem;
    }
    .footer {
        text-align: center;
        margin-top: 2rem;
        color: #6B7280; /* Gray */
        font-size: 0.8rem;
    }
    /* Style tabs */
    .stTabs [data-baseweb="tab-list"] {
		gap: 24px; /* Spacing between tabs */
	}
	.stTabs [data-baseweb="tab"] {
		height: 50px;
        white-space: pre-wrap; /* Allow text wrapping */
		background-color: #F3F4F6; /* Light Gray */
		border-radius: 4px 4px 0px 0px;
		gap: 1px;
		padding: 10px 12px; /* Adjust padding */
        color: #4B5563; /* Default tab text color (Gray) */
        font-size: 0.95rem; /* Slightly smaller font size */
        font-weight: 600; /* Make default tab text bolder */
        display: flex; /* Use flexbox for alignment */
        align-items: center; /* Center text vertically */
        justify-content: center; /* Center text horizontally */
        line-height: 1.3; /* Adjust line height for wrapped text */
    }
	.stTabs [aria-selected="true"] {
  		background-color: #FFFFFF; /* White */
        color: #1E3A8A; /* Dark Blue */
        font-weight: 700; /* Slightly bolder for selected tab */
	}

</style>
""", unsafe_allow_html=True)

# ===== Enhanced Fault System Data =====
# --- NOTE: You had a stray integer '1' at the end of your fault_data list. I've removed it. ---
fault_data = [
    {
        "name": "Apennine Fault System",
        "location": [41.2, 13.5],
        "fault_types": "Normal, Thrust, Strike-Slip",
        "tectonic_drivers": "Extension (back-arc), Historical Compression",
        "examples": "Irpinia Faults, Paganica Fault",
        "last_major_earthquake": "L'Aquila (2009), 6.3 Mw",
        "seismic_risk": "High",
        "description": "Runs along the spine of Italy, responsible for many devastating earthquakes. Characterized by complex normal faulting due to regional extension.",
        "annual_slip_rate": 1.8,  # mm/year
        "color": "#E53E3E"  # red
    },
    {
        "name": "Calabrian Arc",
        "location": [38.5, 16.3],
        "fault_types": "Normal, Strike-Slip, Thrust, Oblique-Slip",
        "tectonic_drivers": "Subduction of Ionian slab, Africa-Eurasia collision",
        "examples": "Rossano Fault",
        "last_major_earthquake": "Crotone (1832), 6.6 Mw",
        "seismic_risk": "Very High",
        "description": "One of the most seismically active regions in the Mediterranean, formed by Ionian plate subduction. Experiences complex deformation.",
        "annual_slip_rate": 2.3,  # mm/year
        "color": "#DD6B20"  # orange
    },
    {
        "name": "Messina Strait",
        "location": [38.2, 15.6],
        "fault_types": "Normal",
        "tectonic_drivers": "Subduction Rollback, Crustal Extension",
        "examples": "Messina-Taormina Fault",
        "last_major_earthquake": "Messina (1908), 7.1 Mw",
        "seismic_risk": "Very High",
        "description": "Produced Italy's devastating 1908 earthquake and tsunami. High hazard zone due to active extensional tectonics.",
        "annual_slip_rate": 2.5,  # mm/year
        "color": "#D53F8C"  # pink
    },
    {
        "name": "Gargano Fault System",
        "location": [41.8, 15.9],
        "fault_types": "Thrust, Strike-Slip, Transpressional, Minor Normal",
        "tectonic_drivers": "Intraforeland Transpression, Adriatic Slab Subduction",
        "examples": "Mattinata Fault",
        "last_major_earthquake": "Gargano (1646), 6.7 Mw",
        "seismic_risk": "Moderate to High",
        "description": "Structural high affected by E-W right-lateral faults accommodating Adria-Apulia microplate movements.",
        "annual_slip_rate": 1.0,  # mm/year
        "color": "#3182CE"  # blue
    },
    {
        "name": "Siculo-Calabrian Rift Zone",
        "location": [38.4, 15.0],
        "fault_types": "Normal",
        "tectonic_drivers": "Extension from Ionian Subduction and Back-Arc Opening",
        "examples": "Scilla Fault, Capo Vaticano Fault",
        "last_major_earthquake": "Southern Calabria (1783), 7.0 Mw",
        "seismic_risk": "High",
        "description": "Extends from NE Sicily to SW Calabria, characterized by normal faults accommodating extension related to Ionian subduction.",
        "annual_slip_rate": 1.6,  # mm/year
        "color": "#805AD5"  # purple
    },
]

# Convert to pandas DataFrame for easier manipulation
# --- Check data before creating DataFrame ---
valid_fault_data = [item for item in fault_data if isinstance(item, dict)]
if len(valid_fault_data) != len(fault_data):
    st.error("Warning: Invalid data detected in fault_data list. Proceeding with valid entries.")
    fault_data = valid_fault_data # Use only the valid dictionaries

df_faults = pd.DataFrame(fault_data)

# --- Add defensive check for required columns before proceeding ---
required_cols = ['location', 'name', 'seismic_risk', 'annual_slip_rate', 'color', 'fault_types', 'tectonic_drivers', 'examples', 'last_major_earthquake', 'description']
missing_cols = [col for col in required_cols if col not in df_faults.columns]
if missing_cols:
    st.error(f"Error: The fault data is missing required columns: {', '.join(missing_cols)}. Cannot proceed.")
    st.stop() # Stop execution if essential data is missing

# Add latitude/longitude columns explicitly for potential future use
df_faults['latitude'] = df_faults['location'].apply(lambda x: x[0])
df_faults['longitude'] = df_faults['location'].apply(lambda x: x[1])


# ===== Historical Earthquake Data =====
historical_earthquakes = [
    {"year": 1693, "location": "Eastern Sicily", "magnitude": 7.4, "lat": 37.1, "lon": 15.0, "deaths": 60000, "description": "Strongest earthquake in Italian history, destroying 45+ towns."},
    {"year": 1783, "location": "Calabria", "magnitude": 7.0, "lat": 38.3, "lon": 15.9, "deaths": 50000, "description": "Sequence of five strong earthquakes struck Calabria within two months."},
    {"year": 1857, "location": "Basilicata", "magnitude": 7.0, "lat": 40.4, "lon": 15.9, "deaths": 11000, "description": "Great Neapolitan Earthquake affecting Basilicata and Campania."},
    {"year": 1908, "location": "Messina Strait", "magnitude": 7.1, "lat": 38.2, "lon": 15.6, "deaths": 123000, "description": "Europe's deadliest quake, caused tsunami, destroyed Messina & Reggio Calabria."},
    {"year": 1915, "location": "Avezzano", "magnitude": 6.7, "lat": 42.0, "lon": 13.5, "deaths": 30000, "description": "Destroyed Avezzano and damaged surrounding areas in Central Italy."},
    {"year": 1930, "location": "Irpinia", "magnitude": 6.6, "lat": 41.0, "lon": 15.3, "deaths": 1400, "description": "Affected the southern Apennines region, causing severe damage."},
    {"year": 1968, "location": "Belice Valley, Sicily", "magnitude": 6.4, "lat": 37.8, "lon": 13.0, "deaths": 300, "description": "Series of earthquakes destroyed several towns in western Sicily."},
    {"year": 1980, "location": "Irpinia", "magnitude": 6.9, "lat": 40.8, "lon": 15.3, "deaths": 2900, "description": "One of Italy's strongest 20th-century quakes, widespread destruction."},
    {"year": 2009, "location": "L'Aquila", "magnitude": 6.3, "lat": 42.3, "lon": 13.4, "deaths": 308, "description": "Severely damaged the historic city of L'Aquila and surrounding villages."},
    {"year": 2016, "location": "Central Italy", "magnitude": 6.2, "lat": 42.7, "lon": 13.2, "deaths": 299, "description": "Sequence devastated towns including Amatrice, Accumoli, Arquata."}
]

df_earthquakes = pd.DataFrame(historical_earthquakes)

# ===== Main App Logic =====
def main():
    # Sidebar
    with st.sidebar:
        st.markdown('<div style="text-align:center; font-size:72px; margin-bottom:15px;">🌋</div>', unsafe_allow_html=True)
        st.header("Control Panel")

        display_options = st.multiselect(
            "Layers to Display",
            ["Fault Systems", "Historical Earthquakes", "Seismic Risk Heatmap"],
            default=["Fault Systems", "Historical Earthquakes"],
            help="Select which data layers to show on the map."
        )

        st.markdown("---")
        st.markdown("### Filters")

        # --- Add check if df_faults is not empty before accessing unique() ---
        if not df_faults.empty:
            risk_options = sorted(df_faults["seismic_risk"].unique())
            default_risk = risk_options
        else:
            risk_options = []
            default_risk = []

        filter_risk = st.multiselect(
            "Filter Faults by Seismic Risk",
            options=risk_options,
            default=default_risk,
            help="Show only fault systems within the selected risk categories."
        )

        min_eq_year, max_eq_year = int(df_earthquakes["year"].min()), int(df_earthquakes["year"].max())
        year_range = st.slider(
            "Historical Earthquake Period",
            min_eq_year, max_eq_year, (1900, max_eq_year), # Default range adjusted
            help="Filter earthquakes based on the year they occurred."
        )

        min_mag, max_mag = float(df_earthquakes["magnitude"].min()), float(df_earthquakes["magnitude"].max())
        magnitude_range = st.slider(
            "Earthquake Magnitude Range (Mw)",
            min_mag, max_mag, (6.0, max_mag), 0.1, # Default range adjusted
            help="Filter earthquakes based on their magnitude."
        )

        st.markdown("---")
        st.markdown("### Map Settings")
        # --- REMOVE Stamen tiles from options ---
        map_tile_options = ['CartoDB positron', 'OpenStreetMap', 'CartoDB dark_matter']
        selected_tile = st.selectbox(
            "Map Background Tile",
            options=map_tile_options,
            index=0,
             help="Choose the background style for the map."
        )


        st.markdown("---")
        st.info("Explore the map and analysis tabs. Hover over map elements for details.")


    # Main Content
    st.markdown('<h1 class="main-header">🌋 Fault Systems & Seismic History of Southern Italy</h1>', unsafe_allow_html=True)

    # Introduction
    with st.expander("ℹ️ About this Explorer", expanded=False):
        st.markdown("""
        <div class="info-box">
        Southern Italy lies at a complex tectonic crossroads, making it one of Europe's most seismically active regions. This interactive application visualizes:
        <ul>
            <li><b>Major Fault Systems:</b> Structures responsible for seismic activity, colored by system.</li>
            <li><b>Historical Earthquakes:</b> Significant events (magnitude > 6.0 by default) since 1900, sized by magnitude and colored by intensity.</li>
            <li><b>Seismic Risk Heatmap:</b> A generalized representation of seismic hazard concentration based on known fault systems.</li>
        </ul>
        Use the <b>Control Panel</b> (sidebar) to filter data and customize the map layers. Explore the <b>Seismic Analysis</b> tabs for charts and summaries.
        </div>
        """, unsafe_allow_html=True)

    # Apply filters
    # --- Add check if df_faults is not empty before filtering ---
    if not df_faults.empty:
        filtered_faults = df_faults[df_faults["seismic_risk"].isin(filter_risk)]
    else:
        filtered_faults = pd.DataFrame() # Create empty DataFrame if no fault data

    filtered_quakes = df_earthquakes[
        (df_earthquakes["year"] >= year_range[0]) &
        (df_earthquakes["year"] <= year_range[1]) &
        (df_earthquakes["magnitude"] >= magnitude_range[0]) &
        (df_earthquakes["magnitude"] <= magnitude_range[1])
    ].copy() # Use .copy() to avoid SettingWithCopyWarning if modifying later

    # Create and display the map and analysis side-by-side
    col1, col2 = st.columns([3, 2]) # Adjust column ratio if needed

    with col1:
        st.markdown('<h2 class="subheader">Interactive Map</h2>', unsafe_allow_html=True)

        # Initialize the Folium map
        map_center = [40.0, 15.5] # Slightly adjusted center
        map_zoom = 6

        m = folium.Map(
            location=map_center,
            zoom_start=map_zoom,
            tiles=None, # Start with no tiles, add them below
            control_scale=True
        )

        # Add base tile layers first using the selected_tile from the sidebar as the default visible one
        # The name parameter is crucial for the LayerControl
        # --- REMOVE Stamen tiles from dictionary ---
        tiles = {
            'CartoDB positron': folium.TileLayer(
                'CartoDB positron',
                attr='© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors © <a href="https://carto.com/attributions">CARTO</a>',
                name='CartoDB Positron'
            ),
            'OpenStreetMap': folium.TileLayer(
                'OpenStreetMap',
                attr='© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                name='OpenStreetMap'
            ),
            'CartoDB dark_matter': folium.TileLayer(
                'CartoDB dark_matter',
                attr='© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors © <a href="https://carto.com/attributions">CARTO</a>',
                name='CartoDB Dark Matter'
            )
        }

        # Add the selected tile layer first to make it the default visible layer
        if selected_tile in tiles:
            tiles[selected_tile].add_to(m)
        else: # Fallback if selected_tile somehow becomes invalid
             tiles['CartoDB positron'].add_to(m)

        # Add the other tile layers for selection in LayerControl
        for tile_name, tile_layer in tiles.items():
            if tile_name != selected_tile:
                tile_layer.add_to(m)


        # Add Fault Systems Layer
        if "Fault Systems" in display_options and not filtered_faults.empty:
            fault_group = folium.FeatureGroup(name="Fault Systems", show=True).add_to(m)
            for _, fault in filtered_faults.iterrows():
                # --- CHANGE Fault Icon ---
                icon = folium.Icon(
                    color="white", # Background of icon circle
                    icon_color=fault["color"], # Color of the icon itself
                    icon="exclamation-triangle", # General hazard icon
                    # Other options: 'mountain', 'wave-square', 'bolt', 'atom'
                    prefix="fa" # Font Awesome prefix
                )

                popup_html = f"""
                <div style="width: 300px; font-family: Arial, sans-serif; font-size: 13px;">
                    <h4 style="color: {fault['color']}; margin-bottom: 5px;">{fault['name']}</h4>
                    <hr style="margin-top: 0; margin-bottom: 10px;">
                    <p><b>Description:</b> {fault['description']}</p>
                    <p><b>Types:</b> {fault['fault_types']}</p>
                    <p><b>Drivers:</b> {fault['tectonic_drivers']}</p>
                    <p><b>Examples:</b> {fault['examples']}</p>
                    <p><b>Last Major EQ:</b> {fault['last_major_earthquake']}</p>
                    <p><b>Seismic Risk:</b> <span style="font-weight: bold; color: {fault['color']};">{fault['seismic_risk']}</span></p>
                    <p><b>Slip Rate:</b> {fault['annual_slip_rate']:.1f} mm/year</p>
                </div>
                """

                folium.Marker(
                    location=fault["location"],
                    popup=folium.Popup(popup_html, max_width=350),
                    tooltip=f"<b>{fault['name']}</b><br>Risk: {fault['seismic_risk']}",
                    icon=icon
                ).add_to(fault_group)

                # Circle representing slip rate influence (scaled visually)
                folium.Circle(
                    location=fault["location"],
                    radius=max(5000, fault["annual_slip_rate"] * 7000), # Ensure minimum size, scale factor adjusted
                    color=fault["color"],
                    fill=True,
                    fill_opacity=0.15,
                    weight=1,
                    tooltip=f"{fault['name']} (Slip: {fault['annual_slip_rate']} mm/yr)"
                ).add_to(fault_group)

        # Add Historical Earthquakes Layer
        if "Historical Earthquakes" in display_options and not filtered_quakes.empty:
            earthquake_group = folium.FeatureGroup(name="Historical Earthquakes", show=True).add_to(m)

            # Define colormap for magnitude
            min_mag_filtered = filtered_quakes['magnitude'].min()
            max_mag_filtered = filtered_quakes['magnitude'].max()
            # Handle case where min and max are the same
            if min_mag_filtered == max_mag_filtered:
                 colormap = LinearColormap(['yellow', 'red'], vmin=min_mag_filtered - 0.1, vmax=max_mag_filtered + 0.1)
            else:
                colormap = LinearColormap(
                    ['#FFFF00', '#FFA500', '#FF0000'], # Yellow -> Orange -> Red
                    vmin=min_mag_filtered,
                    vmax=max_mag_filtered
                )


            for _, quake in filtered_quakes.iterrows():
                # Ensure radius calculation handles potential edge case where min=max
                if min_mag_filtered == max_mag_filtered:
                    radius = 5 # Fixed radius if all magnitudes are the same
                else:
                    radius = 3 + (quake['magnitude'] - min_mag_filtered) * 2 # Scale radius based on magnitude range

                popup_html = f"""
                <div style="width: 250px; font-family: Arial, sans-serif; font-size: 13px;">
                    <h4 style="margin-bottom: 5px;">{quake['year']} {quake['location']}</h4>
                    <hr style="margin-top: 0; margin-bottom: 10px;">
                    <p><b>Magnitude (Mw):</b> {quake['magnitude']}</p>
                    <p><b>Deaths:</b> {quake['deaths']:,}</p>
                    <p><i>{quake['description']}</i></p>
                </div>
                """

                folium.CircleMarker(
                    location=[quake['lat'], quake['lon']],
                    radius=radius,
                    color=colormap(quake['magnitude']),
                    fill=True,
                    fill_color=colormap(quake['magnitude']),
                    fill_opacity=0.6,
                    weight=1,
                    popup=folium.Popup(popup_html, max_width=300),
                    tooltip=f"{quake['year']} {quake['location']} (M{quake['magnitude']})"
                ).add_to(earthquake_group)
            # Add colormap legend to the map (optional, can clutter)
            # colormap.caption = 'Earthquake Magnitude (Mw)'
            # m.add_child(colormap)

        # Add Seismic Risk Heatmap Layer
        if "Seismic Risk Heatmap" in display_options and not filtered_faults.empty:
            # Make heatmap initially not visible if other layers are present
            show_heatmap = not ("Fault Systems" in display_options or "Historical Earthquakes" in display_options)
            heatmap_group = folium.FeatureGroup(name="Seismic Risk Heatmap", show=show_heatmap).add_to(m)
            risk_points = []
            risk_map = {"Low": 1, "Moderate": 2, "Moderate to High": 3, "High": 4, "Very High": 5}

            for _, fault in filtered_faults.iterrows():
                risk_value = risk_map.get(fault["seismic_risk"], 1)
                lat, lon = fault["location"]
                # Generate points weighted by risk and slip rate
                point_count = int(risk_value * fault["annual_slip_rate"] * 15) + 10 # Base + scaled points
                spread_factor = 0.15 + (risk_value * 0.05) # Wider spread for higher risk

                for _ in range(point_count):
                    random_lat = lat + np.random.normal(0, spread_factor)
                    random_lon = lon + np.random.normal(0, spread_factor * 1.5) # Wider E-W spread
                    # Weight can be added as the third element if needed by HeatMapWithTime or similar
                    risk_points.append([random_lat, random_lon])

            if risk_points:
                # Convert float keys in gradient to strings
                gradient_str_keys = {
                    '0.1': 'blue',
                    '0.3': 'lime',
                    '0.5': 'yellow',
                    '0.7': 'orange',
                    '1.0': 'red' # Use '1.0' or '1' as string key
                }

                HeatMap(
                    risk_points,
                    name="Seismic Risk Heatmap", # Name already set in FeatureGroup
                    radius=18,
                    blur=15,
                    gradient=gradient_str_keys, # Use the dictionary with string keys
                    min_opacity=0.2,
                    max_val=5.0 # Corresponds to max risk value
                ).add_to(heatmap_group)

        # Add Layer Control to toggle layers (base maps and feature groups)
        folium.LayerControl(collapsed=False).add_to(m)

        # Display the map
        map_height = 650
        folium_static(m, width=None, height=map_height) # Use container width

    # Dashboard and Analysis
    with col2:
        st.markdown('<h2 class="subheader">Seismic Analysis</h2>', unsafe_allow_html=True)

        # Ensure tabs are created even if data is initially empty
        # --- ADJUST Tab Titles (Emoji + Text) ---
        tab1, tab2 = st.tabs(["📊 Fault Analysis", "📈 Earthquake History"])

        with tab1:
            st.markdown("#### Fault Characteristics")
            if not filtered_faults.empty:
                # --- Plot 1: Slip Rate ---
                slip_fig = px.bar(
                    filtered_faults.sort_values('annual_slip_rate', ascending=False),
                    x='name',
                    y='annual_slip_rate',
                    color='seismic_risk',
                    labels={'annual_slip_rate': 'Avg. Slip Rate (mm/yr)', 'name': 'Fault System Name'},
                    title='Fault System Activity (Slip Rate)',
                    color_discrete_map={
                        'Low': '#2ECC71', # Emerald
                        'Moderate': '#3498DB', # Peter River
                        'Moderate to High': '#9B59B6', # Amethyst
                        'High': '#F39C12', # Orange
                        'Very High': '#E74C3C' # Alizarin
                    },
                    height=350
                )
                slip_fig.update_layout(
                    xaxis_title=None,
                    yaxis_title="Slip Rate (mm/yr)",
                    xaxis_tickangle=-45,
                    margin=dict(t=30, b=0, l=0, r=0),
                    legend_title_text='Risk'
                )
                st.plotly_chart(slip_fig, use_container_width=True)

                # --- Plot 2: Fault Types ---
                all_fault_types = []
                for types in filtered_faults['fault_types']:
                    # Handle potential None or non-string types defensively
                    if isinstance(types, str):
                        all_fault_types.extend([t.strip() for t in types.split(',') if t.strip()]) # Ensure no empty strings
                fault_type_counts = pd.Series(all_fault_types).value_counts()

                if not fault_type_counts.empty:
                    type_fig = px.pie(
                        names=fault_type_counts.index,
                        values=fault_type_counts.values,
                        title='Distribution of Reported Fault Types',
                        hole=0.4,
                        height=300
                    )
                    type_fig.update_traces(textposition='inside', textinfo='percent+label')
                    type_fig.update_layout(margin=dict(t=50, b=0, l=0, r=0), showlegend=False)
                    st.plotly_chart(type_fig, use_container_width=True)
                else:
                     st.info("No fault type data available for the selected systems.")

            else:
                st.warning("No fault systems match the selected risk filter (or no fault data loaded).")

        with tab2:
            st.markdown("#### Historical Earthquake Patterns")
            if not filtered_quakes.empty:
                # --- Plot 1: Timeline ---
                timeline_fig = px.scatter(
                    filtered_quakes.sort_values('year'),
                    x='year',
                    y='magnitude',
                    size='deaths',
                    color='magnitude',
                    hover_name='location',
                    hover_data={'year': True, 'magnitude': True, 'deaths': True, 'location': False, 'description': True}, # Added description
                    size_max=25,
                    color_continuous_scale=px.colors.sequential.OrRd, # Orange-Red scale
                    title=f'Earthquakes ({year_range[0]}-{year_range[1]}, M{magnitude_range[0]:.1f}-{magnitude_range[1]:.1f})',
                    height=350
                )
                timeline_fig.update_layout(
                    xaxis_title='Year',
                    yaxis_title='Magnitude (Mw)',
                    coloraxis_colorbar_title='Mw',
                    margin=dict(t=30, b=0, l=0, r=0)
                )
                timeline_fig.update_traces(hovertemplate=
                    "<b>%{hovertext} (%{customdata[0]})</b><br>" +
                    "Magnitude: %{customdata[1]:.1f} Mw<br>" +
                    "Deaths: %{customdata[2]:,}<br>" +
                    "<i>%{customdata[3]}</i>" + # Show description on hover
                    "<extra></extra>") # Hide extra trace info
                st.plotly_chart(timeline_fig, use_container_width=True)

                # --- Summary: Deadliest ---
                st.markdown('##### Deadliest Events in Filtered Range')
                deadliest = filtered_quakes.nlargest(5, 'deaths')
                for _, quake in deadliest.iterrows():
                    st.markdown(f"- **{quake['year']} {quake['location']} (M{quake['magnitude']})**: {quake['deaths']:,} deaths")
                if len(filtered_quakes) > 5:
                    st.caption(f"Showing top {min(len(deadliest), 5)} deadliest out of {len(filtered_quakes)} filtered events.")
                elif len(filtered_quakes) == 0:
                     st.caption("No events in the filtered range.")
                else:
                     st.caption(f"Showing all {len(filtered_quakes)} filtered events.")

            else:
                st.info("No historical earthquakes match your filter criteria.")

    # Footer with educational information
    st.markdown("---")
    st.markdown('<h2 class="subheader">Understanding Italian Tectonics</h2>', unsafe_allow_html=True)

    st.markdown("""
    Southern Italy's complex geology results from the ongoing collision between the African and Eurasian tectonic plates.
    Key features include:
    - **Subduction:** The African plate dives beneath the Eurasian plate, particularly under the Calabrian Arc, driving volcanism and deep earthquakes.
    - **Extension:** The Tyrrhenian Sea is opening, causing stretching and normal faulting in the Apennines.
    - **Lateral Movement:** Strike-slip faults accommodate sideways motion between crustal blocks.

    This dynamic environment makes the region prone to significant seismic hazards, underscoring the importance of research and preparedness.
    """)

    # Credits
    st.markdown('<p class="footer">App by Elhocine Mohamed-Seghir | Data: Various geological sources (approximate/illustrative) | Tools: Streamlit, Folium, Plotly, Pandas</p>', unsafe_allow_html=True)

# Run the application
if __name__ == "__main__":
    # --- Add checks for data validity before running main ---
    if not isinstance(fault_data, list) or not all(isinstance(item, dict) for item in fault_data):
        st.error("Critical Error: `fault_data` is not a valid list of dictionaries. Please check the data structure.")
    elif not isinstance(historical_earthquakes, list) or not all(isinstance(item, dict) for item in historical_earthquakes):
         st.error("Critical Error: `historical_earthquakes` is not a valid list of dictionaries. Please check the data structure.")
    elif df_faults.empty and not missing_cols: # Check if df is empty AFTER checking for missing cols
         st.warning("Warning: No valid fault data could be loaded into the DataFrame. Some features might be unavailable.")
         main() # Still attempt to run, maybe only earthquake data is wanted
    elif missing_cols:
         pass # Error already displayed and stopped in DataFrame creation phase
    else:
        main()