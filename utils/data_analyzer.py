import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

class DataAnalyzer:
    def __init__(self, df):
        self.df = df
        self.numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
    def get_summary_stats(self):
        """Generate comprehensive summary statistics"""
        stats = {}
        for col in self.numerical_cols:
            stats[col] = {
                'mean': self.df[col].mean(),
                'median': self.df[col].median(),
                'std': self.df[col].std(),
                'min': self.df[col].min(),
                'max': self.df[col].max(),
                'missing': self.df[col].isnull().sum()
            }
        return stats
    
    def get_correlations(self):
        """Calculate correlation matrix for numerical columns"""
        if len(self.numerical_cols) >= 2:
            return self.df[self.numerical_cols].corr()
        return pd.DataFrame()
    
    def detect_outliers(self, method='iqr'):
        """Detect outliers in numerical columns"""
        outliers = {}
        for col in self.numerical_cols:
            if method == 'iqr':
                Q1 = self.df[col].quantile(0.25)
                Q3 = self.df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                outlier_count = self.df[(self.df[col] < lower_bound) | (self.df[col] > upper_bound)].shape[0]
                outliers[col] = {'count': outlier_count, 'lower_bound': lower_bound, 'upper_bound': upper_bound}
        return outliers
    
    def get_trend_analysis(self, date_col=None):
        """Analyze trends if date column exists"""
        if date_col and date_col in self.df.columns:
            try:
                # Convert to datetime if not already
                if not pd.api.types.is_datetime64_any_dtype(self.df[date_col]):
                    self.df[date_col] = pd.to_datetime(self.df[date_col], errors='coerce')
                
                # Drop NaN dates
                temp_df = self.df.dropna(subset=[date_col])
                
                if len(temp_df) > 0:
                    trends = {}
                    for col in self.numerical_cols:
                        try:
                            # Resample by month
                            temp_df.set_index(date_col, inplace=True)
                            monthly_avg = temp_df[col].resample('M').mean()
                            if len(monthly_avg) > 1 and not monthly_avg.iloc[0] == 0:
                                trend_pct = ((monthly_avg.iloc[-1] - monthly_avg.iloc[0]) / abs(monthly_avg.iloc[0])) * 100
                                trends[col] = {'trend_percentage': trend_pct, 'direction': 'up' if trend_pct > 0 else 'down'}
                            temp_df.reset_index(inplace=True)
                        except Exception as e:
                            continue
                    return trends if trends else None
            except Exception as e:
                return None
        return None
    
    def get_column_insights(self):
        """Generate basic insights about each column"""
        insights = []
        for col in self.numerical_cols:
            skewness = self.df[col].skew()
            if abs(skewness) > 1:
                insights.append(f"{col} is highly skewed ({skewness:.2f})")
        
        for col in self.categorical_cols:
            unique_vals = self.df[col].nunique()
            if unique_vals > 0:
                top_val = self.df[col].mode()[0] if not self.df[col].empty else "N/A"
                insights.append(f"{col} has {unique_vals} unique values. Most common: {top_val}")
        
        return insights