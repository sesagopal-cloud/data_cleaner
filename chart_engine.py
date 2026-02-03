import plotly.express as px
import pandas as pd
import config

class ChartEngine:
    @staticmethod
    def plot_trend(df, date_col='Transaction_Date', value_col='Amount', title="Transaction Trend"):
        """
        Generates a line chart showing the trend of a value over time.
        Aggregates by day to make the chart readable.
        """
        if df.empty:
            return None
            
        # Ensure date format
        df[date_col] = pd.to_datetime(df[date_col])
        daily_data = df.groupby(df[date_col].dt.date)[value_col].sum().reset_index()
        
        fig = px.line(daily_data, x=date_col, y=value_col, title=title, markers=True)
        fig.update_layout(template="plotly_white")
        return fig

    @staticmethod
    def plot_distribution(df, category_col, value_col='Amount', title="Distribution"):
        """
        Generates a pie/bar chart showing distribution of a categorical column.
        """
        if df.empty:
            return None
            
        summary = df.groupby(category_col)[value_col].sum().reset_index()
        
        fig = px.bar(summary, x=category_col, y=value_col, title=title, color=category_col)
        fig.update_layout(template="plotly_white")
        return fig
