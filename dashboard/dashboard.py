# IMPORT HERE
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import urllib
import streamlit as st
from scipy import stats
from func import DataAnalyzer, BrazilMapPlotter
from babel.numbers import format_currency
# END IMPORT

# Dataset
datetime_cols = ['order_approved_at', 'order_delivered_carrier_date', 'order_delivered_customer_date', 'order_estimated_delivery_date', 'order_purchase_timestamp', 'shipping_limit_date']
all_df = pd.read_csv('./data/merged/merged_df.csv')
all_df.sort_values(by='order_approved_at', inplace=True)
all_df.reset_index(inplace=True)

# Geological Dataset
data = pd.read_csv('dashboard/geolocation.csv')

for cols in datetime_cols:
    all_df[cols] = pd.to_datetime(all_df[cols])

min_date = all_df['order_approved_at'].min()
max_date = all_df['order_approved_at'].max()

# Sidebar
with st.sidebar:
    # Title
    st.title('Kent Cristopher')

    # Logo Image
    st.image('dashboard/logo.png')

    st.write(
        'kent.christopher03@gmail.com'
        '\nm195b4ky2175@bangkit.academy')

    # Date Range
    start_date, end_date = st.date_input(
        label='Select Date Range',
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

# Main
main_df = all_df[(all_df['order_approved_at'] >= str(start_date)) & 
                 (all_df['order_approved_at'] <= str(end_date))]

function = DataAnalyzer(main_df)
map_plot = BrazilMapPlotter(data, plt, mpimg, urllib, st)

daily_orders_df = function.create_daily_orders_df()
sum_spend_df = function.create_sum_spend_df()
sum_order_items_df = function.create_sum_order_items_df()
review_score, common_score, mean_score = function.review_score_df()
state, most_common_state = function.create_bystate_df()
order_status, common_status = function.create_order_status()

# Title
st.header('Dashboard: e-Commerce Data Analysis')

# Orders Delivered Daily
st.subheader('Orders Delivered Daily')

col1, col2 = st.columns(2)

with col1:
    total_order = daily_orders_df['order_count'].sum()
    st.markdown(f'Total Orders: **{total_order:,}**')

with col1:
    total_revenue = daily_orders_df['revenue'].sum()
    st.markdown(f'Total Revenue: **€ {total_revenue:,.2f}**')


fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(
    daily_orders_df["order_approved_at"],
    daily_orders_df["order_count"],
    marker="o",
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis="x", rotation=45)
ax.tick_params(axis="y", labelsize=15)
st.pyplot(fig)

# Customer Spending
st.subheader("Customer Spending")
col1, col2 = st.columns(2)

with col1:
    total_spend = sum_spend_df['total_spend'].sum()
    st.markdown(f"Total Spend: **€ {total_spend:,.2f}**")

with col2:
    avg_spend = sum_spend_df['total_spend'].mean()
    st.markdown(f"Average Spend: **€ {avg_spend:,.2f}**")

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(
    sum_spend_df["order_approved_at"],
    sum_spend_df["total_spend"],
    marker="o",
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis="x", rotation=45)
ax.tick_params(axis="y", labelsize=15)
st.pyplot(fig)

# Review Score
st.subheader("Review Score")
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"Average Review Score: **{mean_score:.2f}**")

with col2:
    st.markdown(f"Most Common Review Score: **{common_score}**")

total_reviews = review_score.values.sum()

fig, ax = plt.subplots(figsize=(12, 6))
colors = sns.color_palette("viridis", len(review_score))

sns.barplot(x=review_score.index,
            y=review_score.values,
            order=review_score.index,
            palette=colors)

plt.title("Customer Review Scores for Service", fontsize=15)
plt.xlabel("Rating")
plt.ylabel("Count")
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)

for i, value in enumerate(review_score.values):
    percentage = (value / total_reviews) * 100
    ax.text(i, value + 0.5, f'{percentage:.1f}%', ha='center', fontsize=12)  # Adjust position with value + 0.5

st.pyplot(fig)


# Order Items
st.subheader("Order Items")
col1, col2 = st.columns(2)

with col1:
    total_items = sum_order_items_df["product_count"].sum()
    st.markdown(f"Total Items: **{total_items}**")

with col2:
    avg_items = sum_order_items_df["product_count"].mean()
    st.markdown(f"Average Items: **{avg_items:.2f}**")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(50, 25))
colors = ["#295F98", "#CDC2A5", "#CDC2A5", "#CDC2A5", "#CDC2A5"]

sns.barplot(
    x="product_count", 
    y="product_category_name_english", 
    hue="product_category_name_english", 
    data=sum_order_items_df.head(5), 
    palette=colors, 
    ax=ax[0], 
    legend=False
)
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Sales", fontsize=80)
ax[0].set_title("Best Performing Product", loc="center", fontsize=45)
ax[0].tick_params(axis='y', labelsize=55)
ax[0].tick_params(axis='x', labelsize=50)

sns.barplot(
    x="product_count", 
    y="product_category_name_english", 
    hue="product_category_name_english", 
    data=sum_order_items_df.sort_values(by="product_count", ascending=True).head(5), 
    palette=colors, 
    ax=ax[1], 
    legend=False
)
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Sales", fontsize=80)
ax[1].invert_xaxis()  
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=45)
ax[1].tick_params(axis='y', labelsize=55)
ax[1].tick_params(axis='x', labelsize=50)

plt.suptitle("Best and Worst Performing Product by Number of Sales", fontsize=90)

st.pyplot(fig)


# Customer Geographic
st.subheader('Customer Geographic: Brazil Map')
tab1, tab2 = st.tabs(['State', 'Geolocation'])

with tab1:
    most_common_state = state.customer_state.value_counts().index[0]
    st.markdown(f"Most Common State: **{most_common_state}**")

    colors = ["#068DA9" if score == most_common_state else "#D3D3D3" for score in state.customer_state.value_counts().index]

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=state.customer_state.value_counts().index,
                y=state.customer_count.values, 
                data=state,
                palette=colors
                )

    plt.title("Number customers from State", fontsize=15)
    plt.xlabel("State")
    plt.ylabel("Number of Customers")
    plt.xticks(fontsize=12)
    st.pyplot(fig)

with tab2:
    map_plot.plot()

    with st.expander('See Explanation'):
        st.write(
    'Most of our consumer comes from south-eastern and southern Brazil while some of them scattered in other areas in middle, western and northern Brazil. This is factually correct since our most populated state \'SP\' or São Paulo is located at south-eastern Brazil. This insight could be fruitful if we increase our area of operation closer to these populated spot.'
)


