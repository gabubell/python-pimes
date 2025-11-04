import pandas as pd
from transformers import pipeline
import os
import re
from src.text_cleaner import clean_text

def generate_hierarchical_categories(input_csv_path: str, output_csv_path: str, product_name_column: str, num_samples: int = None):
    """
    Generates hierarchical categories for products from a CSV file using a text generation model.

    Args:
        input_csv_path (str): Path to the input CSV file.
        output_csv_path (str): Path to save the output CSV file with generated categories.
        product_name_column (str): Name of the column with product names.
        num_samples (int, optional): Number of products to process. If None, processes all. Defaults to None.
    """
    # 1. Carregar o modelo de geração de texto
    print("Carregando o modelo de geração de texto...")
    generator = pipeline('text2text-generation', model='google/flan-t5-base')

    # 2. Ler o CSV com os produtos
    print(f"Lendo produtos de '{input_csv_path}'...")
    try:
        df = pd.read_csv(input_csv_path)
    except FileNotFoundError:
        print(f"Erro: Arquivo de entrada não encontrado em '{input_csv_path}'")
        return

    if product_name_column not in df.columns:
        print(f"Erro: A coluna '{product_name_column}' não foi encontrada no arquivo de entrada.")
        return

    product_names = df[product_name_column].dropna()
    if num_samples:
        product_names = product_names.sample(n=num_samples, random_state=42)
    
    product_names = product_names.tolist()

    # 3. Gerar categorias para cada produto
    print(f"Gerando categorias para {len(product_names)} produtos")
    
    results = []
    for i, name in enumerate(product_names):
        cleaned_name = clean_text(name)

        # Montar o prompt para o modelo
        prompt = f"""
        Para o seguinte produto, gere uma hierarquia de categorias, da mais específica para a mais geral.
        O formato da saída deve ser uma lista de categorias entre parênteses, separadas por vírgula. Exemplo: (fralda descartável, cuidados com bebês, higiene).

        Produto: "{cleaned_name}"
        Categorias:
        """

        try:
            generated_text = generator(prompt, max_length=50)[0]['generated_text']
            
            match = re.search(r'\((.*?)\)', generated_text)
            if match:
                categories_str = match.group(1)
            else:
                categories_str = 'falha na extração'

            results.append({
                'produto_original': name,
                'produto_limpo': cleaned_name,
                'categorias_geradas': categories_str,
                'texto_gerado_completo': generated_text
            })
            print(f"({i+1}/{len(product_names)}) Produto: {name} -> Categorias: {categories_str}")

        except Exception as e:
            print(f"Erro ao processar o produto '{name}': {e}")
            results.append({
                'produto_original': name,
                'produto_limpo': cleaned_name,
                'categorias_geradas': 'erro',
                'texto_gerado_completo': str(e)
            })


    # 4. Salvar os resultados
    results_df = pd.DataFrame(results)
    print(f"Salvando os resultados em '{output_csv_path}'...")
    results_df.to_csv(output_csv_path, index=False, encoding='utf-8')
    print("Geração de categorias concluída!")


if __name__ == '__main__':
    # --- CONFIGURAÇÃO ---
    script_dir = os.path.dirname(__file__)
    input_file = os.path.join(script_dir, 'data', 'produtos_carrefour.csv')
    output_file = os.path.join(script_dir, 'data', 'produtos_com_categorias_geradas.csv')
    coluna_produto = 'nome'

    numero_de_amostras = 20

    generate_hierarchical_categories(input_file, output_file, coluna_produto, num_samples=numero_de_amostras)
