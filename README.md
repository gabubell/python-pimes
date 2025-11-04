# Classificador de produto de NFe

Objetivo: classificar lista de compras de supermercado em grupos relevantes para análise dos gastos.

Desafio: nomes não padronizados entre supermercados & milhares de produtos diferentes sem um agrupamento granular.

Exemplos (hipótese) (Input -> Output):
a) LI TOSC EXC -> [Linguiça, Carne, Comida, In-natura, Alimentação]
b) ESP BOMBRIL -> [Esponja de louça, Limpeza cozinha, Limpeza]
c) COC 200ML -> [Coca-cola, Refrigerante, Bebidas não alcólicas, Bebidas, Alimentação]

# Tentativa 01 - Na pasta "old"

## Design do sistema

1) Crawler de supermercado para gerar uma lista representativa de produtos
    - Ponto de atenção: formato dos nomes é estruturalmente diferente do normalmente disposto em NFe
2) Utilizar modelo de LLM pré-treinado para gerar uma lista de embeddings correspondente
    - Utilizado um modelo geral para embedding da frase inteira de um produto
3) Gera um cluster não-supervisionado hierárquico utilizando os embeddings
    - Cluster inicial foi feito usando distância do cosseno, melhor para embeddings semântico/textual que euclidiano
    - Pairado com o complete Linkage, pois funciona bem com distância de cosseno e tem tência de "quebrar" clusters grandes em menores, ideal para a revisão seguinte
    - Processo de revisão manual
4) Cria uma anotação para cada nível do cluster utilizando um LLM como Gemini
    - Revisão manual dos nomes
5) Treina um classificador que pega embedding do nome da NFe e assinala a um ramo (nível mais específico)
    - Desafio é que não tenho os nomes em formato de NFe relacionados a grupos para o treinamento. Logo, será usado os nomes do crawler inicial (que são mais longos e completos) para treinar o classificador.
6) Manualmente validar a inferência do classificador para NFe reais

Em um próximo passo futuro, seria criar análises em forma de gráficos e tabelas sumarizando os gastos do usuário, dando informações sobre onde a maior parte da renda está sendo gasta.

### Resultado insatisfatório

Na inspeção manual fiz um processo iterativo nos clusters hierárquivos tentando calibrar a solução, mas não consegui chegar em um resultado satisfatório. No meu entendimento, só conseguiria fazer de duas formas: a) ter vários dados rotulados de NFe e treinar um classificador e b) Utilizar LLM para gerar conteúdo, não apenas focado em gerar embedding, para que ele tenha contexto como input.

Por motivo de tempo/esforço para coleta manual dos dados (eu teria que ter NFe representativa do mercado, e eu só tenho disponível minha própria cesta de consumo), optei por prosseguir com a abordagem "b". Em um cenário que o modelo vire um app, eu poderia coletar os dados dos usuários e o label gerado pelo LLM para treinar o modelo do tipo "a" e comparar a performance usando label feito por humano.

# Tentativa 02

## Design do sistema

1) Crawler de supermercado para gerar lista de produtos
2) Utilizar LLM pré-treinado em classificar
    - Foi gerado uma lista extensa de categorias com ajuda do Gemini em data/categorias_supermercado.json para ser usado pelo modelo
3) Fazer revisão manual do output do modelo
4) Treinar um classificador
    - O LLM é extremamente lento.
    - A ideia é que com o input limpo, um classificador poderia performar tão bem ou até melhor que o LLM zero-shoot

Eu desisti de prosseguir com esse design pois o modelo LLM demora dias para rodar no meu computador para todos produtos (enquanto isso ele fica inutilizável) e ainda comete erros muito graves (mesmo após várias iterações na lista de produtos e modelos diferentes), tenho impressão que um algoritmo determinístico performaria melhor...

Além disso, mesmo que o LLM perfomarsse bem, como são palavras, não consegui pensar em como estruturar um bom classificador para lidar com os embeddings nesse contexto. E por fim, o meu objetivo final é usar em NFe, onde o nome dos produtos é estruturalmente diferente dos produtos do mercado, ou seja, mesmo que conseguisse resultado +- satisfatório, tenho convicção de que ficaria ruim nesse novo formato, pelo que aprendi ao trabalhar com LLM.