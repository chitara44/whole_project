-- FUNCTION: public.leer_prospectos_fn(integer, text)

-- DROP FUNCTION IF EXISTS public.leer_prospectos_fn(integer, text);

CREATE OR REPLACE FUNCTION public.leer_prospectos_fn(
	p_id_sorteo integer,
	p_tipo_sorteo text DEFAULT NULL::text)
    RETURNS TABLE("IdSorteo" integer, "Posicion" integer, "TipoSorteo" text, "TipoProspecto" text, "N1" integer, "N2" integer, "N3" integer, "N4" integer, "N5" integer, "SB" integer, "Peso" double precision) 
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1000

AS $BODY$
BEGIN
    IF p_tipo_sorteo IS NOT NULL THEN
        RETURN QUERY 
        SELECT CAST(p."IdSorteo" AS INTEGER), 
			CAST(p."Posicion" AS INTEGER), 
			CAST(p."TipoSorteo" AS TEXT), 
			CAST(p."TipoProspecto" AS TEXT), 
			CAST(p."N1" AS INTEGER), 
			CAST(p."N2" AS INTEGER), 
			CAST(p."N3" AS INTEGER), 
			CAST(p."N4" AS INTEGER), 
			CAST(p."N5" AS INTEGER), 
			CAST(p."SB" AS INTEGER), 
			CAST(p."Peso" AS FLOAT)
        FROM public.prospectos p
        WHERE p."TipoSorteo" = p_tipo_sorteo AND p."IdSorteo" = p_id_sorteo;

    ELSE
        RETURN QUERY 
        SELECT CAST(p."IdSorteo" AS INTEGER), 
			CAST(p."Posicion" AS INTEGER), 
			CAST(p."TipoSorteo" AS TEXT), 
			CAST(p."TipoProspecto" AS TEXT), 
			CAST(p."N1" AS INTEGER), 
			CAST(p."N2" AS INTEGER), 
			CAST(p."N3" AS INTEGER), 
			CAST(p."N4" AS INTEGER), 
			CAST(p."N5" AS INTEGER), 
			CAST(p."SB" AS INTEGER), 
			CAST(p."Peso" AS FLOAT)
        FROM public.prospectos
        WHERE p."IdSorteo" = p_id_sorteo;
    END IF;
END 
$BODY$;

ALTER FUNCTION public.leer_prospectos_fn(integer, text)
    OWNER TO postgres;