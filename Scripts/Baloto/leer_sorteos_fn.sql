-- FUNCTION: public.leer_sorteos_fn(text)

-- DROP FUNCTION IF EXISTS public.leer_sorteos_fn(text);

CREATE OR REPLACE FUNCTION public.leer_sorteos_fn(
	p_tipo_sorteo text DEFAULT NULL::text)
    RETURNS TABLE("IdSorteo" integer, "FechaSorteo" date, "TipoSorteo" text, "Ganador" text, "Nuevo" boolean, "N1" integer, "N2" integer, "N3" integer, "N4" integer, "N5" integer, "SB" integer) 
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1000

AS $BODY$
BEGIN
    IF p_tipo_sorteo IS NOT NULL THEN
        RETURN QUERY 
        SELECT CAST(s."IdSorteo" AS INTEGER), 
               s."FechaSorteo", 
               CAST(s."TipoSorteo" AS TEXT),  
               CAST(s."Ganador" AS TEXT), 
               CASE 
                   WHEN s."Nuevo" ILIKE 'SI' THEN TRUE
                   WHEN s."Nuevo" ILIKE 'NO' THEN FALSE
                   ELSE NULL
               END AS "Nuevo", 
               CAST(s."N1" AS INTEGER), 
               CAST(s."N2" AS INTEGER), 
               CAST(s."N3" AS INTEGER), 
               CAST(s."N4" AS INTEGER), 
               CAST(s."N5" AS INTEGER), 
               CAST(s."SB" AS INTEGER)
        FROM public.sorteos s
        WHERE s."TipoSorteo" = p_tipo_sorteo;
    ELSE
        RETURN QUERY 
        SELECT CAST(s."IdSorteo" AS INTEGER), 
               s."FechaSorteo", 
               CAST(s."TipoSorteo" AS TEXT),  
               CAST(s."Ganador" AS TEXT), 
               CASE 
                   WHEN s."Nuevo" ILIKE 'SI' THEN TRUE
                   WHEN s."Nuevo" ILIKE 'NO' THEN FALSE
                   ELSE NULL
               END AS "Nuevo", 
               CAST(s."N1" AS INTEGER), 
               CAST(s."N2" AS INTEGER), 
               CAST(s."N3" AS INTEGER), 
               CAST(s."N4" AS INTEGER), 
               CAST(s."N5" AS INTEGER), 
               CAST(s."SB" AS INTEGER)
        FROM public.sorteos s;
    END IF;
END 
$BODY$;

ALTER FUNCTION public.leer_sorteos_fn(text)
    OWNER TO postgres;
