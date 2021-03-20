# Copyright (C) Miłosz Pigłas <milosz@archeocs.com>
#
# Licensed under the European Union Public Licence

from PyQt5.QtCore import *
import os

def translator():
    plugin_dir = os.path.dirname(__file__)
    locale = QSettings().value('locale/userLocale', QLocale().name())[0:2]
    locale_path = os.path.join(
        plugin_dir,
        'i18n',
        'as-square_{}.qm'.format(locale))

    if not os.path.exists(locale_path):
        locale_path = os.path.join(
            plugin_dir,
            'i18n',
            'as-square_en.qm'
        )
    translator = QTranslator()
    translator.load(locale_path)
    QCoreApplication.installTranslator(translator)
    return translator

TR = translator()

def tr(key):
    return TR.translate('@default', key)

