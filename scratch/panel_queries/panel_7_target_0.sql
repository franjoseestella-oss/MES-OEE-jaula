SELECT
  COALESCE(CONVERT(varchar(10), TRY_CAST(Fecha AS DATE), 103), '') AS [Fecha],
  CASE 
    WHEN cl.Laborable = 1 THEN cl.Tipo_Dia
    WHEN EXISTS (
      SELECT 1 FROM dbo.JAULA_ERP erp 
      WHERE erp.fecha_montaje = CONVERT(varchar(8), cl.Fecha, 112)
    ) THEN 'Laborable'
    ELSE cl.Tipo_Dia 
  END AS [Tipo de Día],
  CASE 
    WHEN cl.Laborable = 1 THEN 'Sí'
    WHEN EXISTS (
      SELECT 1 FROM dbo.JAULA_ERP erp 
      WHERE erp.fecha_montaje = CONVERT(varchar(8), cl.Fecha, 112)
    ) THEN 'Sí'
    ELSE 'No' 
  END AS [Laborable],
  CASE 
    WHEN cl.Laborable = 1 THEN cl.Cant_A_Fabricar
    WHEN EXISTS (
      SELECT 1 FROM dbo.JAULA_ERP erp 
      WHERE erp.fecha_montaje = CONVERT(varchar(8), cl.Fecha, 112)
    ) THEN (
      SELECT COUNT(*) FROM dbo.JAULA_ERP erp 
      WHERE erp.fecha_montaje = CONVERT(varchar(8), cl.Fecha, 112)
    )
    ELSE cl.Cant_A_Fabricar 
  END AS [Unidades a Fabricar]
FROM dbo.CALENDARIO_LABORAL cl
ORDER BY cl.Fecha ASC