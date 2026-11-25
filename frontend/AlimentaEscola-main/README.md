# AlimentaEscola

Protótipo acadêmico para apoiar o planejamento da alimentação escolar por meio da estimativa da demanda por refeições.

## Tecnologias

- Python
- Streamlit
- Pandas
- Scikit-learn
- Requests

## Estrutura

- `presentation/`: interface Streamlit, páginas e estilos.
- `application/`: casos de uso.
- `domain/`: entidades e contratos do domínio.
- `infrastructure/`: acesso a dados e comunicação com a API.
- `assets/`: recursos visuais.
- `tests/`: testes automatizados.

## Executar

Instale as dependências com `pip install -r requirements.txt` e execute `python -m streamlit run presentation/app.py` a partir da pasta raiz.

## Integração com a API

Configure `API_BASE_URL` no ambiente ou em um arquivo `.env` local, utilizando `.env.example` como referência. O cliente HTTP mantém uma sessão `requests.Session` para reaproveitar cookies entre chamadas. Os contratos das rotas serão ajustados após o recebimento dos exemplos oficiais da API.

## Observação acadêmica

Os indicadores exibidos na visão geral são ilustrativos. A previsão real depende da integração com a API e os modelos de Machine Learning da equipe.
