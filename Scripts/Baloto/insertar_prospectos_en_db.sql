-- PROCEDURE: public.insertar_prospectos_en_db(integer, integer, character varying, character varying, integer, integer, integer, integer, integer, integer, double precision)

-- DROP PROCEDURE IF EXISTS public.insertar_prospectos_en_db(integer, integer, character varying, character varying, integer, integer, integer, integer, integer, integer, double precision);

CREATE OR REPLACE PROCEDURE public.insertar_prospectos_en_db(
	IN p_idsorteo integer,
	IN p_posicion integer,
	IN p_tiposorteo character varying,
	IN p_tipoprospecto character varying,
	IN p_n1 integer,
	IN p_n2 integer,
	IN p_n3 integer,
	IN p_n4 integer,
	IN p_n5 integer,
	IN p_sb integer DEFAULT NULL::integer,
	IN p_peso double precision DEFAULT NULL::double precision)
LANGUAGE 'plpgsql'
AS $BODY$
BEGIN
    INSERT INTO public.prospectos 
    ("IdSorteo", "Posicion", "TipoSorteo", "TipoProspecto", "N1", "N2", "N3", "N4", "N5", "SB", "Peso")
    VALUES 
    (p_IdSorteo, p_Posicion, p_TipoSorteo, p_TipoProspecto, 
    p_N1, p_N2, p_N3, p_N4, p_N5, p_SB, p_Peso)
    ON CONFLICT ("IdSorteo", "Posicion", "TipoSorteo", "TipoProspecto") DO NOTHING;
END 
$BODY$;
ALTER PROCEDURE public.insertar_prospectos_en_db(integer, integer, character varying, character varying, integer, integer, integer, integer, integer, integer, double precision)
    OWNER TO postgres;
