import pandas as pd
    
def read_and_filter_csv(file_path):
    # Read the CSV file
    df = pd.read_csv(file_path)
    
    # Filter out columns where all values are zero
    non_zero_columns = df.loc[:, (df != 0).any(axis=0)]
    
    # Get the data types of the remaining columns
    data_types = non_zero_columns.dtypes
    
    return non_zero_columns, data_types

file_path = 'ai_task/AdvizorPro_Person_04.24.2024-1.csv'
filtered_df, data_types = read_and_filter_csv(file_path)

print("Filtered DataFrame:")
print(filtered_df.columns)

print("\nData Types of Remaining Columns:")
print(data_types)
