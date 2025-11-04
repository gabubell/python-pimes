import re
import unicodedata

def clean_text(text: str) -> str:
    """
    Cleans product names by converting to lowercase, removing diacritics, removing all numbers,
    removing punctuation, and removing common, truly meaningless stop words, including unit terms.

    Args:
        text: The input product name string.

    Returns:
        The cleaned product name string.
    """
    text = text.lower()

    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'[^a-z\s]', '', text)

    # Combined list of stop words and irrelevant terms
    stop_words = set([
        'e', 'de', 'do', 'da', 'o', 'a', 'os', 'as', 'um', 'uma', 'uns', 'umas', 'para', 'no', 'na', 'nos', 'nas', 'em', 'por', 'sem', 'ao', 'aos', 'à', 'às', 'que', 'com',
        'tipo', 'aprox', 'aproximado', 'aproximadamente', 'desconto', 'cozido', 'vapor', 'carrefour', 'pequeno', 'medio', 'grande', 'mini', 'super', 'caixa', 'original', 'menos', 'zero',
        'litro', 'litros', 'unidade', 'unidades', 'refil', 'economica', 'economico', 'embalagem', 'congelado', 'fresco', 'in-natura', 'natura', 'pote', 'qualidade', 'sabor',
        'temperado', 'tempero', 'organico', 'organic', 'l', 'integral', 'suporte', 'suporta', 'pacote', 'package', 'lata', 'garrafa', 'kit', 'conjunto', 'natural', 'congelada',
        'promo', 'leve', 'pague', 'unid', 'un', 'g', 'm', 'gg', 'xg', 'xxg', 'xxxg', 'feminino', 'masculino', 'pesado', 'pesada', 'na', 'no', 'gluten', 'assado', 'cortado',
        'inteiro', 'pack', 'pet', 'tradicional', 'ate', 'horas', 'noite', 'noites', 'dia', 'dias', 'pra', 'tamanho', 'completo', 'completa',
        'ml', 'g', 'kg', 'l', 'pc', 'pcs', 'cx', 'sachê', 'sache', 'pct'
    ])
    
    text = ' '.join([word for word in text.split() if word not in stop_words])
    text = re.sub(r'\s+', ' ', text).strip()

    return text