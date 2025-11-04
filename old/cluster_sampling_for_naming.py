import pandas as pd
import os
import json

def generate_cluster_samples_for_naming(input_clusters_csv_path: str, output_json_path: str, sample_size: int = 50):
    """
    Reads multi-level cluster data, samples products from each cluster at each level,
    and saves the samples to a JSON file for LLM-based cluster naming.

    Args:
        input_clusters_csv_path (str): Path to the CSV file containing multi-level cluster IDs.
        output_json_path (str): Path where the JSON file with sampled products will be saved.
        sample_size (int): Number of random product names to sample from each cluster.
    """
    print(f"Reading multi-level cluster data from: {input_clusters_csv_path}")
    try:
        df = pd.read_csv(input_clusters_csv_path)
    except FileNotFoundError:
        print(f"Error: Input clusters CSV file not found at {input_clusters_csv_path}")
        return
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    # Identify cluster level columns (e.g., 'cluster_t_0.1', 'cluster_t_0.2')
    cluster_cols = [col for col in df.columns if col.startswith('cluster_t_')]

    if not cluster_cols:
        print("No cluster columns found (e.g., 'cluster_t_X'). Please ensure your input CSV is correct.")
        return

    cluster_cols.sort(key=lambda x: float(x.split('_')[2]))

    sampled_clusters_data = {}

    print("Generating samples for each cluster at each level...")
    for col in cluster_cols:
        level_name = col
        sampled_clusters_data[level_name] = []

        unique_clusters = df[col].unique()
        print(f"Processing level '{level_name}' with {len(unique_clusters)} unique clusters.")

        for cluster_id in sorted(unique_clusters):
            cluster_products = df[df[col] == cluster_id]['nome'].tolist()
            
            current_sample_size = min(sample_size, len(cluster_products))
            
            if current_sample_size > 0:
                sampled_products = pd.Series(cluster_products).sample(n=current_sample_size, random_state=42).tolist()
            else:
                sampled_products = []

            sampled_clusters_data[level_name].append({
                'cluster_id': int(cluster_id),
                'sample_products': sampled_products
            })

    print(f"Saving sampled cluster data to: {output_json_path}")
    try:
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(sampled_clusters_data, f, ensure_ascii=False, indent=4)
        print("Sampled cluster data saved successfully.")
    except Exception as e:
        print(f"Error saving sampled cluster data to JSON: {e}")

if __name__ == '__main__':
    script_dir = os.path.dirname(__file__)
    input_clusters_file = os.path.join(script_dir, 'data', 'product_clusters_multi_level.csv')
    output_samples_file = os.path.join(script_dir, 'data', 'cluster_samples_for_naming.json')

    sample_size_per_cluster = 50

    print("Starting cluster sampling script...")
    generate_cluster_samples_for_naming(input_clusters_file, output_samples_file, sample_size_per_cluster)
    print("Script finished.")
