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

def peak_season():
    data['dateday'] = pd.to_datetime(data['dateday'])
    order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    monthly_sales_df = data.groupby(by='month').agg({
        "count":"sum"
    }).reset_index()
    monthly_sales_df['month'] = pd.Categorical(monthly_sales_df['month'], categories=order, ordered=True)
    monthly_sales_df = monthly_sales_df.sort_values('month').reset_index(drop=True)

    monthly_sales_df['pct_change'] = monthly_sales_df['count'].pct_change() * 100

    spike_threshold = 20  
    drop_threshold = -15   
    # Identifikasi bulan dengan lonjakan signifikan
    spike_months = monthly_sales_df[monthly_sales_df['pct_change'] >= spike_threshold]['month'].tolist()
    drop_months = monthly_sales_df[monthly_sales_df['pct_change'] <= drop_threshold]['month'].tolist()

    # Tentukan awal dan akhir peak season
    if spike_months and drop_months:
        start_peak = spike_months[0]  # Bulan pertama dengan kenaikan signifikan
        end_peak = drop_months[0]     # Bulan pertama dengan penurunan signifikan setelah puncak
        
        # Ambil semua bulan antara start_peak dan end_peak
        peak_season_months = monthly_sales_df[(monthly_sales_df['month'] >= start_peak) & (monthly_sales_df['month'] <= end_peak)]['month'].tolist()
        
        pct_start_peak = monthly_sales_df.loc[monthly_sales_df['month'] == peak_season_months[0], 'pct_change'].values[0]
        pct_end_peak = monthly_sales_df.loc[monthly_sales_df['month'] == peak_season_months[-1], 'pct_change'].values[0]
        
        peak_dict = {
            "start_month":start_peak,
            "end_month":end_peak,
            "start_pct":pct_start_peak,
            "end_pct" : pct_end_peak
        }
    else:
        peak_season_months = []
        peak_dict = [] 
    
    return monthly_sales_df, peak_season_months, peak_dict, spike_months, drop_months


def plot_peak_season(monthly_sales_df, spike_months, drop_months):
    # Visualisasi
    fig = plt.figure(figsize=(10, 5))
    plt.plot(monthly_sales_df['month'], monthly_sales_df['count'], marker='o', label='Penjualan')
    plt.scatter(spike_months, monthly_sales_df[monthly_sales_df['month'].isin(spike_months)]['count'], color='red', label='Lonjakan (Awal Peak)')
    plt.scatter(drop_months, monthly_sales_df[monthly_sales_df['month'].isin(drop_months)]['count'], color='green', label='Penurunan (Akhir Peak)')
    plt.fill_between(monthly_sales_df['month'], monthly_sales_df['count'], where=(monthly_sales_df['month'].isin(peak_season_months)), color='orange', alpha=0.3, label='Peak Season')
    plt.title('Identifikasi Peak Season Berdasarkan Lonjakan Signifikan')
    plt.xlabel('Bulan')
    plt.ylabel('Jumlah Penjualan')
    plt.legend()
    plt.grid(True)
    st.pyplot(fig)
    # st.write(f"Bulan Peak Season: {peak_season_months[0]} - {peak_season_months[-1]}")
    
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
data = pd.read_csv("../sales_data.csv")
data = load_data(data)
today = pd.Timestamp("2013-01-01")

# -------------------------------
# Sidebar: Filter dan Pilihan Analisis
# -------------------------------
st.sidebar.header("Filter Data")
analysis_option = st.sidebar.radio("Pilih Analisis", ("Overview Data", "Analisis per Jam", "Tren Bulanan", "Peak Season"))

# -------------------------------
# Header
# -------------------------------
st.header('Dashboard Penyewaan Sepeda :sparkles:')
st.caption("Last updated: 1 January 2013")

# -------------------------------
# Overview Data
# -------------------------------
if analysis_option == "Overview Data":
    st.header("Overview Data")
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

# -------------------------------
# Analisis Peak Season
# -------------------------------
if analysis_option == "Peak Season":
    monthly_sales_df, peak_season_months, peak_dict, spike_months, drop_months = peak_season()
    if(peak_season_months): 
        start_month = peak_dict["start_month"]
        end_month = peak_dict["end_month"]
        start_pct = peak_dict["start_pct"]
        end_pct = peak_dict["end_pct"]
        
        st.subheader(f"Peak Season terjadi antara bulan {start_month} hingga {end_month}*")
        st.write("*Data yang ditampilkan telah diolah. Hasil grafik ini menunjukkan pola peak season yang terjadi selama 2011-2012")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Start Peak", value=start_month, delta=f"{start_pct:.2f}%")
        with col2:
            st.metric("End Peak", value=end_month, delta=f"{end_pct:.2f}%")
        
    plot_peak_season(monthly_sales_df, spike_months, drop_months)
    
st.markdown("---")
st.caption("**Developed by Muhammad Syafiq Irzaky | Contact: syafiqirzaky@gmail.com | GitHub: (https://github.com/syafiqirz)**")
