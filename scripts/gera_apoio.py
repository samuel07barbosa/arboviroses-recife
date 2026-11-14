"""Gera as tabelas de apoio usadas nas mesclas do painel.

- apoio_bairros.csv: grafias de bairro encontradas nas bases do SINAN
  (oficiais e variantes com erro de digitação/codificação) -> bairro
  padronizado e distrito sanitário.
- apoio_meses.csv: calendário mensal de 2013 a 2025.
- apoio_anos.csv: calendário anual de 2013 a 2025.

Uso: python scripts/gera_apoio.py   (grava os arquivos em dados/)
"""
import csv
import os

SAIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dados")
ds = {
 "DS I": ["RECIFE|Recife","SANTO AMARO|Santo Amaro","BOA VISTA|Boa Vista","CABANGA|Cabanga","ILHA DO LEITE|Ilha do Leite","PAISSANDU|Paissandu","SANTO ANTONIO|Santo Antônio","SAO JOSE|São José","COELHOS|Coelhos","SOLEDADE|Soledade","ILHA JOANA BEZERRA|Ilha Joana Bezerra"],
 "DS II": ["ARRUDA|Arruda","CAMPINA DO BARRETO|Campina do Barreto","CAMPO GRANDE|Campo Grande","ENCRUZILHADA|Encruzilhada","HIPODROMO|Hipódromo","PEIXINHOS|Peixinhos","PONTO DE PARADA|Ponto de Parada","ROSARINHO|Rosarinho","TORREAO|Torreão","AGUA FRIA|Água Fria","ALTO SANTA TEREZINHA|Alto Santa Terezinha","BOMBA DO HEMETERIO|Bomba do Hemetério","CAJUEIRO|Cajueiro","FUNDAO|Fundão","PORTO DA MADEIRA|Porto da Madeira","BEBERIBE|Beberibe","DOIS UNIDOS|Dois Unidos","LINHA DO TIRO|Linha do Tiro"],
 "DS III": ["AFLITOS|Aflitos","ALTO DO MANDU|Alto do Mandu","APIPUCOS|Apipucos","CASA AMARELA|Casa Amarela","CASA FORTE|Casa Forte","DERBY|Derby","DOIS IRMAOS|Dois Irmãos","ESPINHEIRO|Espinheiro","GRACAS|Graças","JAQUEIRA|Jaqueira","MONTEIRO|Monteiro","PARNAMIRIM|Parnamirim","POCO|Poço da Panela","SANTANA|Santana","SITIO DOS PINTOS|Sítio dos Pintos","TAMARINEIRA|Tamarineira"],
 "DS IV": ["CORDEIRO|Cordeiro","ILHA DO RETIRO|Ilha do Retiro","IPUTINGA|Iputinga","MADALENA|Madalena","PRADO|Prado","TORRE|Torre","ZUMBI|Zumbi","ENGENHO DO MEIO|Engenho do Meio","TORROES|Torrões","CAXANGA|Caxangá","CIDADE UNIVERSITARIA|Cidade Universitária","VARZEA|Várzea"],
 "DS V": ["AFOGADOS|Afogados","AREIAS|Areias","BARRO|Barro","BONGI|Bongi","CACOTE|Caçote","COQUEIRAL|Coqueiral","CURADO|Curado","ESTANCIA|Estância","JARDIM SAO PAULO|Jardim São Paulo","JIQUIA|Jiquiá","MANGUEIRA|Mangueira","MUSTARDINHA|Mustardinha","SAN MARTIN|San Martin","SANCHO|Sancho","TEJIPIO|Tejipió","TOTO|Totó"],
 "DS VI": ["BOA VIAGEM|Boa Viagem","BRASILIA TEIMOSA|Brasília Teimosa","IMBIRIBEIRA|Imbiribeira","IPSEP|Ipsep","PINA|Pina"],
 "DS VII": ["ALTO JOSE BONIFACIO|Alto José Bonifácio","ALTO JOSE DO PINHO|Alto José do Pinho","BREJO DA GUABIRABA|Brejo da Guabiraba","BREJO DE BEBERIBE|Brejo de Beberibe","CORREGO DO JENIPAPO|Córrego do Jenipapo","GUABIRABA|Guabiraba","MACAXEIRA|Macaxeira","MANGABEIRA|Mangabeira","MORRO DA CONCEICAO|Morro da Conceição","NOVA DESCOBERTA|Nova Descoberta","PASSARINHO|Passarinho","PAU FERRO|Pau-Ferro","VASCO DA GAMA|Vasco da Gama"],
 "DS VIII": ["IBURA|Ibura","JORDAO|Jordão","COHAB|Cohab"],
}
codigo = {"DS I":117,"DS II":118,"DS III":119,"DS IV":120,"DS V":121,"DS VI":122,"DS VII":546,"DS VIII":547}
canon = {}
for d, lst in ds.items():
    for item in lst:
        raw, nome = item.split("|")
        canon[raw] = (nome, d)
assert len(canon) == 94, len(canon)
# variantes com erro de digitação/codificação encontradas nas três bases
variantes = {
 "ALTO JOS DO PINHO":"ALTO JOSE DO PINHO","Alto Jos' do Pinho":"ALTO JOSE DO PINHO","ALTO JOSE DO PINH":"ALTO JOSE DO PINHO",
 "AREAIS":"AREIAS","BOMBA DO HEMET╔RIO":"BOMBA DO HEMETERIO","BREJO DE GUABIRABA":"BREJO DA GUABIRABA",
 "CORDRIRO":"CORDEIRO","CORREGO JENIPAPO":"CORREGO DO JENIPAPO","CORREGO DO JENPAPO":"CORREGO DO JENIPAPO",
 "FundÆo":"FUNDAO","GRAAS":"GRACAS","HIPàDROMO":"HIPODROMO","INBIRIBEIRA":"IMBIRIBEIRA",
 "JD.JORDAO":"JORDAO","JORDO":"JORDAO","JORDAO ALTO":"JORDAO","JORDAO BAIXO":"JORDAO",
 "JOANA BEZERRA":"ILHA JOANA BEZERRA","ILHA DE JOANA BEZERRA":"ILHA JOANA BEZERRA","ILHA DE RETIRO":"ILHA DO RETIRO",
 "MACA\\EIRA":"MACAXEIRA","MANGABERIA":"MANGABEIRA","MANGUEIRA - BAIRRO":"MANGUEIRA",
 "MORRO DA CONCEIAO":"MORRO DA CONCEICAO","MORRO DA CONCEIO":"MORRO DA CONCEICAO","MUSTADINHA":"MUSTARDINHA",
 "PONRO DE PARADA":"PONTO DE PARADA","SAN MARTIM":"SAN MARTIN","SANATO AMARO":"SANTO AMARO","SANTE AMARO":"SANTO AMARO",
 "SO JOSE":"SAO JOSE","TEJIPI":"TEJIPIO","VASIO DAGAMA":"VASCO DA GAMA","VASO DA GAMA":"VASCO DA GAMA",
 "Campo Grande":"CAMPO GRANDE","CAMPO GRANE":"CAMPO GRANDE","CASA MARELA":"CASA AMARELA","%AGUAFRIA%":"AGUA FRIA",
 "MONTERIO":"MONTEIRO","ENGENHO MEIO":"ENGENHO DO MEIO","BEERIBE":"BEBERIBE","VAR\\EA":"VARZEA",
 "GUAB":"GUABIRABA","GUABIR":"GUABIRABA","VASC":"VASCO DA GAMA","VASCO":"VASCO DA GAMA","IMB":"IMBIRIBEIRA",
}
with open(os.path.join(SAIDA, "apoio_bairros.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["bairro_nome_residencia", "bairro", "distrito_sanitario", "distrito_codigo", "tipo_registro"])
    for raw, (nome, d) in sorted(canon.items(), key=lambda kv: (codigo[kv[1][1]], kv[1][0])):
        w.writerow([raw, nome, d, codigo[d], "oficial"])
    for raw, alvo in sorted(variantes.items()):
        nome, d = canon[alvo]
        w.writerow([raw, nome, d, codigo[d], "variante"])

meses = ["jan","fev","mar","abr","mai","jun","jul","ago","set","out","nov","dez"]
with open(os.path.join(SAIDA, "apoio_meses.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["ano_mes", "data_mes", "ano", "mes", "mes_nome"])
    for a in range(2013, 2026):
        for m in range(1, 13):
            w.writerow([f"{a}{m:02d}", f"{a}-{m:02d}-01", a, m, meses[m-1]])

with open(os.path.join(SAIDA, "apoio_anos.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["ano", "data_ano"])
    for a in range(2013, 2026):
        w.writerow([a, f"{a}-01-01"])

print("Tabelas de apoio gravadas em", os.path.normpath(SAIDA))
