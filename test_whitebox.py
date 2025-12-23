import unittest
from services.predictor_service import PredictorService


class TestPredictorService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.predictor = PredictorService()

    # -------------------------------------------------------
    # Test Case 1 – Boş Metinde Hata Fırlatmalı
    # -------------------------------------------------------
    def test_empty_text(self):
        with self.assertRaises(ValueError):
            self.predictor.predict("")

    # -------------------------------------------------------
    # Test Case 2 – İnsan Yazımına Yakın Örnek
    # -------------------------------------------------------
    def test_human_like_text(self):
        text = "Bugün hava çok güzeldi ve yürüyüşe çıktım. Kendimi oldukça iyi hissettim."
        result = self.predictor.predict(text)

        print("\n[Human-like Text Result]", result)

        self.assertIn("Naive Bayes", result.model_results)
        self.assertGreaterEqual(result.overall_human, 10)   # insanlar %10-100 arası
        self.assertLessEqual(result.overall_ai, 90)

    # -------------------------------------------------------
    # Test Case 3 – Yapay Zeka Yazımına Yakın Örnek
    # -------------------------------------------------------
    def test_ai_like_text(self):
        text = "Modern yapay zeka modelleri, derin öğrenme yöntemleriyle yüksek doğruluk oranlarına ulaşmaktadır."
        result = self.predictor.predict(text)

        print("\n[AI-like Text Result]", result)

        self.assertIn("Random Forest", result.model_results)
        self.assertGreaterEqual(result.overall_ai, 10)     # AI yüzdesi en az %10
        self.assertLessEqual(result.overall_human, 90)


if __name__ == "__main__":
    unittest.main()
