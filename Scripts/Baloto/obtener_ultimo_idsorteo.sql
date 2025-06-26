-- FUNCTION: public.obtener_ultimo_idsorteo()

-- DROP FUNCTION IF EXISTS public.obtener_ultimo_idsorteo();

CREATE OR REPLACE FUNCTION public.obtener_ultimo_idsorteo(
	)
    RETURNS integer
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$
DECLARE
    v_ultimo_id INTEGER;
BEGIN
    SELECT MAX("IdSorteo")
    INTO v_ultimo_id
    FROM public.sorteos;

    RETURN v_ultimo_id;
END;
$BODY$;

ALTER FUNCTION public.obtener_ultimo_idsorteo()
    OWNER TO postgres;
