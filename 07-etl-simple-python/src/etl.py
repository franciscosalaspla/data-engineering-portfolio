import pandas as pd

# 1. Cargar el dataset
df = pd.read_csv("data/raw/ecommerce_orders.csv")

# 2. Ver primeras filas
print("Primeras filas:")
print(df.head())

# 3. Ver tamaño del dataset
print("\nFilas y columnas:")
print(df.shape)

# 4. Ver tipos de datos
print("\nInformación del dataset:")
print(df.info())

# 5. Ver valores nulos
print("\nValores nulos por columna:")
print(df.isnull().sum())

# 6. Ver duplicados
print("\nDuplicados:")
print(df.duplicated().sum())

# 7. Manejar valores nulos

# Eliminar filas sin customer_id porque no se puede asociar la venta a un cliente
df = df.dropna(subset=["customer_id"])

# Rellenar unit_price nulo con el promedio de precio por categoría
df["unit_price"] = df["unit_price"].fillna(
    df.groupby("category")["unit_price"].transform("mean")
)

# Convertir order_date a fecha
df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")

# Rellenar fechas nulas con una fecha controlada
df["order_date"] = df["order_date"].fillna(pd.Timestamp("1900-01-01"))

print("\nValores nulos después de la limpieza:")
print(df.isnull().sum())


# 8. Eliminar duplicados

print("\nFilas antes de eliminar duplicados:")
print(df.shape[0])

df = df.drop_duplicates()

print("\nFilas después de eliminar duplicados:")
print(df.shape[0])

print("\nDuplicados después de la limpieza:")
print(df.duplicated().sum())

# 9. Revisar tipos de datos después de la limpieza

print("\nTipos de datos después de la limpieza:")
df.info()

# 10. Crear métrica de venta total

df["total_sales"] = df["quantity"] * df["unit_price"]

print("\nDataset con columna total_sales:")
print(df[["order_id", "customer_id", "product", "quantity", "unit_price", "total_sales"]].head())


# 11. Top clientes por gasto

top_customers = (
    df.groupby("customer_id")["total_sales"]
    .sum()
    .reset_index()
    .sort_values("total_sales", ascending=False)
)

print("\nTop clientes por gasto:")
print(top_customers)


# 12. Producto más vendido por cantidad

top_products = (
    df.groupby("product")["quantity"]
    .sum()
    .reset_index()
    .sort_values("quantity", ascending=False)
)

print("\nProductos más vendidos:")
print(top_products)


# 13. Ventas por mes

df_valid_dates = df[df["order_date"] != pd.Timestamp("1900-01-01")]

df_valid_dates["order_month"] = df_valid_dates["order_date"].dt.to_period("M").astype(str)

sales_by_month = (
    df_valid_dates.groupby("order_month")["total_sales"]
    .sum()
    .reset_index()
    .sort_values("order_month")
)

print("\nVentas por mes:")
print(sales_by_month)

# 14. Guardar outputs

df.to_csv("output/clean_orders.csv", index=False)
df.to_parquet("output/clean_orders.parquet", index=False)

top_customers.to_csv("output/top_customers.csv", index=False)
top_products.to_csv("output/top_products.csv", index=False)
sales_by_month.to_csv("output/sales_by_month.csv", index=False)

print("\nArchivos guardados correctamente en la carpeta output/")
