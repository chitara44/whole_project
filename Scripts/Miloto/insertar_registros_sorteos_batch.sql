-- PROCEDURE: public.insertar_registros_sorteos_batch(integer[], date[], text[], text[], text[], integer[], integer[], integer[], integer[], integer[], integer[])

-- DROP PROCEDURE IF EXISTS public.insertar_registros_sorteos_batch(integer[], date[], text[], text[], text[], integer[], integer[], integer[], integer[], integer[], integer[]);

CREATE OR REPLACE PROCEDURE public.insertar_registros_sorteos_batch(
	IN p_id_sorteo integer[],
	IN p_fecha_sorteo date[],
	IN p_ganador text[],
	IN p_n1 integer[],
	IN p_n2 integer[],
	IN p_n3 integer[],
	IN p_n4 integer[],
	IN p_n5 integer[])
LANGUAGE 'plpgsql'
AS $BODY$
BEGIN
    -- Verificar que todos los arrays tengan la misma longitud
    IF array_length(p_id_sorteo, 1) IS DISTINCT FROM array_length(p_fecha_sorteo, 1) THEN
        RAISE EXCEPTION 'Los arrays deben tener la misma longitud';
    END IF;

    -- Insertar en batch
    INSERT INTO public.sorteos ("IdSorteo", "FechaSorteo", "Ganador", "N1", "N2", "N3", "N4", "N5")
    SELECT unnest(p_id_sorteo), unnest(p_fecha_sorteo), unnest(p_ganador), unnest(p_n1), unnest(p_n2), unnest(p_n3), unnest(p_n4), unnest(p_n5)
    ON CONFLICT ("IdSorteo", "TipoSorteo") DO NOTHING;
END 
$BODY$;
ALTER PROCEDURE public.insertar_registros_sorteos_batch(integer[], date[], text[], integer[], integer[], integer[], integer[], integer[])
    OWNER TO postgres;
