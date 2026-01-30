"""
Clustering interpretation and validation tools for development clusters.
FIXED VERSION - Minimal patch: fixes only issues flagged as wrong in review.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt


def validate_clustering(df: pd.DataFrame, scaled_data: np.ndarray, kmeans_model, features: list) -> dict:
    """
    Compute multiple validation metrics for clustering quality.
    """
    silhouette = silhouette_score(scaled_data, kmeans_model.labels_)
    davies_bouldin = davies_bouldin_score(scaled_data, kmeans_model.labels_)
    calinski = calinski_harabasz_score(scaled_data, kmeans_model.labels_)

    metrics = {
        'silhouette_score': silhouette,
        'davies_bouldin_index': davies_bouldin,
        'calinski_harabasz_index': calinski
    }

    print(f"✅ Silhouette Score: {silhouette:.3f}")
    print(f"   → Interpretation: Average similarity within vs between clusters")
    print(f"   → Note: Development data often shows gradual transitions between clusters")
    print(f"   → Your score indicates: {'distinct clusters' if silhouette > 0.5 else 'overlapping/transitional groups'}")
    print(f"   → Benchmark: >0.5 (distinct), >0.7 (very distinct). You have: {'✅ Distinct' if silhouette > 0.5 else '⚠️ Overlapping'}")
    print()
    print(f"✅ Davies-Bouldin Index: {davies_bouldin:.3f}")
    print(f"   → Interpretation: Ratio of within to between cluster distances")
    print(f"   → Benchmark: <1.0 (good separation), <0.5 (excellent). You have: {'✅ Good' if davies_bouldin < 1.0 else '⚠️ Weak'}")
    print()
    print(f"✅ Calinski-Harabasz Index: {calinski:.1f}")
    print(f"   → Interpretation: Ratio of between to within cluster variances")
    print(f"   → Benchmark: >30 (reasonable), >50 (good). You have: {'✅ Good' if calinski > 30 else '⚠️ Weak'}")

    return metrics


def cluster_profile_table(df: pd.DataFrame, features: list, original_feature_names: dict = None) -> pd.DataFrame:
    """
    Create a detailed cluster profile showing mean values per cluster.
    Uses ORIGINAL (untransformed) values for interpretability.
    """
    features_to_use = features.copy()
    if original_feature_names:
        features_to_use = [original_feature_names.get(f, f) for f in features]

    profile = df.groupby('Cluster')[features_to_use].agg(['mean', 'std', 'min', 'max'])

    print("\n📊 CLUSTER PROFILES (Mean ± Std) - Original Scale:")
    print("=" * 100)

    for cluster in sorted(df['Cluster'].unique()):
        print(f"\n🎯 CLUSTER {cluster}:")
        cluster_data = df[df['Cluster'] == cluster]
        print(f"   Countries: {len(cluster_data)} ({len(cluster_data)/len(df)*100:.1f}%)")

        if 'Country' in df.columns:
            print(f"   Examples: {', '.join(cluster_data['Country'].head(3).tolist())}")
        print()

        for feature in features_to_use:
            mean_val = cluster_data[feature].mean()
            std_val = cluster_data[feature].std()

            if 'GDP' in feature or 'gdp' in feature:
                print(f"   {feature}: ${mean_val:,.0f} ± ${std_val:,.0f}")
            else:
                print(f"   {feature}: {mean_val:.2f} ± {std_val:.2f}")

    return profile


def report_missing_data(df: pd.DataFrame, features: list):
    """
    Report missing data that was imputed during preprocessing.
    """
    missing_summary = df[features].isnull().sum()

    if missing_summary.any():
        print("\n⚠️ MISSING DATA IMPUTED (filled with median):")
        print("=" * 60)
        for feature, count in missing_summary[missing_summary > 0].items():
            pct = (count / len(df)) * 100
            print(f"   {feature}: {count} values ({pct:.1f}%)")
        print()
    else:
        print("\n✅ No missing data detected.\n")


def plot_cluster_radar(df: pd.DataFrame, features: list, n_clusters: int):
    """
    Create a radar chart comparing cluster profiles across all features.
    """
    cluster_summary = df.groupby('Cluster')[features].mean()

    for col in features:
        col_min = cluster_summary[col].min()
        col_max = cluster_summary[col].max()
        if col_max - col_min > 0:
            cluster_summary[col] = (cluster_summary[col] - col_min) / (col_max - col_min)

    fig = go.Figure()
    colors = px.colors.qualitative.Plotly[:n_clusters]

    for cluster_id in sorted(df['Cluster'].unique()):
        values = cluster_summary.loc[cluster_id].tolist()
        values += values[:1]

        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=features + [features[0]],
            fill='toself',
            name=f'Cluster {cluster_id}',
            line_color=colors[cluster_id % len(colors)]
        ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        title='Cluster Profiles (Radar Chart) - Normalized Scale',
        hovermode='closest',
        height=600
    )
    return fig


def plot_pca_clusters(df: pd.DataFrame, scaled_data: np.ndarray):
    """
    Project high-dimensional clustering into 2D PCA space for visualization.
    FIX: Force categorical clusters and remove continuous colorscale.
    """
    pca = PCA(n_components=2)
    pca_data = pca.fit_transform(scaled_data)

    df_pca = pd.DataFrame(pca_data, columns=['PC1', 'PC2'])

    # --- FIX 1: Force categorical cluster labels for plotting ---
    df_pca['Cluster'] = df['Cluster'].astype(str).values

    if 'Country' in df.columns:
        df_pca['Country'] = df['Country'].values

    total_variance = pca.explained_variance_ratio_.sum()
    variance_warning = " ⚠️ Low variance - consider 3D view" if total_variance < 0.7 else ""

    # --- FIX 2: Remove color_continuous_scale (categorical coloring) ---
    fig = px.scatter(
        df_pca,
        x='PC1',
        y='PC2',
        color='Cluster',
        hover_name='Country' if 'Country' in df_pca.columns else None,
        title=f'Cluster Separation (PCA) - Explained Variance: {total_variance:.1%}{variance_warning}',
        labels={'PC1': f'PC1 ({pca.explained_variance_ratio_[0]:.1%})',
                'PC2': f'PC2 ({pca.explained_variance_ratio_[1]:.1%})'},
        category_orders={'Cluster': [str(x) for x in sorted(df['Cluster'].unique())]}
    )

    fig.update_traces(marker_size=8)
    fig.update_layout(height=600)

    print(f"\n📊 PCA Variance Explained:")
    print(f"   PC1: {pca.explained_variance_ratio_[0]:.1%}")
    print(f"   PC2: {pca.explained_variance_ratio_[1]:.1%}")
    print(f"   Total (2D): {total_variance:.1%}")
    if total_variance < 0.7:
        print(f"   ⚠️ Warning: Only {total_variance:.1%} of variance captured in 2D")
        print(f"   → Cluster separation in this plot may not reflect true separation")
    print()

    return fig, pca


def plot_feature_distributions(df: pd.DataFrame, features: list, n_clusters: int):
    """
    Box plots showing feature distributions per cluster.
    Creates subplots for better readability.
    """
    fig = make_subplots(
        rows=len(features),
        cols=1,
        subplot_titles=features,
        vertical_spacing=0.05
    )

    colors = px.colors.qualitative.Plotly[:n_clusters]

    for i, feature in enumerate(features, start=1):
        for cluster_id in sorted(df['Cluster'].unique()):
            cluster_data = df[df['Cluster'] == cluster_id][feature].dropna()

            fig.add_trace(
                go.Box(
                    y=cluster_data,
                    name=f'C{cluster_id}',
                    marker_color=colors[cluster_id % len(colors)],
                    boxmean='sd',
                    legendgroup=f'C{cluster_id}',
                    showlegend=(i == 1)
                ),
                row=i,
                col=1
            )

    fig.update_layout(
        title='Feature Distributions by Cluster (Box Plots)',
        boxmode='group',
        height=300 * len(features),
        hovermode='closest',
        showlegend=True
    )

    for i, _feature in enumerate(features, start=1):
        fig.update_yaxes(title_text="Value", row=i, col=1)

    return fig


def elbow_method_analysis(scaled_data: np.ndarray, max_clusters: int = 10):
    """
    Compute inertia and silhouette scores for different cluster counts.
    """
    inertias = []
    silhouette_scores = []
    K_range = range(2, max_clusters + 1)

    print(f"\n🔍 Testing K from 2 to {max_clusters}...")

    for k in K_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(scaled_data)
        inertias.append(kmeans.inertia_)
        silhouette_scores.append(silhouette_score(scaled_data, kmeans.labels_))
        print(f"   K={k}: Inertia={kmeans.inertia_:.1f}, Silhouette={silhouette_scores[-1]:.3f}")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    ax1.plot(K_range, inertias, 'bo-', linewidth=2, markersize=8)
    ax1.set_xlabel('Number of Clusters (K)', fontsize=12)
    ax1.set_ylabel('Inertia (Within-cluster sum of squares)', fontsize=12)
    ax1.set_title('Elbow Method - Find Optimal K', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(K_range)

    ax2.plot(K_range, silhouette_scores, 'ro-', linewidth=2, markersize=8)
    ax2.axhline(y=0.5, color='green', linestyle='--', alpha=0.5, label='Good threshold (0.5)')
    ax2.set_xlabel('Number of Clusters (K)', fontsize=12)
    ax2.set_ylabel('Silhouette Score', fontsize=12)
    ax2.set_title('Silhouette Score by K (Higher = Better)', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.set_xticks(K_range)
    ax2.legend()

    plt.tight_layout()

    best_silhouette_k = K_range[np.argmax(silhouette_scores)]
    print(f"\n💡 Suggestion: K={best_silhouette_k} has highest silhouette score ({max(silhouette_scores):.3f})")
    print(f"   Look for an 'elbow' in the inertia plot where the curve bends")
    print()

    return fig


def cluster_country_listing(df: pd.DataFrame):
    """
    Print countries grouped by cluster for manual inspection.
    """
    if 'Country' not in df.columns:
        print("\n⚠️ No 'Country' column found in DataFrame")
        return

    print("\n" + "=" * 80)
    print("🌍 COUNTRY LISTING BY CLUSTER")
    print("=" * 80)

    for cluster_id in sorted(df['Cluster'].unique()):
        countries = df[df['Cluster'] == cluster_id].sort_values('Country')['Country'].tolist()
        print(f"\n🎯 CLUSTER {cluster_id} ({len(countries)} countries):")
        for i in range(0, len(countries), 3):
            row_countries = countries[i:i + 3]
            print("   " + " | ".join(f"{c:25s}" for c in row_countries))


def analyze_cluster_stability(df: pd.DataFrame, scaled_data: np.ndarray, n_clusters: int, n_iterations: int = 10):
    """
    Assess cluster stability through subsampling (FIXED).
    FIX: Compare clusterings on the SAME subset only (no broken mapping with duplicates).
    """
    from sklearn.metrics import adjusted_rand_score

    print(f"\n🔄 Testing cluster stability with {n_iterations} subsamples...")

    original_labels = df['Cluster'].values
    rand_scores = []

    rng = np.random.default_rng(42)

    for i in range(n_iterations):
        # --- FIX: subsample WITHOUT replacement (e.g., 80%) ---
        subset_size = int(0.8 * len(scaled_data))
        subset_idx = rng.choice(len(scaled_data), size=subset_size, replace=False)

        subset_data = scaled_data[subset_idx]

        kmeans_sub = KMeans(n_clusters=n_clusters, random_state=42 + i, n_init=10)
        subset_labels = kmeans_sub.fit_predict(subset_data)

        # --- FIX: compare only on subset (ARI is permutation-invariant) ---
        rand_score = adjusted_rand_score(original_labels[subset_idx], subset_labels)
        rand_scores.append(rand_score)

    mean_stability = float(np.mean(rand_scores))
    std_stability = float(np.std(rand_scores))

    print(f"\n📊 Stability Results:")
    print(f"   Mean Adjusted Rand Index: {mean_stability:.3f} ± {std_stability:.3f}")
    print(f"   → Interpretation: Similarity between original and subsample clusterings (on same rows)")
    print(f"   → Benchmark: >0.7 (stable), >0.85 (very stable)")
    print(f"   → Your clusters are: {'✅ Stable' if mean_stability > 0.7 else '⚠️ Unstable'}")

    return {
        'mean_stability': mean_stability,
        'std_stability': std_stability,
        'rand_scores': rand_scores
    }


def run_full_clustering_analysis(df: pd.DataFrame, scaled_data: np.ndarray, kmeans_model,
                                 features: list, n_clusters: int,
                                 original_feature_names: dict = None):
    """
    Run complete clustering interpretation and validation pipeline.
    """
    print("\n" + "=" * 80)
    print("🎯 COMPREHENSIVE CLUSTERING ANALYSIS")
    print("=" * 80)

    results = {}

    print("\n" + "=" * 80)
    print("📊 STEP 1: VALIDATION METRICS")
    print("=" * 80)
    results['metrics'] = validate_clustering(df, scaled_data, kmeans_model, features)

    print("\n" + "=" * 80)
    print("📊 STEP 2: DATA QUALITY CHECK")
    print("=" * 80)
    features_to_check = [original_feature_names.get(f, f) for f in features] if original_feature_names else features
    report_missing_data(df, features_to_check)

    print("\n" + "=" * 80)
    print("📊 STEP 3: CLUSTER PROFILES")
    print("=" * 80)
    results['profile'] = cluster_profile_table(df, features, original_feature_names)

    print("\n" + "=" * 80)
    print("📊 STEP 4: COUNTRY ASSIGNMENTS")
    print("=" * 80)
    cluster_country_listing(df)

    print("\n" + "=" * 80)
    print("📊 STEP 5: STABILITY ANALYSIS")
    print("=" * 80)
    results['stability'] = analyze_cluster_stability(df, scaled_data, n_clusters)

    print("\n" + "=" * 80)
    print("📊 STEP 6: VISUALIZATIONS")
    print("=" * 80)
    print("Creating plots...")

    results['fig_radar'] = plot_cluster_radar(df, features, n_clusters)
    results['fig_pca'], results['pca'] = plot_pca_clusters(df, scaled_data)
    results['fig_distributions'] = plot_feature_distributions(df, features, n_clusters)

    print("✅ All visualizations created!")
    print("\n" + "=" * 80)
    print("🎉 ANALYSIS COMPLETE!")
    print("=" * 80)

    return results


# ============ USAGE EXAMPLE ============

if __name__ == "__main__":
    """
    Minimal fix in the example preprocessing:
    FIX: Use log1p instead of log to avoid -inf when GDP can be 0.
    """
    # Example (uncomment and adapt to your project):
    #
    # df = load_data_into_df()
    # features = [...]
    # df_clean = df[features + ['Country']].copy()
    # report_missing_data(df_clean, features)
    # for col in features:
    #     df_clean[col] = df_clean[col].fillna(df_clean[col].median())
    # df_clean['Real_GDP_per_Capita_USD_original'] = df_clean['Real_GDP_per_Capita_USD'].copy()
    #
    # # --- FIX: safer log transform ---
    # df_clean['Real_GDP_per_Capita_USD'] = np.log1p(df_clean['Real_GDP_per_Capita_USD'])
    #
    # scaler = StandardScaler()
    # scaled_data = scaler.fit_transform(df_clean[features])
    # n_clusters = 4
    # kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    # df_clean['Cluster'] = kmeans.fit_predict(scaled_data)
    #
    # original_feature_map = {'Real_GDP_per_Capita_USD': 'Real_GDP_per_Capita_USD_original'}
    # results = run_full_clustering_analysis(df_clean, scaled_data, kmeans, features, n_clusters, original_feature_map)
    #
    # results['fig_radar'].show()
    # results['fig_pca'].show()
    # results['fig_distributions'].show()
    pass