# CHANGELOG

## 0.9.0
 
 - support multipart layers, including ones saved in non-spatialite
   sources (for example SHP files)

## 0.8.0

- feat: i18n - Polish translations. English translation are used by 
  default 

## 0.7.0

- feat: Database migrations - user can trigger database migration when
  required

## 0.6.0

* feat: each record might have multiple rows, that represents sources
  classifictation (chronology and culuture name). User can change this value
  after she clicks on button 'Classification'
  
* fix: clear editor when no feature is selected or more than one is selected
  
## 0.5.0

* feat: show warning in QGIS when user removes layer AS_RECORDS or she 
  tries to add new record, but AS_RECORDS is not loaded
  
* fix: initialize required layers when AS_RECORDS is removed and added
  again to the project
