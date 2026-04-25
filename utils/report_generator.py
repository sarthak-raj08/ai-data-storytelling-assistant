import os
import base64
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO

class ReportGenerator:
    """Generate downloadable reports in PDF and HTML formats"""
    
    def __init__(self):
        self.sns_style = sns.set_style("whitegrid")
        
    def generate_html_report(self, df, insights, recommendations, story, charts_data, filters_applied):
        """Generate an HTML report that can be saved or printed to PDF"""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>AI Analytics Report - {timestamp}</title>
            <meta charset="UTF-8">
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 40px 20px;
                }}
                
                .report-container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 20px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    overflow: hidden;
                }}
                
                .header {{
                    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                    color: white;
                    padding: 40px;
                    text-align: center;
                }}
                
                .header h1 {{
                    font-size: 2.5em;
                    margin-bottom: 10px;
                }}
                
                .header p {{
                    opacity: 0.9;
                    font-size: 1.1em;
                }}
                
                .section {{
                    padding: 30px 40px;
                    border-bottom: 1px solid #e0e0e0;
                }}
                
                .section h2 {{
                    color: #1e3c72;
                    margin-bottom: 20px;
                    font-size: 1.8em;
                    border-left: 4px solid #667eea;
                    padding-left: 15px;
                }}
                
                .section h3 {{
                    color: #2a5298;
                    margin: 20px 0 10px 0;
                }}
                
                .metric-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin: 20px 0;
                }}
                
                .metric-card {{
                    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                    padding: 20px;
                    border-radius: 15px;
                    text-align: center;
                    transition: transform 0.3s;
                }}
                
                .metric-card:hover {{
                    transform: translateY(-5px);
                }}
                
                .metric-value {{
                    font-size: 2em;
                    font-weight: bold;
                    color: #1e3c72;
                }}
                
                .metric-label {{
                    color: #555;
                    margin-top: 5px;
                }}
                
                .insight-box {{
                    background: #e8f4f8;
                    padding: 20px;
                    border-radius: 15px;
                    margin: 15px 0;
                    border-left: 4px solid #00b4d8;
                }}
                
                .recommendation-item {{
                    background: #f0fdf4;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 10px;
                    border-left: 4px solid #22c55e;
                }}
                
                .story-box {{
                    background: #fef3c7;
                    padding: 25px;
                    border-radius: 15px;
                    font-style: italic;
                    line-height: 1.6;
                }}
                
                .chart-container {{
                    margin: 30px 0;
                    text-align: center;
                }}
                
                .chart-container img {{
                    max-width: 100%;
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }}
                
                .footer {{
                    background: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    color: #666;
                    font-size: 0.9em;
                }}
                
                .badge {{
                    display: inline-block;
                    background: #667eea;
                    color: white;
                    padding: 5px 12px;
                    border-radius: 20px;
                    font-size: 0.8em;
                    margin: 5px;
                }}
                
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                
                th, td {{
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }}
                
                th {{
                    background: #1e3c72;
                    color: white;
                }}
                
                tr:hover {{
                    background: #f5f5f5;
                }}
            </style>
        </head>
        <body>
            <div class="report-container">
                <div class="header">
                    <h1>📊 AI Data Analytics Report</h1>
                    <p>Generated on {timestamp}</p>
                    <p>Powered by Groq AI & Advanced Analytics Engine</p>
                </div>
                
                <div class="section">
                    <h2>📋 Executive Summary</h2>
                    <div class="metric-grid">
                        <div class="metric-card">
                            <div class="metric-value">{df.shape[0]:,}</div>
                            <div class="metric-label">Total Records</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{df.shape[1]}</div>
                            <div class="metric-label">Features/Variables</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{df.select_dtypes(include=['number']).shape[1]}</div>
                            <div class="metric-label">Numerical Columns</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{df.select_dtypes(include=['object']).shape[1]}</div>
                            <div class="metric-label">Categorical Columns</div>
                        </div>
                    </div>
                    
                    <h3>📊 Data Sample</h3>
                    {df.head(10).to_html(classes='data-table', border=0)}
                </div>
                
                <div class="section">
                    <h2>🤖 AI-Generated Insights</h2>
                    <div class="insight-box">
                        {insights}
                    </div>
                </div>
                
                <div class="section">
                    <h2>📖 Data Story</h2>
                    <div class="story-box">
                        {story}
                    </div>
                </div>
                
                <div class="section">
                    <h2>💡 Strategic Recommendations</h2>
                    {recommendations}
                </div>
                
                <div class="section">
                    <h2>📈 Key Visualizations</h2>
                    {self._format_charts_html(charts_data)}
                </div>
                
                <div class="section">
                    <h2>🔍 Statistical Summary</h2>
                    <h3>Descriptive Statistics</h3>
                    {df.describe().to_html(classes='data-table', border=0)}
                    
                    <h3>Missing Values</h3>
                    {df.isnull().sum().to_frame('Missing Count').to_html(border=0)}
                    
                    <h3>Data Types</h3>
                    {df.dtypes.to_frame('Data Type').to_html(border=0)}
                </div>
                
                <div class="footer">
                    <p>Report generated by AI Data Analytics Studio | Automated Insights Engine</p>
                    <p>Filters Applied: {filters_applied}</p>
                    <p>© 2024 - All analytical insights are AI-assisted</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def _format_charts_html(self, charts_data):
        """Format charts for HTML display"""
        if not charts_data:
            return "<p>No charts available for this report.</p>"
        
        html = ""
        for chart_name, chart_base64 in charts_data.items():
            html += f"""
            <div class="chart-container">
                <h3>{chart_name}</h3>
                <img src="data:image/png;base64,{chart_base64}" alt="{chart_name}">
            </div>
            """
        return html
    
    def create_download_link(self, html_content, filename="analytics_report.html"):
        """Create a download link for the report"""
        b64 = base64.b64encode(html_content.encode()).decode()
        href = f'<a href="data:text/html;base64,{b64}" download="{filename}" class="download-btn" style="background: linear-gradient(120deg, #1e3c72, #2a5298); color: white; border-radius: 30px; padding: 10px 30px; font-weight: 600; text-decoration: none; display: inline-block; margin: 5px;">📥 Download Full Report (HTML)</a>'
        return href
    
    def create_csv_download(self, df, filename="filtered_data.csv"):
        """Create CSV download link for filtered data"""
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="{filename}" class="download-btn" style="background: linear-gradient(120deg, #1e3c72, #2a5298); color: white; border-radius: 30px; padding: 10px 30px; font-weight: 600; text-decoration: none; display: inline-block; margin: 5px;">📥 Download Filtered Data (CSV)</a>'
        return href