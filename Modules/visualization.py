"""
Data Visualization Module using Plotly
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from typing import Optional, Dict, List, Tuple
import logging
import numpy as np

class DataVisualizer:
    """Create interactive visualizations from query results"""
    
    def __init__(self):
        """Initialize the data visualizer"""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Default color scheme
        self.color_palette = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
        ]
        
    def auto_visualize(self, df: pd.DataFrame, query: str = "") -> Optional[go.Figure]:
        """Automatically determine the best visualization type for the data"""
        if df is None or df.empty:
            return None
            
        try:
            # Analyze data structure
            num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
            
            # Convert date-like strings to datetime
            for col in df.columns:
                if df[col].dtype == 'object' and 'date' in col.lower():
                    try:
                        df[col] = pd.to_datetime(df[col])
                        date_cols.append(col)
                        if col in cat_cols:
                            cat_cols.remove(col)
                    except:
                        pass
            
            num_rows = len(df)
            
            # Decision logic for visualization type
            if num_rows == 1 and len(num_cols) == 1:
                # Single metric
                return self.create_metric_card(df, num_cols[0])
                
            elif len(cat_cols) >= 1 and len(num_cols) >= 1:
                # Categorical vs Numerical
                if 'total' in query.lower() or 'sum' in query.lower() or 'revenue' in query.lower():
                    return self.create_bar_chart(df, cat_cols[0], num_cols[0])
                else:
                    return self.create_bar_chart(df, cat_cols[0], num_cols[0])
                    
            elif len(date_cols) >= 1 and len(num_cols) >= 1:
                # Time series
                return self.create_line_chart(df, date_cols[0], num_cols[0])
                
            elif len(num_cols) >= 2:
                # Multiple numerical columns
                return self.create_scatter_plot(df, num_cols[0], num_cols[1])
                
            else:
                # Default table view with some styling
                return self.create_table_view(df)
                
        except Exception as e:
            self.logger.error(f"Auto visualization failed: {e}")
            return self.create_table_view(df)
            
    def create_bar_chart(self, df: pd.DataFrame, x_col: str, y_col: str, title: str = None) -> go.Figure:
        """Create an interactive bar chart"""
        try:
            if title is None:
                title = f"{y_col.title()} by {x_col.title()}"
                
            fig = px.bar(
                df, 
                x=x_col, 
                y=y_col,
                title=title,
                color_discrete_sequence=self.color_palette,
                template="plotly_white"
            )
            
            fig.update_layout(
                xaxis_title=x_col.replace('_', ' ').title(),
                yaxis_title=y_col.replace('_', ' ').title(),
                showlegend=False,
                height=500
            )
            
            fig.update_traces(
                hovertemplate=f"<b>{x_col.title()}</b>: %{{x}}<br>" +
                             f"<b>{y_col.title()}</b>: %{{y:,.0f}}<extra></extra>"
            )
            
            return fig
            
        except Exception as e:
            self.logger.error(f"Bar chart creation failed: {e}")
            return None
            
    def create_line_chart(self, df: pd.DataFrame, x_col: str, y_col: str, title: str = None) -> go.Figure:
        """Create an interactive line chart"""
        try:
            if title is None:
                title = f"{y_col.title()} Over Time"
                
            fig = px.line(
                df,
                x=x_col,
                y=y_col,
                title=title,
                template="plotly_white"
            )
            
            fig.update_layout(
                xaxis_title=x_col.replace('_', ' ').title(),
                yaxis_title=y_col.replace('_', ' ').title(),
                height=500
            )
            
            fig.update_traces(
                line=dict(color=self.color_palette[0], width=3),
                hovertemplate=f"<b>{x_col.title()}</b>: %{{x}}<br>" +
                             f"<b>{y_col.title()}</b>: %{{y:,.2f}}<extra></extra>"
            )
            
            return fig
            
        except Exception as e:
            self.logger.error(f"Line chart creation failed: {e}")
            return None
            
    def create_pie_chart(self, df: pd.DataFrame, labels_col: str, values_col: str, title: str = None) -> go.Figure:
        """Create an interactive pie chart"""
        try:
            if title is None:
                title = f"Distribution of {values_col.title()}"
                
            fig = px.pie(
                df,
                names=labels_col,
                values=values_col,
                title=title,
                color_discrete_sequence=self.color_palette,
                template="plotly_white"
            )
            
            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate="<b>%{label}</b><br>" +
                             "Value: %{value:,.0f}<br>" +
                             "Percentage: %{percent}<extra></extra>"
            )
            
            fig.update_layout(height=500)
            
            return fig
            
        except Exception as e:
            self.logger.error(f"Pie chart creation failed: {e}")
            return None
            
    def create_scatter_plot(self, df: pd.DataFrame, x_col: str, y_col: str, title: str = None) -> go.Figure:
        """Create an interactive scatter plot"""
        try:
            if title is None:
                title = f"{y_col.title()} vs {x_col.title()}"
                
            fig = px.scatter(
                df,
                x=x_col,
                y=y_col,
                title=title,
                template="plotly_white",
                color_discrete_sequence=self.color_palette
            )
            
            fig.update_layout(
                xaxis_title=x_col.replace('_', ' ').title(),
                yaxis_title=y_col.replace('_', ' ').title(),
                height=500
            )
            
            fig.update_traces(
                marker=dict(size=8, opacity=0.7),
                hovertemplate=f"<b>{x_col.title()}</b>: %{{x}}<br>" +
                             f"<b>{y_col.title()}</b>: %{{y}}<extra></extra>"
            )
            
            return fig
            
        except Exception as e:
            self.logger.error(f"Scatter plot creation failed: {e}")
            return None
            
    def create_metric_card(self, df: pd.DataFrame, value_col: str) -> go.Figure:
        """Create a metric card for single values"""
        try:
            value = df[value_col].iloc[0]
            
            # Format the value
            if isinstance(value, (int, float)):
                if value >= 1000000:
                    display_value = f"${value/1000000:.1f}M"
                elif value >= 1000:
                    display_value = f"${value/1000:.1f}K"
                else:
                    display_value = f"${value:,.2f}"
            else:
                display_value = str(value)
                
            fig = go.Figure()
            
            fig.add_trace(go.Indicator(
                mode = "number",
                value = float(value) if isinstance(value, (int, float)) else 0,
                number = {"font": {"size": 80, "color": self.color_palette[0]}},
                title = {"text": value_col.replace('_', ' ').title(), 
                        "font": {"size": 24}},
            ))
            
            fig.update_layout(
                height=300,
                template="plotly_white"
            )
            
            return fig
            
        except Exception as e:
            self.logger.error(f"Metric card creation failed: {e}")
            return None
            
    def create_table_view(self, df: pd.DataFrame) -> go.Figure:
        """Create a styled table view"""
        try:
            fig = go.Figure(data=[go.Table(
                header=dict(
                    values=list(df.columns),
                    fill_color=self.color_palette[0],
                    font=dict(color='white', size=14),
                    align="left"
                ),
                cells=dict(
                    values=[df[col] for col in df.columns],
                    fill_color='lightgray',
                    font=dict(color='black', size=12),
                    align="left"
                )
            )])
            
            fig.update_layout(
                title="Query Results",
                height=min(600, len(df) * 40 + 100),
                template="plotly_white"
            )
            
            return fig
            
        except Exception as e:
            self.logger.error(f"Table view creation failed: {e}")
            return None
            
    def create_multi_chart_dashboard(self, df: pd.DataFrame) -> go.Figure:
        """Create a dashboard with multiple chart types"""
        try:
            num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            
            if len(num_cols) < 1 or len(cat_cols) < 1:
                return self.auto_visualize(df)
                
            # Create subplots
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Bar Chart', 'Pie Chart', 'Data Table', 'Summary Stats'),
                specs=[[{"type": "bar"}, {"type": "pie"}],
                       [{"type": "table"}, {"type": "table"}]]
            )
            
            # Bar chart
            fig.add_trace(
                go.Bar(x=df[cat_cols[0]], y=df[num_cols[0]], 
                      name="Bar Chart", marker_color=self.color_palette[0]),
                row=1, col=1
            )
            
            # Pie chart
            fig.add_trace(
                go.Pie(labels=df[cat_cols[0]], values=df[num_cols[0]], 
                      name="Pie Chart"),
                row=1, col=2
            )
            
            # Data table
            fig.add_trace(
                go.Table(
                    header=dict(values=list(df.columns)),
                    cells=dict(values=[df[col] for col in df.columns])
                ),
                row=2, col=1
            )
            
            # Summary statistics
            summary_df = df[num_cols].describe()
            fig.add_trace(
                go.Table(
                    header=dict(values=['Statistic'] + list(summary_df.columns)),
                    cells=dict(values=[summary_df.index] + 
                                     [summary_df[col].round(2) for col in summary_df.columns])
                ),
                row=2, col=2
            )
            
            fig.update_layout(height=800, showlegend=False, title="Dashboard Overview")
            
            return fig
            
        except Exception as e:
            self.logger.error(f"Multi-chart dashboard creation failed: {e}")
            return self.auto_visualize(df)
            
    def suggest_visualization_type(self, df: pd.DataFrame) -> List[str]:
        """Suggest appropriate visualization types for the data"""
        if df is None or df.empty:
            return []
            
        suggestions = []
        
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
        
        if len(cat_cols) >= 1 and len(num_cols) >= 1:
            suggestions.extend(["Bar Chart", "Pie Chart"])
            
        if len(date_cols) >= 1 and len(num_cols) >= 1:
            suggestions.append("Line Chart")
            
        if len(num_cols) >= 2:
            suggestions.append("Scatter Plot")
            
        if len(df) == 1 and len(num_cols) >= 1:
            suggestions.append("Metric Card")
            
        suggestions.append("Table View")
        
        return suggestions
        
    def create_custom_visualization(self, df: pd.DataFrame, chart_type: str, 
                                  x_col: str = None, y_col: str = None) -> Optional[go.Figure]:
        """Create a custom visualization based on user selection"""
        try:
            if chart_type.lower() == "bar chart" and x_col and y_col:
                return self.create_bar_chart(df, x_col, y_col)
            elif chart_type.lower() == "line chart" and x_col and y_col:
                return self.create_line_chart(df, x_col, y_col)
            elif chart_type.lower() == "pie chart" and x_col and y_col:
                return self.create_pie_chart(df, x_col, y_col)
            elif chart_type.lower() == "scatter plot" and x_col and y_col:
                return self.create_scatter_plot(df, x_col, y_col)
            elif chart_type.lower() == "metric card" and y_col:
                return self.create_metric_card(df, y_col)
            elif chart_type.lower() == "table view":
                return self.create_table_view(df)
            else:
                return self.auto_visualize(df)
                
        except Exception as e:
            self.logger.error(f"Custom visualization creation failed: {e}")
            return None