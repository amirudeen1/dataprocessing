import pandas as pd

# Load all data, conveniently placed the 7 .csv files in the same directory as my .py file
files = [
    "perSpecies_perTime_1100_1159.csv",
    "perSpecies_perTime_1200_1259.csv",
    "perSpecies_perTime_1300_1359.csv",
    "perSpecies_perTime_1400_1459.csv",
    "perSpecies_perTime_1510_1559.csv",
    "perSpecies_perTime_1600_1659.csv",
    "perSpecies_perTime_1700_1759.csv"
]

# Initialize empty df
compiled_df = pd.DataFrame()

# Processing and concatenating
for file in files:
    df = pd.read_csv(file) # Load
    df = df.drop(df.columns[:3], axis=1) # Remove first 3 columns
    compiled_df = pd.concat([compiled_df, df], axis=1) # Concatenate side by side  

# Species name (initially 2nd column) to the very first column
compound_names = pd.read_csv(files[0], usecols=[1]) # 0-indexed, 1 picks the column we want
compound_names = compound_names.squeeze() # Convert df to series, easier to work with

# Insert first col. as compound names
compiled_df.insert(0, "", compound_names)

# Add right-most col with avg 
# RHS, avg across each row, as a series
# Assigned to LHS to creat a col with the avg
# Exclude the first column (which contains compound names) when calculating the avg
# Selecting all relevant data, axis=1 to avg across each row
compiled_df["Avg"] = compiled_df.iloc[:, 1:].mean(axis=1)

# Make a filtered df which excludes rows for the following compounds
excl = ["SA", "AMMSUL", "core", "H2O", "O3"]
# ~ bitwise NOT operator, inverts the boolean of isin
# selects first col of entire df which is NOT in excl
filtered_df = compiled_df[~compiled_df.iloc[:, 0].str.strip().isin(excl)]
sums = filtered_df.iloc[:, 1:].sum() # by default sum along column axis=0

soa_row_data = ["SOA"] + list(sums) # create list, contains "SOA, sum, sum, ..."

# create new df, [soa_row_data] > list is treated as single row of data 
# column label specified with compiled_df
soa_row = pd.DataFrame([soa_row_data], columns=compiled_df.columns) 

# combine both df, for updated compiled df, axis=0, row-wise
compiled_df = pd.concat([compiled_df, soa_row], ignore_index=True) # Clean index for concat-ed df

# Sort the df by the avg column in descending order
# Separate last row first
last_row = compiled_df.iloc[[-1]]

# Sort the rest of the df
sorted_df = compiled_df.iloc[:-1].sort_values(by="Avg", ascending=False)

# Concatenate the last row back
compiled_df = pd.concat([sorted_df, last_row])

# Basic cleanup of whitespaces in compound names
compiled_df.iloc[:, 0] = compiled_df.iloc[:, 0].str.strip()

# Output the DataFrame to a CSV file
compiled_df.to_csv("Output.csv", index=False)

### This sorts all original compounds except SOA, leaving SOA
### untouched at the bottom row
