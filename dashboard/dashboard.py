import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# -------------------------------
# Fungsi untuk Memuat dan Memproses Data
# -------------------------------
def load_data(data):
    data['dateday'] = pd.to_datetime(data['dateday'])
    data['month_year'] = data['dateday'].dt.strftime("%b %Y")
    data['month_year_sort'] = data['dateday'].dt.to_period("M").astype(str)
    return data

# -------------------------------
# Fungsi untuk Menampilkan Grafik Overview
# -------------------------------
def plot_overview_graph(data, show_stacked):
    monthly_data = data.groupby(["month_year", "month_year_sort"]).agg({"count": "sum", "registered": "sum", "casual": "sum"}).reset_index()
    monthly_data = monthly_data.sort_values(by="month_year_sort")
    
    fig, ax = plt.subplots(figsize=(12, 6))
    if show_stacked:
        monthly_data.set_index("month_year")[['registered', 'casual']].plot(kind='bar', stacked=True, colormap='coolwarm', ax=ax)
    else:
        sns.barplot(data=monthly_data, x="month_year", y="count", color="blue", width=0.5, ax=ax)
    ax.set_title("Tren Penyewaan Sepeda Perbulan (2011-2012)")
    ax.set_xlabel("Bulan")
    ax.set_ylabel("Total Penyewaan")
    plt.xticks(rotation=45)
    st.pyplot(fig)

def plot_user_graph(data, user_type, title, color):
    user_data = data.groupby(data['dateday'].dt.to_period("M")).agg({user_type: "sum"}).reset_index()
    user_data['dateday'] = user_data['dateday'].astype(str)
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(data=user_data, x="dateday", y=user_type, color=color, ax=ax)
    ax.set_title(title)
    ax.set_xlabel("Bulan")
    ax.set_ylabel("Total Penyewaan")
    plt.xticks(rotation=45)
    st.pyplot(fig)

# -------------------------------
# Fungsi untuk Menampilkan Grafik per Jam
# -------------------------------
def plot_hourly_analysis(data, timeframe, today):
    st.header("Analisis Penyewaan Sepeda per Jam")
    show_stacked = st.sidebar.checkbox("Lihat proporsi pengguna")
    filtered_data = filter_timeframe(data, timeframe, today)
    
    hour_range = st.sidebar.slider("Pilih Rentang Jam", 0, 23, (0, 23))
    filtered_data = filtered_data[(filtered_data["hour"] >= hour_range[0]) & (filtered_data["hour"] <= hour_range[1])]
    
    hourly_data = filtered_data.groupby("hour").agg({"count": "sum", "registered": "sum", "casual": "sum"}).reset_index()
    
    fig, ax = plt.subplots(figsize=(10, 5))
    if show_stacked:
        hourly_data.set_index("hour")[['registered', 'casual']].plot(kind='bar', stacked=True, colormap='coolwarm', ax=ax)
    else:
        sns.barplot(data=hourly_data, x="hour", y="count", color="blue", ax=ax)
    
    ax.set_title("Total Penyewaan per Jam")
    ax.set_xlabel("Jam")
    ax.set_ylabel("Total Penyewaan")
    plt.xticks(rotation=0)
    st.pyplot(fig)

# -------------------------------
# Fungsi untuk Filter Rentang Waktu
# -------------------------------
def filter_timeframe(data, timeframe, today):
    if timeframe == "1 Tahun Terakhir":
        return data[data['dateday'] >= "2012-01-01"]
    elif timeframe == "6 Bulan Terakhir":
        return data[data['dateday'] >= today - pd.DateOffset(months=6)]
    elif timeframe == "1 Bulan Terakhir":
        return data[data['dateday'] >= today - pd.DateOffset(months=1)]
    elif timeframe == "1 Minggu Terakhir":
        return data[data['dateday'] >= today - pd.DateOffset(weeks=1)]
    elif timeframe == "1 Hari Terakhir":
        return data[data['dateday'] >= today - pd.DateOffset(days=1)]
    else:
        return data.copy()

# -------------------------------
# Fungsi untuk Analisis Tren Bulanan
# -------------------------------
def plot_monthly_analysis():
    st.header("Tren Penyewaan Sepeda")
    today = pd.Timestamp("2013-01-01")
    
    if timeframe == "Custom":
        col1, col2,col3,col4 = st.columns([1,1,1,1])
        with col1:
            start_month = st.selectbox("Pilih Bulan Mulai", ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
        with col2:
            start_year = st.selectbox("Pilih Tahun Mulai", [2011, 2012])
        with col3:
            end_month = st.selectbox("Pilih Bulan Akhir", ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
        with col4:
            end_year = st.selectbox("Pilih Tahun Akhir", [2011, 2012])
        
        start_date = pd.to_datetime(f"{start_year}-{start_month}-01")
        end_date = pd.to_datetime(f"{end_year}-{end_month}-01") + pd.DateOffset(months=1) - pd.DateOffset(days=1)
        filtered_data = data[(data['dateday'] >= start_date) & (data['dateday'] <= end_date)]
        
        if start_year == end_year and start_month == end_month:
            aggregate_period = "D"  # Harian jika hanya satu bulan
        else:
            aggregate_period = "M"  # Bulanan jika lebih dari satu bulan
    else:
        if timeframe == "1 Tahun Terakhir":
            filtered_data = data[(data['dateday'] >= "2012-01-01")]
            aggregate_period = "M"
        elif timeframe == "6 Bulan Terakhir":
            filtered_data = data[(data['dateday'] >= today - pd.DateOffset(months=6))]
            aggregate_period = "M"
        elif timeframe == "3 Bulan Terakhir":
            filtered_data = data[(data['dateday'] >= today - pd.DateOffset(months=3))]
            aggregate_period = "M"
        elif timeframe == "1 Bulan Terakhir":
            filtered_data = data[(data['dateday'] >= today - pd.DateOffset(months=1))]
            aggregate_period = "D"
        elif timeframe == "1 Minggu Terakhir":
            filtered_data = data[(data['dateday'] >= today - pd.DateOffset(weeks=1))]
            aggregate_period = "D"
        elif timeframe == "3 Hari Terakhir":
            filtered_data = data[(data['dateday'] >= today - pd.DateOffset(days=3))]
            aggregate_period = "D"
        else:
            filtered_data = data.copy()
            aggregate_period = "M"
    
    if aggregate_period == "M":
        grouped_data = filtered_data.groupby(filtered_data['dateday'].dt.to_period("M")).agg({"count": "sum"}).reset_index()
        grouped_data['dateday'] = grouped_data['dateday'].dt.to_timestamp()
    else:
        grouped_data = filtered_data.groupby(filtered_data['dateday'].dt.to_period("D")).agg({"count": "sum"}).reset_index()
        grouped_data['dateday'] = grouped_data['dateday'].dt.to_timestamp()
    
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(data=grouped_data, x="dateday", y="count", color = "blue", width=0.5, ax=ax)
    ax.set_title("Tren Penyewaan Sepeda")
    ax.set_xlabel("Bulan")
    ax.set_ylabel("Total Penyewaan")
    plt.xticks(rotation=45)
    st.pyplot(fig)
    
# -------------------------------
# Load Data
# -------------------------------
data = pd.read_csv("https://raw.githubusercontent.com/syafiqirz/Bike-Sharing/refs/heads/main/dashboard/sales_data.csv")
data = load_data(data)
today = pd.Timestamp("2013-01-01")

# -------------------------------
# Sidebar: Filter dan Pilihan Analisis
# -------------------------------
st.sidebar.header("Filter Data")
analysis_option = st.sidebar.radio("Pilih Analisis", ("Overview Data", "Analisis per Jam", "Tren Bulanan"))

# -------------------------------
# Header
# -------------------------------
st.header('Dashboar Penyewaan Sepeda :sparkles:')
st.caption("Last updated: 1 January 2013")
st.subheader('Total Penyewaan')

col1, col2 = st.columns(2)

with col1:
    total_sales = data["count"].sum()
    st.metric("Total Sales", value=total_sales)

with col2:
    last_30_days = data[data["dateday"] >= today - pd.DateOffset(days=30)]["count"].mean()
    prev_30_days = data[(data["dateday"] >= today - pd.DateOffset(days=60)) & (data["dateday"] < today - pd.DateOffset(days=30))]["count"].mean()
    delta_percentage = ((last_30_days - prev_30_days) / prev_30_days) * 100
    st.metric("Average Sales in Last 30 Days", value=f"{last_30_days:.0f}", delta=f"{delta_percentage:.2f}%")

# -------------------------------
# Overview Data
# -------------------------------
if analysis_option == "Overview Data":
    st.header("Overview Data")
    tab1, tab2, tab3 = st.tabs(["Tren Penjualan", "Registered Users", "Casual Users"])
    
    with tab1:
        show_stacked = st.checkbox("Lihat proporsi pengguna")
        plot_overview_graph(data, show_stacked)
    
    with tab2:
        plot_user_graph(data, "registered", "Tren Pengguna Registered Perbulan", "blue")
    
    with tab3:
        plot_user_graph(data, "casual", "Tren Pengguna Casual Perbulan", "red")

# -------------------------------
# Analisis per Jam dengan Opsi Proporsi User
# -------------------------------
if analysis_option == "Analisis per Jam":
    timeframe = st.sidebar.selectbox("Pilih Rentang Waktu", ["Keseluruhan", "1 Tahun Terakhir", "6 Bulan Terakhir", "1 Bulan Terakhir", "1 Minggu Terakhir", "1 Hari Terakhir"])
    plot_hourly_analysis(data, timeframe, today)
    
# -------------------------------
# Analisis Tren Bulanan
# -------------------------------
if analysis_option == "Tren Bulanan":
    timeframe = st.sidebar.selectbox("Pilih Rentang Waktu", ["Keseluruhan", "1 Tahun Terakhir", "6 Bulan Terakhir", "3 Bulan Terakhir", "1 Bulan Terakhir", "1 Minggu Terakhir", "3 Hari Terakhir", "Custom"])
    plot_monthly_analysis()

st.markdown("---")
st.caption("**Developed by Muhammad Syafiq Irzaky | Contact: syafiqirzaky@gmail.com | GitHub: (https://github.com/syafiqirz)**")
