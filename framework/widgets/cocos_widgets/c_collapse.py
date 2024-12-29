from PySide6 import QtWidgets
from framework.widgets.dayu_widgets.collapse import MCollapse


class CCollapse(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(CCollapse, self).__init__(parent)
        # 初始化UI
        self._init_ui()

    def _init_ui(self):
        main_lay = QtWidgets.QVBoxLayout()
        main_lay.setContentsMargins(5, 5, 5, 5)
        main_lay.setSpacing(0)
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        self.m_collapse = MCollapse()
        scroll.setWidget(self.m_collapse)
        main_lay.addWidget(scroll)
        self.setLayout(main_lay)

        main_lay = QtWidgets.QVBoxLayout()
        main_lay.addWidget(self.m_collapse)
        main_lay.addStretch()

    def set_section_list(self, section_list):
        self.m_collapse.add_section_list(section_list)
