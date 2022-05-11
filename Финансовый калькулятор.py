from PyQt5.QtCore import Qt, QLocale

from PyQt5.QtGui import QDoubleValidator, QIntValidator
from PyQt5.QtWidgets import (QApplication, QWidget, 
        QHBoxLayout, QVBoxLayout, QGridLayout,
        QSpinBox, QLabel, QLineEdit, QPushButton)

QSS_LabelBold = '''QLabel { 
    font: bold 20px;
}'''
QSS_Columns = '''QLabel { 
    font: bold 14px "Courier New";
}'''

def fix_point(amount):
    try:
        result = float(amount)
        return result
    except ValueError:
        try:
            result = float(amount.replace(',', '.'))
            return result
        except ValueError:
            return 0

def discount(amount, years, months, base, rate):
    total_months = 12 * years + months
    periods = total_months // base
    tail = total_months % base
    rate = rate/100
    simple = 1 + (tail * rate) / base
    compound = pow(1 + rate, periods)
    return round( amount / (simple * compound) , 4)

class FutureAmount(QWidget):
    def __init__(self, rate_widget, base_widget, amount=0, years=0, months=0, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        self.years = years
        self.months = months
        self.amount = amount
        self.rate_widget = rate_widget
        self.base_widget = base_widget
        # размещаем визуальные элементы:
        self.create_widgets()
        self.recalc()
        self.connects()
        self.show()
    
    def create_widgets(self):
        self.txt_amount = QLineEdit(str(self.amount))
        loc = QLocale(QLocale.English, QLocale.UnitedStates)
        validator = QDoubleValidator()
        validator.setLocale(loc)
        self.txt_amount.setValidator(validator)
        self.txt_years = QLineEdit(str(self.years))
        self.txt_years.setValidator(QIntValidator(0, 10000))
        self.txt_months = QLineEdit(str(self.months))
        self.txt_months.setValidator(QIntValidator(0, 11))
        self.lbl_pv = QLabel()
        self.lay_widgets()

    def lay_widgets(self):
        layout_h = QHBoxLayout()
        layout_h.setContentsMargins(20, 0, 20, 0)
        layout_h.addWidget(self.txt_years)
        layout_h.addWidget(self.txt_months)
        layout_h.addStretch(1)
        layout_h.addWidget(self.txt_amount)
        layout_h.addStretch(1)
        layout_h.addWidget(self.lbl_pv)
        self.setLayout(layout_h)

    def connects(self):
        self.txt_amount.editingFinished.connect(self.recalc)
        self.txt_years.editingFinished.connect(self.recalc)
        self.txt_months.editingFinished.connect(self.recalc)

    def recalc(self):
        base = int(self.base_widget.text())
        rate = fix_point(self.rate_widget.text())
        self.amount = fix_point(self.txt_amount.text())
        self.years = int(self.txt_years.text())
        self.months = int(self.txt_months.text())
        result = discount(self.amount, self.years, self.months, base, rate)
        self.lbl_pv.setText("{0:.4f}".format(result))

class CashFlow(QWidget):
    def __init__(self, rate=0.0, base=12, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        self.rate = rate
        self.base = base
        self.NPV = 0 
        self.amounts = []
        self.create_widgets()
        self.connects()
        self.show()

    def add_fa(self):
        months = self.months_to_add()
        years, months = months // 12, months % 12
        fa = FutureAmount(self.txt_rate, self.spin_base, self.last_amount(), years, months)
        self.layout_famounts.addWidget(fa)
        fa.txt_amount.editingFinished.connect(self.recalc)
        fa.txt_years.editingFinished.connect(self.recalc)
        fa.txt_months.editingFinished.connect(self.recalc)
        self.amounts.append(fa)
        self.recalc()
    
    def months_to_add(self):
        total = len(self.amounts)
        if 0 == total:
            return 0
        elif 1 == total:
            return 12
        else:
            fa_2 = self.amounts[total - 2] # вторая строка с конца
            fa_1 = self.amounts[total - 1] # первая с конца
            months_1 = int(fa_1.txt_years.text()) * 12 + int(fa_1.txt_months.text())
            months_2 = int(fa_2.txt_years.text()) * 12 + int(fa_2.txt_months.text())
            return months_1 + (months_1 - months_2)
    
    def last_amount(self):
        total = len(self.amounts)
        if total:
            fa = self.amounts[total - 1]
            return fix_point(fa.txt_amount.text())
        return 0

    def recalc(self):
        result = 0
        for future_amount in self.amounts:
            result += float(future_amount.lbl_pv.text())
        self.lbl_npv.setText(str(round(result, 4)))
    
    def recalc_them_all(self):
        for future_amount in self.amounts:
            future_amount.recalc()
        self.recalc()

    def connects(self):
        self.button_plus.clicked.connect(self.add_fa)
        self.txt_rate.editingFinished.connect(self.recalc_them_all)
        self.spin_base.valueChanged.connect(self.recalc_them_all)
    
    def create_widgets(self):
        self.lbl_base1 = QLabel('начисление раз в')
        self.spin_base = QSpinBox()
        self.spin_base.setValue(self.base)
        self.spin_base.setRange(1, 12)
        self.lbl_base2 = QLabel('месяцев')
        self.lbl_rate1 = QLabel('ставка:')
        self.txt_rate = QLineEdit('0')
        loc = QLocale(QLocale.English, QLocale.UnitedStates)
        validator = QDoubleValidator()
        validator.setLocale(loc)
        self.txt_rate.setValidator(validator)
        self.lbl_rate2 = QLabel('процентов')
        self.lbl_result1 = QLabel('Итог:')
        self.lbl_npv = QLabel(str(self.NPV))
        self.lbl_npv.setStyleSheet(QSS_LabelBold)
        self.lbl_result2 = QLabel(' рублей')
        self.button_ok = QPushButton('OK')
        self.button_plus = QPushButton(' + ')
        self.lay_widgets()

    def lay_widgets(self):
        self.layout_main = QVBoxLayout()
        self.layout_famounts = QVBoxLayout()
        layout_h1 = QHBoxLayout()
        layout_h2 = QHBoxLayout()
        layout_h3 = QHBoxLayout()
        layout_top = QHBoxLayout()
        layout_bottom = QHBoxLayout()
        layout_h1.addWidget(self.lbl_result1, alignment=Qt.AlignRight)
        layout_h1.addWidget(self.lbl_npv)
        layout_h1.addWidget(self.lbl_result2, alignment=Qt.AlignLeft)
        layout_h2.addWidget(self.lbl_rate1, alignment=Qt.AlignRight)
        layout_h2.addWidget(self.txt_rate)
        layout_h2.addWidget(self.lbl_rate2, alignment=Qt.AlignLeft)
        layout_h3.addWidget(self.lbl_base1, alignment=Qt.AlignRight)
        layout_h3.addWidget(self.spin_base)
        layout_h3.addWidget(self.lbl_base2, alignment=Qt.AlignLeft)
        layout_top.addLayout(layout_h2)
        layout_top.addStretch(2)
        layout_top.addLayout(layout_h3)
        self.layout_main.addLayout(layout_top)
        layout_bottom.addWidget(self.button_ok)
        layout_bottom.addStretch(2)
        layout_bottom.addLayout(layout_h1)
        layout_bottom.addStretch(2)
        layout_bottom.addWidget(self.button_plus, alignment=Qt.AlignRight)
        self.layout_main.addLayout(layout_bottom)


        layout_h = QHBoxLayout()
        layout_h.setContentsMargins(20, 0, 20, 0)
        lbc1 = QLabel(':      лет      :') 
        lbc1.setStyleSheet(QSS_Columns)
        layout_h.addWidget(lbc1, alignment=Qt.AlignHCenter)
        lbc2 = QLabel(':    месяцев    :')
        lbc2.setStyleSheet(QSS_Columns)
        layout_h.addWidget(lbc2, alignment=Qt.AlignHCenter)
        layout_h.addStretch(1)
        lbc3 = QLabel(':     сумма     :')
        lbc3.setStyleSheet(QSS_Columns)
        layout_h.addWidget(lbc3, alignment=Qt.AlignHCenter)
        layout_h.addStretch(1)
        lbc4 = QLabel('итог:')
        lbc4.setStyleSheet(QSS_Columns)
        layout_h.addWidget(lbc4, alignment=Qt.AlignRight)
    
        self.layout_famounts.addLayout(layout_h)
        self.layout_main.addLayout(self.layout_famounts) # добавили

        self.setLayout(self.layout_main)

app = QApplication([])
main = CashFlow()
main.resize(750, 200)
main.setWindowTitle('Финансовый калькулятор')
app.exec()