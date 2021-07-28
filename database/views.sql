-- Author : Estéban Ristich <esteban.ristich@protonmail.com>

CREATE OR REPLACE VIEW v_read_password_item_std AS
    SELECT 
        t1.name,
        t1.description,
        t1.login,
        t1.password,
        t1.url,
        t3.name AS tag_name,
        t3.color AS tag_color
    FROM linkers AS t4
        INNER JOIN passwords AS t1
            ON t4.f_item = t1.id 
        INNER JOIN accounts AS t2
            ON t1.f_owner = t2.id 
        LEFT JOIN tags AS t3
            ON t4.f_tag = t3.id
    ORDER BY t1.updated_on DESC LIMIT 40;  