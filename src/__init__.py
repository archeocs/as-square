import sys
sys.path.extend(__path__)

def name():
    return "Asquare"

def description():
    return "List of opened layers"

def version():
    return "0.1"

def qgisMinimumVersion():
    return "1.7"

def authorName():
    return u"Milosz Piglas"

def classFactory(iface):
    import main
    return main.Plugin(iface)
