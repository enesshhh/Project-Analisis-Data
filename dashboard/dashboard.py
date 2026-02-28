import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import streamlit as st
import os
from babel.numbers import format_currency

sns.set(style='dark')

def create_df_monthly_revenue(df):
    df_monthly_revenue = df.resample('M', on='order_purchase_timestamp').agg({'order_id': 'nunique', 'price': 'sum'})
    df_monthly_revenue = df_monthly_revenue.reset_index()
    df_monthly_revenue.rename(columns={'order_id': 'order_count', 'price': 'revenue'}, inplace=True)
    return df_monthly_revenue

def create_df_sum_items(df):
    df_sum_items = df.groupby('product_category_name').price.sum().sort_values(ascending=False).reset_index()
    return df_sum_items

def create_df_delivery_rating(df):
    df_delivery_rating = df.groupby('review_score').delivery_time_days.mean().reset_index()
    return df_delivery_rating

def create_df_rfm(df):
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    df_rfm = df.groupby('customer_id', as_index=False).agg({
        'order_purchase_timestamp': 'max',
        'order_id': 'nunique',
        'price': 'sum'
    })
    df_rfm.columns = ['customer_id', 'max_order_timestamp', 'frequency', 'monetary']
    df_rfm['max_order_timestamp'] = pd.to_datetime(df_rfm['max_order_timestamp'])
    recent_date = df['order_purchase_timestamp'].max() + pd.Timedelta(days=1)
    df_rfm['recency'] = (recent_date - df_rfm['max_order_timestamp']).dt.days
    df_rfm.drop('max_order_timestamp',axis=1, inplace=True)
    return df_rfm

current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, "main_data.csv")
df_all = pd.read_csv(file_path)
df_all['order_purchase_timestamp'] = pd.to_datetime(df_all['order_purchase_timestamp'])

with st.sidebar:
    st.image('https://img.pikbest.com/png-images/ecommerce-logo-vector-graphics-element--e-commerce-logo-icon-design-online-store-logo-icon_1726010.png!w700wp', width=200)

    min_date = df_all['order_purchase_timestamp'].min()
    max_date = df_all['order_purchase_timestamp'].max()

    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    
df_main = df_all[(df_all['order_purchase_timestamp'] >= pd.to_datetime(start_date)) & 
                 (df_all['order_purchase_timestamp'] <= pd.to_datetime(end_date))]

df_monthly_revenue = create_df_monthly_revenue(df_main) 
df_sum_items = create_df_sum_items(df_main)
df_delivery_rating = create_df_delivery_rating(df_main)
df_rfm = create_df_rfm(df_main)

st.header('E-Commerce Public Dashboard')
#Monthly Revenue
st.subheader('Total Revenue')
col1, col2 = st.columns(2)
with col1:
    total_orders = df_monthly_revenue.order_count.sum()
    st.metric('Total Orders', value=total_orders)

with col2:
    total_revenue = format_currency(df_monthly_revenue.revenue.sum(), 'BRL', locale='es_CO')
    st.metric('Total Revenue', value=total_revenue)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(df_monthly_revenue['order_purchase_timestamp'], df_monthly_revenue['revenue'], marker='o', linewidth=2, color='#90CAF9')
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)
#Product Performance
st.subheader('Product Category Revenue')
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x='price', y='product_category_name', ax=ax, palette='Blues_r', data=df_sum_items.head(10))
ax.set_title('10 Product Category by Revenue', fontsize=20, loc='center')
ax.set_xlabel(None)
ax.set_ylabel(None)
ax.tick_params(axis='y', labelsize=15)
st.pyplot(fig)
#Delivery Performance Vs Review Score
st.subheader('Delivery Performance vs Review Score')
fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(x='review_score', y='delivery_time_days', ax=ax, data=df_delivery_rating, color='#90CAF9')
ax.set_title('Delivery Performance vs Review Score', fontsize=15, loc='center')
ax.set_xlabel('Review Score', fontsize=15)
ax.set_ylabel('Average Delivery Time (Days)', fontsize=15)
st.pyplot(fig)
#Best Customers on RFM Analysis
st.subheader('Best Customers on RFM Analysis')
col1, col2, col3 = st.columns(3)
with col1:
    avg_recency = round(df_rfm.recency.mean(), 1)
    st.metric('Average Recency (Days)', value=avg_recency)
with col2:
    avg_frequency = round(df_rfm.frequency.mean(), 2)
    st.metric('Average Frequency', value=avg_frequency)
with col3:
    avg_monetary = format_currency(df_rfm.monetary.mean(), 'BRL', locale='es_CO')
    st.metric('Average Monetary', value=avg_monetary)
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(20, 10))
colors = ['#90CAF9','#90CAF9','#90CAF9', '#90CAF9', '#90CAF9']

sns.barplot(y='recency', x='customer_id', data=df_rfm.sort_values(by='recency', ascending=True).head(5), ax=ax[0], palette=colors)
ax[0].set_title('By Recency (days)', fontsize=15, loc='center')
ax[0].set_xticks([])

sns.barplot(y='frequency', x='customer_id', data=df_rfm.sort_values(by='frequency', ascending=False).head(5), ax=ax[1], palette=colors)
ax[1].set_title('By Frequency', fontsize=15, loc='center')
ax[1].set_xticks([])

sns.barplot(y='monetary', x='customer_id', data=df_rfm.sort_values(by='monetary', ascending=False).head(5), ax=ax[2], palette=colors)
ax[2].set_title('By Monetary', fontsize=15, loc='center')
ax[2].set_xticks([])
st.pyplot(fig)
st.caption('E-Commerce Public Dataset - Copyright Dicoding 2026')
