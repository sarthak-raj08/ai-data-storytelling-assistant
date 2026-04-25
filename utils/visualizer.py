import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

class Visualizer:
    def __init__(self):
        plt.style.use('seaborn-v0_8-darkgrid')
        
    def create_bar_chart(self, df, x_col, y_col, title="Bar Chart"):
        """Interactive bar chart using Plotly"""
        fig = px.bar(df, x=x_col, y=y_col, title=title, 
                     color_discrete_sequence=['#1f77b4'],
                     text_auto='.2s')
        fig.update_layout(height=500, width=700, template='plotly_white')
        return fig
    
    def create_histogram(self, df, column, title="Histogram"):
        """Histogram for distribution analysis"""
        fig = px.histogram(df, x=column, title=title, 
                          nbins=30, color_discrete_sequence=['#2ca02c'],
                          marginal='box')
        fig.update_layout(height=500, width=700, template='plotly_white')
        return fig
    
    def create_clustered_bar_chart(self, df, x_col, group_col, y_col, title="Clustered Bar Chart"):
        """Clustered/Grouped bar chart for comparison"""
        fig = px.bar(df, x=x_col, y=y_col, color=group_col, 
                    title=title, barmode='group',
                    color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(height=500, width=800, template='plotly_white')
        return fig
    
    def create_correlation_heatmap(self, df, numerical_cols, title="Correlation Heatmap"):
        """Correlation heatmap using Plotly"""
        corr_matrix = df[numerical_cols].corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmin=-1, zmax=1,
            text=np.round(corr_matrix.values, 2),
            texttemplate='%{text}',
            textfont={"size": 10},
            hoverongaps=False
        ))
        
        fig.update_layout(title=title, height=600, width=700, template='plotly_white')
        return fig
    
    def create_line_chart(self, df, date_col, value_col, title="Time Series Trend"):
        """Line chart for time series"""
        fig = px.line(df, x=date_col, y=value_col, title=title,
                     markers=True, color_discrete_sequence=['#ff7f0e'])
        fig.update_layout(height=500, width=700, template='plotly_white')
        return fig
    
    def create_matplotlib_chart(self, df, chart_type, **kwargs):
        """Fallback matplotlib charts"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        if chart_type == 'bar':
            ax.bar(kwargs.get('x'), kwargs.get('y'), color='steelblue')
            ax.set_title(kwargs.get('title', 'Bar Chart'))
        elif chart_type == 'histogram':
            ax.hist(df[kwargs.get('column')], bins=30, color='green', alpha=0.7)
            ax.set_title(kwargs.get('title', 'Histogram'))
        elif chart_type == 'heatmap':
            sns.heatmap(df[kwargs.get('columns')].corr(), annot=True, cmap='coolwarm', ax=ax)
            ax.set_title(kwargs.get('title', 'Correlation Heatmap'))
        
        ax.set_xlabel(kwargs.get('xlabel', ''))
        ax.set_ylabel(kwargs.get('ylabel', ''))
        return fig