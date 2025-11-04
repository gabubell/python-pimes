import requests
from bs4 import BeautifulSoup
import time
import csv
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

def build_paginated_url(base_url: str, page_number: int) -> str:
    """
    Constrói a URL paginada. A página 0 é a URL base. As páginas
    subsequentes usam o parâmetro de consulta '&page=X', começando em page=2.

    Args:
        base_url: A URL original da categoria.
        page_number: O número da página a ser acessada (0-indexed).

    Returns:
        A URL formatada para a página correta.
    """
    url_without_fragment = base_url.split('#')[0]
    parsed_url = urlparse(url_without_fragment)
    query_params = parse_qs(parsed_url.query)
    query_params.pop('page', None)

    # Para a primeira página (nosso page_number == 0), não adicionamos o parâmetro 'page'.
    # Para as páginas seguintes, adicionamos o parâmetro, começando em 2.
    if page_number > 0:
        query_params['page'] = [page_number + 1]

    new_query_string = urlencode(query_params, doseq=True)
    
    paginated_url = urlunparse(
        (parsed_url.scheme, parsed_url.netloc, parsed_url.path, 
         parsed_url.params, new_query_string, parsed_url.fragment)
    )
    return paginated_url

def scrape_carrefour_product_names(url: str, session: requests.Session) -> list[str]:
    """
    Coleta os nomes de todos os produtos de uma URL de coleção do Carrefour,
    lidando com a paginação e evitando loops infinitos.

    Args:
        url: A URL inicial da página de coleção do Carrefour.
        session: A sessão de requests para reutilização.

    Returns:
        Uma lista contendo os nomes de todos os produtos encontrados na URL.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    product_names = []
    page_number = 0
    last_page_products = None
    
    while True:
        paginated_url = build_paginated_url(url, page_number)
        
        try:
            response = session.get(paginated_url, headers=headers, timeout=15)
            response.raise_for_status()
            response.encoding = 'utf-8'
        except requests.RequestException as e:
            print(f"Erro ao acessar a página {page_number + 1}: {e}")
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        products_on_page_elements = soup.find_all('h2', class_='truncate-text')
        
        if not products_on_page_elements:
            break
        
        current_page_products = [p.get_text(strip=True) for p in products_on_page_elements]
        
        if current_page_products == last_page_products:
            print("[Debug] Página duplicada detectada, finalizando a coleta para esta URL.")
            break
            
        product_names.extend(current_page_products)
        
        print(f"Página {page_number + 1} processada. {len(current_page_products)} produtos encontrados.")
        
        last_product_name = current_page_products[-1]
        print(f"[Debug] Último produto da página: {last_product_name}")
        
        last_page_products = current_page_products
        page_number += 1
        time.sleep(1)
        
    return product_names

def save_to_csv(product_list: list[str], filename: str) -> None:
    """
    Salva uma lista de nomes de produtos em um arquivo CSV.

    Args:
        product_list: A lista de nomes de produtos.
        filename: O nome do arquivo CSV a ser criado.
    """
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['Nome do Produto'])
            for name in product_list:
                csv_writer.writerow([name])
        print(f"\nDados salvos com sucesso no arquivo '{filename}'")
    except IOError as e:
        print(f"Erro ao salvar o arquivo CSV: {e}")


if __name__ == '__main__':
    url_list = [
        # A estrutura da url muda ao selecionar número máximo de itens = 60 e fica mais simples
        "https://mercado.carrefour.com.br/colecao/24391/score-desc/0?map=productClusterIds&count=60",
        "https://mercado.carrefour.com.br/categoria/bebidas?count=60",
        "https://mercado.carrefour.com.br/categoria/congelados?category-1=congelados&category-2=pratos-prontos&sellername=carrefour&facets=category-1%2Ccategory-2%2Csellername&sort=orders_desc&page=0&count=60",
        "https://mercado.carrefour.com.br/colecao/11336?productClusterIds=11336&facets=productClusterIds&count=60",
        "https://mercado.carrefour.com.br/categoria/higiene-e-perfumaria?count=60",
        "https://mercado.carrefour.com.br/colecao/24365/score-desc/0?map=productClusterIds&count=60",
        "https://mercado.carrefour.com.br/categoria/bebe-e-infantil?count=60",
        "https://mercado.carrefour.com.br/colecao/19581/score-desc/0?map=productClusterIds&count=60",
        "https://mercado.carrefour.com.br/colecao/19582/score-desc/0?map=productClusterIds%2Csort%2Cpage&count=60",
        "https://mercado.carrefour.com.br/colecao/19583/score-desc/0?map=productClusterIds%2Csort%2Cpage&count=60",
        "https://mercado.carrefour.com.br/colecao/19584/score-desc/0?map=productClusterIds%2Csort%2Cpage&count=60",
        "https://mercado.carrefour.com.br/colecao/19585/score-desc/0?map=productClusterIds%2Csort%2Cpage&count=60",
        "https://mercado.carrefour.com.br/colecao/25532/score-desc/0?map=productClusterIds%2Csort%2Cpage&count=60"
    ]
    
    all_products = []
    
    with requests.Session() as session:
        for url in url_list:
            print(f"\n--- Coletando da URL: {url} ---")
            products_from_url = scrape_carrefour_product_names(url, session)
            all_products.extend(products_from_url)
            time.sleep(2)

    if all_products:
        unique_products = sorted(list(set(all_products)))
        print(f"\nTotal de {len(all_products)} produtos coletados ({len(unique_products)} únicos).")
        save_to_csv(unique_products, 'data', 'produtos_carrefour.csv')
    else:
        print("\nNenhum produto foi encontrado nas URLs fornecidas.")