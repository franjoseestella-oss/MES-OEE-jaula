SELECT
  fichero AS [Fichero Excel],
  regularizacion AS [Regularización],
  CONVERT(varchar(5), hora_inicio_jornada, 108) AS [Inicio Jornada],
  CONVERT(varchar(5), hora_inicio_parada, 108) AS [Inicio Parada],
  CONVERT(varchar(5), duracion_parada, 108) AS [Duración Parada],
  CONVERT(varchar(5), hora_fin_jornada, 108) AS [Fin Jornada]
FROM dbo.TURNO_TRABAJO