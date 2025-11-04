
import json
import pandas as pd
from transformers import pipeline
from src.text_cleaner import clean_text
import os
import argparse

def get_leaf_nodes(node):
    """
    Recursively traverses the category tree and returns a flat list of all unique leaf node strings.
    """
    leaves = []
    if isinstance(node, dict):
        for key, value in node.items():
            leaves.extend(get_leaf_nodes(value))
    elif isinstance(node, list):
        leaves.extend(node)
    
    return list(set(leaves))

def main():
    # --- CONFIGURAÇÃO DOS ARGUMENTOS ---
    parser = argparse.ArgumentParser(description="Classifica produtos de um arquivo CSV usando um modelo zero-shot.")
    parser.add_argument("--num_samples", type=int, default=None, help="Número de amostras para classificar. Se não for fornecido, classifica todos os produtos.")
    args = parser.parse_args()

    # --- CONFIGURAÇÃO DOS CAMINHOS ---
    script_dir = os.path.dirname(__file__)
    json_path = os.path.join(script_dir, 'data', 'categorias_supermercado.json')
    products_csv_path = os.path.join(script_dir, 'data', 'produtos_carrefour.csv')
    output_csv_path = os.path.join(script_dir, 'data', 'produtos_classificados_folhas.csv')
    product_name_column = 'nome'

    # 1. Carregar a árvore de categorias e extrair apenas as folhas
    print(f"Carregando árvore de categorias de '{json_path}'...")
    with open(json_path, 'r', encoding='utf-8') as f:
        category_tree = json.load(f)
    
    print("Extraindo categorias de nível final (folhas)...")
    leaf_labels = get_leaf_nodes(category_tree)
    print(f"{len(leaf_labels)} etiquetas de folhas únicas extraídas.")

    # 2. Carregar o modelo de classificação
    print("Carregando o modelo de classificação zero-shot...")
    classifier = pipeline(
        "zero-shot-classification",
        model="joeddav/xlm-roberta-large-xnli",
        hypothesis_template="A categoria para este produto é {}."
    )

    # 3. Ler o CSV de produtos e aplicar amostragem se necessário
    print(f"Lendo produtos de '{products_csv_path}'...")
    df = pd.read_csv(products_csv_path)
    df.dropna(subset=[product_name_column], inplace=True)

    if args.num_samples:
        print(f"Selecionando uma amostra aleatória de {args.num_samples} produtos...")
        product_sample = df.sample(n=min(args.num_samples, len(df)), random_state=42)
    else:
        print("Processando todos os produtos do arquivo...")
        product_sample = df

    # 4. Classificar cada produto da amostra em um loop
    print(f"Iniciando classificação para {len(product_sample)} produtos usando apenas as folhas...")
    
    results = []
    for index, row in product_sample.iterrows():
        original_name = row[product_name_column]
        cleaned_name = clean_text(original_name)

        print(f"\nProcessando: '{original_name}'...")

        # Classifica um produto de cada vez contra a lista de folhas
        classification = classifier(cleaned_name, leaf_labels, multi_label=False)
        
        best_label = classification['labels'][0]
        best_score = classification['scores'][0]

        print(f"--> Classificado como: {best_label} (Confiança: {best_score:.2f})")

        results.append({
            'produto_original': original_name,
            'produto_limpo': cleaned_name,
            'categoria_folha': best_label,
            'confianca': best_score
        })

    # 5. Salvar os resultados
    results_df = pd.DataFrame(results)
    print(f"\nSalvando os resultados em '{output_csv_path}'...")
    results_df.to_csv(output_csv_path, index=False, encoding='utf-8')
    print("Classificação concluída com sucesso!")

if __name__ == '__main__':
    main()
