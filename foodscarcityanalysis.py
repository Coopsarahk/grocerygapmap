import pandas as pd

df = pd.read_csv("boston_grocery_stores.csv")

###### Add Neighborhood info#######
df['neighborhood'] = df.apply(
    lambda row: row['address'].split(',')[-1].strip(),
    axis=1
)

df = df[~df['neighborhood'].isin(["Cambridge", "Somerville", "Chelsea", "Everett", "Medford",
                                           "Revere", "Malden", "Brookline"])]

df.loc[df['neighborhood'] == "Dorchester Center", 'neighborhood'] = "Dorchester"

####### Add population #####
data = pd.read_csv("boston_population_estimates_2025_neighborhood_level.csv")

df = df.merge(
    data[['name', 'population_b01001_001e']],
    left_on='neighborhood',
    right_on='name',
    how='left'
)

df.loc[df['neighborhood'] == "Boston", 'population_b01001_001e'] = 673000

# Count stores per neighborhood
neighborhood_counts = df.groupby('neighborhood').size().reset_index(name='store_count')

# Merge back into main dataframe
df = df.merge(neighborhood_counts, on='neighborhood', how='left')

# Calculate stores per person
df['people_per_store'] = df['population_b01001_001e'] / df['store_count']

df.to_csv("boston_grocery_stores_analysis.csv", index=False)