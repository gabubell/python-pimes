import pandas as pd
import numpy as np
from src.embedding_utils import generate_embedding
from src.text_cleaner import clean_text
import os

def generate_product_embeddings(input_csv_path: str, output_csv_path: str, product_name_column: str):
    """
    Reads product names from an input CSV, generates embeddings for each, and saves
    the product name and its embedding to an output CSV.

    Args:
        input_csv_path: Path to the input CSV file containing product names.
        output_csv_path: Path where the output CSV with embeddings will be saved.
        product_name_column: The name of the column in the input CSV containing product names.
    """
    print(f"Reading product data from: {input_csv_path}")
    try:
        df = pd.read_csv(input_csv_path)
    except FileNotFoundError:
        print(f"Error: Input CSV file not found at {input_csv_path}")
        return
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    if product_name_column not in df.columns:
        print(f"Error: Column '{product_name_column}' not found in the input CSV.")
        return

    embeddings_data = []
    total_products = len(df)
    print(f"Generating embeddings for {total_products} products...")

    for index, row in df.iterrows():
        original_product_name = str(row[product_name_column])
        cleaned_product_name = clean_text(original_product_name)

        words = cleaned_product_name.split()
        if len(words) > 0:
            # Take the first 2 words and repeat them 3 times
            emphasized_part = " ".join(words[:2])
            processed_text_for_embedding = f"{emphasized_part} {emphasized_part} {emphasized_part} {cleaned_product_name}"
        else:
            processed_text_for_embedding = cleaned_product_name

        embedding = generate_embedding(processed_text_for_embedding)
        embeddings_data.append({
            'nome': original_product_name,
            'cleaned_nome': cleaned_product_name,
            'processed_for_embedding': processed_text_for_embedding,
            'embedding': embedding.tolist()
        })
        if (index + 1) % 100 == 0 or (index + 1) == total_products:
            print(f"Processed {index + 1}/{total_products} products.")

    embeddings_df = pd.DataFrame(embeddings_data)

    print(f"Saving embeddings to: {output_csv_path}")
    try:
        embeddings_df.to_csv(output_csv_path, index=False)
        print("Embeddings saved successfully.")
    except Exception as e:
        print(f"Error saving embeddings to CSV: {e}")

if __name__ == '__main__':
    script_dir = os.path.dirname(__file__)
    input_csv = os.path.join(script_dir, 'data', 'produtos_carrefour.csv')
    output_csv = os.path.join(script_dir, 'data', 'product_embeddings.csv')
    product_col = 'nome'

    print("Starting embedding generation script...")
    generate_product_embeddings(input_csv, output_csv, product_col)
    print("Script finished.")
