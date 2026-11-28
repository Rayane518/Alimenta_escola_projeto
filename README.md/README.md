# Alimenta Escola

Sistema acadêmico de previsão de demanda de merenda escolar, desenvolvido para auxiliar o planejamento das refeições e reduzir o desperdício de alimentos.

## Tecnologias

- Python 3.12.10 (versão de referência)
- Flask (API REST)
- Streamlit (interface)
- MariaDB 10.4.32 (banco utilizado no desenvolvimento)
- pandas, scikit-learn e joblib (Machine Learning)

## Estrutura

```text
Alimenta_escola_projeto/
├── backend/
├── database/
│   └── alimenta_escola.sql
├── frontend/
│   └── AlimentaEscola-main/
│       └── presentation/app.py
└── README.md
```

## 1. Pré-requisitos

Instale Python 3.12, Git e MariaDB Server. O MySQL Workbench pode ser utilizado para importar o banco. A compatibilidade com outros servidores ou versões ainda precisa ser validada.

## 2. Baixar o projeto

No Prompt de Comando (CMD) do Windows:

```cmd
git clone https://github.com/Rayane518/Alimenta_escola_projeto.git
cd Alimenta_escola_projeto
```

## 3. Importar o banco

Inicie o serviço MariaDB. No MySQL Workbench, conecte-se ao servidor local, abra Server > Data Import, selecione Import from Self-Contained File e escolha `database/alimenta_escola.sql`. Inicie a importação.

Alternativamente, no CMD, com o cliente MariaDB disponível no PATH:

```cmd
mariadb -u root -p < database\alimenta_escola.sql
```

Se o cliente instalado se chamar `mysql`, substitua `mariadb` por `mysql`. Informe a senha local do banco quando solicitada.

**Atenção:** utilize uma instalação limpa. O script contém comandos DROP TABLE e pode substituir tabelas existentes do banco `alimenta_escola`. Faça backup antes de importar sobre uma instalação existente.

O script inclui a escola e o gestor fictícios, turmas, cardápios, frequência, refeições e histórico de previsões.

## 4. Configurar e iniciar o backend

Na raiz do projeto, execute no CMD:

```cmd
cd backend
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m pip check
if not exist .env copy .env.example .env
.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))"
```

Abra o `.env`, configure as credenciais locais do MariaDB e copie a chave gerada para SECRET_KEY. Preserve as demais configurações do `.env.example`, incluindo os caminhos dos modelos definidos pelo código.

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
CORS_ORIGINS=http://localhost:8501,http://127.0.0.1:8501
SESSION_COOKIE_SECURE=false
```

Preencha DB_PASSWORD com a senha do seu servidor (deixe vazia somente se a instalação local não exigir senha) e SECRET_KEY com a chave gerada. Não publique o `.env`.

```cmd
.venv\Scripts\python.exe run.py
```

Mantenha o terminal aberto. Verifique a resposta da API em http://127.0.0.1:5000/.

## 5. Treinar os modelos

Caso os arquivos `.joblib` não estejam disponíveis, treine os modelos após importar o banco. Com o backend em execução, utilize o endpoint autenticado de treinamento. Em outro CMD, na pasta backend, execute `.venv\Scripts\python.exe` e informe:

```python
import requests
s = requests.Session()
r = s.post('http://127.0.0.1:5000/api/login', json={'email': 'gestorpaulo@gmail.com', 'senha': 'Gestorp@ulo1'}, timeout=30)
print(r.status_code, r.text)
r.raise_for_status()
r = s.post('http://127.0.0.1:5000/api/modelo/treinar', json={'id_escola': 1}, timeout=300)
print(r.status_code, r.text)
r.raise_for_status()
```

O exemplo considera o ID 1 da escola de demonstração. Ao terminar, digite `exit()` para sair do Python. Confira o contrato atual da API caso o login ou treinamento retorne erro de validação. Aguarde a conclusão e verifique as métricas e os arquivos gerados. Não prossiga se o treinamento falhar.

## 6. Configurar e iniciar o frontend

Abra outro CMD na raiz do projeto:

```cmd
cd frontend\AlimentaEscola-main
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m pip check
if not exist .env copy .env.example .env
```

Configure o `.env` do frontend com `API_BASE_URL=http://127.0.0.1:5000`, sem acrescentar `/api`.

```cmd
.venv\Scripts\python.exe -m streamlit run presentation/app.py
```

Acesse http://localhost:8501. Mantenha ambos os terminais abertos.

## 7. Credenciais de demonstração

- E-mail: `gestorpaulo@gmail.com`
- Senha: `Gestorp@ulo1`

Conta fictícia exclusiva para demonstração local. Não reutilize essa senha em outros serviços. O cadastro pela interface não está integrado nesta versão; o gestor já está cadastrado no banco importado.

## 8. Utilizar o sistema

Faça login, acesse a tela de demanda de refeições, selecione data e turno e informe os campos solicitados. A previsão utiliza o histórico de presença e refeições, matrícula, dia da semana, turno e cardápio conforme o modelo. A margem de segurança configurável de 0 a 20% complementa a previsão de refeições. Consulte o histórico e os indicadores disponíveis.

## Machine Learning

O projeto utiliza dois modelos RandomForestRegressor: estimativa de presença e previsão de refeições servidas. O treinamento utiliza divisão temporal para avaliação por MAE (erro absoluto médio), seguida de treinamento com todo o histórico válido. As previsões antecipadas não dependem da presença real do próprio dia. Os resultados são estimativas, não garantias de consumo.

## Segurança e limitações

- Senhas armazenadas como hash; autenticação por sessão Flask.
- Uma escola e um gestor principal por instalação.
- Dados de demonstração; não utilizar como ambiente de produção.
- Cadastro inicial administrativo; cadastro pela interface não integrado.
- Retreinamento automático não implementado.
- Não publicar arquivos `.env`, ambientes virtuais ou credenciais reais.

## Solução de problemas

- Falha de conexão: verifique o serviço MariaDB, porta 3306 e credenciais do `.env`.
- Falha de login: confira a importação e a comunicação com a API.
- Modelo ausente: execute o treinamento e confira os caminhos dos arquivos.
- Frontend indisponível: verifique o diretório de execução e as dependências.
- Porta ocupada: libere a porta ou ajuste as configurações correspondentes.

## Validação da instalação

As instruções devem ser verificadas em um segundo computador com instalação limpa. Confirme importação, login, treinamento, previsão e persistência no histórico. As configurações e rotas de autenticação foram revisadas, mas a instalação limpa e a integração de todas as telas ainda precisam ser verificadas.

## Documentação técnica

- [Backend e Machine Learning](backend/README.md)
- [Frontend](frontend/AlimentaEscola-main/README.md)
