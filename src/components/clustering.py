from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np
from src.components.clustering_analysis import *

def create_development_clusters_with_analysis(df: pd.DataFrame, n_clusters: int = 2):
                                
    features = [
        'Population_Growth_Rate_(percentage)',
        'Real_GDP_per_Capita_USD',
        'Median_Age',
        'Total_Fertility_Rate',
        'Expected_Years_of_Schooling_(years)',
        'Youth_Unemployment_Rate_percent'
    ]

    df_clean = df[features + ['Country']].copy()

    report_missing_data(df_clean, features)

    for col in features:
       df_clean[col] = df_clean[col].fillna(df_clean[col].median())

    df_clean['Real_GDP_per_Capita_USD_original'] = df_clean['Real_GDP_per_Capita_USD'].copy()
    df_clean['Real_GDP_per_Capita_USD'] = np.log1p(df_clean['Real_GDP_per_Capita_USD'])

    #Scaling
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df_clean[features])

    #Elbow Method
    fig_elbow = elbow_method_analysis(scaled_data, max_clusters=10)
    plt.show()

    #K-means #change based on elbow method
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df_clean['Cluster'] = kmeans.fit_predict(scaled_data)

    ### Analysis

    original_feature_map = {
        'Real_GDP_per_Capita_USD': 'Real_GDP_per_Capita_USD_original'
    }

    results = run_full_clustering_analysis(
        df=df_clean,
        scaled_data=scaled_data,
        kmeans_model=kmeans,
        features=features,
        n_clusters=n_clusters,
        original_feature_names=original_feature_map
    )

    # ===== STEP 7: Display visualizations =====
    results['fig_radar'].show()
    results['fig_pca'].show()
    results['fig_distributions'].show()
    
    # ===== STEP 8: Save results =====
    results['profile'].to_csv('cluster_profiles.csv')
    df_clean.to_csv('clustered_countries.csv', index=False)
    
    return df.merge(df_clean[['Country', 'Cluster']], on='Country')


def create_development_clusters_without_analysis(df: pd.DataFrame, n_clusters: int = 4):
    features = [
        'Population_Growth_Rate_(percentage)',
        'Real_GDP_per_Capita_USD',
        'Median_Age',
        'Total_Fertility_Rate',
        'Expected_Years_of_Schooling_(years)',
        'Youth_Unemployment_Rate_percent'
    ]

    df_clean = df[features + ['ISO3']].copy()

    #report_missing_data(df_clean, features)

    for col in features:
       df_clean[col] = df_clean[col].fillna(df_clean[col].median())

    #Scaling
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df_clean[features])

    #K-means #change based on elbow method
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df_clean['Cluster'] = kmeans.fit_predict(scaled_data)

    # Reorder clusters by mean Median_Age (descending) so cluster 0 is always most developed
    cluster_order = df_clean.groupby('Cluster')['Median_Age'].mean().sort_values(ascending=False).index
    cluster_mapping = {old_cluster: new_cluster for new_cluster, old_cluster in enumerate(cluster_order)}
    df_clean['Cluster'] = df_clean['Cluster'].map(cluster_mapping)

    return df.merge(df_clean[['ISO3', 'Cluster']], on='ISO3')


