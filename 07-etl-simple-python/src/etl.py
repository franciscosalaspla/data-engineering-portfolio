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
