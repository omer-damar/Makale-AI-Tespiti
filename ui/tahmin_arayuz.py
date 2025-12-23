import sys
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPlainTextEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QHeaderView, QComboBox
)
from PyQt5.QtCore import Qt

# Grafik (matplotlib)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from services.predictor_service import PredictorService


class TahminPenceresi(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AI / İnsan Yazı Tahmini - 3 Model Karşılaştırma")
        self.setMinimumSize(900, 650)

        # Service katmanı
        try:
            self.predictor = PredictorService()
        except Exception as e:
            QMessageBox.critical(self, "Başlatma Hatası", str(e))
            sys.exit(1)

        self.last_result = None  # son tahmini saklarız

        # Ana widget + layout
        merkez_widget = QWidget()
        self.setCentralWidget(merkez_widget)

        ana_layout = QVBoxLayout()
        ana_layout.setContentsMargins(20, 20, 20, 20)
        ana_layout.setSpacing(15)
        merkez_widget.setLayout(ana_layout)

        # Açıklama
        lbl_aciklama = QLabel("Analiz edilmesini istediğiniz metni aşağıya yazın:")
        lbl_aciklama.setStyleSheet("font-size: 15px; font-weight: bold;")
        ana_layout.addWidget(lbl_aciklama)

        # Metin alanı
        self.txtMetin = QPlainTextEdit()
        self.txtMetin.setPlaceholderText(
            "Buraya insan veya yapay zeka tarafından yazıldığı düşünülen metni yapıştırın..."
        )
        self.txtMetin.setMinimumHeight(150)
        ana_layout.addWidget(self.txtMetin)

        # Üst satır: model seçimi + buton
        ust_satir = QHBoxLayout()
        ust_satir.setSpacing(12)

        lbl_model = QLabel("Seçilecek Yapay Zeka (Model):")
        lbl_model.setStyleSheet("font-size: 13px; font-weight: bold;")
        ust_satir.addWidget(lbl_model)

        self.cmbModel = QComboBox()
        self.cmbModel.addItems([
            "Genel (3 model ortalaması)",
            "Naive Bayes",
            "Logistic Regression",
            "Random Forest"
        ])
        self.cmbModel.setFixedWidth(240)
        self.cmbModel.currentIndexChanged.connect(self.secili_model_gorunumu_guncelle)
        ust_satir.addWidget(self.cmbModel)

        ust_satir.addStretch(1)

        self.btnTahmin = QPushButton("TAHMİN ET")
        self.btnTahmin.setFixedWidth(150)
        self.btnTahmin.clicked.connect(self.tahmin_yap)
        ust_satir.addWidget(self.btnTahmin)

        ana_layout.addLayout(ust_satir)

        # Tablo (3 satır sabit)
        self.tblSonuc = QTableWidget()
        self.tblSonuc.setRowCount(3)
        self.tblSonuc.setColumnCount(3)
        self.tblSonuc.setHorizontalHeaderLabels(["MODEL", "İNSAN (%)", "YAPAY ZEKA (%)"])
        self.tblSonuc.verticalHeader().setVisible(False)
        self.tblSonuc.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tblSonuc.setMinimumHeight(200)

        header = self.tblSonuc.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)

        self.model_isimleri = ["Naive Bayes", "Logistic Regression", "Random Forest"]
        for i, ad in enumerate(self.model_isimleri):
            self.tblSonuc.setItem(i, 0, QTableWidgetItem(ad))
            self._set_cell(i, 1, "-")
            self._set_cell(i, 2, "-")

        ana_layout.addWidget(self.tblSonuc)

        # Seçilen modele göre sonuç etiketi
        self.lblSeciliSonuc = QLabel("Seçilen Model Sonucu → (Tahmin yapınca dolacak)")
        self.lblSeciliSonuc.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            padding: 10px;
            background-color: #ecf0f1;
            border-radius: 8px;
        """)
        ana_layout.addWidget(self.lblSeciliSonuc)

        # Grafik alanı (Pie)
        self.fig = Figure(figsize=(4, 3))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setMinimumHeight(260)
        ana_layout.addWidget(self.canvas)

        # Genel sonuç etiketi (sadece Genel seçiliyken gösterilecek)
        self.lblGenelSonuc = QLabel("")
        self.lblGenelSonuc.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            padding: 12px;
            background-color: #dfe6e9;
            border-radius: 8px;
            margin-top: 5px;
        """)
        ana_layout.addWidget(self.lblGenelSonuc)

        # Genel stil
        self.setStyleSheet("""
            QMainWindow { background-color: #f5f6fa; }
            QPlainTextEdit {
                border: 1px solid #dcdde1; border-radius: 8px;
                padding: 10px; font-size: 14px; background-color: #ffffff;
            }
            QPushButton {
                background-color: #0984e3; color: white;
                padding: 10px; border-radius: 8px; border: none; font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #74b9ff; }
            QComboBox {
                background-color: #ffffff;
                border: 1px solid #dcdde1;
                border-radius: 8px;
                padding: 6px;
                font-size: 13px;
            }
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #dcdde1;
                border-radius: 8px;
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: #dfe6e9;
                font-weight: bold;
                border: none;
                padding: 6px;
            }
        """)

        # İlk açılış grafik/label
        self.grafik_guncelle(50, 50, "Henüz tahmin yok")
        self.lblGenelSonuc.setVisible(False)

    # -----------------------------
    # Yardımcı: hücreye değer yaz + ortala
    # -----------------------------
    def _set_cell(self, row: int, col: int, text: str):
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignCenter)
        self.tblSonuc.setItem(row, col, item)

    # -----------------------------
    # Tahmin
    # -----------------------------
    def tahmin_yap(self):
        metin = self.txtMetin.toPlainText().strip()

        try:
            result = self.predictor.predict(metin)
        except ValueError as ve:
            QMessageBox.warning(self, "Uyarı", str(ve))
            return
        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))
            return

        self.last_result = result

        # Seçime göre tablo/label/grafik güncelle
        self.secili_model_gorunumu_guncelle()

        # (Genel seçiliyse genel ortalamayı yaz)
        if self.cmbModel.currentText() == "Genel (3 model ortalaması)":
            genel_etiket_yazi = (
                "Bu metin büyük ihtimalle YAPAY ZEKA tarafından yazılmış."
                if result.overall_label == "yapay_zeka"
                else "Bu metin büyük ihtimalle İNSAN tarafından yazılmış."
            )

            self.lblGenelSonuc.setText(
                f"Genel Ortalama (3 Model) → İnsan: %{float(result.overall_human):.2f} | "
                f"Yapay Zeka: %{float(result.overall_ai):.2f}\n{genel_etiket_yazi}"
            )

    # -----------------------------
    # Seçime göre her şeyi güncelle
    # -----------------------------
    def secili_model_gorunumu_guncelle(self):
        if not self.last_result:
            return

        secim = self.cmbModel.currentText()

        # 1) Tabloyu seçime göre güncelle:
        # - Genel seçiliyse tüm modellerin oranı görünür
        # - Model seçiliyse SADECE seçilen modelin oranı görünür, diğerleri "-"
        self.tabloyu_secime_gore_guncelle(secim)

        # 2) Seçilen modele göre grafik + seçili sonuç etiketi
        insan, ai, label, baslik = self._secime_gore_yuzdeler(secim)

        etiket_yazi = "Büyük ihtimalle YAPAY ZEKA." if label == "yapay_zeka" else "Büyük ihtimalle İNSAN."
        self.lblSeciliSonuc.setText(
            f"{baslik} → İnsan: %{insan:.2f} | Yapay Zeka: %{ai:.2f}  —  {etiket_yazi}"
        )

        self.grafik_guncelle(insan, ai, baslik)

        # 3) Genel sonuç paneli sadece Genel seçiliyken görünsün
        self.lblGenelSonuc.setVisible(secim == "Genel (3 model ortalaması)")

    def _secime_gore_yuzdeler(self, secim: str):
        if secim == "Genel (3 model ortalaması)":
            insan = float(self.last_result.overall_human)
            ai = float(self.last_result.overall_ai)
            label = self.last_result.overall_label
            baslik = "Genel Ortalama (3 Model)"
            return insan, ai, label, baslik

        # Tek model
        insan = float(self.last_result.model_results[secim]["insan"])
        ai = float(self.last_result.model_results[secim]["yapay_zeka"])
        label = "yapay_zeka" if ai > insan else "insan"
        baslik = f"Seçili Model: {secim}"
        return insan, ai, label, baslik

    # -----------------------------
    # Tablo filtreleme (3 satır sabit, seçilmeyenler "-")
    # -----------------------------
    def tabloyu_secime_gore_guncelle(self, secim: str):
        if not self.last_result:
            return

        if secim == "Genel (3 model ortalaması)":
            # Hepsini doldur
            for i, ad in enumerate(self.model_isimleri):
                insan = float(self.last_result.model_results[ad]["insan"])
                ai = float(self.last_result.model_results[ad]["yapay_zeka"])
                # model adı zaten var ama garanti olsun:
                self.tblSonuc.setItem(i, 0, QTableWidgetItem(ad))
                self._set_cell(i, 1, f"{insan:.2f}")
                self._set_cell(i, 2, f"{ai:.2f}")
        else:
            # Sadece seçili model görünsün, diğerleri "-"
            for i, ad in enumerate(self.model_isimleri):
                self.tblSonuc.setItem(i, 0, QTableWidgetItem(ad))
                if ad == secim:
                    insan = float(self.last_result.model_results[ad]["insan"])
                    ai = float(self.last_result.model_results[ad]["yapay_zeka"])
                    self._set_cell(i, 1, f"{insan:.2f}")
                    self._set_cell(i, 2, f"{ai:.2f}")
                else:
                    self._set_cell(i, 1, "-")
                    self._set_cell(i, 2, "-")

    # -----------------------------
    # Grafik
    # -----------------------------
    def grafik_guncelle(self, insan_yuzde: float, ai_yuzde: float, title: str):
        self.ax.clear()

        values = [insan_yuzde, ai_yuzde]
        labels = [f"İnsan\n%{insan_yuzde:.2f}", f"Yapay Zeka\n%{ai_yuzde:.2f}"]

        # Başlığı yukarı al (pad arttıkça yukarı çıkar)
        self.ax.set_title(title, pad=18)

        # Pie'ı biraz aşağı kaydırmak için subplot alanını ayarla
        # top küçüldükçe çizim alanı aşağı kayar
        self.fig.subplots_adjust(top=0.85, bottom=0.05)

        self.ax.pie(
          values,
          labels=labels,
          autopct="%1.1f%%",
          startangle=90
    )

        self.ax.axis("equal")
        self.canvas.draw()

