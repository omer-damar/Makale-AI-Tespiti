import unittest
import os
import sqlite3
import pandas as pd

from model_egitimi import (
    sqlite3, pd, TfidfVectorizer, MultinomialNB,
    LogisticRegression, RandomForestClassifier
)


class TestModelTraining(unittest.TestCase):

    # -------------------------------------------------------
    # Test Case 1 – Veritabanına bağlanabiliyor mu?
    # -------------------------------------------------------
    def test_database_connection(self):
        try:
            conn = sqlite3.connect("proje_veritabani.db")
            df = pd.read_sql("SELECT temiz_icerik, etiket FROM makale_veriseti", conn)
            conn.close()
        except Exception as e:
            self.fail(f"Veritabanına bağlanılamadı: {e}")

        # En az 1 satır veri olmalı
        self.assertGreater(len(df), 0)

    # -------------------------------------------------------
    # Test Case 2 – TF-IDF vektörleştirme düzgün çalışıyor mu?
    # -------------------------------------------------------
    def test_tfidf_vectorization(self):
        sample_texts = ["insan yazısı", "yapay zeka metni"]
        tfidf = TfidfVectorizer(max_features=5000)

        try:
            X = tfidf.fit_transform(sample_texts)
        except Exception as e:
            self.fail(f"TF-IDF hatası: {e}")

        # 2 metin -> X satır sayısı 2 olmalı
        self.assertEqual(X.shape[0], 2)

    # -------------------------------------------------------
    # Test Case 3 – Modeller eğitiliyor mu? (Naive Bayes)
    # -------------------------------------------------------
    def test_model_training(self):
        # Sahte eğitim verisi (küçük dataset)
        X = [[0, 1, 1], [1, 0, 1], [0, 0, 1]]
        y = ["insan", "yapay_zeka", "insan"]

        try:
            nb = MultinomialNB()
            nb.fit(X, y)
        except Exception as e:
            self.fail(f"Model eğitimi sırasında hata: {e}")

        # Model bir sınıf tahmini döndürmeli
        pred = nb.predict([[1, 0, 0]])[0]
        self.assertIn(pred, ["insan", "yapay_zeka"])


if __name__ == "__main__":
    unittest.main()
