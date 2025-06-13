import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import PyPDF2
from io import BytesIO

st.set_page_config(layout="wide")
st.title("💳 Expense Dashboard with Smart Categorization")

# File upload
uploaded_file = st.file_uploader("Upload your HDFC credit card statement (PDF or Excel)", type=['pdf', 'csv', 'xlsx'])

if uploaded_file:
    # Detect format
    filename = uploaded_file.name.lower()
    if filename.endswith('.pdf'):
        reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        # Simulate parsing
        st.write("📄 **PDF text extracted.** Add your parser logic here.")
        st.code(text[:1000] + "...")
        st.warning("Demo PDF parser in place. Real parser will extract Date, Description, Amount.")
    else:
        if filename.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # Basic cleanup
        df.columns = df.columns.str.lower().str.strip()
        df.rename(columns={'date': 'date', 'description': 'description', 'amount': 'amount'}, inplace=True)
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df.dropna(subset=['date'], inplace=True)
        df['amount'] = df['amount'].astype(float)
        df['month'] = df['date'].dt.to_period('M')

        # Categorization logic
        categories = {
            'subscriptions': ['spotify', 'youtube', 'prime', 'zee', 'hotstar'],
            'food': ['swiggy', 'zomato', 'dominos', 'instamart', 'blinkit'],
            'shopping': ['amazon', 'flipkart', 'myntra'],
            'utilities': ['airtel', 'jio', 'electricity', 'gas'],
            'education': ['school', 'fees', 'footprints'],
            'others': []
        }

        def assign_category(desc):
            desc = str(desc).lower()
            for cat, keywords in categories.items():
                if any(k in desc for k in keywords):
                    return cat
            return 'others'

        df['category'] = df['description'].apply(assign_category)

        st.success(f"Parsed {len(df)} transactions.")
        st.dataframe(df[['date', 'description', 'amount', 'category']])

        # Charts
        st.subheader("📊 Monthly Spending")
        monthly = df.groupby('month')['amount'].sum()
        st.bar_chart(monthly)

        st.subheader("🥧 Category-wise Spending")
        category_sum = df.groupby('category')['amount'].sum()
        st.pyplot(category_sum.plot.pie(autopct='%1.1f%%', figsize=(5,5)).get_figure())

        st.subheader("📌 Top Vendors")
        vendor_sum = df.groupby('description')['amount'].sum().sort_values(ascending=False).head(10)
        st.dataframe(vendor_sum)

        st.subheader("📁 Export Data")
        csv = df.to_csv(index=False).encode()
        st.download_button("Download Categorized CSV", csv, "categorized_expenses.csv", "text/csv")
