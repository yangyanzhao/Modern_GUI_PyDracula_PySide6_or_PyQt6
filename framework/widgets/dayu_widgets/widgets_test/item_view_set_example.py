
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from PySide6 import QtWidgets

from framework.widgets.dayu_widgets import utils
from framework.widgets.dayu_widgets.divider import MDivider
from framework.widgets.dayu_widgets.field_mixin import MFieldMixin
from framework.widgets.dayu_widgets.item_view_set import MItemViewSet
from framework.widgets.dayu_widgets.push_button import MPushButton
from framework.widgets.dayu_widgets.widgets_test import _mock_data


@utils.add_settings("DaYu", "DaYuExample", event_name="hideEvent")
class ItemViewSetExample(QtWidgets.QWidget, MFieldMixin):
    def __init__(self, parent=None):
        super(ItemViewSetExample, self).__init__(parent)
        self._init_ui()

    def _init_ui(self):
        item_view_set_table = MItemViewSet(view_type=MItemViewSet.TableViewType)
        item_view_set_table.set_header_list(_mock_data.header_list)
        item_view_set_list = MItemViewSet(view_type=MItemViewSet.ListViewType)
        item_view_set_list.set_header_list(_mock_data.header_list)
        item_view_set_tree = MItemViewSet(view_type=MItemViewSet.TreeViewType)
        item_view_set_tree.set_header_list(_mock_data.header_list)
        item_view_set_thumbnail = MItemViewSet(view_type=MItemViewSet.BigViewType)
        item_view_set_thumbnail.set_header_list(_mock_data.header_list)

        item_view_set_search = MItemViewSet(view_type=MItemViewSet.TreeViewType)
        item_view_set_search.set_header_list(_mock_data.header_list)
        item_view_set_search.searchable()
        expand_button = MPushButton("Expand All")
        expand_button.clicked.connect(item_view_set_search.item_view.expandAll)
        coll_button = MPushButton("Collapse All")
        coll_button.clicked.connect(item_view_set_search.item_view.collapseAll)
        item_view_set_search.insert_widget(coll_button)
        item_view_set_search.insert_widget(expand_button)

        refresh_button = MPushButton("Refresh Data")
        refresh_button.clicked.connect(self.slot_update_data)
        main_lay = QtWidgets.QVBoxLayout()
        main_lay.addWidget(MDivider("Table View"))
        main_lay.addWidget(refresh_button)
        main_lay.addWidget(item_view_set_table)
        main_lay.addWidget(MDivider("List View"))
        main_lay.addWidget(item_view_set_list)
        main_lay.addWidget(MDivider("Tree View"))
        main_lay.addWidget(item_view_set_tree)
        main_lay.addWidget(MDivider("Big View"))
        main_lay.addWidget(item_view_set_thumbnail)
        main_lay.addWidget(MDivider("With Search line edit"))
        main_lay.addWidget(item_view_set_search)
        main_lay.addStretch()
        self.setLayout(main_lay)

        item_view_set_tree.setup_data(_mock_data.tree_data_list)
        item_view_set_search.setup_data(_mock_data.tree_data_list)
        self.view_list = [
            item_view_set_table,
            item_view_set_list,
            item_view_set_thumbnail,
        ]
        self.bind(
            "item_view_set_example_header_state",
            item_view_set_table.item_view.header_view,
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
        test = ItemViewSetExample()
        dayu_theme.apply(test)
        test.show()
