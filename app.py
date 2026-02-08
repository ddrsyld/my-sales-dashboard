import streamlit as st
import pandas as pd
import plotly.express as px

# Konfigurasi Halaman
st.set_page_config(page_title="Sales Dashboard", layout="wide")

# Fungsi untuk memuat data
@st.cache_data
def load_data(file):
    df = pd.read_csv(file)
    # Konversi kolom tanggal
    df['Transaction Date'] = pd.to_datetime(df['Transaction Date'])
    return df

# Judul Utama
st.title("📊 Business Sales Dashboard")
st.markdown("Dashboard ini menganalisis tren penjualan dan performa item berdasarkan data transaksi.")

# Sidebar - Upload & Filter
st.sidebar.header("Konfigurasi & Filter")
uploaded_file = st.sidebar.file_uploader("Upload CSV Anda", type=["csv"])

# Gunakan file yang diupload atau default dataset.csv
target_file = uploaded_file if uploaded_file is not None else "archive/dataset.csv"

try:
    df = load_data(target_file)

    # --- SIDEBAR FILTER ---
    # Filter Rentang Tanggal
    min_date = df['Transaction Date'].min()
    max_date = df['Transaction Date'].max()
    date_range = st.sidebar.date_input("Pilih Rentang Tanggal", [min_date, max_date])

    # Filter Item
    items = df['Item'].unique().tolist()
    selected_items = st.sidebar.multiselect("Pilih Item", items, default=items)

    # Apply Filter ke Dataframe
    if len(date_range) == 2:
        start_date, end_date = date_range
        mask = (df['Transaction Date'].dt.date >= start_date) & \
               (df['Transaction Date'].dt.date <= end_date) & \
               (df['Item'].isin(selected_items))
        df_filtered = df.loc[mask]
    else:
        df_filtered = df[df['Item'].isin(selected_items)]

    # --- MAIN KPI METRICS ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Revenue", f"${df_filtered['Total Spent'].sum():,.2f}")
    with col2:
        st.metric("Total Items Sold", int(df_filtered['Quantity'].sum()))
    with col3:
        st.metric("Avg. Transaction", f"${df_filtered['Total Spent'].mean():,.2f}")
    with col4:
        st.metric("Total Transactions", len(df_filtered))

    # --- DATA PREVIEW & STATS ---
    with st.expander("🔍 Lihat Detail Data & Statistik Deskriptif"):
        col_table, col_stats = st.columns(2)
        with col_table:
            st.write("**Preview Data (Top 10)**")
            st.dataframe(df_filtered.head(10), use_container_width=True)
        with col_stats:
            st.write("**Statistik Deskriptif**")
            st.dataframe(df_filtered.describe(), use_container_width=True)

    st.divider()

    # --- VISUALISASI ---
    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:
        # Bar Chart: Sales per Item
        st.subheader("Total Sales per Item")
        fig_bar = px.bar(
            df_filtered.groupby('Item')['Total Spent'].sum().reset_index().sort_values('Total Spent', ascending=False),
            x='Item', y='Total Spent',
            color='Item',
            text_auto='.2s',
            template="plotly_white"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with row1_col2:
        # Pie Chart: Quantity Distribution
        st.subheader("Item Quantity Distribution")
        fig_pie = px.pie(
            df_filtered, values='Quantity', names='Item',
            hole=0.4,
            template="plotly_white"
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # Line Chart: Trend Penjualan Harian
    st.subheader("Daily Sales Trend")
    daily_sales = df_filtered.groupby('Transaction Date')['Total Spent'].sum().reset_index()
    fig_line = px.line(
        daily_sales, x='Transaction Date', y='Total Spent',
        labels={'Total Spent': 'Revenue ($)'},
        template="plotly_white"
    )
    st.plotly_chart(fig_line, use_container_width=True)

except Exception as e:
    st.error(f"Terjadi kesalahan: {e}")
    st.info("Pastikan file 'dataset.csv' tersedia di direktori yang sama atau upload file melalui sidebar.")
