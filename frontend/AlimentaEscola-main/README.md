# Alimenta Escola — Frontend

O Alimenta Escola é um protótipo acadêmico de apoio ao planejamento da alimentação escolar. A interface permite ao gestor interagir com o sistema de estimativa de demanda de refeições por data e turno, buscando reduzir desperdícios.

## Tecnologias

Ambiente utilizado no desenvolvimento:

- Python 3.12.10
- Streamlit 1.67.0
- pandas 3.1.1
- scikit-learn 1.9.1
- requests 2.34.2
- python-dotenv 1.2.4

As dependências estão especificadas em `requirements.txt`. O treinamento e a inferência dos modelos oficiais são responsabilidades do backend.

## Estrutura

```text
frontend/AlimentaEscola-main/
├── .streamlit/
├── application/       # Casos de uso
├── assets/            # Recursos visuais
├── domain/            # Entidades e contratos
├── infrastructure/   # Acesso a dados e comunicação com a API
│   └── api/
│       ├── api_client.py
│       └── auth_api.py
├── presentation/      # Interface, páginas e estilos
│   └── app.py         # Entrada do Streamlit
├── tests/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Pré-requisitos

- Python 3.12 (versão de referência: 3.12.10).
- Banco de demonstração importado conforme o README geral do repositório.
- Backend Flask configurado e em execução.
- Modelos treinados no backend para utilizar as previsões.

## Instalação no Windows

A partir da raiz do repositório, abra o PowerShell e execute:

```powershell
cd frontend/AlimentaEscola-main
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
Copy-Item .env.example .env
```

Caso já exista um `.env`, preserve-o e confira sua configuração em vez de sobrescrevê-lo. Os comandos utilizam diretamente o Python do ambiente virtual, sem exigir sua ativação.

## Configuração da API

No arquivo `.env` do frontend, configure:

```dotenv
API_BASE_URL=http://127.0.0.1:5000
```

Esse endereço deve corresponder ao backend. Não acrescente `/api` ao final da variável, pois as funções de autenticação já incluem esse prefixo nas rotas.

O frontend não precisa receber a senha do banco de dados nem a chave secreta do Flask. Essas configurações pertencem ao backend.

## Executar o sistema

1. Inicie o serviço MySQL/MariaDB e confirme a importação do banco de demonstração.
2. Inicie o backend conforme as instruções de `backend/README.md`, em um terminal separado.
3. Na pasta `frontend/AlimentaEscola-main`, execute:

```powershell
.\.venv\Scripts\python.exe -m streamlit run presentation/app.py
```

Se estiver utilizando um ambiente Python já configurado com as dependências, também é possível executar:

```powershell
python -m streamlit run presentation/app.py
```

Acesse http://localhost:8501 (ou o endereço informado pelo Streamlit no terminal). Mantenha o backend e o frontend em execução durante a utilização.

## Integração com o backend

```text
Interface Streamlit → API Flask → Banco MySQL/MariaDB e Machine Learning
```

O arquivo `infrastructure/api/api_client.py` utiliza `requests.Session()` para preservar cookies e mantém o cliente em `st.session_state` entre reexecuções da interface. O endereço da API é obtido do ambiente, com valor padrão `http://127.0.0.1:5000`. O timeout padrão é de 30 segundos.

O arquivo `infrastructure/api/auth_api.py` implementa as seguintes chamadas:

| Método | Rota | Finalidade |
|---|---|---|
| POST | `/api/login` | Autenticar o gestor |
| GET | `/api/me` | Consultar o usuário autenticado |
| POST | `/api/logout` | Encerrar a sessão |

As demais rotas de negócio e seus contratos devem ser consultados na documentação do backend e nos respectivos controllers e schemas.

## Acesso de demonstração

Utilize a conta fictícia previamente cadastrada no banco de demonstração, conforme as credenciais disponibilizadas nas instruções gerais do projeto. Não utilize dados pessoais reais nem reutilize a senha demonstrativa em outros serviços.

O cadastro inicial do gestor é administrativo; o cadastro pela interface não está integrado nesta versão. Não é necessário cadastrar uma nova escola para demonstrar o sistema.

## Previsões e indicadores

A finalidade da interface é permitir a consulta de previsões por data e turno, com estimativa de presença, previsão de refeições, margem de segurança e total recomendado, conforme os recursos disponibilizados pela API.

Os modelos de Machine Learning são executados no backend. A integração das telas de previsão, histórico e indicadores deve ser validada em teste integrado. Valores ilustrativos eventualmente presentes nas telas não devem ser interpretados como resultados reais da API.

## Solução de problemas

| Problema | Verificação |
|---|---|
| Erro de conexão com a API | Confirme se o Flask está em execução e se `API_BASE_URL` está correto. |
| Erro de autenticação (401) | Confira as credenciais de demonstração e faça login novamente. |
| Dependência não encontrada | Instale `requirements.txt` no mesmo ambiente Python utilizado para executar o Streamlit. |
| Previsão indisponível | Confira o histórico importado, o treinamento dos modelos e a resposta da API. |
| Porta 8501 ocupada | Consulte o endereço informado pelo Streamlit ou utilize `--server.port 8502`. |

## Testes de instalação

- Confirmar que `pip check` não apresenta conflitos.
- Abrir a interface e autenticar o gestor fictício.
- Consultar o usuário autenticado e navegar entre as telas.
- Solicitar uma previsão e conferir a resposta do backend e a persistência no banco.
- Conferir histórico e indicadores, distinguindo valores ilustrativos de dados da API.
- Realizar logout e verificar o bloqueio de operações protegidas.

## Segurança e limitações

- Não publicar `.env`, ambientes virtuais ou arquivos com credenciais privadas.
- Utilizar exclusivamente dados fictícios na demonstração pública.
- Uma escola por instalação, com gestor principal.
- Previsões por turno: manhã e tarde.
- A versão acadêmica não está homologada para produção.
- A instalação em outro computador e a integração completa das telas precisam de validação prática.

Para configurar o banco, executar o backend e treinar os modelos, consulte o README geral e o README do backend.
