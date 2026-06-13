# DSE Make Money (Digital Family Office)

![Versão](https://img.shields.io/badge/vers%C3%A3o-v1.2.0-blueviolet)

Este projeto estabelece a arquitetura fundacional e o código para o **DSE Make Money**, focado em gerenciamento de patrimônio familiar, com rebalanceamento de ativos de alta frequência (B3 & Crypto), ativos ilíquidos (Imóveis/FIIs) e tesouraria de baixo risco (Renda Fixa/CDBs).

---

## 1. Arquitetura do Sistema

O sistema é desenhado de forma desacoplada seguindo uma arquitetura orientada a serviços e pipelines de dados (Workers):

```
                                      ┌────────────────┐
                                      │  MetaTrader 5  │ B3 Trade
                                      └───────┬────────┘
                                              │
┌─────────────────┐  SGS API          ┌───────▼────────┐      ┌─────────────┐
│  Banco Central  ├──────────────────►│   cdi_worker   ├─────►│             │
└─────────────────┘                   └────────────────┘      │             │
                                                              │             │
┌─────────────────┐  yfinance / BS4   ┌────────────────┐      │  PostgreSQL │
│ FIIs / Portais  ├──────────────────►│  re_worker     ├─────►│     &       │
└─────────────────┘                   └────────────────┘      │ TimescaleDB │
                                                              │   (Hybrid)  │
┌─────────────────┐  ccxt / web3.py   ┌────────────────┐      │             │
│ Crypto / DeFi   ├──────────────────►│  crypto_worker ├─────►│             │
└─────────────────┘                   └────────────────┘      │             │
                                                              │             │
┌─────────────────┐  Open Finance     ┌────────────────┐      │             │
│ Broker Shelves  ├──────────────────►│ fi_scraper     ├─────►│             │
└─────────────────┘                   └────────────────┘      └──────┬──────┘
                                                                     │
                                      ┌────────────────┐             │
                                      │  Streamlit UI  │◄────────────┘
                                      │  (Dashboard)   │
                                      └────────────────┘
```

- **Módulos Ingestion (Workers)**: Roteiros dedicados para extrair dados em frequências específicas (milissegundos para Crypto/B3 e diário para CDBs/CDI/Selic).
- **Core Engine (Risk & Rebalancer)**: Lógica quantitativa que monitora o *drawdown* e gerencia o *Treasury Sweep* (transferência de lucros de trading de alta frequência para CDBs de baixo risco).
- **Database Layer**: Modelo híbrido utilizando **SQL Relacional** tradicional para controle transacional/auditoria (carteira, saldos, transações) e **Tabelas Temporais (Time-Series)** para cotações e curvas de juros históricas.

---

## 2. Fórmulas Quantitativas Implementadas

### 2.1. Taxa CDI Anualizada
A taxa CDI diária fornecida pelo Banco Central do Brasil (SGS Série 12) é expressa em percentual ao dia ($d$). A capitalização anualizada correspondente baseada no ano padrão de 252 dias úteis é dada por:

$$\text{CDI}_{\text{anual}} = \left( \left(1 + \frac{d}{100}\right)^{252} - 1 \right) \times 100$$

### 2.2. Equivalência Tributária (Grossing-Up)
Para comparar de forma justa ativos isentos de Imposto de Renda (LCI/LCA) com CDBs (tributáveis), calculamos o **CDB Equivalente Bruto** utilizando a tabela regressiva do IR com base nos dias até o vencimento ($t$):

$$\text{Taxa CDB Equivalente} = \frac{\text{Taxa LCI/LCA}}{1 - \text{Alíquota IR}}$$

Onde a alíquota de IR é definida por:
- $t \le 180$ dias: $22.5\%$
- $181 \le t \le 360$ dias: $20.0\%$
- $361 \le t \le 720$ dias: $17.5\%$
- $t > 720$ dias: $15.0\%$

---

## 3. Estrutura de Diretórios Criada

```
dse_make_money/
├── config/                  # Configurações do ambiente e parâmetros de risco
│   └── settings.py
├── database/                # Conexões e esquemas DDL (Relacional + Time-Series)
│   ├── connection.py
│   └── schemas.sql
├── core/                    # Motores de risco e plano de rebalanceamento
│   ├── risk_manager.py
│   └── rebalancer.py
├── workers/                 # Serviços de ingestão de dados e raspagem
│   ├── cdi_worker.py        # Worker funcional do CDI (SGS API)
│   ├── b3_worker.py         # Stub MetaTrader5
│   ├── crypto_worker.py     # Stub ccxt/web3.py
│   ├── real_estate_worker.py# Stub BS4/yfinance
│   └── fixed_income_scraper.py # Classificador de taxas de CDB/LCI/LCA
└── dashboard/               # Interface visual Streamlit
    └── app.py
```

---

## 4. Instruções de Execução

### 4.1. Instalação das Dependências
Instale os pacotes básicos usando o `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 4.2. Rodar o Worker de CDI
Execute o script no terminal para buscar a taxa CDI atual do Banco Central:
```bash
python dse_make_money/workers/cdi_worker.py
```

### 4.3. Iniciar o Dashboard Streamlit
Para inicializar o painel visual e ver o rebalanceamento de carteira interativo e o ranking de CDBs equivalentes em tempo real:
```bash
streamlit run dse_make_money/dashboard/app.py
```

---

## 👥 Colaboradores

Atualmente, o projeto é mantido e desenvolvido por:
* **Fernando Torres Ferreira Silva** ([@fertorresfs](https://github.com/fertorresfs)) — Idealizador e desenvolvedor ativo, responsável pela arquitetura do bot, integração de RAG, segurança e painel administrativo web.

---

## ⚖️ Licença

Este projeto é de uso interno e educacional da comunidade **Data Science Enthusiasts (DSE)**. Consulte as políticas internas de contribuição antes de realizar pull requests.
