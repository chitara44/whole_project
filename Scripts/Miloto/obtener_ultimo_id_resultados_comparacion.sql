-- FUNCTION: public.obtener_ultimo_id_resultados_comparacion()

-- DROP FUNCTION IF EXISTS public.obtener_ultimo_id_resultados_comparacion();

CREATE OR REPLACE FUNCTION public.obtener_ultimo_id_resultados_comparacion(
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
    FROM public.resultados_comparacion;

    RETURN v_ultimo_id;
END;
$BODY$;

ALTER FUNCTION public.obtener_ultimo_id_resultados_comparacion()
    OWNER TO postgres;
