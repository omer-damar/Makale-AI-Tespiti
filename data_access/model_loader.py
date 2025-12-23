import pickle
from pathlib import Path


class _Singleton(type):
    """Basit Singleton metaclass."""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class ModelLoader(metaclass=_Singleton):
    """
    Tüm modelleri ve TF-IDF nesnesini tek yerden yükleyen SİNGLETON sınıf.
    Uygulama boyunca sadece 1 kez yüklenir, her yerde aynı instance kullanılır.
    """

    def __init__(self, base_path: str = "."):
        base = Path(base_path)
        self.tfidf = self._load_pickle(base / "tfidf.pkl")
        self.nb_model = self._load_pickle(base / "model_nb.pkl")
        self.lr_model = self._load_pickle(base / "model_lr.pkl")
        self.rf_model = self._load_pickle(base / "model_rf.pkl")

        # sınıf etiketleri (insan / yapay_zeka)
        self.class_labels = list(self.nb_model.classes_)

    @staticmethod
    def _load_pickle(path: Path):
        if not path.exists():
            raise FileNotFoundError(f"Beklenen model dosyası bulunamadı: {path}")
        with open(path, "rb") as f:
            return pickle.load(f)