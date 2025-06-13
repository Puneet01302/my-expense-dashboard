import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import PyPDF2
import re
st.set_page_config(layout="wide")
st.title("💳 Expense Dashboard — PDF & Excel Ready")
# -----------------------------------
# 1️⃣ PDF Parser for HDFC Statements
# -----------------------------------
def parse_hdfc_pdf(pdf_reader):
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    lines = text.split("\n")
    transactions = []
    date_pattern = re.compile(r'\d{2}/\d{2}/\d{4}')
    for line in lines:
        line = line.strip()
        if date_pattern.match(line):
            parts = line.split()
            date = parts[0]
            amount = parts[-1].replace(",", "").replace("CR", "").strip()
            description = " ".join(parts[1:-1])
            try:
                amt = float(amount)
                if "CR" in line:
                    amt = -amt
                transactions.append([date, description, amt])
            except:
                pass
    df = pd.DataFrame(transactions, columns=['date', 'description', 'amount'])
    df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
    df.dropna(subset=['date'], inplace=True)
    return df
# -----------------------------------
# 2️⃣ Categorization function
# -----------------------------------
def assign_category(desc):
    categories = {
        'subscriptions': ['spotify', 'youtube', 'prime', 'zee', 'hotstar'],
        'food': ['swiggy', 'zomato', 'dominos', 'instamart', 'blinkit'],
        'shopping': ['amazon', 'flipkart', 'myntra'],
        'utilities': ['airtel', 'jio', 'electricity', 'gas'],
        'education': ['school', 'fees', 'footprints'],
        'others': []
    }
    desc = str(desc).lower()
    for cat, keywords in categories.items():
        if any(k in desc for k in keywords):
            return cat
    return 'others'
# -----------------------------------
# 3️⃣ File Upload
# -----------------------------------
uploaded_file = st.file_uploader("Upload HDFC PDF, CSV, or Excel", type=['pdf', 'csv', 'xlsx'])
if uploaded_file:
    filename = uploaded_file.name.lower()
    if filename.endswith('.pdf'):
        st.info("🔍 Parsing PDF...")
        reader = PyPDF2.PdfReader(uploaded_file)
        df = parse_hdfc_pdf(reader)
    elif filename.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    elif filename.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)
    else:
        st.error("Unsupported file type")
        st.stop()
    # Common processing
    if not filename.endswith('.pdf'):
        df.columns = df.columns.str.lower().str.strip()
        df.rename(columns={'date': 'date', 'description': 'description', 'amount': 'amount'}, inplace=True)
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df.dropna(subset=['date'], inplace=True)
        df['amount'] = df['amount'].astype(float)
    df['category'] = df['description'].apply(assign_category)
    df['month'] = df['date'].dt.to_period('M')
    st.success(f"✅ Parsed {len(df)} transactions.")
    st.dataframe(df)
    # -----------------------------------
    # 4️⃣ Insights & Charts
    # -----------------------------------
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📅 Monthly Spend")
        monthly = df.groupby('month')['amount'].sum()
        st.bar_chart(monthly)
    with col2:
        st.subheader("📊 Category Breakdown")
        cat_sum = df.groupby('category')['amount'].sum()
        fig, ax = plt.subplots()
        cat_sum.plot.pie(autopct='%1.1f%%', ax=ax)
        ax.set_ylabel('')
        st.pyplot(fig)
    st.subheader("🏷️ Top Vendors")
    vendor_sum = df.groupby('description')['amount'].sum().sort_values(ascending=False).head(10)
    st.dataframe(vendor_sum)
    # -----------------------------------
    # 5️⃣ Export
    # -----------------------------------
    st.subheader("⬇️ Export")
    csv = df.to_csv(index=False).encode()
    st.download_button("Download Categorized CSV", csv, "categorized_expenses.csv", "text/csv")
else:
    st.info("👆 Upload a file to get started.")
