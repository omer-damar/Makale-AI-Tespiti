import sys
from PyQt5.QtWidgets import QApplication
from qt_material import apply_stylesheet

from ui.tahmin_arayuz import TahminPenceresi


def main():
    app = QApplication(sys.argv)

    # Google Material Design Teması:
    apply_stylesheet(app, theme='light_blue_500.xml')

    pencere = TahminPenceresi()
    pencere.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()