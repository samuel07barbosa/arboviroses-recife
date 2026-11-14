# Metodologia

Documentação técnica do painel: de onde vêm os dados, como os indicadores são calculados e como foram conferidos.

## Fontes

Três bases do SINAN publicadas no [Portal de Dados Abertos do Recife](https://dados.recife.pe.gov.br/dataset/casos-de-dengue-zika-e-chikungunya), consolidadas em planilhas Google e conectadas ao Looker Studio.

| Base | Registros | Colunas | Observação |
|---|---:|---:|---|
| Dengue | 107.117 | 152 | 2013 a 2025; os registros de 2023 estão na base de chikungunya |
| Chikungunya | 48.247 | 134 | inclui notificações de dengue de 2023 |
| Zika | 24.844 | 131 | 2015 a 2025; o bloco de 2021 do arquivo é de chikungunya |

Cada linha é uma notificação individual de residente do Recife, feita em qualquer município. As bases trazem todas as notificações: confirmadas, descartadas, inconclusivas e em investigação.

## Caso confirmado

A doença de cada registro é definida pelo CID (`co_cid`), não pelo arquivo de origem. A confirmação usa a classificação final (`classificacao_final`), cujos códigos mudam entre agravos e versões da ficha:

| CID | Agravo | Confirmado | Descartado |
|---|---|---|---|
| A90 | Dengue | 1, 2, 3, 4 (ficha antiga) · 10, 11, 12 (ficha atual) | 5 |
| A92.0 | Chikungunya | 13 | 5 |
| A92.8 | Zika | 1 | 2 |

Os registros com CID A90 encontrados na base de chikungunya entram no total de dengue (`dengue_conf_bc`).

## Indicadores

| Indicador | Definição |
|---|---|
| Casos confirmados | `dengue_conf + dengue_conf_bc + chik_conf + zika_conf` |
| Curas | confirmados com `evolucao_caso = 1` |
| Óbitos pelo agravo | confirmados com `evolucao_caso = 2` |
| Faixa etária | derivada de `idade_codigo` (fórmula abaixo) |
| Sintomas e comorbidades | campos da ficha marcados como 1 (sim); 2 (não) e 9 (ignorado) ficam de fora |

Sintomas considerados: febre, mialgia, cefaleia, artralgia, exantema, náusea, vômito, dor retro-orbital, dor nas costas, artrite, petéquias, conjuntivite e leucopenia. Comorbidades: hipertensão, diabetes, doença ácido-péptica, hepatopatia, doença hematológica, doença renal e doença autoimune. A prova do laço não foi incluída.

### Campos calculados principais

`idade_codigo` traz a unidade no primeiro dígito (1 hora, 2 dia, 3 mês, 4 ano) e o valor nos três seguintes: 4059 = 59 anos. Códigos abaixo de 4000 são menores de um ano e entram em 00-10.

```sql
-- faixa_etaria
CASE
  WHEN idade_codigo IS NULL OR idade_codigo < 1000 THEN "Não informado"
  WHEN idade_codigo <= 4010 THEN "00-10"
  WHEN idade_codigo <= 4020 THEN "11-20"
  WHEN idade_codigo <= 4030 THEN "21-30"
  WHEN idade_codigo <= 4040 THEN "31-40"
  WHEN idade_codigo <= 4050 THEN "41-50"
  WHEN idade_codigo <= 4060 THEN "51-60"
  WHEN idade_codigo <= 4070 THEN "61-70"
  WHEN idade_codigo <= 4080 THEN "71-80"
  WHEN idade_codigo <= 4120 THEN "81+"
  ELSE "Não informado"
END
```

```sql
-- um campo por sintoma ou comorbidade, em cada base (prefixos d_, c_ e z_)
d_febre = SUM(IF(febre = 1, dengue_conf, 0))
```

```sql
-- casos confirmados por bairro conforme a doença escolhida no menu (parâmetro)
SUM(CASE
  WHEN doenca_sel = "Dengue"      THEN IFNULL(dengue_conf, 0) + IFNULL(dengue_conf_bc, 0)
  WHEN doenca_sel = "Chikungunya" THEN IFNULL(chik_conf, 0)
  WHEN doenca_sel = "Zika"        THEN IFNULL(zika_conf, 0)
  ELSE IFNULL(dengue_conf, 0) + IFNULL(dengue_conf_bc, 0) + IFNULL(chik_conf, 0) + IFNULL(zika_conf, 0)
END)
```

## Modelo de dados

As três bases são fontes separadas. Para combiná-las sem dupla contagem, cada gráfico usa uma mescla: o Looker Studio agrega cada base pela chave da mescla e só depois junta os resultados. Nas tabelas das doenças, a dimensão de período é a data de notificação (`dt_notificacao`).

| Mescla | Tabela de referência | Usada em |
|---|---|---|
| Mescla mensal | calendário mensal (`apoio_meses`) | série temporal |
| Mescla bairros | bairros padronizados (`apoio_bairros_geo`) | mapa, ranking e filtro de bairro |
| Mescla raça/cor | categorias de raça/cor | gráfico de raça/cor |
| Mescla sexo | categorias de sexo | gráfico de sexo |
| Mescla faixa etária | combinações de sexo e faixa etária | gráfico de faixa etária e sexo |
| Mescla clínica | lista de sintomas e comorbidades, em junção cruzada | gráficos de sintomas e comorbidades |

## Tabelas de apoio

Ficam em [`dados/`](../dados). As três primeiras são geradas por [`scripts/gera_apoio.py`](../scripts/gera_apoio.py).

| Arquivo | Conteúdo |
|---|---|
| `apoio_bairros.csv` | 141 grafias de bairro encontradas nas bases (94 oficiais e 47 variantes com erro de digitação ou codificação), cada uma ligada ao bairro padronizado e ao distrito sanitário (DS I a DS VIII) |
| `apoio_meses.csv` | calendário mensal de 2013 a 2025 |
| `apoio_anos.csv` | calendário anual de 2013 a 2025; também serve de lista de categorias para a mescla clínica |
| `apoio_bairros_geo.csv` | os 94 bairros com coordenadas aproximadas do centro, usadas no mapa |

## Validação

Nenhum número foi aceito só por aparecer no painel. Os totais foram recontados nos arquivos originais, e os resultados das mesclas foram conferidos com a soma por doença.

| Indicador | Painel | Conferência |
|---|---:|---|
| Casos confirmados | 95.174 | 62.951 dengue + 31.900 chikungunya + 323 zika |
| Curas | 90.336 | 58.832 + 31.193 + 311 |
| Óbitos pelo agravo | 125 | 58 + 66 + 1 |
| Sexo | 54.994 F · 40.016 M · 164 ignorado | igual à recontagem por doença |
| Raça/cor | 59.408 ignorado · 27.253 parda · 6.096 branca · 1.842 preta · 338 amarela · 237 indígena | igual à recontagem por doença |
| Faixa etária | soma das faixas = 95.174 | nenhum caso perdido na mescla |
| Bairros | 91.204 com bairro identificado | 62.591 + 28.290 + 323; os 3.970 restantes não têm bairro correspondente |
| Febre | 59.014 | 31.249 dengue + 27.765 chikungunya + 0 zika |
| Hipertensão | 2.321 | 955 + 1.366 + 0 |

## Limitações

- O filtro de período usa a data de notificação, não a data de início dos sintomas.
- Os totais não excluem coinfecções nem notificações duplicadas entre as bases.
- Raça/cor está ignorada ou em branco em 62% dos casos confirmados.
- Os casos confirmados de zika não têm sintomas nem comorbidades preenchidos.
- 3.970 casos confirmados (360 de dengue e 3.610 de chikungunya) não têm bairro identificado.
- Um mesmo caso pode ter vários sintomas: os percentuais do gráfico de sintomas são parcelas das menções, não dos casos.
- O painel não calcula incidência, porque não usa população de referência por bairro e ano.
