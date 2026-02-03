import pandas as pd
import re
import config

class BankingAI:
    def __init__(self, data_path=None):
        if data_path:
            self.df = pd.read_csv(data_path)
            # Ensure dates are datetime objects for querying
            if 'Transaction_Date' in self.df.columns:
                self.df['Transaction_Date'] = pd.to_datetime(self.df['Transaction_Date'])
        else:
            self.df = pd.DataFrame()

    def parse_intent(self, query):
        """
        Determines what the user wants: 'query', 'chart', 'summary'.
        """
        query = query.lower()
        if any(w in query for w in ['plot', 'chart', 'graph', 'visualize']):
            return 'chart'
        elif any(w in query for w in ['summary', 'insight', 'overview']):
            return 'summary'
        return 'query'

    def process_query(self, query):
        """
        The Core AI Logic.
        Translates Natural Language -> Filtered DataFrame -> Answer.
        """
        query = query.lower()
        response = {"text": "", "data": None, "type": "text"}
        
        if self.df.empty:
            return {"text": "No data loaded. Please run the cleaning pipeline first.", "type": "error"}

        filtered_df = self.df.copy()
        
        # --- 1. Entity Extraction (Simple Regex-based) ---
        
        # Detect Branch
        # Assumes branches are single words or we have a list. 
        # For this demo, we check if any known branch is in the query.
        known_branches = self.df['Branch'].unique().tolist() if 'Branch' in self.df.columns else []
        selected_branch = None
        for branch in known_branches:
            if branch.lower() in query:
                filtered_df = filtered_df[filtered_df['Branch'].str.lower() == branch.lower()]
                selected_branch = branch
                break
                
        # Detect Transaction Type
        known_types = self.df['Transaction_Type'].unique().tolist() if 'Transaction_Type' in self.df.columns else []
        for t_type in known_types:
            if t_type.lower() in query:
                filtered_df = filtered_df[filtered_df['Transaction_Type'].str.lower() == t_type.lower()]
                break

        # --- 2. Calculation Logic ---
        
        # "Total Amount" / "Sum"
        if any(w in query for w in ['total', 'sum', 'how much']):
            total_amt = filtered_df['Amount'].sum()
            count = len(filtered_df)
            
            context = f" for {selected_branch}" if selected_branch else ""
            response['text'] = f"The **Total Transaction Amount**{context} is **${total_amt:,.2f}** over {count} transactions."
            response['data'] = filtered_df
            response['type'] = 'kpi'

        # "Average"
        elif 'average' in query:
            avg_amt = filtered_df['Amount'].mean()
            response['text'] = f"The **Average Transaction Amount** is **${avg_amt:,.2f}**."
            response['data'] = filtered_df
            response['type'] = 'kpi'

        # "List" / "Show" (Default)
        else:
            limit = 10  # Default limit
            response['text'] = f"Here are the top {limit} transactions fitting your criteria."
            response['data'] = filtered_df.head(limit)
            response['type'] = 'table'
            
        return response
