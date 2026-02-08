from PyQt5 import QtCore, QtGui, QtWidgets
from main_window import Ui_main_window_Dialog

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main_window_Dialog = QtWidgets.QDialog()
    ui = Ui_main_window_Dialog()
    ui.setupUi(main_window_Dialog)
    main_window_Dialog.show()
    sys.exit(app.exec_())

