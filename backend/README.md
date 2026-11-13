# Alimenta Escola — Backend em camadas

Esta versão reorganiza o backend em Controllers, Services, Schemas, Domain, Repositories, Infrastructure e Machine Learning. O nome das tabelas e colunas segue a documentação técnica atualizada do banco `alimenta_escola` (MySQL 8.0.16+).

## Estrutura

```text
backend/
├── app/
│   ├── controllers/       # rotas HTTP/Blueprints
│   ├── services/          # regras e orquestração de negócio
│   ├── schemas/           # validação de entrada
│   ├── domain/            # entidades e exceções
│   ├── repositories/      # contratos e implementação MySQL
│   ├── infrastructure/    # configuração e conexão
│   └── machine_learning/  # treinamento, modelo e inferência
├── tests/
├── .env.example
├── requirements.txt
└── run.py
```

## Instalação no Windows

Abra o terminal na pasta `backend`:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edite `.env` com o usuário e a senha do MySQL. Não compartilhe o `.env` e não o envie ao Git.

## Executar

```powershell
python run.py
```

API local: `http://127.0.0.1:5000`

## Rotas desta base

- `GET /` — status da API.
- `GET /api/saude` — testa conexão MySQL.
- `GET /api/historico?id_escola=1` — histórico agregado por escola/data/turno. O filtro é opcional.
- `GET /api/indicadores?id_escola=1` — indicadores de produção e sobras.
- `POST /api/modelo/treinar` — treina e salva o modelo.
- `POST /api/previsao` — calcula e persiste previsão.

Exemplo de previsão antecipada:

```json
{
  "id_escola": 1,
  "data": "2026-11-13",
  "turno": "MANHÃ",
  "tipo_previsao": "ANTECIPADA",
  "cardapio": "Arroz, feijão e frango"
}
```

Quando `alunos_referencia` não é enviado, o service estima a referência usando matrículas ativas e a taxa histórica de presença daquele turno. Sem histórico de presença, usa a matrícula ativa como referência; essa é uma regra de contingência, não uma previsão de presença por ML.

Exemplo de previsão atualizada após a confirmação da frequência:

```json
{
  "id_escola": 1,
  "data": "2026-11-13",
  "turno": "MANHÃ",
  "alunos_referencia": 43,
  "tipo_previsao": "ATUALIZADA",
  "cardapio": "Arroz, feijão e frango"
}
```

## Como os dados chegam ao Machine Learning

O repositório primeiro agrega `presencas` por escola, data e turno; depois associa o cardápio e `registros_merenda`. A consulta agrega as presenças antes do JOIN com a merenda para evitar duplicar valores de refeições quando há várias turmas no mesmo turno. O alvo inicial do modelo é `refeicoes_servidas`, que é uma aproximação operacional e não necessariamente a demanda ideal.

O treinamento exige pelo menos 10 registros históricos válidos nesta implementação. Com menos registros, a previsão usa uma média histórica por aluno. Isso é uma regra inicial de contingência, não uma garantia de precisão. Avalie o modelo com dados reais separados do treinamento e valide a variável-alvo com a equipe escolar.

## Limites e próximos ajustes

- Esta é uma refatoração inicial da arquitetura, não uma auditoria completa de produção.
- O CRUD de escolas, turmas, cardápios, presenças e registros de merenda ainda deve ser implementado em módulos próprios, conforme as telas e requisitos do frontend.
- A regra de não sobreposição de períodos em `historico_turmas` exige validação transacional adicional ao implementar alteração de matrícula.
- Configure `CORS_ORIGINS` com o endereço do frontend antes de publicar.
- Não exponha o servidor Flask de desenvolvimento na internet.
