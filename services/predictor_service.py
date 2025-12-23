from dataclasses import dataclass
from typing import Dict

from data_access.model_loader import ModelLoader


@dataclass
class PredictionResult:
    model_results: Dict[str, Dict[str, float]]
    overall_human: float
    overall_ai: float
    overall_label: str  # "insan" veya "yapay_zeka"


class PredictorService:
    """
    İş mantığı (Business Logic) katmanı.
    - Metni TF-IDF'e çevirir
    - Üç modelden de olasılıkları alır
    - Ortalamayı hesaplar
    UI bu sınıfı kullanır, ML detayıyla uğraşmaz.
    """

    def __init__(self):
        self.loader = ModelLoader()
        self.tfidf = self.loader.tfidf
        self.nb_model = self.loader.nb_model
        self.lr_model = self.loader.lr_model
        self.rf_model = self.loader.rf_model
        self.class_labels = self.loader.class_labels

        if "insan" not in self.class_labels or "yapay_zeka" not in self.class_labels:
            raise ValueError(f"etiket değerleri beklenen gibi değil: {self.class_labels}")

        self.idx_insan = self.class_labels.index("insan")
        self.idx_ai = self.class_labels.index("yapay_zeka")

    def _to_percent(self, proba_list, idx) -> float:
        return round(float(proba_list[idx]) * 100, 2)

    def predict(self, text: str) -> PredictionResult:
        text = (text or "").strip()
        if not text:
            raise ValueError("Boş metin için tahmin yapılamaz.")

        X = self.tfidf.transform([text])

        nb_proba = self.nb_model.predict_proba(X)[0]
        lr_proba = self.lr_model.predict_proba(X)[0]
        rf_proba = self.rf_model.predict_proba(X)[0]

        model_prob_list = [
            ("Naive Bayes", nb_proba),
            ("Logistic Regression", lr_proba),
            ("Random Forest", rf_proba),
        ]

        model_results = {}
        toplam_insan = 0.0
        toplam_ai = 0.0

        for name, proba in model_prob_list:
            insan_p = self._to_percent(proba, self.idx_insan)
            ai_p = self._to_percent(proba, self.idx_ai)

            model_results[name] = {
                "insan": insan_p,
                "yapay_zeka": ai_p,
            }

            toplam_insan += insan_p
            toplam_ai += ai_p

        ort_insan = round(toplam_insan / len(model_prob_list), 2)
        ort_ai = round(toplam_ai / len(model_prob_list), 2)

        genel_etiket = "yapay_zeka" if ort_ai > ort_insan else "insan"

        return PredictionResult(
            model_results=model_results,
            overall_human=ort_insan,
            overall_ai=ort_ai,
            overall_label=genel_etiket,
        )