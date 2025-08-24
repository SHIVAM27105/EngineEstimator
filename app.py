import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math

# Page configuration
st.set_page_config(
    page_title="IC Engine Performance Estimator",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling and card layout
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    
    .main-header {
        font-family: 'Roboto', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        color: #2E86C1;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .result-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        border-left: 4px solid #2E86C1;
    }
    
    .metric-label {
        font-family: 'Roboto', sans-serif;
        font-weight: 600;
        color: #2C3E50;
        font-size: 1rem;
    }
    
    .metric-value {
        font-family: 'Roboto', sans-serif;
        font-weight: 700;
        color: #2E86C1;
        font-size: 1.5rem;
    }
    
    .section-header {
        font-family: 'Roboto', sans-serif;
        font-weight: 600;
        color: #2C3E50;
        font-size: 1.3rem;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #2E86C1;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown('<div class="main-header">🔧 IC Engine Performance Estimator</div>', unsafe_allow_html=True)

# Sidebar for inputs
st.sidebar.markdown('<div class="section-header">Engine Parameters</div>', unsafe_allow_html=True)

# Input parameters
with st.sidebar:
    # Engine geometry
    st.subheader("Engine Geometry")
    bore = st.number_input("Bore (mm)", min_value=10.0, max_value=1000.0, value=80.0, step=1.0)
    stroke = st.number_input("Stroke (mm)", min_value=10.0, max_value=500.0, value=90.0, step=1.0)
    num_cylinders = st.number_input("Number of Cylinders", min_value=1, max_value=12, value=4, step=1)
    
    # Engine specifications
    st.subheader("Engine Specifications")
    engine_type = st.selectbox("Engine Type", ["4-Stroke", "2-Stroke"])
    compression_ratio = st.number_input("Compression Ratio", min_value=6.0, max_value=20.0, value=9.5, step=0.1)
    rpm = st.number_input("RPM", min_value=0, max_value=8000, value=3000, step=100)
    
    # Power and torque input
    st.subheader("Power Input")
    
    imep = st.number_input("Indicated Mean Effective Pressure (bar)", min_value=1.0, max_value=30.0, value=8.0, step=0.1)
        
    torque = st.number_input("Torque (Nm)", min_value=10.0, max_value=1000.0, value=150.0, step=1.0)
        
    
    # Fuel properties
    st.subheader("Fuel Properties")
    fuel_type = st.selectbox("Fuel Type", ["Petrol", "Diesel"])
    
    # Default calorific values
    default_cv = 44000 if fuel_type == "Petrol" else 42000
    calorific_value = st.number_input("Calorific Value (kJ/kg)", min_value=30000, max_value=50000, value=default_cv, step=100)
    fuel_consumption = st.number_input("Fuel Consumption (kg/hr)", min_value=0.1, max_value=100.0, value=5.0, step=0.1)

# Engine calculations
def calculate_engine_performance(bore, stroke, num_cylinders, engine_type, compression_ratio, rpm, 
                                imep, torque, calorific_value, fuel_consumption):
    """
    Calculate comprehensive engine performance parameters
    """
    # Convert units
    bore_m = bore / 1000  # mm to m
    stroke_m = stroke / 1000  # mm to m
    
    # Calculate swept volume per cylinder (m³)
    swept_volume_per_cylinder = (math.pi / 4) * (bore_m ** 2) * stroke_m
    
    # Total swept volume (cc)
    total_swept_volume = swept_volume_per_cylinder * num_cylinders * 1e6  # m³ to cc

    
    # Calculate brake power (kW)
    brake_power = (2 * math.pi * rpm * torque) / (60 * 1000)  # kW
    
    # Calculate indicated power (assuming mechanical efficiency)
    # Typical mechanical efficiency ranges: 80-90% for modern engines
    # Indicated Power (kW) using textbook formula
    # Convert mep (bar) → Pa
    imep_pa = imep * 1e5  

    # Piston area
    piston_area = (math.pi / 4) * (bore_m ** 2)

    # Working strokes per minute
    if engine_type == "2-Stroke":
        n = rpm
    else:  # 4-Stroke
        n = rpm / 2

    # Indicated Power (kW)
    indicated_power = (imep_pa * stroke_m * piston_area * n * num_cylinders) / 60 / 1000

    
    # Calculate friction power
    friction_power = indicated_power - brake_power
    
    # Calculate mechanical efficiency
    mechanical_efficiency = (brake_power / indicated_power) * 100
    
    # Calculate brake thermal efficiency
    fuel_power = (fuel_consumption / 3600) * calorific_value   # kW (fuel energy input rate)
    brake_thermal_efficiency = (brake_power / fuel_power) * 100
    
    # Calculate indicated thermal efficiency
    indicated_thermal_efficiency = (indicated_power / fuel_power) * 100
    
    # Calculate BSFC (Brake Specific Fuel Consumption) in g/kWh
    bsfc = (fuel_consumption * 1000) / brake_power  # g/kWh
    
    # Calculate ISFC (Indicated Specific Fuel Consumption) in g/kWh
    isfc = (fuel_consumption * 1000) / indicated_power  # g/kWh
    
    return {
        'swept_volume': total_swept_volume,
        'indicated_power': indicated_power,
        'brake_power': brake_power,
        'friction_power': friction_power,
        'mechanical_efficiency': mechanical_efficiency,
        'brake_thermal_efficiency': brake_thermal_efficiency,
        'indicated_thermal_efficiency': indicated_thermal_efficiency,
        'bsfc': bsfc,
        'isfc': isfc,
        'torque': torque,
        'imep': imep
    }

# Calculate performance
results = calculate_engine_performance(
    bore, stroke, num_cylinders, engine_type, compression_ratio, rpm,
    imep, torque, calorific_value, fuel_consumption
)

# Display results in cards
st.markdown('<div class="section-header">Performance Results</div>', unsafe_allow_html=True)

# Create columns for result cards
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="result-card">
        <div class="metric-label">Swept Volume</div>
        <div class="metric-value">{:.2f} cc</div>
    </div>
    """.format(results['swept_volume']), unsafe_allow_html=True)
    
    st.markdown("""
    <div class="result-card">
        <div class="metric-label">Brake Power (BP)</div>
        <div class="metric-value">{:.2f} kW</div>
    </div>
    """.format(results['brake_power']), unsafe_allow_html=True)
    
    st.markdown("""
    <div class="result-card">
        <div class="metric-label">Brake Thermal Efficiency</div>
        <div class="metric-value">{:.2f} %</div>
    </div>
    """.format(results['brake_thermal_efficiency']), unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="result-card">
        <div class="metric-label">Indicated Power (IP)</div>
        <div class="metric-value">{:.2f} kW</div>
    </div>
    """.format(results['indicated_power']), unsafe_allow_html=True)
    
    st.markdown("""
    <div class="result-card">
        <div class="metric-label">Friction Power (FP)</div>
        <div class="metric-value">{:.2f} kW</div>
    </div>
    """.format(results['friction_power']), unsafe_allow_html=True)
    
    st.markdown("""
    <div class="result-card">
        <div class="metric-label">BSFC</div>
        <div class="metric-value">{:.2f} g/kWh</div>
    </div>
    """.format(results['bsfc']), unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="result-card">
        <div class="metric-label">Mechanical Efficiency</div>
        <div class="metric-value">{:.2f} %</div>
    </div>
    """.format(results['mechanical_efficiency']), unsafe_allow_html=True)
    
    st.markdown("""
    <div class="result-card">
        <div class="metric-label">Torque</div>
        <div class="metric-value">{:.2f} Nm</div>
    </div>
    """.format(results['torque']), unsafe_allow_html=True)
    
    st.markdown("""
    <div class="result-card">
        <div class="metric-label">ISFC</div>
        <div class="metric-value">{:.2f} g/kWh</div>
    </div>
    """.format(results['isfc']), unsafe_allow_html=True)

# Performance Analysis Charts
st.markdown('<div class="section-header">Performance Analysis</div>', unsafe_allow_html=True)

# Create two columns for charts
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("Brake Thermal Efficiency vs Compression Ratio")
    
    # Generate data for efficiency vs compression ratio
    cr_range = np.linspace(6, 20, 50)
    
    # Theoretical efficiency calculation (Otto cycle for petrol, Diesel cycle approximation for diesel)
    if fuel_type == "Petrol":
        # Otto cycle efficiency: η = 1 - (1/r^(γ-1))
        gamma = 1.4  # for air
        theoretical_efficiency = (1 - (1 / (cr_range ** (gamma - 1)))) * 100
    else:
        # Diesel cycle approximation
        gamma = 1.35  # slightly lower for diesel
        theoretical_efficiency = (1 - (1 / (cr_range ** (gamma - 1)))) * 100 * 0.9  # Diesel typically lower
    
    # Practical efficiency (accounting for losses)
    practical_efficiency = theoretical_efficiency * 0.6  # Typical practical efficiency factor
    
    # Create efficiency chart
    fig_eff = go.Figure()
    fig_eff.add_trace(go.Scatter(
        x=cr_range, y=theoretical_efficiency,
        mode='lines', name='Theoretical Efficiency',
        line=dict(color='#2E86C1', width=3)
    ))
    fig_eff.add_trace(go.Scatter(
        x=cr_range, y=practical_efficiency,
        mode='lines', name='Practical Efficiency',
        line=dict(color='#E74C3C', width=3, dash='dash')
    ))
    
    # Add current operating point
    current_theoretical = (1 - (1 / (compression_ratio ** (gamma - 1)))) * 100
    if fuel_type == "Diesel":
        current_theoretical *= 0.9
    current_practical = current_theoretical * 0.6
    
    fig_eff.add_trace(go.Scatter(
        x=[compression_ratio], y=[results['brake_thermal_efficiency']],
        mode='markers', name='Current Operating Point',
        marker=dict(color='#F39C12', size=12, symbol='diamond')
    ))
    
    fig_eff.update_layout(
        title="Brake Thermal Efficiency vs Compression Ratio",
        xaxis_title="Compression Ratio",
        yaxis_title="Brake Thermal Efficiency (%)",
        height=400,
        template="plotly_white"
    )
    
    st.plotly_chart(fig_eff, use_container_width=True)

with chart_col2:
    st.subheader("Brake Power vs RPM")
    
    # Generate data for power vs RPM
    rpm_range = np.linspace(1000, 6000, 50)
    
    # Simplified power curve (torque typically decreases with RPM after peak)
    # Assuming peak torque around 3000 RPM
    peak_rpm = 3000
    max_torque = results['torque']
    
    # Simplified torque curve
    torque_curve = []
    for r in rpm_range:
        if r <= peak_rpm:
            # Linear increase to peak
            t = max_torque * (r / peak_rpm)
        else:
            # Exponential decay after peak
            decay_factor = np.exp(-0.0005 * (r - peak_rpm))
            t = max_torque * decay_factor
        torque_curve.append(t)
    
    torque_curve = np.array(torque_curve)
    
    # Calculate power curve: P = 2πNT/60000 (kW)
    power_curve = (2 * np.pi * rpm_range * torque_curve) / 60000
    
    # Create power chart
    fig_power = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add power curve
    fig_power.add_trace(
        go.Scatter(x=rpm_range, y=power_curve, mode='lines', name='Power',
                  line=dict(color='#2E86C1', width=3)),
        secondary_y=False,
    )
    
    # Add torque curve
    fig_power.add_trace(
        go.Scatter(x=rpm_range, y=torque_curve, mode='lines', name='Torque',
                  line=dict(color='#E74C3C', width=3, dash='dash')),
        secondary_y=True,
    )
    
    # Add current operating point
    fig_power.add_trace(
        go.Scatter(x=[rpm], y=[results['brake_power']], mode='markers',
                  name='Current Operating Point',
                  marker=dict(color='#F39C12', size=12, symbol='diamond')),
        secondary_y=False,
    )
    
    # Set y-axes titles
    fig_power.update_yaxes(title_text="Brake Power (kW)", secondary_y=False)
    fig_power.update_yaxes(title_text="Torque (Nm)", secondary_y=True)
    
    fig_power.update_layout(
        title="Brake Power and Torque vs RPM",
        xaxis_title="RPM",
        height=400,
        template="plotly_white"
    )
    
    st.plotly_chart(fig_power, use_container_width=True)

# Additional information
st.markdown('<div class="section-header">Engine Information</div>', unsafe_allow_html=True)

info_col1, info_col2 = st.columns(2)

with info_col1:
    st.info(f"""
    **Engine Configuration:**
    - Type: {engine_type}
    - Cylinders: {num_cylinders}
    - Bore × Stroke: {bore:.1f} × {stroke:.1f} mm
    - Displacement: {results['swept_volume']:.0f} cc
    - Compression Ratio: {compression_ratio:.1f}:1
    """)

with info_col2:
    st.info(f"""
    **Operating Conditions:**
    - RPM: {rpm:,}
    - Fuel: {fuel_type}
    - iMEP: {results['imep']:.1f} bar
    - Fuel Consumption: {fuel_consumption:.1f} kg/hr
    - Calorific Value: {calorific_value:,} kJ/kg
    """)

# Footer with calculation notes
st.markdown("---")
st.markdown("""
**Calculation Notes:**
- Friction power is calculated as the difference between indicated and brake power
- BSFC and ISFC are calculated based on the fuel consumption and their respective power outputs
- Charts show theoretical performance curves for analysis
""")
