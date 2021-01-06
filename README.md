# as-square

## Archaeological Survey Data ready for spatial analysis

With `as-square` QGIS plugin you can manage data collected in archaeological field
survey and make it ready for spatial analysis.

`as-square` always support [QGIS Long Term Releases](https://qgis.org/en/site/getinvolved/development/roadmap.html#release-schedule). 

## Installation

`as-square` can be installed with QGIS plugins manager. Every time new version is 
released QGIS downloads it and installs on workstation.

1. Open QGIS plugin settings `Plugins` > `Manage and Install Plugins` > `Settings`.

2. Add URL `https://github.com/archeocs/as-square/releases/latest/download/plugins.xml` 
   to repositories list.
   
## Database

`as-square` supports only [spatialite](https://www.gaia-gis.it/fossil/spatialite-tools/index) vector layers. Last version of empty database
with supported schema can be downloaded from [link](https://github.com/archeocs/as-square/releases/latest/download/empty-db.zip).

You can learn more about spatialite support in [QGIS documentation](https://docs.qgis.org/3.10/en/docs/training_manual/databases/spatialite.html)

