from pathlib import Path
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from app.infrastructure.config import load_config
from app.domain.exceptions.business_error import BusinessError

class MealDemandModel:
    """Treina/usa modelo de demanda com histórico agregado por escola, data e turno."""

    def __init__(self):
        config = load_config()

        caminho_original = Path(config["MODEL_PATH"])

        pasta_modelos = caminho_original.parent

        self.model_path = (
            pasta_modelos / "refeicoes" / "modelo_merenda.joblib"
        )

        self.attendance_model_path = (
            pasta_modelos / "presenca" / "modelo_presenca.joblib"
        )

    @staticmethod
    def _prepare(history):
        df = pd.DataFrame(history)
        if df.empty:
            raise BusinessError("Não há histórico para treinar ou prever.")
        df["data"] = pd.to_datetime(df["data"], errors="coerce")
        for col in ("alunos_presentes", "alunos_previstos", "refeicoes_servidas"):
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df["dia_semana"] = df["data"].dt.dayofweek
        df["turno"] = df["turno"].astype(str)
        df["cardapio"] = df["cardapio"].fillna("não informado").astype(str)
        return df.dropna(
            subset=[
                "data",
                "alunos_previstos",
                "alunos_presentes",
                "refeicoes_servidas"
            ]
        ).query(
            "alunos_previstos >= 0 and "
            "alunos_presentes >= 0 and "
            "refeicoes_servidas >= 0 and "
            "alunos_presentes <= alunos_previstos"
        )
    @staticmethod
    def _features(df):
        return df[["alunos_presentes", "dia_semana", "turno", "cardapio"]].copy()
    
    @staticmethod
    def _attendance_features(df):
        return df[
            [
                "alunos_previstos",
                "dia_semana",
                "turno"
            ]
        ].copy()
    
    def train_attendance(self, history):
        df = self._prepare(history)

        if len(df) < 10:
            raise BusinessError(
                "Histórico insuficiente para treinar "
                "o modelo de presença."
            )

        df = df.sort_values("data")

         # Verificar a quantidade de datas diferentes
        datas = sorted(df["data"].unique())

        if len(datas) < 5:
            raise BusinessError(
                "São necessárias pelo menos 5 datas "
                "diferentes para treinar o modelo de presença."
            )

        X = self._attendance_features(df)
        y = df["alunos_presentes"].astype(float)

        preprocess = ColumnTransformer(
            [
                (
                    "categorias",
                    OneHotEncoder(handle_unknown="ignore"),
                    ["turno"]
                )
            ],
            remainder="passthrough"
        )

        model = Pipeline([
            ("preprocessamento", preprocess),
            (
                "regressor",
                RandomForestRegressor(
                    n_estimators=150,
                    random_state=42,
                    min_samples_leaf=2
                )
            )
        ])

        # Separar as datas em ordem cronológica
        datas = sorted(df["data"].unique())
        ponto_corte = int(len(datas) * 0.8)

        datas_treino = datas[:ponto_corte]
        datas_teste = datas[ponto_corte:]

        treino = df[df["data"].isin(datas_treino)]
        teste = df[df["data"].isin(datas_teste)]

        X_train = self._attendance_features(treino)
        y_train = treino["alunos_presentes"].astype(float)

        X_test = self._attendance_features(teste)
        y_test = teste["alunos_presentes"].astype(float)

        # Treinar somente com os dados antigos
        model.fit(X_train, y_train)

        # Gerar previsões para os dados de teste
        previsoes = model.predict(X_test)

        # Calcular o erro médio absoluto
        mae = mean_absolute_error(y_test, previsoes)

        # Treinar novamente com todo o histórico
        # para utilizar o modelo em previsões futuras
        model.fit(X, y)

        # Criar a pasta, caso não exista
        self.attendance_model_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        # Salvar o modelo treinado
        joblib.dump(
            model,
            self.attendance_model_path
        )

        return {
            "status": "treinado",
            "modelo": "RandomForestRegressor",
            "registros_utilizados": int(len(df)),
            "registros_treino": int(len(treino)),
            "registros_teste": int(len(teste)),
            "mae_teste": round(float(mae), 2)
        }
    
    def predict_attendance(
        self, target_date, shift, expected_students
    ):
        # Verificar se o modelo já foi treinado
        if not self.attendance_model_path.exists():
            raise BusinessError(
                "O modelo de presença ainda não foi treinado."
            )

        # Validar a quantidade de alunos
        if expected_students < 0:
            raise BusinessError(
                "A quantidade de alunos não pode ser negativa."
            )

        # Carregar o modelo treinado
        model = joblib.load(self.attendance_model_path)

        # Identificar o dia da semana
        day = pd.Timestamp(target_date).dayofweek

        # Preparar as informações para previsão
        dados = pd.DataFrame([{
            "alunos_previstos": expected_students,
            "dia_semana": day,
            "turno": shift
        }])

        # Gerar a previsão
        prediction = model.predict(dados)[0]

        # Arredondar e limitar ao número de alunos previstos
        estimated_students = max(
            0,
            min(expected_students, round(float(prediction)))
        )

        return {
            "alunos_estimados": estimated_students,
            "modelo": "RandomForestRegressor"
        }

    def train(self, history):
        df = self._prepare(history)

        if len(df) < 10:
            raise BusinessError(
                "Histórico insuficiente para treinar "
                "o modelo de refeições."
            )

        # Organizar os registros por data
        df = df.sort_values("data")

        # Separar as datas cronologicamente
        datas = sorted(df["data"].unique())


        if len(datas) < 5:
            raise BusinessError(
                "São necessárias pelo menos 5 datas "
                "diferentes para avaliar o modelo."
            )

        ponto_corte = int(len(datas) * 0.8)

        datas_treino = datas[:ponto_corte]
        datas_teste = datas[ponto_corte:]

        treino = df[df["data"].isin(datas_treino)]
        teste = df[df["data"].isin(datas_teste)]

        # Entradas e resultados esperados
        X_train = self._features(treino)
        y_train = treino["refeicoes_servidas"].astype(float)

        X_test = self._features(teste)
        y_test = teste["refeicoes_servidas"].astype(float)

        # Preparar as informações categóricas
        preprocess = ColumnTransformer(
            [
                (
                    "categorias",
                    OneHotEncoder(handle_unknown="ignore"),
                    ["turno", "cardapio"]
                )
            ],
            remainder="passthrough"
        )

        model = Pipeline([
            ("preprocessamento", preprocess),
            (
                "regressor",
                RandomForestRegressor(
                    n_estimators=150,
                    random_state=42,
                    min_samples_leaf=2
                )
            )
        ])

        # Treinar com os registros mais antigos
        model.fit(X_train, y_train)

        # Avaliar com os registros mais recentes
        previsoes = model.predict(X_test)

        mae = mean_absolute_error(y_test, previsoes)

        # Treinar novamente com todo o histórico
        X = self._features(df)
        y = df["refeicoes_servidas"].astype(float)

        model.fit(X, y)

        # Salvar o modelo de refeições
        self.model_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        joblib.dump(model, self.model_path)

        return {
            "status": "treinado",
            "modelo": "RandomForestRegressor",
            "registros_utilizados": int(len(df)),
            "registros_treino": int(len(treino)),
            "registros_teste": int(len(teste)),
            "mae_teste": round(float(mae), 2)
        }

    def predict(self, history, target_date, shift, students, menu):
        df = self._prepare(history)
        if df.empty:
            raise BusinessError("Não há registros históricos válidos para previsão.")
        if not self.model_path.exists():
            # Verificar se o modelo de refeições foi treinado
         if not self.model_path.exists():
            raise BusinessError(
                "O modelo de refeições ainda não foi treinado. "
                "Execute o treinamento antes de solicitar previsões."
            )
        model = joblib.load(self.model_path)
        day = pd.Timestamp(target_date).dayofweek
        row = pd.DataFrame([{"alunos_presentes": students, "dia_semana": day, "turno": shift, "cardapio": menu or "não informado"}])
         # Limitar a demanda prevista ao número de alunos
        estimate = max(
            0,
            min(students, int(round(float(model.predict(row)[0]))))
        )
        return {"refeicoes_estimadas": estimate, "modelo": "RandomForestRegressor", "observacao": "Estimativa de apoio ao planejamento; deve ser validada pela equipe escolar."}
