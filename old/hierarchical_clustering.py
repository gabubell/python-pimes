import pandas as pd
import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster
import os
import ast 

def perform_hierarchical_clustering_multi_level(input_embeddings_csv_path: str, output_clusters_csv_path: str, thresholds: list[float]):
    """
    Performs hierarchical clustering on product embeddings and generates multiple levels of flat clusters.

    Args:
        input_embeddings_csv_path (str): Path to the CSV file containing product names and embeddings.
        output_clusters_csv_path (str): Path where the output CSV with product names and multi-level cluster IDs will be saved.
        thresholds (list[float]): A list of dissimilarity thresholds to cut the dendrogram.
                                  Each threshold generates a different level of clustering.
    """
    print(f"Reading embeddings from: {input_embeddings_csv_path}")
    try:
        df = pd.read_csv(input_embeddings_csv_path)
    except FileNotFoundError:
        print(f"Error: Input embeddings CSV file not found at {input_embeddings_csv_path}")
        return
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    if 'nome' not in df.columns or 'embedding' not in df.columns:
        print("Error: Input CSV must contain 'nome' and 'embedding' columns.")
        return

    embeddings = np.array([ast.literal_eval(e) for e in df['embedding']])

    print(f"Loaded {len(embeddings)} embeddings. Performing hierarchical clustering with {len(thresholds)} levels...")

    Z = linkage(embeddings, method='complete', metric='cosine')

    output_df = pd.DataFrame({'nome': df['nome']})

    sort_columns = []
    for i, t in enumerate(sorted(thresholds, reverse=True)):
        # Cut the dendrogram to form flat clusters for each threshold
        clusters = fcluster(Z, t=t, criterion='distance')
        col_name = f'cluster_t_{t}'
        output_df[col_name] = clusters
        sort_columns.append(col_name)
        print(f"Generated {len(np.unique(clusters))} clusters for threshold={t}.")

    output_df = output_df.sort_values(by=sort_columns).reset_index(drop=True)

    try:
        output_df.to_csv(output_clusters_csv_path, index=False)
        print("Multi-level clustering completed and results saved successfully.")
    except Exception as e:
        print(f"Error saving clusters to CSV: {e}")

if __name__ == '__main__':
    script_dir = os.path.dirname(__file__)
    input_embeddings_file = os.path.join(script_dir, 'data', 'product_embeddings.csv')
    output_clusters_file = os.path.join(script_dir, 'data', 'product_clusters_multi_level.csv')

    # Define a list of thresholds to generate different levels of clustering.
    clustering_thresholds = [0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.99, 1]

    print("Starting multi-level hierarchical clustering script...")
    perform_hierarchical_clustering_multi_level(input_embeddings_file, output_clusters_file, clustering_thresholds)
    print("Script finished.")