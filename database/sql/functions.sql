-- Author : Estéban Ristich <esteban.ristich@protonmail.com>

CREATE OR REPLACE FUNCTION func_update_tmstmp()
    RETURNS TRIGGER AS
$$
BEGIN
    -- my function
    NEW.updated_on = NOW();
    RETURN NEW;
END;
$$
LANGUAGE 'plpgsql';