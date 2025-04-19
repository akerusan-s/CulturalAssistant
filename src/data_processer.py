import os
import pandas as pd


file_path = "../data/raw/"

df_list = []
for file in os.listdir(file_path):
    df_per_group = pd.read_csv(file_path + file, sep='\t')
    df_list.append(df_per_group)

pd.concat(df_list, ignore_index=True).to_csv(file_path + "goods.csv")
