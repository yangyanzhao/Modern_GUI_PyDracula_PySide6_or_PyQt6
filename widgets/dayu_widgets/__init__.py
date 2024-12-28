# 大鱼控件集合
# -*- coding: utf-8 -*-
# Import future modules
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# Import built-in modules
import os
import sys

DEFAULT_STATIC_FOLDER = os.path.join(sys.modules[__name__].__path__[0], "static")
CUSTOM_STATIC_FOLDERS = []
# Import local modules
from widgets.dayu_widgets.theme import MTheme

dayu_theme = MTheme("dark", primary_color=MTheme.orange)
# dayu_theme.default_size = dayu_theme.small
# dayu_theme = MTheme('light')

# Import local modules
from widgets.dayu_widgets.carousel import MCarousel

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
