-- FUNCTION: public.obtener_ultimo_idprospecto()

-- DROP FUNCTION IF EXISTS public.obtener_ultimo_idprospecto();

CREATE OR REPLACE FUNCTION public.obtener_ultimo_idprospecto(
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
    FROM public.prospectos;

    RETURN v_ultimo_id;
END;
$BODY$;

ALTER FUNCTION public.obtener_ultimo_idprospecto()
    OWNER TO postgres;
