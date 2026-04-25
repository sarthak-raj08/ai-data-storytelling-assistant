import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import io
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import tempfile
import os
import re

# ReportLab imports
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

import plotly.io as pio

# Import from utils
from utils.data_analyzer import DataAnalyzer
from utils.visualizer import Visualizer
from utils.insight_engine import InsightEngine
from utils.storyteller import Storyteller
from utils.report_generator import ReportGenerator
from utils.dashboard_filters import DashboardFilters

# Page configuration
st.set_page_config(
    page_title="AI Data Analytics Studio",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
    
    .metric-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.07);
        transition: transform 0.3s ease;
    }
    .metric-card:hover { transform: translateY(-5px); }
    
    .kpi-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 20px;
        text-align: center;
        color: white;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .dashboard-section {
        background: rgba(255,255,255,0.95);
        border-radius: 20px;
        padding: 25px;
        margin-top: 30px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .insight-card {
        background: linear-gradient(135deg, #f0f4ff 0%, #e8eeff 100%);
        border-left: 4px solid #667eea;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        max-height: 450px;
        overflow-y: auto;
    }
    
    .insight-card strong {
        color: #2a5298;
    }
    
    .recommendation-card {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border-left: 4px solid #f59e0b;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        max-height: 450px;
        overflow-y: auto;
    }
    
    .recommendation-title {
        font-weight: bold;
        font-style: italic;
        color: #92400e;
        font-size: 1.05rem;
        margin-bottom: 8px;
    }
    
    .recommendation-details {
        margin-left: 20px;
        color: #5a3a0e;
        line-height: 1.5;
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    [data-testid="stSidebar"] * { color: #1a1a2e !important; }
    
    h1 { color: #1e3c72; font-size: 2.5rem !important; }
    h2 { color: #1e3c72; font-size: 1.5rem !important; }
    h3 { color: #2a5298; font-size: 1.2rem !important; }
    
    .download-btn {
        background: linear-gradient(120deg, #1e3c72, #2a5298);
        color: white;
        border-radius: 30px;
        padding: 10px 25px;
        font-weight: 600;
        text-decoration: none;
        display: inline-block;
        margin: 5px;
        text-align: center;
        cursor: pointer;
        border: none;
    }
    
    .stButton > button {
        background: linear-gradient(120deg, #1e3c72, #2a5298);
        color: white;
        border-radius: 30px;
        padding: 8px 25px;
        font-weight: 600;
        width: 100%;
        border: none;
    }
    
    .insight-card::-webkit-scrollbar, .recommendation-card::-webkit-scrollbar {
        width: 6px;
    }
    
    .insight-card::-webkit-scrollbar-track {
        background: #e0e0e0;
        border-radius: 10px;
    }
    
    .insight-card::-webkit-scrollbar-thumb {
        background: #667eea;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = None
if 'filtered_df' not in st.session_state:
    st.session_state.filtered_df = None
if 'active_filters' not in st.session_state:
    st.session_state.active_filters = []
if 'current_insights' not in st.session_state:
    st.session_state.current_insights = ""
if 'current_recommendations' not in st.session_state:
    st.session_state.current_recommendations = ""

# Initialize components
@st.cache_resource
def init_insight_engine():
    try:
        return InsightEngine()
    except Exception as e:
        st.sidebar.warning(f"AI Insights unavailable: {str(e)[:50]}")
        return None

report_generator = ReportGenerator()
insight_engine = init_insight_engine()

# Function to format insights
def format_insights_beautiful(insights_text):
    """Format insights with better structure"""
    if not insights_text:
        return '<p>No insights available</p>'
    
    lines = insights_text.split('\n')
    formatted_html = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        line = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line)
        
        if line.startswith('*'):
            line = '📌 ' + line[1:]
            formatted_html.append(f'<div style="margin: 10px 0; line-height: 1.5;">{line}</div>')
        else:
            formatted_html.append(f'<p style="margin: 8px 0; line-height: 1.5;">{line}</p>')
    
    return ''.join(formatted_html)

# Function to format recommendations
def format_recommendations_beautiful(recommendations_text):
    """Format recommendations with bold italic titles"""
    if not recommendations_text:
        return '<p>No recommendations available.</p>'
    
    lines = recommendations_text.split('\n')
    formatted_html = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        line = re.sub(r'^[\*\s]+', '', line)
        
        if re.match(r'^\d+\.', line):
            title = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line)
            formatted_html.append(f'<div style="margin: 15px 0 5px 0; font-weight: bold; font-style: italic; color: #92400e;">✨ {title}</div>')
        elif line.startswith('-') or line.startswith('*'):
            detail = re.sub(r'^[\*\-\s]+', '', line)
            detail = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', detail)
            formatted_html.append(f'<div style="margin: 5px 0 5px 20px;">■ {detail}</div>')
        elif ':' in line and len(line.split(':')[0]) < 30:
            parts = line.split(':', 1)
            key = parts[0].strip()
            value = parts[1].strip() if len(parts) > 1 else ''
            formatted_html.append(f'<div style="margin: 5px 0 5px 20px;"><strong>{key}:</strong> {value}</div>')
        else:
            line = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line)
            formatted_html.append(f'<div style="margin: 5px 0 5px 20px;">{line}</div>')
    
    return ''.join(formatted_html)

# Function to create box plot
def create_box_plot(df, x_col, y_col, title):
    """Create box plot for distribution analysis"""
    fig = px.box(df, x=x_col, y=y_col, title=title,
                 color_discrete_sequence=['#667eea'],
                 points="all",  # Show all points
                 notched=True)  # Add notches for confidence intervals
    fig.update_layout(height=450, template='plotly_white',
                     xaxis_title=x_col, yaxis_title=y_col)
    fig.update_traces(marker=dict(size=6, color='#764ba2', opacity=0.6))
    return fig

# Function to generate PDF report
def generate_pdf_report(df, insights, recommendations, active_filters, chart_images):
    """Generate PDF report with all analytics"""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    
    pdf_path = tempfile.mktemp(suffix='.pdf')
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, 
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=72)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle', parent=styles['Heading1'],
        fontSize=24, textColor=colors.HexColor('#1e3c72'),
        alignment=TA_CENTER, spaceAfter=30
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading', parent=styles['Heading2'],
        fontSize=16, textColor=colors.HexColor('#2a5298'),
        spaceAfter=12, spaceBefore=20
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal', parent=styles['Normal'],
        fontSize=10, spaceAfter=6
    )
    
    story = []
    
    story.append(Paragraph("AI Data Analytics Studio - Complete Report", title_style))
    story.append(Paragraph(f"Generated on: {timestamp}", normal_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Executive Summary", heading_style))
    story.append(Paragraph(f"<b>Total Records:</b> {df.shape[0]:,}", normal_style))
    story.append(Paragraph(f"<b>Total Columns:</b> {df.shape[1]}", normal_style))
    story.append(Paragraph(f"<b>Numerical Features:</b> {len(numeric_cols)}", normal_style))
    story.append(Paragraph(f"<b>Categorical Features:</b> {len(categorical_cols)}", normal_style))
    story.append(Paragraph(f"<b>Active Filters:</b> {', '.join(active_filters) if active_filters else 'None'}", normal_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Key AI Insights", heading_style))
    if insights:
        clean_insights = insights.replace('*', '•').replace('**', '')
        for line in clean_insights.split('\n')[:15]:
            if line.strip():
                story.append(Paragraph(line, normal_style))
    else:
        story.append(Paragraph("No AI insights generated.", normal_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Strategic Recommendations", heading_style))
    if recommendations:
        clean_rec = recommendations.replace('*', '•').replace('**', '')
        for line in clean_rec.split('\n')[:12]:
            if line.strip():
                story.append(Paragraph(line, normal_style))
    else:
        story.append(Paragraph("No recommendations available.", normal_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Statistical Summary", heading_style))
    if len(numeric_cols) > 0:
        stats_df = df[numeric_cols].describe()
        data = [['Statistic'] + list(stats_df.columns)]
        for idx in stats_df.index:
            row = [idx] + [f'{stats_df.loc[idx, col]:.2f}' for col in stats_df.columns]
            data.append(row)
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3c72')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Data Sample (First 20 rows)", heading_style))
    sample_data = df.head(20).values.tolist()
    sample_headers = list(df.columns)
    sample_table_data = [sample_headers] + sample_data
    sample_table = Table(sample_table_data)
    sample_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))
    story.append(sample_table)
    
    if chart_images:
        story.append(Spacer(1, 20))
        story.append(Paragraph("Key Visualizations", heading_style))
        for chart_name, chart_path in chart_images.items():
            story.append(Paragraph(f"<b>{chart_name}</b>", normal_style))
            try:
                img = Image(chart_path, width=6*inch, height=4*inch)
                story.append(img)
                story.append(Spacer(1, 10))
            except:
                pass
    
    doc.build(story)
    return pdf_path

# Header
st.markdown("<h1 style='text-align: center'>✨ AI Data Analytics Studio</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666'>Intelligent Data Analysis | Smart Visualizations | AI-Powered Insights</p>", unsafe_allow_html=True)
st.markdown("---")

# Sidebar
with st.sidebar:
    st.markdown("### 🎯 Upload Your Data")
    uploaded_file = st.file_uploader("Choose CSV or Excel file", type=['csv', 'xlsx', 'xls'])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.session_state.df = df
            st.session_state.filtered_df = df.copy()
            st.success(f"✅ Loaded {len(df):,} rows, {len(df.columns)} columns")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    st.markdown("---")
    st.markdown("### 🚀 Features")
    st.markdown("""
    - ✅ Data Overview & Preview
    - ✅ Interactive Filters
    - ✅ Bar & Box Plot Charts
    - ✅ Donut & Heatmap
    - ✅ Key Insights
    - ✅ Recommendations
    - ✅ PDF Report Download
    """)

# Main content
if st.session_state.df is not None:
    df = st.session_state.df
    
    dashboard = DashboardFilters(df)
    filtered_df, active_filters = dashboard.create_filters_ui()
    
    st.session_state.filtered_df = filtered_df
    st.session_state.active_filters = active_filters
    
    current_df = filtered_df
    
    if len(current_df) == 0:
        st.warning("⚠️ No data matches the current filters. Showing all data.")
        current_df = df.copy()
    
    # Data Overview
    st.markdown("## 📊 Data Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    numeric_cols = current_df.select_dtypes(include=[np.number]).columns
    categorical_cols = current_df.select_dtypes(include=['object', 'category']).columns
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📊 Total Rows</h3>
            <h2 style="color: #667eea;">{current_df.shape[0]:,}</h2>
            <small>of {df.shape[0]:,} total</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📋 Columns</h3>
            <h2 style="color: #667eea;">{current_df.shape[1]}</h2>
            <small>total features</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🔢 Numeric</h3>
            <h2 style="color: #667eea;">{len(numeric_cols)}</h2>
            <small>columns</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🏷️ Categorical</h3>
            <h2 style="color: #667eea;">{len(categorical_cols)}</h2>
            <small>columns</small>
        </div>
        """, unsafe_allow_html=True)
    
    with st.expander("🔍 View Raw Data (First 100 rows)", expanded=False):
        st.dataframe(current_df.head(100), use_container_width=True)
    
    with st.expander("📈 Quick Statistics", expanded=False):
        if len(numeric_cols) > 0:
            st.dataframe(current_df[numeric_cols].describe(), use_container_width=True)
    
    if active_filters:
        st.markdown("---")
        st.markdown("### 🎯 Active Filters")
        for f in active_filters:
            st.markdown(f"• {f}")
    
    st.markdown("---")
    
    # Key Insights & Recommendations
    st.markdown("## 💡 Key Insights & Recommendations")
    
    if insight_engine and (not st.session_state.current_insights or len(st.session_state.current_insights) < 100):
        with st.spinner("🤖 Generating key insights..."):
            try:
                analyzer = DataAnalyzer(current_df)
                stats = analyzer.get_summary_stats()
                correlations = analyzer.get_correlations().to_dict() if not analyzer.get_correlations().empty else {}
                outliers = analyzer.detect_outliers()
                date_cols = current_df.select_dtypes(include=['datetime64']).columns
                trends = analyzer.get_trend_analysis(date_cols[0] if len(date_cols) > 0 else None)
                
                data_context = f"Dataset with {current_df.shape[0]} rows, {current_df.shape[1]} columns."
                insights = insight_engine.generate_insights(data_context, stats, correlations, outliers, trends)
                st.session_state.current_insights = insights
                
                stats_summary = f"{current_df.shape[0]} records, {len(numeric_cols)} numerical features"
                recommendations = insight_engine.generate_recommendations(insights, stats_summary)
                st.session_state.current_recommendations = recommendations
            except Exception as e:
                st.warning(f"Could not generate AI insights: {str(e)[:100]}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🧠 Key Insights")
        if st.session_state.current_insights:
            formatted_insights = format_insights_beautiful(st.session_state.current_insights)
            st.markdown(f"""
            <div class="insight-card">
                {formatted_insights}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("💡 Upload data to generate AI insights")
            st.markdown(f"""
            <div class="insight-card">
                <p><strong>📊 Data Summary:</strong></p>
                <p>• {current_df.shape[0]:,} records, {current_df.shape[1]} features</p>
                <p>• {len(numeric_cols)} numerical columns</p>
                <p>• {len(categorical_cols)} categorical columns</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### 💡 Recommendations")
        if st.session_state.current_recommendations:
            formatted_recs = format_recommendations_beautiful(st.session_state.current_recommendations)
            st.markdown(f"""
            <div class="recommendation-card">
                {formatted_recs}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="recommendation-card">
                <p><strong>🎯 Suggested Actions:</strong></p>
                <p>📌 Explore visualizations to identify patterns</p>
                <p>📌 Apply filters to focus on specific segments</p>
                <p>📌 Review correlation heatmap for relationships</p>
                <p>📌 Download PDF report for documentation</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Interactive Dashboard
    st.markdown('<div class="dashboard-section">', unsafe_allow_html=True)
    st.markdown("## 🎛️ Interactive Analytics Dashboard")
    st.markdown("---")
    
    # KPI Cards
    if len(numeric_cols) > 0:
        st.markdown("### Key Performance Indicators")
        kpi_cols = st.columns(min(4, len(numeric_cols)))
        for i, col in enumerate(numeric_cols[:4]):
            avg_val = current_df[col].mean()
            min_val = current_df[col].min()
            max_val = current_df[col].max()
            with kpi_cols[i]:
                st.markdown(f"""
                <div class="kpi-card">
                    <div style="font-size: 0.9rem; opacity: 0.9;">{col}</div>
                    <div style="font-size: 2rem; font-weight: bold;">{avg_val:.2f}</div>
                    <div style="font-size: 0.8rem; opacity: 0.8;">Min: {min_val:.2f} | Max: {max_val:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("---")
    
    # Row 1: Bar Chart & Box Plot
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Bar Chart")
        if len(categorical_cols) > 0 and len(numeric_cols) > 0:
            bar_cat = st.selectbox("Select X-axis (Category)", categorical_cols, key="bar_cat_dash")
            bar_num = st.selectbox("Select Y-axis (Value)", numeric_cols, key="bar_num_dash")
            bar_data = current_df.groupby(bar_cat)[bar_num].mean().reset_index()
            fig = px.bar(bar_data, x=bar_cat, y=bar_num, 
                        title=f"Average {bar_num} by {bar_cat}",
                        color_discrete_sequence=['#667eea'],
                        text_auto='.2s')
            fig.update_layout(height=450, template='plotly_white', showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Need categorical and numerical columns for bar chart")
    
    with col2:
        st.markdown("#### 📦 Box Plot (Distribution Analysis)")
        if len(categorical_cols) > 0 and len(numeric_cols) > 0:
            box_cat = st.selectbox("Select Category (X-axis)", categorical_cols, key="box_cat_dash")
            box_num = st.selectbox("Select Value (Y-axis)", numeric_cols, key="box_num_dash")
            
            fig = create_box_plot(current_df, box_cat, box_num, 
                                  f"Distribution of {box_num} by {box_cat}")
            st.plotly_chart(fig, use_container_width=True)
            
            # Add interpretation help
            with st.expander("📖 How to read this Box Plot"):
                st.markdown("""
                - **Box**: Shows the interquartile range (25th to 75th percentile)
                - **Line in box**: Median value
                - **Whiskers**: Show data range (excluding outliers)
                - **Dots**: Individual data points
                - **Notch**: Confidence interval around the median
                """)
        else:
            st.info("Need categorical and numerical columns for box plot")
    
    st.markdown("---")
    
    # Row 2: Donut Chart & Heatmap
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🥧 Donut Chart")
        if len(categorical_cols) > 0:
            donut_col = st.selectbox("Select Category", categorical_cols, key="donut_dash")
            donut_data = current_df[donut_col].value_counts().reset_index()
            donut_data.columns = ['Category', 'Count']
            fig = px.pie(donut_data, values='Count', names='Category', 
                        title=f"Distribution of {donut_col}",
                        hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Need categorical column for donut chart")
    
    with col2:
        st.markdown("#### 🔥 Correlation Heatmap")
        if len(numeric_cols) >= 2:
            corr_matrix = current_df[numeric_cols].corr()
            fig = go.Figure(data=go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns,
                y=corr_matrix.columns,
                colorscale='RdBu',
                zmin=-1, zmax=1,
                text=np.round(corr_matrix.values, 2),
                texttemplate='%{text}',
                textfont={"size": 10}
            ))
            fig.update_layout(title="Feature Correlations", height=400, template='plotly_white')
            st.plotly_chart(fig, use_container_width=True)
            
            # Show strongest correlations
            strong_corrs = []
            for i in range(len(corr_matrix)):
                for j in range(i+1, len(corr_matrix)):
                    if abs(corr_matrix.iloc[i,j]) > 0.5:
                        strong_corrs.append(f"• {corr_matrix.columns[i]} ↔ {corr_matrix.columns[j]}: {corr_matrix.iloc[i,j]:.2f}")
            if strong_corrs:
                with st.expander("💡 Strong Correlations Found"):
                    for corr in strong_corrs[:5]:
                        st.markdown(corr)
        else:
            st.info("Need at least 2 numerical columns for correlation")
    
    # Row 3: Histogram
    st.markdown("---")
    st.markdown("#### 📊 Histogram")
    if len(numeric_cols) > 0:
        hist_col = st.selectbox("Select Column", numeric_cols, key="hist_dash")
        fig = px.histogram(current_df, x=hist_col, nbins=30, 
                          title=f"Distribution of {hist_col}",
                          color_discrete_sequence=['#1e3c72'],
                          marginal='box')
        fig.update_layout(height=400, template='plotly_white')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Need numerical column for histogram")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Download Reports
    st.markdown("---")
    st.markdown("## 📥 Download Reports")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Download PDF Report", use_container_width=True):
            with st.spinner("Generating PDF..."):
                try:
                    chart_images = {}
                    temp_dir = tempfile.mkdtemp()
                    
                    if len(categorical_cols) > 0 and len(numeric_cols) > 0:
                        bar_data = current_df.groupby(categorical_cols[0])[numeric_cols[0]].mean().reset_index()
                        fig_bar = px.bar(bar_data, x=categorical_cols[0], y=numeric_cols[0])
                        bar_path = os.path.join(temp_dir, "bar_chart.png")
                        fig_bar.write_image(bar_path, width=800, height=400)
                        chart_images["Bar Chart"] = bar_path
                    
                    if len(categorical_cols) > 0 and len(numeric_cols) > 0:
                        fig_box = create_box_plot(current_df, categorical_cols[0], numeric_cols[0], "Box Plot")
                        box_path = os.path.join(temp_dir, "box_plot.png")
                        fig_box.write_image(box_path, width=800, height=400)
                        chart_images["Box Plot"] = box_path
                    
                    insights = st.session_state.current_insights or "No AI insights"
                    recommendations = st.session_state.current_recommendations or "No recommendations"
                    
                    pdf_path = generate_pdf_report(current_df, insights, recommendations, active_filters, chart_images)
                    
                    with open(pdf_path, 'rb') as f:
                        pdf_data = f.read()
                    
                    b64_pdf = base64.b64encode(pdf_data).decode()
                    href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="analytics_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf" class="download-btn">📥 Click to Download PDF</a>'
                    st.markdown(href, unsafe_allow_html=True)
                    st.success("✅ PDF Ready!")
                    
                    for file in chart_images.values():
                        try:
                            os.remove(file)
                        except:
                            pass
                    try:
                        os.rmdir(temp_dir)
                        os.remove(pdf_path)
                    except:
                        pass
                except Exception as e:
                    st.error(f"PDF Error: {str(e)}")
    
    with col2:
        if st.button("📥 Download CSV", use_container_width=True):
            csv = current_df.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv" class="download-btn">📥 Click to Download CSV</a>'
            st.markdown(href, unsafe_allow_html=True)
            st.success("✅ CSV Ready!")

else:
    st.markdown("""
    <div style="text-align: center; padding: 60px 20px;">
        <h2 style="color: #1e3c72;">🚀 Welcome to AI Data Analytics Studio</h2>
        <p style="font-size: 1.1rem;">Upload your dataset from the sidebar to begin</p>
        <br>
        <div style="display: flex; justify-content: center; gap: 20px; flex-wrap: wrap;">
            <div style="background: white; border-radius: 15px; padding: 20px; width: 150px;">
                <h3>📂</h3>
                <p>Upload</p>
            </div>
            <div style="background: white; border-radius: 15px; padding: 20px; width: 150px;">
                <h3>📊</h3>
                <p>Visualize</p>
            </div>
            <div style="background: white; border-radius: 15px; padding: 20px; width: 150px;">
                <h3>🤖</h3>
                <p>AI Insights</p>
            </div>
            <div style="background: white; border-radius: 15px; padding: 20px; width: 150px;">
                <h3>📥</h3>
                <p>PDF Reports</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("<p style='text-align: center; color: #888;'>✨ AI Data Analytics Studio ✨</p>", unsafe_allow_html=True)