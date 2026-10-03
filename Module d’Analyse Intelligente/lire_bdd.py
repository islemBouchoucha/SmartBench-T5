import sqlite3
import pandas as pd

# Connexion à la base SQLite
conn = sqlite3.connect("base_production.db")

# Lecture de la table sous forme de tableau Pandas
df_historique = pd.read_sql_query("SELECT * FROM Historique_Tests", conn)

conn.close()

print("==================================================")
print("📊 HISTORIQUE DES TESTS EN BASE DE DONNÉES")
print("==================================================")
print(df_historique)