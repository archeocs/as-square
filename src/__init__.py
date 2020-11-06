import sys
sys.path.extend(__path__)

def name():
    return "as-square"

def description():
    return "Archeological Survey Squared"

def version():
    return "0.1"

def qgisMinimumVersion():
    return "3.10"

def authorName():
    return u"Milosz Piglas"

def classFactory(iface):
    import as_square
    return as_square.Plugin(iface)
