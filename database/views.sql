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
    FROM password_tag_linkers AS t4
        INNER JOIN passwords AS t1
            ON t4.f_item = t1.id 
        INNER JOIN accounts AS t2
            ON t1.f_owner = t2.id 
        LEFT JOIN tags AS t3
            ON t4.f_tag = t3.id
    ORDER BY t1.updated_on DESC LIMIT 40;  




SELECT COUNT(t3.id) AS tag_count, t1.name, t1.description, t1.login, t1.password, t1.url, t3.name AS tag_name, t3.color AS tag_color FROM password_tag_linkers AS t4 INNER JOIN passwords AS t1 ON t4.f_password = t1.id INNER JOIN accounts AS t2 ON t1.f_owner = t2.id LEFT JOIN tags AS t3 ON t4.f_tag = t3.id WHERE t2.id = 'tom' ORDER BY t1.updated_on DESC;

SELECT t2.id AS password_id, t2.name AS password_name, t3.id AS tag_id, t3.name AS tag_name FROM password_tag_linkers AS t1 LEFT OUTER JOIN passwords AS t2 ON t1.f_password = t2.id RIGHT OUTER JOIN tags AS t3 ON t1.f_tag = t3.id WHERE t2.id = 'a073dfb4-99b0-452b-ae60-ba14abaa8f2f' AND t3.id = '48438b9d-ba97-4136-931f-e1dd0e50481a' AND t2.f_owner = 'esteban' AND t3.f_owner = 'esteban';

SELECT t1.id AS link_id, t2.id AS password_id, t2.name AS password_name FROM password_tag_linkers AS t1 INNER JOIN passwords AS t2 ON t1.f_password = t2.id LEFT JOIN tags AS t3 ON t1.f_tag = t3.id WHERE t2.id = 'a073dfb4-99b0-452b-ae60-ba14abaa8f2f' AND t3.id = '48438b9d-ba97-4136-931f-e1dd0e50481a' AND t2.f_owner = 'esteban' AND t3.f_owner = 'esteban';

