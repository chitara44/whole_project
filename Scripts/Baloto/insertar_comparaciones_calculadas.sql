-- PROCEDURE: public.insertar_comparaciones_calculadas(integer, character varying, character varying, character varying, integer, character varying, integer, character varying)

-- DROP PROCEDURE IF EXISTS public.insertar_comparaciones_calculadas(integer, character varying, character varying, character varying, integer, character varying, integer, character varying);

CREATE OR REPLACE PROCEDURE public.insertar_comparaciones_calculadas(
	IN p_idsorteo integer,
	IN p_tiposorteo character varying,
	IN p_numeros_sorteo character varying,
	IN p_numeros_prospecto character varying,
	IN p_aciertos integer,
	IN p_numeros_acertados character varying,
	IN p_numero_superbalota integer DEFAULT NULL::integer,
	IN p_superbalota_acertada character varying DEFAULT NULL::character varying)
LANGUAGE 'plpgsql'
AS $BODY$
BEGIN
    INSERT INTO public.resultados_comparacion 
    ("IdSorteo", "TipoSorteo", "Numeros_Sorteo", "Numeros_Prospecto", 
    "Aciertos", "Numeros_Acertados", "Numero_Superbalota", "Superbalota_Acertada")
    VALUES 
    (p_IdSorteo, p_TipoSorteo, p_Numeros_Sorteo, p_Numeros_Prospecto, 
    p_Aciertos, p_Numeros_Acertados, p_Numero_Superbalota, p_Superbalota_Acertada)
    ON CONFLICT ("IdSorteo", "TipoSorteo") DO NOTHING;
END 
$BODY$;
ALTER PROCEDURE public.insertar_comparaciones_calculadas(integer, character varying, character varying, character varying, integer, character varying, integer, character varying)
    OWNER TO postgres;
