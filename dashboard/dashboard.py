import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from datetime import datetime


sns.set(style='darkgrid')

main_data_df = pd.read_csv("dashboard/main_data.csv")
main_data_df['order_delivered_customer_date'] = pd.to_datetime(main_data_df['order_delivered_customer_date'], errors='coerce')

#Sidebar
st.sidebar.header("Filter by Date")
start_date = st.sidebar.date_input("Start Date", value=datetime(2018, 1, 1))
end_date = st.sidebar.date_input("End Date", value=datetime.now())

#Filter data
main_data_df = main_data_df[(main_data_df['order_delivered_customer_date'] >= pd.to_datetime(start_date)) & 
                             (main_data_df['order_delivered_customer_date'] <= pd.to_datetime(end_date))]

def plot_best_least_selling_items(data):
    st.subheader("Best and Least Selling Items")
    sum_order_items_df = data.groupby("product_category_name").order_item_id.sum().sort_values(ascending=False).reset_index()

    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 6))
    
    colors = ["#ff7f0e", "#c7c7c7", "#c7c7c7", "#c7c7c7", "#c7c7c7"] 

    sns.barplot(x="order_item_id", y="product_category_name", hue="product_category_name", 
                data=sum_order_items_df.head(5), palette=colors, ax=ax[0], legend=False)
    ax[0].set_ylabel(None)
    ax[0].set_xlabel(None)
    ax[0].set_title("Best Selling Items", loc="center", fontsize=25)
    ax[0].tick_params(axis='y', labelsize=12)

    sns.barplot(x="order_item_id", y="product_category_name", hue="product_category_name", 
                data=sum_order_items_df.sort_values(by="order_item_id", ascending=True).head(5), 
                palette=colors, ax=ax[1], legend=False)
    ax[1].set_ylabel(None)
    ax[1].set_xlabel(None)
    ax[1].invert_xaxis()
    ax[1].yaxis.set_label_position("right")
    ax[1].yaxis.tick_right()
    ax[1].set_title("Least Selling Items", loc="center", fontsize=25)
    ax[1].tick_params(axis='y', labelsize=12)

    st.pyplot(fig)

def plot_top_states(data):
    st.subheader("Top 10 States with Most Customers")
    bystate_df = data.groupby(by="customer_state").customer_id.nunique().reset_index()
    bystate_df.rename(columns={"customer_id": "customer_count"}, inplace=True)

    top_10_countries = bystate_df.sort_values(by="customer_count", ascending=False).head(10)

    plt.figure(figsize=(10, 5))
    colors_ = ["#ff7f0e"] * 10 

    sns.barplot(
        x="customer_state",
        y="customer_count",
        data=top_10_countries,
        palette=colors_,
        hue="customer_state",
        dodge=False,
        legend=False
    )

    plt.xlabel(None)
    plt.ylabel(None)
    plt.tick_params(axis='x', labelsize=12, rotation=45)

    st.pyplot(plt.gcf())
    plt.close()  

def plot_rfm(data):
    st.subheader("Best Customer Based on RFM Parameters (customer_state)")
    
    data['order_delivered_customer_date'] = pd.to_datetime(data['order_delivered_customer_date'], errors='coerce')

    rfm_df = data.groupby(by="customer_state", as_index=False).agg({
        "order_delivered_customer_date": "max",
        "order_id": "nunique",
        "payment_value": "sum"
    })
    rfm_df.columns = ["customer_state", "max_order_timestamp", "frequency", "monetary"]
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = data["order_delivered_customer_date"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)

    #RFM metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        avg_recency = round(rfm_df.recency.mean(), 1)
        st.metric("Average Recency (days)", value=avg_recency)

    with col2:
        avg_frequency = round(rfm_df.frequency.mean(), 2)
        st.metric("Average Frequency", value=avg_frequency)

    with col3:
        avg_monetary = round(rfm_df.monetary.mean(), 2)
        st.metric("Average Monetary", value=avg_monetary)

    fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 6))

    colors = ["#ff7f0e"] * 5 

    sns.barplot(y="recency", x="customer_state", data=rfm_df.sort_values(by="recency", ascending=True).head(5), 
                hue="customer_state", palette=colors, legend=False, ax=ax[0])
    ax[0].set_ylabel(None)
    ax[0].set_xlabel(None)
    ax[0].tick_params(axis='x', labelsize=15, rotation=45)

    sns.barplot(y="frequency", x="customer_state", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), 
                hue="customer_state", palette=colors, legend=False, ax=ax[1])
    ax[1].set_ylabel(None)
    ax[1].set_xlabel(None)
    ax[1].tick_params(axis='x', labelsize=15, rotation=45)

    sns.barplot(y="monetary", x="customer_state", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), 
                hue="customer_state", palette=colors, legend=False, ax=ax[2])
    ax[2].set_ylabel(None)
    ax[2].set_xlabel(None)
    ax[2].tick_params(axis='x', labelsize=15, rotation=45)

    st.pyplot(fig)

#Main
def main():
    st.markdown("<h1 style='text-align: center; font-size: 48px;'>E-Commerce Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; font-size: 20px; color: grey;'>by Kunny</h3>", unsafe_allow_html=True)

    plot_best_least_selling_items(main_data_df)
    plot_top_states(main_data_df)
    plot_rfm(main_data_df)

if __name__ == "__main__":
    main()
