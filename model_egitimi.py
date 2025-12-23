import sqlite3
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import pickle

print("🔍 Veritabanına bağlanılıyor…")

# 1️⃣ VERİYİ ÇEK
conn = sqlite3.connect("proje_veritabani.db")
df = pd.read_sql("SELECT temiz_icerik, etiket FROM makale_veriseti", conn)
conn.close()

print("Veri çekildi! Toplam kayıt:", len(df))

# 2️⃣ VEKTÖRLEŞTİRME
tfidf = TfidfVectorizer(max_features=5000)
X = tfidf.fit_transform(df["temiz_icerik"])
y = df["etiket"]

# TF-IDF’i kaydet (User Story 4’te lazım olacak)
with open("tfidf.pkl", "wb") as f:
    pickle.dump(tfidf, f)

# 3️⃣ VERİYİ BÖL (%80 Eğitim – %20 Test)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42
)

# 4️⃣ 3 FARKLI MODEL EĞİT

# --- Naive Bayes ---
print("📘 Naive Bayes eğitiliyor…")
nb_model = MultinomialNB()
nb_model.fit(X_train, y_train)
nb_pred = nb_model.predict(X_test)
nb_acc = accuracy_score(y_test, nb_pred)
print("Naive Bayes Accuracy:", nb_acc)

# --- Logistic Regression ---
print("📙 Logistic Regression eğitiliyor…")
lr_model = LogisticRegression(max_iter=2000)
lr_model.fit(X_train, y_train)
lr_pred = lr_model.predict(X_test)
lr_acc = accuracy_score(y_test, lr_pred)
print("Logistic Regression Accuracy:", lr_acc)

# --- Random Forest ---
print("📗 Random Forest eğitiliyor…")
rf_model = RandomForestClassifier(n_estimators=200)
rf_model.fit(X_train, y_train)
rf_pred = rf_model.predict(X_test)
rf_acc = accuracy_score(y_test, rf_pred)
print("Random Forest Accuracy:", rf_acc)

# 5️⃣ MODELLERİ PICKLE OLARAK KAYDET
pickle.dump(nb_model, open("model_nb.pkl", "wb"))
pickle.dump(lr_model, open("model_lr.pkl", "wb"))
pickle.dump(rf_model, open("model_rf.pkl", "wb"))

print("\n🎉 EĞİTİM TAMAMLANDI! MODELLER KAYDEDİLDİ:")
print("✔ model_nb.pkl")
print("✔ model_lr.pkl")
print("✔ model_rf.pkl")
print("✔ tfidf.pkl")
