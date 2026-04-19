import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

df = pd.read_csv("online_retail.csv", encoding='latin1')

df=df.dropna(subset=['CustomerID'])

df=df.fillna('Unknown')

df=df[df['UnitPrice']>0]

df['InvoiceDate']=pd.to_datetime(df['InvoiceDate'])

df=df.reset_index(drop=True)

df['Revenue']=df['Quantity'] * df['UnitPrice']

product_data = df.groupby('StockCode').agg({
    'Revenue': 'sum',
    'Quantity': 'sum',
    'InvoiceNo': 'nunique',
    'CustomerID': 'nunique'
}).reset_index()

product_data.columns = [
    'StockCode',
    'TotalRevenue',
    'TotalQuantity',
    'PurchaseFrequency',
    'UniqueCustomers'
]

returns = df[df['Quantity'] < 0].groupby('StockCode')['Quantity'].count()

product_data['ReturnRate'] = product_data['StockCode'].map(returns)
product_data['ReturnRate'] = product_data['ReturnRate'].fillna(0)

print(product_data.head(10))
print(product_data.shape)
print(product_data.describe())

print(df['InvoiceDate'])


sales = df[df['Quantity'] > 0]
returns_df = df[df['Quantity'] < 0]


sales_revenue = sales.groupby('StockCode')['Revenue'].sum()
return_loss = returns_df.groupby('StockCode')['Revenue'].sum()


product_data['SalesRevenue'] = product_data['StockCode'].map(sales_revenue)
product_data['ReturnLoss'] = product_data['StockCode'].map(return_loss)


product_data['SalesRevenue'] = product_data['SalesRevenue'].fillna(0)
product_data['ReturnLoss'] = product_data['ReturnLoss'].fillna(0)

product_data['NetRevenue'] = product_data['SalesRevenue'] + product_data['ReturnLoss']

x = product_data[[
    'TotalRevenue',
    'TotalQuantity',
    'PurchaseFrequency',
    'UniqueCustomers',
    'ReturnRate',
    'NetRevenue' 
]]

sc=StandardScaler()

x_scaled=sc.fit_transform(x)

inertia = []

for k in range(1, 10):
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(x_scaled)
    inertia.append(kmeans.inertia_)

plt.plot(range(1, 10), inertia, marker='o')
plt.xlabel("Number of Clusters")
plt.ylabel("Inertia")
plt.title("Elbow Method")
plt.show()

kmeans = KMeans(n_clusters=4, random_state=42)
product_data['Cluster'] = kmeans.fit_predict(x_scaled)

print(product_data.head())

cluster_summary = product_data.groupby('Cluster').mean(numeric_only=True)
print(cluster_summary)

def label_cluster(row):
    if row['Cluster'] == 0:
        return "Low Demand"
    elif row['Cluster'] == 1:
        return "Stable"
    elif row['Cluster'] == 2:
        return "Hidden Loss"
    else:
        return "Critical Loss"

product_data['Category'] = product_data.apply(label_cluster, axis=1)

print(product_data['Category'])

plt.figure()

plt.scatter(
    product_data['TotalRevenue'],
    product_data['TotalQuantity'],
    c=product_data['Cluster']
)

plt.xlabel("Total Revenue")
plt.ylabel("Total Quantity")
plt.title("Product Clusters Visualization")

plt.show()

plt.figure()

plt.scatter(
    product_data['TotalRevenue'],
    product_data['ReturnRate'],
    c=product_data['Cluster']
)

plt.xlabel("Total Revenue")
plt.ylabel("Return Rate")
plt.title("Hidden Loss Detection")

plt.show()

print(product_data['Cluster'].value_counts())

def generate_insight(row):
    if row['NetRevenue'] < 0:
        return "🚨 Loss Making Product"
    elif row['ReturnRate'] > 10 and row['NetRevenue'] < 5000:
        return "⚠️ High Return Risk"
    elif row['TotalRevenue'] < 200:
            return "📉 Low Performance"
    else:
        return "✅ Profitable Product"

product_data['Insight'] = product_data.apply(generate_insight, axis=1)

print(product_data['Insight'])

#product_data.to_csv("processed_data.csv", index=False)

