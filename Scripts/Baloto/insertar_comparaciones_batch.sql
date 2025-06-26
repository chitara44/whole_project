-- PROCEDURE: public.insertar_comparaciones_batch(jsonb)

-- DROP PROCEDURE IF EXISTS public.insertar_comparaciones_batch(jsonb);

CREATE OR REPLACE PROCEDURE public.insertar_comparaciones_batch(
	IN p_registros jsonb)
LANGUAGE 'plpgsql'
AS $BODY$
BEGIN
    -- Insertar múltiples registros en un solo comando
    INSERT INTO public.comparaciones 
    ("IdSorteo", "Numeros_Sorteo", "Numeros_Prospecto", "Aciertos", "Numeros_Acertados")
    SELECT 
        (r->>'IdSorteo')::INTEGER, 
        r->>'Numeros_Sorteo',
        r->>'Numeros_Prospecto',
        (r->>'Aciertos')::INTEGER, 
        r->>'Numeros_Acertados'
    FROM jsonb_array_elements(p_registros) AS r
    ON CONFLICT ("IdSorteo", "TipoSorteo") DO NOTHING;
END 
$BODY$;
ALTER PROCEDURE public.insertar_comparaciones_batch(jsonb)
    OWNER TO postgres;
