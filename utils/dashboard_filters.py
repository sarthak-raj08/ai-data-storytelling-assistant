import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

class DashboardFilters:
    """Interactive dashboard filters manager"""
    
    def __init__(self, df):
        self.df = df.copy()
        self.filtered_df = df.copy()
        self.active_filters = {}
        
    def create_filters_ui(self):
        """Create interactive filter panel - NO automatic filtering"""
        st.sidebar.markdown("### 🎛️ Interactive Filters")
        st.sidebar.markdown("---")
        
        filters_applied = []
        
        # Start with original data
        self.filtered_df = self.df.copy()
        
        # Date filter if date column exists
        date_columns = []
        
        # First check for datetime columns
        date_columns = self.df.select_dtypes(include=['datetime64']).columns.tolist()
        
        # If no datetime columns, try to detect date-like columns
        if len(date_columns) == 0:
            for col in self.df.columns:
                if 'date' in col.lower() or 'time' in col.lower():
                    try:
                        self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
                        self.filtered_df = self.df.copy()
                        date_columns = [col]
                        break
                    except:
                        pass
        
        if len(date_columns) > 0:
            date_col = date_columns[0]
            
            try:
                valid_dates = self.df[date_col].dropna()
                if len(valid_dates) > 0:
                    min_date = valid_dates.min()
                    max_date = valid_dates.max()
                    
                    min_date_obj = min_date.date() if hasattr(min_date, 'date') else min_date
                    max_date_obj = max_date.date() if hasattr(max_date, 'date') else max_date
                    
                    st.sidebar.markdown("#### 📅 Date Range")
                    
                    # Use session state to remember filter
                    filter_key = f"date_filter_{date_col}"
                    default_dates = (min_date_obj, max_date_obj)
                    
                    date_range = st.sidebar.date_input(
                        "Select date range",
                        value=default_dates,
                        min_value=min_date_obj,
                        max_value=max_date_obj,
                        key=filter_key
                    )
                    
                    # Only apply if not default range
                    if isinstance(date_range, tuple) and len(date_range) == 2:
                        start_date, end_date = date_range
                        # Check if different from default
                        if start_date != min_date_obj or end_date != max_date_obj:
                            start_ts = pd.Timestamp(start_date)
                            end_ts = pd.Timestamp(end_date)
                            mask = (self.filtered_df[date_col] >= start_ts) & (self.filtered_df[date_col] <= end_ts)
                            self.filtered_df = self.filtered_df[mask]
                            filters_applied.append(f"Date: {start_date} to {end_date}")
            except Exception as e:
                pass
        
        # Categorical filters - only apply if user selects something
        categorical_cols = self.df.select_dtypes(include=['object', 'category']).columns.tolist()
        if categorical_cols:
            st.sidebar.markdown("#### 🏷️ Category Filters")
            for col in categorical_cols[:3]:
                unique_vals = self.df[col].dropna().unique().tolist()
                if len(unique_vals) > 1 and len(unique_vals) <= 20:
                    filter_key = f"cat_filter_{col}"
                    selected = st.sidebar.multiselect(
                        f"Filter by {col}",
                        options=unique_vals,
                        default=[],
                        key=filter_key
                    )
                    if selected:
                        self.filtered_df = self.filtered_df[self.filtered_df[col].isin(selected)]
                        filters_applied.append(f"{col}: {', '.join(selected[:2])}{'...' if len(selected)>2 else ''}")
        
        # Numerical range filters - only apply if user changes range
        numerical_cols = self.df.select_dtypes(include=['number']).columns.tolist()
        if numerical_cols:
            st.sidebar.markdown("#### 📊 Value Range")
            for col in numerical_cols[:2]:
                min_val = float(self.df[col].min())
                max_val = float(self.df[col].max())
                
                if min_val != max_val and not np.isnan(min_val) and not np.isnan(max_val):
                    filter_key = f"num_filter_{col}"
                    default_range = (min_val, max_val)
                    
                    range_val = st.sidebar.slider(
                        f"{col} range",
                        min_value=min_val,
                        max_value=max_val,
                        value=default_range,
                        step=(max_val - min_val) / 100,
                        key=filter_key
                    )
                    
                    # Only apply if range changed
                    if range_val != default_range:
                        self.filtered_df = self.filtered_df[
                            (self.filtered_df[col] >= range_val[0]) & 
                            (self.filtered_df[col] <= range_val[1])
                        ]
                        filters_applied.append(f"{col}: {range_val[0]:.1f} - {range_val[1]:.1f}")
        
        # Search filter
        st.sidebar.markdown("#### 🔍 Text Search")
        search_term = st.sidebar.text_input("Search in all text columns", "", key="search_filter")
        if search_term:
            text_cols = self.df.select_dtypes(include=['object']).columns
            if len(text_cols) > 0:
                mask = pd.Series([False] * len(self.filtered_df))
                for col in text_cols:
                    mask = mask | self.filtered_df[col].astype(str).str.contains(search_term, case=False, na=False)
                self.filtered_df = self.filtered_df[mask]
                filters_applied.append(f"Search: '{search_term}'")
        
        # Clear filters button
        st.sidebar.markdown("---")
        if st.sidebar.button("🗑️ Clear All Filters", use_container_width=True):
            # Reset all filter keys in session state
            for key in list(st.session_state.keys()):
                if key.startswith(('date_filter_', 'cat_filter_', 'num_filter_', 'search_filter')):
                    del st.session_state[key]
            st.rerun()
        
        # Show filtered count
        st.sidebar.markdown("---")
        if len(filters_applied) > 0:
            st.sidebar.markdown(f"**Active Filters:** {len(filters_applied)}")
            st.sidebar.markdown(f"**Showing:** {len(self.filtered_df):,} / {len(self.df):,} rows")
        else:
            st.sidebar.markdown(f"**Showing all:** {len(self.filtered_df):,} rows")
        
        return self.filtered_df, filters_applied
    
    def create_quick_insights_panel(self, filtered_df, original_df):
        """Create quick insights panel showing filter impact"""
        
        if len(filtered_df) != len(original_df):
            st.markdown("### 🎯 Filter Impact")
            col1, col2 = st.columns(2)
            with col1:
                reduction_pct = (1 - len(filtered_df)/len(original_df)) * 100
                st.metric("Data Reduction", f"{reduction_pct:.1f}%", 
                         delta=f"-{len(original_df) - len(filtered_df)} rows")
            with col2:
                st.metric("Filtered Rows", f"{len(filtered_df):,}", 
                         delta=f"of {len(original_df):,}")