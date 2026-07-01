DECLARE @ActiveDate VARCHAR(8);
SET @ActiveDate = CONVERT(varchar(8), CAST(CAST($__timeFrom() AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATE), 112);

DECLARE @SelectedDate DATE = TRY_CAST(@ActiveDate AS DATE);

IF OBJECT_ID('tempdb..#CalendarSlots') IS NOT NULL DROP TABLE #CalendarSlots;
CREATE TABLE #CalendarSlots (
    global_slot_idx INT IDENTITY(1,1) PRIMARY KEY,
    fecha DATE
);

WITH CalendarBase AS (
    SELECT 
        Fecha,
        Laborable,
        Cant_A_Fabricar,
        SUM(CASE WHEN Cant_A_Fabricar = 18.5 THEN 1 ELSE 0 END) OVER (ORDER BY Fecha ASC) AS Count185
    FROM dbo.CALENDARIO_LABORAL
    WHERE Fecha >= '2026-06-24'
)
INSERT INTO #CalendarSlots (fecha)
SELECT 
    cb.Fecha
FROM CalendarBase cb
CROSS APPLY (
    SELECT ROW_NUMBER() OVER (ORDER BY id) AS seq_idx
    FROM dbo.HHSS_18
    WHERE cb.Cant_A_Fabricar = 18.0 OR cb.Cant_A_Fabricar IS NULL OR (cb.Cant_A_Fabricar NOT IN (19.0, 18.5) AND cb.Cant_A_Fabricar > 0)
    
    UNION ALL
    
    SELECT ROW_NUMBER() OVER (ORDER BY id) AS seq_idx
    FROM dbo.HHSS_19
    WHERE cb.Cant_A_Fabricar = 19.0
    
    UNION ALL
    
    SELECT ROW_NUMBER() OVER (ORDER BY id) AS seq_idx
    FROM dbo.HHSS_18_5
    WHERE cb.Cant_A_Fabricar = 18.5 AND cb.Count185 % 2 = 1 AND id BETWEEN 1 AND 19
    
    UNION ALL
    
    SELECT ROW_NUMBER() OVER (ORDER BY id) AS seq_idx
    FROM dbo.HHSS_18_5
    WHERE cb.Cant_A_Fabricar = 18.5 AND cb.Count185 % 2 = 0 AND id BETWEEN 20 AND 38
) s
WHERE cb.Laborable = 1 AND cb.Cant_A_Fabricar > 0
ORDER BY cb.Fecha ASC, s.seq_idx ASC;

IF OBJECT_ID('tempdb..#MappedSeqs') IS NOT NULL DROP TABLE #MappedSeqs;
CREATE TABLE #MappedSeqs (
    id INT PRIMARY KEY,
    planned_date DATE
);

WITH OrderedERP AS (
    SELECT 
        id,
        ROW_NUMBER() OVER (ORDER BY TRY_CAST(fecha_montaje AS DATE) ASC, TRY_CAST(secuencia AS INT) ASC) as global_seq_idx
    FROM dbo.JAULA_ERP
    WHERE TRY_CAST(secuencia AS INT) >= 227
)
INSERT INTO #MappedSeqs (id, planned_date)
SELECT 
    o.id,
    cs.fecha
FROM OrderedERP o
INNER JOIN #CalendarSlots cs ON cs.global_slot_idx = o.global_seq_idx;

DECLARE @Teorico INT, @Real INT, @OK INT, @NOK INT;

SELECT @Teorico = COUNT(*)
FROM #MappedSeqs
WHERE planned_date = @SelectedDate;

SELECT 
    @Real = COUNT(DISTINCT log.NBASTIDOR),
    @OK = COUNT(DISTINCT CASE WHEN log.OK_NOK = 'OK' THEN log.NBASTIDOR END),
    @NOK = COUNT(DISTINCT CASE WHEN log.OK_NOK = 'NOK' THEN log.NBASTIDOR END)
FROM dbo.LOG_TABLA log
INNER JOIN dbo.JAULA_ERP erp ON erp.bastidor = log.NBASTIDOR
WHERE log.FECHA_HORA_FIN_SEC IS NOT NULL
  AND CAST(CAST(log.FECHA_HORA_FIN_SEC AS datetime2) AT TIME ZONE 'UTC' AT TIME ZONE 'Romance Standard Time' AS DATE) = @SelectedDate;

SELECT 
    COALESCE(@Teorico, 0) AS [PLANIFICADAS (TEÓRICO)],
    COALESCE(@Real, 0) AS [COMPLETADAS (REAL)],
    COALESCE(@OK, 0) AS [SECUENCIAS OK],
    COALESCE(@NOK, 0) AS [SECUENCIAS NOK],
    COALESCE(@Real, 0) - COALESCE(@Teorico, 0) AS [DESVIACIÓN];