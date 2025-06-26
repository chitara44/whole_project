-- FUNCTION: public.leer_resultados_comparacion_fn(text)

-- DROP FUNCTION IF EXISTS public.leer_resultados_comparacion_fn(text);

CREATE OR REPLACE FUNCTION public.leer_resultados_comparacion_fn(
	p_tipo_sorteo text DEFAULT NULL::text)
    RETURNS TABLE("IdSorteo" integer, "TipoSorteo" text, "Numeros_Sorteo" text, "Numeros_Prospecto" text, "Aciertos" integer, "Numeros_Acertados" text, "Numero_Superbalota" integer, "Superbalota_Acertada" text) 
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1000

AS $BODY$
BEGIN
    IF p_tipo_sorteo IS NOT NULL THEN
        RETURN QUERY 
        SELECT  CAST(rc."IdSorteo" AS Integer), 
				CAST(rc."TipoSorteo" AS TEXT),
				CAST(rc."Numeros_Sorteo" AS TEXT),
				CAST(rc."Numeros_Prospecto" AS TEXT), 
				CAST(rc."Aciertos" AS Integer), 
				CAST(rc."Numeros_Acertados" AS TEXT),
				CAST(rc."Numero_Superbalota" AS Integer), 
				CAST(rc."Superbalota_Acertada" AS TEXT)		
        FROM public.resultados_comparacion rc
        WHERE rc."TipoSorteo" = p_tipo_sorteo;
    ELSE
        RETURN QUERY 
        SELECT  CAST(rc."IdSorteo" AS Integer), 
				CAST(rc."TipoSorteo" AS TEXT),
				CAST(rc."Numeros_Sorteo" AS TEXT),
				CAST(rc."Numeros_Prospecto" AS TEXT), 
				CAST(rc."Aciertos" AS Integer), 
				CAST(rc."Numeros_Acertados" AS TEXT),
				CAST(rc."Numero_Superbalota" AS Integer), 
				CAST(rc."Superbalota_Acertada" AS TEXT)
        FROM public.resultados_comparacion rc;
    END IF;
END 
$BODY$;

ALTER FUNCTION public.leer_resultados_comparacion_fn(text)
    OWNER TO postgres;
