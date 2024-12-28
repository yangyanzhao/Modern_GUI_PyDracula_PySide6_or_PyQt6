# 大鱼控件集合
# -*- coding: utf-8 -*-
# Import future modules
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import os
import sys

from .alert import MAlert
from framework.widgets.dayu_widgets.avatar import MAvatar
from framework.widgets.dayu_widgets.badge import MBadge
from framework.widgets.dayu_widgets.breadcrumb import MBreadcrumb
from framework.widgets.dayu_widgets.browser import MClickBrowserFilePushButton, MClickBrowserFileToolButton, \
    MClickBrowserFolderPushButton, MClickBrowserFolderToolButton, MDragFileButton, MDragFolderButton
from framework.widgets.dayu_widgets.button_group import MCheckBoxGroup, MPushButtonGroup, MRadioButtonGroup, \
    MToolButtonGroup
from framework.widgets.dayu_widgets.card import MCard, MMeta
from framework.widgets.dayu_widgets.carousel import MCarousel
from framework.widgets.dayu_widgets.check_box import MCheckBox
from framework.widgets.dayu_widgets.checkable_tag import MCheckableTag
from framework.widgets.dayu_widgets.collapse import MCollapse
from framework.widgets.dayu_widgets.combo_box import MComboBox
from framework.widgets.dayu_widgets.divider import MDivider
from framework.widgets.dayu_widgets.field_mixin import MFieldMixin
from framework.widgets.dayu_widgets.flow_layout import MFlowLayout
from framework.widgets.dayu_widgets.item_model import MSortFilterModel, MTableModel
from framework.widgets.dayu_widgets.item_view import MBigView, MListView, MTableView, MTreeView
from framework.widgets.dayu_widgets.item_view_full_set import MItemViewFullSet
from framework.widgets.dayu_widgets.item_view_set import MItemViewSet
from framework.widgets.dayu_widgets.label import MLabel
from framework.widgets.dayu_widgets.line_edit import MLineEdit
from framework.widgets.dayu_widgets.line_tab_widget import MLineTabWidget
from framework.widgets.dayu_widgets.loading import MLoading, MLoadingWrapper
from framework.widgets.dayu_widgets.menu import MMenu
from framework.widgets.dayu_widgets.menu_tab_widget import MMenuTabWidget
from framework.widgets.dayu_widgets.message import MMessage
from framework.widgets.dayu_widgets.new_tag import MNewTag
from framework.widgets.dayu_widgets.page import MPage
from framework.widgets.dayu_widgets.progress_bar import MProgressBar
from framework.widgets.dayu_widgets.progress_circle import MProgressCircle
from framework.widgets.dayu_widgets.push_button import MPushButton
from framework.widgets.dayu_widgets.radio_button import MRadioButton
from framework.widgets.dayu_widgets.sequence_file import MSequenceFile
from framework.widgets.dayu_widgets.slider import MSlider
from framework.widgets.dayu_widgets.spin_box import MDateEdit, MDateTimeEdit, MDoubleSpinBox, MSpinBox, MTimeEdit
from framework.widgets.dayu_widgets.switch import MSwitch
from framework.widgets.dayu_widgets.tab_widget import MTabWidget
from framework.widgets.dayu_widgets.tag import MTag
from framework.widgets.dayu_widgets.text_edit import MTextEdit
from framework.widgets.dayu_widgets.toast import MToast
from framework.widgets.dayu_widgets.tool_button import MToolButton
from framework.widgets.dayu_widgets.theme import MTheme

DEFAULT_STATIC_FOLDER = os.path.join(sys.modules[__name__].__path__[0], "static")
CUSTOM_STATIC_FOLDERS = []

dayu_theme = MTheme("dark", primary_color=MTheme.orange)

__all__ = [
    "MAlert",
    "MAvatar",
    "MBadge",
    "MBreadcrumb",
    "MClickBrowserFilePushButton",
    "MClickBrowserFileToolButton",
    "MClickBrowserFolderPushButton",
    "MClickBrowserFolderToolButton",
    "MDragFileButton",
    "MDragFolderButton",
    "MCheckBoxGroup",
    "MPushButtonGroup",
    "MRadioButtonGroup",
    "MToolButtonGroup",
    "MCard",
    "MMeta",
    "MCarousel",
    "MCheckBox",
    "MCollapse",
    "MComboBox",
    "MDivider",
    "MFieldMixin",
    "MFlowLayout",
    "MSortFilterModel",
    "MTableModel",
    "MBigView",
    "MListView",
    "MTableView",
    "MTreeView",
    "MItemViewFullSet",
    "MItemViewSet",
    "MLabel",
    "MLineEdit",
    "MLineTabWidget",
    "MLoading",
    "MLoadingWrapper",
    "MMenu",
    "MMenuTabWidget",
    "MMessage",
    "MPage",
    "MProgressBar",
    "MProgressCircle",
    "MPushButton",
    "MRadioButton",
    "MSequenceFile",
    "MSlider",
    "MDateEdit",
    "MDateTimeEdit",
    "MDoubleSpinBox",
    "MSpinBox",
    "MTimeEdit",
    "MSwitch",
    "MTabWidget",
    "MTextEdit",
    "MToast",
    "MToolButton",
    "MNewTag",
    "MCheckableTag",
    "MTag",
]
