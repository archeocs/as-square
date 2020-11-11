import sys
sys.path.extend(__path__)

def name():
    return "as-square"

def description():
    return "Archeological Survey Squared"

def version():
    return "@__PLUGIN_VERSION__@"

def qgisMinimumVersion():
    return "3.10"

def authorName():
    return u"Milosz Piglas"

def classFactory(iface):
    import main
    return main.Plugin(iface)
