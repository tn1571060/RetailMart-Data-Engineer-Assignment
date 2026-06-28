
import pandas as pd
import numpy as np
import sqlite3

def run_pipeline():
    try:
        # Task 1: Data Ingestion
        sales_df = pd.read_csv("sales_data.csv")
        products_df = pd.read_csv("products.csv")
        stores_df = pd.read_csv("stores.csv")

        print("Sales Shape:", sales_df.shape)
        print(sales_df.head())

        print("Products Shape:", products_df.shape)
        print(products_df.head())

        print("Stores Shape:", stores_df.shape)
        print(stores_df.head())

        print("\nMissing Values Summary")
        print("Sales:\n", sales_df.isnull().sum())
        print("Products:\n", products_df.isnull().sum())
        print("Stores:\n", stores_df.isnull().sum())

        # Task 2: Data Cleaning
        duplicates = sales_df.duplicated().sum()
        sales_df = sales_df.drop_duplicates()
        print(f"\nDuplicates Removed: {duplicates}")

        sales_df["quantity"] = sales_df["quantity"].fillna(0)
        sales_df = sales_df.dropna(subset=["amount"])

        sales_df["sale_date"] = pd.to_datetime(
            sales_df["sale_date"],
            errors="coerce"
        )
        sales_df["amount"] = pd.to_numeric(
            sales_df["amount"],
            errors="coerce"
        )
        sales_df = sales_df.dropna(subset=["sale_date", "amount"])
        

        print("Cleaned Sales Shape:", sales_df.shape)

        # Task 3: Data Transformation
        final_df = sales_df.merge(products_df, on="product_id", how="left")
        final_df = final_df.merge(stores_df, on="store_id", how="left")

        final_df["total_revenue"] = final_df["quantity"] * final_df["price"]
        print("\nDATA QUALITY CHECK")

        missing_products = final_df[final_df["product_name"].isna()]
        missing_stores = final_df[final_df["store_name"].isna()]

        if missing_products.empty:
            print("No missing product information found.")
        else:
            print(missing_products)

        if missing_stores.empty:
            print("No missing store information found.")
        else:
            print(missing_stores)
        print("\nMerged DataFrame")
        print(final_df)

        print("\nRevenue Statistics")
        print("Mean:", np.mean(final_df["total_revenue"]))
        print("Max:", np.max(final_df["total_revenue"]))
        print("Min:", np.min(final_df["total_revenue"]))

        city_revenue = (
            final_df.groupby("city")["total_revenue"]
            .sum()
            .sort_values(ascending=False)
        )

        print("\nRevenue by City")
        print(city_revenue)

        # Task 4: Data Loading (SQLite)
        with sqlite3.connect("retailmart.db") as conn:

            final_df.to_sql(
            "retail_sales",
            conn,
            if_exists="replace",
            index=False
        )

        top_3_products_query = """
        SELECT
            product_name,
            SUM(quantity) AS total_quantity_sold
        FROM retail_sales
        GROUP BY product_name
        ORDER BY total_quantity_sold DESC
        LIMIT 3;
        """

        print("\nTop 3 Best-Selling Products")
        print(pd.read_sql_query(top_3_products_query, conn))

        # Task 5: Reporting & Insights
        revenue_per_store_day_query = """
        SELECT
            store_name,
            sale_date,
            SUM(total_revenue) AS revenue
        FROM retail_sales
        GROUP BY store_name, sale_date
        ORDER BY revenue DESC;
        """

        print("\nRevenue Per Store Per Day")
        print(pd.read_sql_query(revenue_per_store_day_query, conn))

        total_transactions = len(final_df)
        total_revenue = final_df["total_revenue"].sum()

        top_city = (
            final_df.groupby("city")["total_revenue"]
            .sum()
            .idxmax()
        )

        top_product = (
            final_df.groupby("product_name")["quantity"]
            .sum()
            .idxmax()
        )

        print("\n===== SUMMARY REPORT =====")
        print("Total Transactions:", total_transactions)
        print(f"Total Revenue: ₹{total_revenue:,.2f}")
        print("Top Selling City:", top_city)
        print("Top Selling Product:", top_product)
        final_df.to_csv("cleaned_retail_sales.csv", index=False)
        print("\nCleaned dataset saved as cleaned_retail_sales.csv")
        print("\nPipeline executed successfully!")

    

    except FileNotFoundError as e:
        print(f"File Error: {e}")
    except Exception as e:
        print(f"Pipeline Error: {e}")


if __name__ == "__main__":
    run_pipeline()
