"""
regioes_mg.py
=============

Mapeamento de municípios mineiros para grandes regiões internas de Minas Gerais.

Este módulo centraliza:

- listas de municípios por região;
- dicionário de mapeamento `MAP_REGIOES`;
- dicionário de nomes formatados para exibição;
- função utilitária para atribuir região a partir do nome do município.

Uso principal
-------------
Este arquivo é utilizado na etapa de consolidação/recorte dos dados
para classificar municípios de Minas Gerais em agrupamentos regionais
mais interpretáveis para análise exploratória e dashboards.

Observações
-----------
- A comparação é feita após remoção de espaços excedentes.
- Municípios não encontrados no mapeamento recebem a categoria `"outra"`.
- Os nomes das chaves em `MAP_REGIOES` são identificadores internos.
  Para visualização, recomenda-se usar `MAP_NOME_REGIAO`.
"""

from __future__ import annotations

from typing import Dict, List


# ---------------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------------

def _norm(texto: str) -> str:
    """
    Normaliza um nome de município para comparação.

    Parameters
    ----------
    texto : str
        Nome do município.

    Returns
    -------
    str
        Texto sem espaços excedentes nas extremidades.
    """
    return texto.strip()


def _parse_cidades(texto: str) -> List[str]:
    """
    Converte um bloco de texto multilinha em lista de municípios.

    Parameters
    ----------
    texto : str
        String com um município por linha.

    Returns
    -------
    list[str]
        Lista de municípios limpos e não vazios.
    """
    return [_norm(cidade) for cidade in texto.splitlines() if cidade.strip()]


# ---------------------------------------------------------------------
# Municípios por região
# ---------------------------------------------------------------------

CID_NOROESTE = """
Arinos
Bonfinópolis de Minas
Buritis
Cabeceira Grande
Dom Bosco
Formoso
Natalândia
Unaí
Uruana de Minas
Brasilândia de Minas
Guarda-Mor
João Pinheiro
Lagamar
Lagoa Grande
Paracatu
Presidente Olegário
São Gonçalo do Abaeté
Varjão de Minas
Vazante
"""

CID_NORTE = """
Bonito de Minas
Chapada Gaúcha
Cônego Marinho
Icaraí de Minas
Itacarambi
Januária
Juvenília
Manga
Matias Cardoso
Miravânia
Montalvânia
Pedras de Maria da Cruz
Pintópolis
São Francisco
São João das Missões
Urucuia
Janaúba
Catuti
Espinosa
Gameleiras
Jaíba
Mamonas
Mato Verde
Monte Azul
Nova Porteirinha
Pai Pedro
Porteirinha
Riacho dos Machados
Serranópolis de Minas
Salinas
Águas Vermelhas
Berizal
Curral de Dentro
Divisa Alegre
Fruta de Leite
Indaiabira
Montezuma
Ninheira
Novorizonte
Rio Pardo de Minas
Rubelita
Santa Cruz de Salinas
Santo Antônio do Retiro
São João do Paraíso
Taiobeiras
Vargem Grande do Rio Pardo
Pirapora
Buritizeiro
Ibiaí
Jequitaí
Lagoa dos Patos
Lassance
Riachinho
Santa Fé de Minas
São Romão
Várzea da Palma
Montes Claros
Brasília de Minas
Campo Azul
Capitão Enéas
Claro dos Poções
Coração de Jesus
Francisco Sá
Glaucilândia
Ibiracatu
Japonvar
Juramento
Lontra
Luislândia
Mirabela
Patis
Ponto Chique
São João da Lagoa
São João da Ponte
São João do Pacuí
Ubaí
Varzelândia
Verdelândia
Grão Mogol
Botumirim
Cristália
Itacambira
Josenópolis
Padre Carvalho
Bocaiúva
Engenheiro Navarro
Francisco Dumont
Guaraciama
Olhos-d'Água
"""

CID_JEQUITINHONHA = """
Couto de Magalhães de Minas
Datas
Diamantina
Felício dos Santos
Gouveia
Presidente Kubitschek
São Gonçalo do Rio Preto
Senador Modestino Gonçalves
Angelândia
Aricanduva
Berilo
Capelinha
Carbonita
Chapada do Norte
Francisco Badaró
Itamarandiba
Jenipapo de Minas
José Gonçalves de Minas
Leme do Prado
Minas Novas
Turmalina
Veredinha
Araçuaí
Caraí
Coronel Murta
Itinga
Novo Cruzeiro
Padre Paraíso
Ponto dos Volantes
Virgem da Lapa
Cachoeira de Pajeú
Comercinho
Itaobim
Medina
Pedra Azul
Almenara
Bandeira
Divisópolis
Felisburgo
Jacinto
Jequitinhonha
Joaíma
Jordânia
Mata Verde
Monte Formoso
Palmópolis
Rio do Prado
Rubim
Salto da Divisa
Santa Maria do Salto
Santo Antônio do Jacinto
"""

CID_VALE_MUCURI = """
Ataléia
Catuji
Franciscópolis
Frei Gaspar
Itaipé
Ladainha
Malacacheta
Novo Oriente de Minas
Ouro Verde de Minas
Pavão
Poté
Setubinha
Teófilo Otoni
Águas Formosas
Bertópolis
Carlos Chagas
Crisólita
Fronteira dos Vales
Machacalis
Nanuque
Santa Helena de Minas
Serra dos Aimorés
Umburatiba
"""

CID_TRIANGULO_MINEIRO = """
Cachoeira Dourada
Capinópolis
Gurinhatã
Ipiaçu
Ituiutaba
Santa Vitória
Araguari
Araporã
Canápolis
Cascalho Rico
Centralina
Indianópolis
Monte Alegre de Minas
Prata
Tupaciguara
Uberlândia
Abadia dos Dourados
Coromandel
Cruzeiro da Fortaleza
Douradoquara
Estrela do Sul
Grupiara
Iraí de Minas
Monte Carmelo
Patrocínio
Romaria
Serra do Salitre
Arapuá
Carmo do Paranaíba
Guimarânia
Lagoa Formosa
Matutina
Patos de Minas
Rio Paranaíba
Santa Rosa da Serra
São Gotardo
Tiros
Campina Verde
Carneirinho
Comendador Gomes
Fronteira
Frutal
Itapagipe
Iturama
Limeira do Oeste
Pirajuba
Planura
São Francisco de Sales
União de Minas
Água Comprida
Campo Florido
Conceição das Alagoas
Conquista
Delta
Uberaba
Veríssimo
Araxá
Campos Altos
Ibiá
Nova Ponte
Pedrinópolis
Perdizes
Pratinha
Sacramento
Santa Juliana
Tapira
"""

CID_CENTRO = """
Abaeté
Biquinhas
Cedro do Abaeté
Morada Nova de Minas
Paineiras
Pompéu
Três Marias
Augusto de Lima
Buenópolis
Corinto
Curvelo
Felixlândia
Inimutaba
Joaquim Felício
Monjolos
Morro da Garça
Presidente Juscelino
Santo Hipólito
Araújos
Bom Despacho
Dores do Indaiá
Estrela do Indaiá
Japaraíba
Lagoa da Prata
Leandro Ferreira
Luz
Martinho Campos
Moema
Quartel Geral
Serra da Saudade
"""

CID_BELO_HORIZONTE = """
Araçaí
Baldim
Cachoeira da Prata
Caetanópolis
Capim Branco
Cordisburgo
Fortuna de Minas
Funilândia
Inhaúma
Jaboticatubas
Jequitibá
Maravilhas
Matozinhos
Papagaios
Paraopeba
Pequi
Prudente de Morais
Santana de Pirapama
Santana do Riacho
Sete Lagoas
Alvorada de Minas
Conceição do Mato Dentro
Congonhas do Norte
Dom Joaquim
Itambé do Mato Dentro
Morro do Pilar
Passabém
Rio Vermelho
Santo Antônio do Itambé
Santo Antônio do Rio Abaixo
São Sebastião do Rio Preto
Serra Azul de Minas
Serro
Florestal
Onça de Pitangui
Pará de Minas
Pitangui
São José da Varginha
Belo Horizonte
Betim
Brumadinho
Caeté
Confins
Contagem
Esmeraldas
Ibirité
Igarapé
Juatuba
Lagoa Santa
Mário Campos
Mateus Leme
Nova Lima
Pedro Leopoldo
Raposos
Ribeirão das Neves
Rio Acima
Sabará
Santa Luzia
São Joaquim de Bicas
São José da Lapa
Sarzedo
Vespasiano
Alvinópolis
Barão de Cocais
Bela Vista de Minas
Bom Jesus do Amparo
Catas Altas
Dionísio
Ferros
Itabira
João Monlevade
Nova Era
Nova União
Rio Piracicaba
Santa Bárbara
Santa Maria de Itabira
São Domingos do Prata
São Gonçalo do Rio Abaixo
São José do Goiabal
Taquaraçu de Minas
Belo Vale
Bonfim
Crucilândia
Itaguara
Itatiaiuçu
Jeceaba
Moeda
Piedade dos Gerais
Rio Manso
Diogo de Vasconcelos
Itabirito
Mariana
Ouro Preto
Casa Grande
Catas Altas da Noruega
Congonhas
Conselheiro Lafaiete
Cristiano Otoni
Desterro de Entre Rios
Entre Rios de Minas
Itaverava
Ouro Branco
Queluzito
Santana dos Montes
São Brás do Suaçuí
"""

CID_VALE_RIO_DOCE = """
Braúnas
Carmésia
Coluna
Divinolândia de Minas
Dores de Guanhães
Gonzaga
Guanhães
Materlândia
Paulistas
Sabinópolis
Santa Efigênia de Minas
São João Evangelista
Sardoá
Senhora do Porto
Virginópolis
Água Boa
Cantagalo
Frei Lagonegro
José Raydan
Peçanha
Santa Maria do Suaçuí
São José do Jacuri
São Pedro do Suaçuí
São Sebastião do Maranhão
Alpercata
Campanário
Capitão Andrade
Coroaci
Divino das Laranjeiras
Engenheiro Caldas
Fernandes Tourinho
Frei Inocêncio
Galileia
Governador Valadares
Itambacuri
Itanhomi
Jampruca
Marilac
Mathias Lobato
Nacip Raydan
Nova Módica
Pescador
São Geraldo da Piedade
São Geraldo do Baixio
São José da Safira
São José do Divino
Sobrália
Tumiritinga
Virgolândia
Central de Minas
Itabirinha
Mantena
Mendes Pimentel
Nova Belém
São Félix de Minas
São João do Manteninha
Açucena
Antônio Dias
Belo Oriente
Coronel Fabriciano
Ipatinga
Jaguaraçu
Joanésia
Marliéria
Mesquita
Naque
Periquito
Santana do Paraíso
Timóteo
Bom Jesus do Galho
Bugre
Caratinga
Córrego Novo
Dom Cavati
Entre Folhas
Iapu
Imbé de Minas
Inhapim
Ipaba
Piedade de Caratinga
Pingo-d'Água
Santa Bárbara do Leste
Santa Rita de Minas
São Domingos das Dores
São João do Oriente
São Sebastião do Anta
Tarumirim
Ubaporanga
Vargem Alegre
Aimorés
Alvarenga
Conceição de Ipanema
Conselheiro Pena
Cuparaque
Goiabeira
Ipanema
Itueta
Mutum
Pocrane
Resplendor
Santa Rita do Itueto
Taparuba
"""

CID_OESTE = """
Bambuí
Córrego Danta
Doresópolis
Iguatama
Medeiros
Piumhi
São Roque de Minas
Tapiraí
Vargem Bonita
Carmo do Cajuru
Cláudio
Conceição do Pará
Divinópolis
Igaratinga
Itaúna
Nova Serrana
Perdigão
Santo Antônio do Monte
São Gonçalo do Pará
São Sebastião do Oeste
Arcos
Camacho
Córrego Fundo
Formiga
Itapecerica
Pains
Pedra do Indaiá
Pimenta
Aguanil
Campo Belo
Cana Verde
Candeias
Cristais
Perdões
Santana do Jacaré
Bom Sucesso
Carmo da Mata
Carmópolis de Minas
Ibituruna
Oliveira
Passa Tempo
Piracema
Santo Antônio do Amparo
São Francisco de Paula
"""

CID_SUDOESTE = """
Além Paraíba
Andrelândia
Antônio Prado de Minas
Aracitaba
Arantina
Argirita
Astolfo Dutra
Barão de Monte Alto
Belmiro Braga
Bias Fortes
Bicas
Bocaina de Minas
Bom Jardim de Minas
Brás Pires
Caiana
Caparaó
Carangola
Cataguases
Chácara
Chiador
Coimbra
Coronel Pacheco
Descoberto
Divinésia
Divino
Dona Eusébia
Dores do Turvo
Ervália
Espera Feliz
Estrela Dalva
Eugenópolis
Ewbank da Câmara
Faria Lemos
Fervedouro
Goianá
Guarani
Guarará
Guidoval
Guiricema
Itamarati de Minas
Juiz de Fora
Laranjal
Leopoldina
Liberdade
Lima Duarte
Mar de Espanha
Maripá de Minas
Matias Barbosa
Mercês
Miradouro
Miraí
Muriaé
Olaria
Oliveira Fortes
Orizânia
Palma
Passa-Vinte
Patrocínio do Muriaé
Pedra Bonita
Pedra Dourada
Pedro Teixeira
Pequeri
Piau
Pirapetinga
Piraúba
Presidente Bernardes
Recreio
Rio Novo
Rio Pomba
Rio Preto
Rochedo de Minas
Rodeiro
Rosário da Limeira
Santa Bárbara do Monte Verde
Santa Rita de Jacutinga
Santana de Cataguases
Santana do Deserto
Santo Antônio do Aventureiro
Santos Dumont
São Francisco do Glória
São Geraldo
São João Nepomuceno
São Sebastião da Vargem Alegre
Senador Cortes
Senador Firmino
Silveirânia
Simão Pereira
Tabuleiro
Tocantins
Tombos
Ubá
Vieiras
Visconde do Rio Branco
Volta Grande
"""

CID_SUL_MINAS = """
Aguanil
Aiuruoca
Alagoa
Albertina
Alfenas
Alpinópolis
Alterosa
Andradas
Arceburgo
Areado
Baependi
Bandeira do Sul
Boa Esperança
Bom Jesus da Penha
Bom Repouso
Bom Sucesso
Borda da Mata
Botelhos
Brazópolis
Bueno Brandão
Cabo Verde
Cachoeira de Minas
Caldas
Camanducaia
Cambuí
Cambuquira
Campanha
Campestre
Campo Belo
Campo do Meio
Campos Gerais
Cana Verde
Candeias
Capetinga
Capitólio
Careaçu
Carmo da Cachoeira
Carmo de Minas
Carmo do Rio Claro
Carrancas
Carvalhópolis
Carvalhos
Cássia
Caxambu
Claraval
Conceição da Aparecida
Conceição das Pedras
Conceição do Rio Verde
Conceição dos Ouros
Congonhal
Consolação
Coqueiral
Cordislândia
Córrego do Bom Jesus
Cristais
Cristina
Cruzília
Delfim Moreira
Delfinópolis
Divisa Nova
Dom Viçoso
Doresópolis
Elói Mendes
Espírito Santo do Dourado
Estiva
Extrema
Fama
Fortaleza de Minas
Gonçalves
Guapé
Guaranésia
Guaxupé
Heliodora
Ibiraci
Ibitiúra de Minas
Ibituruna
Ijaci
Ilicínea
Inconfidentes
Ingaí
Ipuiúna
Itajubá
Itamogi
Itamonte
Itanhandu
Itapeva
Itaú de Minas
Itumirim
Itutinga
Jacuí
Jacutinga
Jesuânia
Juruaia
Lambari
Lavras
Luminárias
Machado
Maria da Fé
Marmelópolis
Minduri
Monsenhor Paulo
Monte Belo
Monte Santo de Minas
Monte Sião
Munhoz
Muzambinho
Natércia
Nepomuceno
Nova Resende
Olímpio Noronha
Ouro Fino
Paraguaçu
Paraisópolis
Passa Quatro
Passos
Pedralva
Perdões
Piranguçu
Piranguinho
Piumhi
Poço Fundo
Poços de Caldas
Pouso Alegre
Pouso Alto
Pratápolis
Ribeirão Vermelho
Santa Rita de Caldas
Santa Rita do Sapucaí
Santana da Vargem
Santana do Jacaré
Santo Antônio do Amparo
São Bento Abade
São Gonçalo do Sapucaí
São João Batista do Glória
São João da Mata
São José da Barra
São José do Alegre
São Lourenço
São Pedro da União
São Roque de Minas
São Sebastião da Bela Vista
São Sebastião do Paraíso
São Sebastião do Rio Verde
São Thomé das Letras
São Tomás de Aquino
Sapucaí-Mirim
Senador Amaral
Senador José Bento
Seritinga
Serrania
Serranos
Silvianópolis
Soledade de Minas
Tocos do Moji
Toledo
Três Corações
Três Pontas
Turvolândia
Vargem Bonita
Varginha
Virgínia
Wenceslau Braz
"""

CID_CAMPO_VERTENTES = """
Barbacena
Bom Sucesso
Camacho
Campo Belo
Cana Verde
Candeias
Carmo da Mata
Conceição da Barra de Minas
Ibituruna
Nazareno
Oliveira
Perdões
Ritápolis
Santana do Jacaré
Santo Antônio do Amparo
São Francisco de Paula
São João del Rei
São Tiago
"""

CID_ZONA_MATA = """
Acaiaca
Barra Longa
Dom Silvério
Guaraciaba
Jequeri
Oratórios
Piedade de Ponte Nova
Ponte Nova
Raul Soares
Rio Casca
Rio Doce
Santa Cruz do Escalvado
Santo Antônio do Grama
São Pedro dos Ferros
Sem-Peixe
Sericita
Urucânia
Vermelho Novo
Abre Campo
Alto Caparaó
Alto Jequitibá
Caparaó
Caputira
Chalé
Durandé
Lajinha
Luisburgo
Manhuaçu
Manhumirim
Martins Soares
Matipó
Pedra Bonita
Reduto
Santa Margarida
Santana do Manhuaçu
São João do Manhuaçu
São José do Mantimento
Simonésia
Alto Rio Doce
Amparo da Serra
Araponga
Brás Pires
Cajuri
Canaã
Cipotânea
Coimbra
Ervália
Lamim
Paula Cândido
Pedra do Anta
Piranga
Porto Firme
Presidente Bernardes
Rio Espera
São Miguel do Anta
Senhora de Oliveira
Teixeiras
Viçosa
Antônio Prado de Minas
Barão de Monte Alto
Caiana
Carangola
Divino
Espera Feliz
Eugenópolis
Faria Lemos
Fervedouro
Miradouro
Miraí
Muriaé
Orizânia
Patrocínio do Muriaé
Pedra Dourada
Rosário da Limeira
São Francisco do Glória
São Sebastião da Vargem Alegre
Tombos
Vieiras
Astolfo Dutra
Divinésia
Dores do Turvo
Guarani
Guidoval
Guiricema
Mercês
Piraúba
Rio Pomba
Rodeiro
São Geraldo
Senador Firmino
Silveirânia
Tabuleiro
Tocantins
Ubá
Visconde do Rio Branco
Aracitaba
Belmiro Braga
Bias Fortes
Bicas
Chácara
Chiador
Coronel Pacheco
Descoberto
Ewbank da Câmara
Goianá
Guarará
Juiz de Fora
Lima Duarte
Mar de Espanha
Maripá de Minas
Matias Barbosa
Olaria
Oliveira Fortes
Paiva
Pedro Teixeira
Pequeri
Piau
Rio Novo
Rio Preto
Rochedo de Minas
Santa Bárbara do Monte Verde
Santa Rita de Ibitipoca
Santa Rita de Jacutinga
Santana do Deserto
Santos Dumont
São João Nepomuceno
Senador Cortes
Simão Pereira
Além Paraíba
Argirita
Cataguases
Dona Eusébia
Estrela Dalva
Itamarati de Minas
Laranjal
Leopoldina
Palma
Pirapetinga
Recreio
Santana de Cataguases
Santo Antônio do Aventureiro
Volta Grande
"""


# ---------------------------------------------------------------------
# Estruturas de mapeamento
# ---------------------------------------------------------------------

MAP_REGIOES: Dict[str, List[str]] = {
    "noroeste": _parse_cidades(CID_NOROESTE),
    "norte": _parse_cidades(CID_NORTE),
    "jequitinhonha": _parse_cidades(CID_JEQUITINHONHA),
    "vale_mucuri": _parse_cidades(CID_VALE_MUCURI),
    "triangulo_mineiro": _parse_cidades(CID_TRIANGULO_MINEIRO),
    "centro": _parse_cidades(CID_CENTRO),
    "belo_horizonte": _parse_cidades(CID_BELO_HORIZONTE),
    "vale_rio_doce": _parse_cidades(CID_VALE_RIO_DOCE),
    "oeste": _parse_cidades(CID_OESTE),
    "sudoeste": _parse_cidades(CID_SUDOESTE),
    "sul_minas": _parse_cidades(CID_SUL_MINAS),
    "campo_vertentes": _parse_cidades(CID_CAMPO_VERTENTES),
    "zona_mata": _parse_cidades(CID_ZONA_MATA),
}

MAP_NOME_REGIAO: Dict[str, str] = {
    "noroeste": "Noroeste de Minas",
    "norte": "Norte de Minas",
    "jequitinhonha": "Vale do Jequitinhonha",
    "vale_mucuri": "Vale do Mucuri",
    "triangulo_mineiro": "Triâng. Min. e Alto Paran.",
    "centro": "Centro de Minas",
    "belo_horizonte": "Metrop. de Belo Horizonte",
    "vale_rio_doce": "Vale do Rio Doce",
    "oeste": "Oeste de Minas",
    "sudoeste": "Sudoeste de Minas",
    "sul_minas": "Sul de Minas",
    "campo_vertentes": "Campo das Vertentes",
    "zona_mata": "Zona da Mata",
    "outra": "Outra / não classificada",
}


# ---------------------------------------------------------------------
# Funções públicas
# ---------------------------------------------------------------------

def atribuir_regiao(municipio: str) -> str:
    """
    Retorna a chave da região correspondente a um município mineiro.

    Parameters
    ----------
    municipio : str
        Nome do município.

    Returns
    -------
    str
        Identificador interno da região. Caso o município não seja encontrado,
        retorna `"outra"`.
    """
    m = _norm(municipio)

    for regiao, cidades in MAP_REGIOES.items():
        if m in cidades:
            return regiao

    return "outra"