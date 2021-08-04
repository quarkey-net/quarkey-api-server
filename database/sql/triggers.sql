-- Author : Estéban Ristich <esteban.ristich@protonmail.com>

CREATE TRIGGER trgg_auto_update_accounts
    BEFORE UPDATE ON accounts FOR EACH ROW
    EXECUTE PROCEDURE func_update_tmstmp();


CREATE TRIGGER trgg_auto_update_passwords
    BEFORE UPDATE ON passwords FOR EACH ROW
    EXECUTE PROCEDURE func_update_tmstmp();


CREATE TRIGGER trgg_auto_update_auth_token_rsa
    BEFORE UPDATE ON auth_token_rsa FOR EACH ROW
    EXECUTE PROCEDURE func_update_tmstmp();