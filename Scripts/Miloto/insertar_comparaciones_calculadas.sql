-- PROCEDURE: public.insertar_comparaciones_calculadas(integer, character varying, character varying, character varying, integer, character varying, integer, character varying)

-- DROP PROCEDURE IF EXISTS public.insertar_comparaciones_calculadas(integer, character varying, character varying, character varying, integer, character varying, integer, character varying);

CREATE OR REPLACE PROCEDURE public.insertar_comparaciones_calculadas(
	IN p_idsorteo integer,
	IN p_numeros_sorteo character varying,
	IN p_numeros_prospecto character varying,
	IN p_aciertos integer,
	IN p_numeros_acertados character varying)
LANGUAGE 'plpgsql'
AS $BODY$
BEGIN
    INSERT INTO public.resultados_comparacion 
    ("IdSorteo", "Numeros_Sorteo", "Numeros_Prospecto", "Aciertos", "Numeros_Acertados")
    VALUES 
    (p_IdSorteo, p_Numeros_Sorteo, p_Numeros_Prospecto, p_Aciertos, p_Numeros_Acertados)
    ON CONFLICT ("IdSorteo") DO NOTHING;
END 
$BODY$;
ALTER PROCEDURE public.insertar_comparaciones_calculadas(integer, character varying, character varying, integer, character varying)
    OWNER TO postgres;
