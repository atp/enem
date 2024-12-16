# enem_atp
Aqui vamos analisar os microdados do ENEM (veja [aqui](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem)). 

A ideia é processar os dados e disponibilizar numa forma onde fica fácil criar novas análises. No notebook [00-PrepareData](00-PrepareData.ipynb) temos um "pipeline" de pré-processamento que resulta em arquivos no diretório `data` que são usados pelas funções de conveniência em `util.py`.

No notebook [01-Notas](01-Notas.ipynb) mostramos que é possível reproduzir, exatamente, as notas do ENEM divulgados pelo INEP, usando os parâmetros dos itens do INEP. 

Outros notebooks mostram outros tipos de análises possíveis. 