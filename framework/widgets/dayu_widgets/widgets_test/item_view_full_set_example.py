from PySide6 import QtWidgets

# Import local modules
from framework.widgets.dayu_widgets import utils
from framework.widgets.dayu_widgets.divider import MDivider
from framework.widgets.dayu_widgets.field_mixin import MFieldMixin
from framework.widgets.dayu_widgets.item_view_full_set import MItemViewFullSet
from framework.widgets.dayu_widgets.push_button import MPushButton
from framework.widgets.dayu_widgets.widgets_test import _mock_data


@utils.add_settings("DaYu", "DaYuExample", event_name="hideEvent")
class ItemViewFullSetExample(QtWidgets.QWidget, MFieldMixin):
    def __init__(self, parent=None):
        super(ItemViewFullSetExample, self).__init__(parent)
        self._init_ui()

    def _init_ui(self):
        item_view_set_table = MItemViewFullSet()
        item_view_set_table.set_header_list(_mock_data.header_list)
        item_view_set_table.tool_bar_visible(True)
        item_view_set_table.enable_context_menu()
        item_view_set_table.searchable()
        custom_button1 = MPushButton("Custom Button1")
        custom_button2 = MPushButton("Custom Button2")
        item_view_set_table.tool_bar_append_widget(custom_button1)  # 添加到工具栏末尾
        item_view_set_table.tool_bar_insert_widget(custom_button2)  # 插入到工具栏开头

        item_view_set_all = MItemViewFullSet(big_view=True)
        item_view_set_all.set_header_list(_mock_data.header_list)
        item_view_set_all.tool_bar_visible(True)
        item_view_set_all.enable_context_menu()
        item_view_set_all.searchable()

        refresh_button = MPushButton("Refresh Data")
        refresh_button.clicked.connect(self.slot_update_data)
        main_lay = QtWidgets.QVBoxLayout()
        main_lay.addWidget(MDivider("Only Table View"))
        main_lay.addWidget(refresh_button)
        main_lay.addWidget(item_view_set_table)
        main_lay.addWidget(MDivider("Table View and Big View"))
        main_lay.addWidget(item_view_set_all)
        self.setLayout(main_lay)

        self.view_list = [
            item_view_set_table,
            item_view_set_all,
        ]
        self.bind(
            "item_view_full_set_example_header_state",
            item_view_set_table.table_view.header_view,
            "state",
        )
        self.slot_update_data()

    def slot_update_data(self):
        for view in self.view_list:
            view.setup_data(_mock_data.data_list)
if __name__ == "__main__":
    # Import local modules
    from framework.widgets.dayu_widgets import dayu_theme
    from framework.widgets.dayu_widgets.qt import application

    with application() as app:
        test = ItemViewFullSetExample()
        dayu_theme.apply(test)
        test.show()
