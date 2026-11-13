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
        self.model_path = Path(load_config()["MODEL_PATH"])

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
        return df.dropna(subset=["data", "alunos_presentes", "refeicoes_servidas"]).query("alunos_presentes >= 0 and refeicoes_servidas >= 0")

    @staticmethod
    def _features(df):
        return df[["alunos_presentes", "dia_semana", "turno", "cardapio"]].copy()

    def train(self, history):
        df = self._prepare(history)
        if len(df) < 10:
            raise BusinessError(f"Histórico insuficiente: {len(df)} registros válidos; o treinamento inicial requer pelo menos 10.")
        X = self._features(df)
        y = df["refeicoes_servidas"].astype(float)
        preprocess = ColumnTransformer([("categorias", OneHotEncoder(handle_unknown="ignore"), ["turno", "cardapio"])], remainder="passthrough")
        model = Pipeline([("preprocessamento", preprocess), ("regressor", RandomForestRegressor(n_estimators=150, random_state=42, min_samples_leaf=2))])
        mae = None
        if len(df) >= 20:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            model.fit(X_train, y_train)
            mae = mean_absolute_error(y_test, model.predict(X_test))
        model.fit(X, y)
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, self.model_path)
        return {"status": "treinado", "registros_utilizados": int(len(df)), "modelo": "RandomForestRegressor", "mae_teste": round(float(mae), 2) if mae is not None else None}

    def predict(self, history, target_date, shift, students, menu):
        df = self._prepare(history)
        if df.empty:
            raise BusinessError("Não há registros históricos válidos para previsão.")
        if not self.model_path.exists():
            if len(df) >= 10:
                self.train(history)
            else:
                same_shift = df[df["turno"] == shift]
                if same_shift.empty: same_shift = df
                ratios = same_shift["refeicoes_servidas"] / same_shift["alunos_presentes"].replace(0, pd.NA)
                ratio = float(ratios.dropna().mean()) if not ratios.dropna().empty else 1.0
                estimate = round(students * ratio)
                return {"refeicoes_estimadas": max(0, estimate), "modelo": "media_historica_por_aluno", "observacao": "Estimativa inicial baseada na média histórica; requer validação com dados reais."}
        model = joblib.load(self.model_path)
        day = pd.Timestamp(target_date).dayofweek
        row = pd.DataFrame([{"alunos_presentes": students, "dia_semana": day, "turno": shift, "cardapio": menu or "não informado"}])
        estimate = max(0, int(round(float(model.predict(row)[0]))))
        return {"refeicoes_estimadas": estimate, "modelo": "RandomForestRegressor", "observacao": "Estimativa de apoio ao planejamento; deve ser validada pela equipe escolar."}
