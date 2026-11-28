# Alimenta Escola — Backend e Machine Learning

O Alimenta Escola é um sistema acadêmico de apoio ao planejamento da alimentação escolar. Estima a demanda de refeições por data e turno para auxiliar na redução do desperdício. O backend disponibiliza uma API REST para o frontend Streamlit e integra o banco de dados aos modelos de Machine Learning.

## Tecnologias

- Python 3.12.10 e Flask
- MariaDB 10.4.32 (servidor utilizado no desenvolvimento), com MySQL Workbench como ferramenta administrativa
- mysql-connector-python, pandas, scikit-learn e joblib
- Random Forest Regressor
- pytest para testes

As versões das bibliotecas estão especificadas em `requirements.txt`. A compatibilidade com outros servidores MySQL deve ser testada.

## Arquitetura

```text
backend/
├── app/
│   ├── controllers/       # Rotas HTTP e Blueprints
│   ├── services/          # Regras de negócio
│   ├── schemas/           # Validação de entradas
│   ├── domain/            # Entidades e exceções
│   ├── repositories/      # Acesso aos dados
│   ├── infrastructure/    # Configuração e conexão
│   └── machine_learning/  # Treinamento e inferência
├── tests/
├── .env.example
├── requirements.txt
└── run.py
```

Fluxo: frontend → controllers → schemas/services → repositories e Machine Learning → resposta da API. Os repositories acessam o banco relacional.

## Instalação no Windows

### 1. Obter o projeto

```powershell
git clone https://github.com/Rayane518/Alimenta_escola_projeto.git
cd Alimenta_escola_projeto
```

### 2. Banco de dados

Instale e inicie um servidor MariaDB local. Importe `database/alimenta_escola.sql` utilizando o MySQL Workbench (Server > Data Import > Import from Self-Contained File) ou o cliente de linha de comando. O script cria o banco `alimenta_escola`, suas tabelas, view e dados de demonstração, incluindo escola, turmas, histórico e gestor fictícios.

**Atenção:** o script contém comandos DROP TABLE. Utilize uma instalação separada, sem dados importantes. Não importe sobre um banco existente sem backup.

### 3. Ambiente Python

Na raiz do repositório, execute no PowerShell:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
Copy-Item .env.example .env
```

Os comandos utilizam diretamente o Python do ambiente virtual, dispensando sua ativação. O resultado esperado do pip check é `No broken requirements found.`

### 4. Configuração local

Edite `.env` seguindo o `.env.example` distribuído. Exemplo:

```dotenv
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=alimenta_escola
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
FLASK_DEBUG=false
SECRET_KEY=
SESSION_COOKIE_SECURE=false
CORS_ORIGINS=http://localhost:8501,http://127.0.0.1:8501
```

Informe as credenciais do servidor local. Preserve as demais variáveis de caminhos dos modelos conforme o `.env.example` vigente. Gere uma chave de sessão exclusiva:

```powershell
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))"
```

Copie o resultado para `SECRET_KEY` no `.env`. Nunca publique esse arquivo. A configuração de cookie sem HTTPS é destinada somente ao ambiente local.

### 5. Executar o backend

```powershell
.\.venv\Scripts\python.exe run.py
```

Acesse http://127.0.0.1:5000 para verificar o status da API. Mantenha o terminal aberto durante a utilização do frontend. Cada computador executa seu próprio banco e backend.

## Autenticação e segurança

O gestor é autenticado por sessão Flask (cookies) e vinculado à escola. As rotas protegidas utilizam a identificação da escola na sessão. O frontend reutiliza um `requests.Session()` armazenado no estado da sessão Streamlit.

A conta fictícia já está cadastrada no SQL. Consulte as credenciais de demonstração no README geral. Não reutilize essa conta em produção. O cadastro inicial é administrativo; o cadastro pela interface não está integrado nesta versão.

A política de senha prevê 8 a 20 caracteres, pelo menos uma maiúscula, uma minúscula, um número e um caractere especial, sem espaços, e confirmação no cadastro. As senhas são armazenadas como hashes. Configure CORS com origens específicas, preserve os cookies nas requisições e não exponha o servidor Flask de desenvolvimento à internet.

## Rotas da API

| Método | Rota | Finalidade |
|---|---|---|
| GET | `/` | Status da API |
| GET | `/api/saude` | Verificação da conexão com o banco |
| POST | `/api/login` | Autenticação |
| POST | `/api/logout` | Encerramento da sessão |
| GET | `/api/me` | Usuário autenticado |
| GET | `/api/historico` | Histórico agregado de frequência e merenda |
| GET | `/api/indicadores` | Indicadores de produção e sobras |
| POST | `/api/modelo/treinar` | Treinamento dos modelos |
| POST | `/api/previsao` | Geração e persistência da previsão |
| GET, PUT | `/api/escola` | Consulta e atualização da escola |
| GET, POST, PUT | `/api/turmas` | Gerenciamento de turmas, conforme rota específica |

As rotas de negócio exigem autenticação. A tabela acima não é um inventário exaustivo: consulte controllers e schemas para confirmar caminhos específicos, incluindo atualização de turmas, cardápios, registros de merenda, histórico de previsões e campos JSON. O histórico de previsões é distinto do histórico de frequência e merenda.

## Machine Learning

São utilizados dois modelos RandomForestRegressor:

| Modelo | Entradas | Alvo |
|---|---|---|
| Presença | Alunos previstos, dia da semana, turno | Alunos presentes |
| Refeições | Alunos presentes (estimados na previsão antecipada), dia da semana, turno, cardápio | Refeições servidas |

Os registros de presença são agregados por escola, data e turno antes da associação aos registros de merenda, evitando duplicação por turma. A preparação valida os valores numéricos e utiliza codificação OneHotEncoder para variáveis categóricas, com tratamento de categorias desconhecidas.

Na implementação revisada, ambos os modelos utilizam 150 árvores, `random_state=42` e `min_samples_leaf=2`. O treinamento exige pelo menos 10 registros válidos e 5 datas distintas. A divisão temporal utiliza aproximadamente 80% das datas para treino e 20% para teste. O MAE (erro absoluto médio) é calculado no teste:

`MAE = soma dos erros absolutos / quantidade de previsões avaliadas`

Após a avaliação, os modelos são treinados com todo o histórico válido e armazenados em arquivos joblib:

```text
app/machine_learning/models/
├── presenca/modelo_presenca.joblib
└── refeicoes/modelo_merenda.joblib
```

### Treinar em uma nova instalação

Os modelos gerados não precisam ser versionados. Após importar o SQL e iniciar a API, autentique-se e solicite o treinamento pela rota `POST /api/modelo/treinar`. Exemplo em Python, executado no ambiente do backend:

```python
import requests

base = "http://127.0.0.1:5000"
with requests.Session() as sessao:
    login = sessao.post(base + "/api/login", json={
        "email": input("E-mail do gestor fictício: "),
        "senha": input("Senha de demonstração: ")
    }, timeout=30)
    login.raise_for_status()
    treino = sessao.post(base + "/api/modelo/treinar",
                         json={"id_escola": 1}, timeout=300)
    print(treino.status_code, treino.text)
    treino.raise_for_status()
```

O exemplo considera a escola de demonstração de ID 1 e o contrato de treinamento anteriormente utilizado. Confirme o schema vigente se houver erro de validação. Confira as métricas retornadas e os arquivos gerados antes de solicitar previsões.

### Previsão antecipada

O gestor informa data, turno, cardápio e margem conforme os campos aceitos pela API. A escola é identificada pela sessão. A previsão antecipada não depende da presença real nem das refeições servidas no próprio dia. Utiliza a matrícula ativa e a estimativa de presença, com regras de contingência conforme a implementação.

A frequência real não deve ser informada manualmente pelo gestor ou professor. Uma previsão atualizada depende de fonte confiável de frequência, cuja integração não está confirmada nesta versão.

### Margem de segurança

A margem configurável de 0% a 20% é aplicada sobre a previsão de refeições, preservando o resultado original do modelo.

`Total recomendado = refeições previstas × (1 + margem percentual / 100)`

Exemplo: 100 refeições previstas e margem de 10% resultam em 110 refeições recomendadas. O arredondamento segue a implementação do service. São registradas a estimativa de alunos, a previsão de refeições, a margem e a recomendação.

## Indicadores

Refeições preparadas, servidas, sobras e percentual de sobras em relação à quantidade preparada.

## Testes

Use somente o banco de demonstração. Com o ambiente configurado, consulte os testes disponíveis em `tests/` antes de executá-los. Utilize Postman ou scripts Python preservando a sessão autenticada.

- Verificar status da API e conexão com o banco.
- Testar login válido e inválido, consulta de usuário e logout.
- Verificar bloqueio de rotas protegidas sem autenticação.
- Treinar modelos e conferir métricas e arquivos.
- Gerar previsão e verificar persistência.
- Testar margem inválida e turno inválido.
- Consultar indicadores e histórico.
- Validar integração com o frontend.

A instalação completa em outro computador ainda deve ser validada.

## Escopo e limitações

- Uma escola por instalação, com gestor principal.
- Previsões por turno (manhã e tarde).
- Versão acadêmica de demonstração, não homologada para produção.
- Cadastro de gestor pela interface, retreinamento automático, múltiplas escolas e integração automática de frequência não fazem parte das funcionalidades confirmadas nesta versão.
- Dados fictícios demonstram funcionamento, mas não comprovam precisão em escolas reais.
- Refeições servidas são uma aproximação da demanda, não necessariamente da demanda ideal.
- A previsão auxilia decisões, sem garantir o consumo futuro.

Consulte o [README geral](../README.md) para instruções de execução conjunta com o frontend.
