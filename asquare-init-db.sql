CREATE TABLE AS_SQUARES  (
  ID INTEGER PRIMARY KEY,
  SQUARE_ID TEXT NOT NULL,
  SQUARE_DIMENSION TEXT,
  AZP TEXT,
  SURVEY_DATE TEXT,
  PEOPLE TEXT,
  PLOW_DEPTH TEXT,
  AGRO_TREATMENTS TEXT,
  WEATHER TEXT,
  TEMPERATURE TEXT,
  OBSERVATION TEXT,
  REMARKS TEXT
);

CREATE TABLE AS_SOURCES (
  ID INTEGER PRIMARY KEY,
  POTTERY TEXT,
  GLASS TEXT,
  BONES TEXT,
  METAL TEXT,
  FLINT TEXT,
  CLAY TEXT,
  OTHER TEXT,
  CHRONOLOGY TEXT,
  CULTURE TEXT,
  AUTHOR TEXT,
  S_REMARKS  TEXT,
  SQUARE INTEGER REFERENCES AS_SQUARES(ID)
);

SELECT AddGeometryColumn('AS_SQUARES', 'GEOMETRY',
  2180, 'POLYGON', 'XY');

CREATE VIEW AS_RECORDS AS
SELECT S.ID AS FEATURE_ID,
       S.SQUARE_ID AS 'SQUARE ID',
       S.SQUARE_DIMENSION AS 'SQUARE DIMENSION',
       S.AZP AS 'AZP NUMBER',
       S.SURVEY_DATE AS 'SURVEY DATE',
       S.PEOPLE AS 'PEOPLE',
       S.PLOW_DEPTH AS 'PLOW DEPTH',
       S.AGRO_TREATMENTS AS 'AGRICULTURAL TREATMENTS',
       S.WEATHER AS 'WEATHER',
       S.TEMPERATURE AS 'TEMPERATURE',
       S.OBSERVATION AS 'OBSERVATION',
       S.REMARKS AS 'OBSERVATION REMARKS',
       X.POTTERY,
       X.GLASS,
       X.BONES,
       X.METAL,
       X.FLINT,
       X.CLAY,
       X.OTHER,
       X.CHRONOLOGY,
       X.CULTURE,
       X.AUTHOR,
       X.S_REMARKS AS 'SOURCES REMARKS',
       S.GEOMETRY
FROM AS_SQUARES S LEFT JOIN AS_SOURCES X ON S.ID = X.SQUARE;

INSERT INTO VIEWS_GEOMETRY_COLUMNS VALUES ('as_records', 'geometry', 'feature_id', 'as_squares', 'geometry', 1);
