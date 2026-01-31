-- DROP SCHEMA campaign_stats;

CREATE SCHEMA campaign_stats AUTHORIZATION postgres;

-- DROP FUNCTION campaign_stats.update_updated_at_column();

CREATE OR REPLACE FUNCTION campaign_stats.update_updated_at_column()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$function$
;

-- DROP SEQUENCE campaign_stats.report_id_seq;

CREATE SEQUENCE campaign_stats.report_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 9223372036854775807
	START 1
	CACHE 1
	NO CYCLE;

-- campaign_stats.status определение

-- Drop table

-- DROP TABLE campaign_stats.status;

CREATE TABLE campaign_stats.status (
	id int4 NOT NULL, -- Уникальный идентификатор
	"name" text NOT NULL, -- Название статуса
	description text NULL, -- Расширенное описание статуса
	CONSTRAINT status_pkey PRIMARY KEY (id)
);
COMMENT ON TABLE campaign_stats.status IS 'справочник статусов';

-- Column comments

COMMENT ON COLUMN campaign_stats.status.id IS 'Уникальный идентификатор';
COMMENT ON COLUMN campaign_stats.status."name" IS 'Название статуса';
COMMENT ON COLUMN campaign_stats.status.description IS 'Расширенное описание статуса';

-- campaign_stats.product определение

-- Drop table

-- DROP TABLE campaign_stats.product;

CREATE TABLE campaign_stats.product (
	id int4 GENERATED ALWAYS AS IDENTITY( INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE) NOT NULL, -- Уникальный идентификатор
	"name" text NOT NULL, -- Название продукта
	ym_counter text NOT NULL, -- Номер счетчика яндекс метрики
	yd_login text NOT NULL, -- Логин агентского кабинета Директа (текущий)
	links _text NOT NULL, -- Ссылки на продукт
	user_id int4 NOT NULL, -- связь с юзером из БД dit-services
	created_at timestamp DEFAULT now() NOT NULL, -- Дата-время создания
	updated_at timestamp NULL, -- Дата-время последнего обновления
	to_delete bool DEFAULT false NOT NULL, -- Флаг используемый для "мягкого" удаления продукта
	CONSTRAINT product_name_key UNIQUE (name),
	CONSTRAINT product_pkey PRIMARY KEY (id)
);
CREATE INDEX idx_product_created_at ON campaign_stats.product USING btree (created_at);
CREATE UNIQUE INDEX idx_product_name_unique ON campaign_stats.product USING btree (name);
CREATE INDEX idx_product_user_id ON campaign_stats.product USING btree (user_id);
COMMENT ON TABLE campaign_stats.product IS 'Таблица продуктов';

-- Column comments

COMMENT ON COLUMN campaign_stats.product.id IS 'Уникальный идентификатор';
COMMENT ON COLUMN campaign_stats.product."name" IS 'Название продукта';
COMMENT ON COLUMN campaign_stats.product.ym_counter IS 'Номер счетчика яндекс метрики';
COMMENT ON COLUMN campaign_stats.product.yd_login IS 'Логин агентского кабинета Директа (текущий)';
COMMENT ON COLUMN campaign_stats.product.links IS 'Ссылки на продукт';
COMMENT ON COLUMN campaign_stats.product.user_id IS 'связь с юзером из БД dit-services';
COMMENT ON COLUMN campaign_stats.product.created_at IS 'Дата-время создания';
COMMENT ON COLUMN campaign_stats.product.updated_at IS 'Дата-время последнего обновления';
COMMENT ON COLUMN campaign_stats.product.to_delete IS 'Флаг используемый для "мягкого" удаления продукта';

-- Table Triggers

create trigger update_product_updated_at before
update
    on
    campaign_stats.product for each row execute function campaign_stats.update_updated_at_column();


-- campaign_stats.report определение

-- Drop table

-- DROP TABLE campaign_stats.report;

CREATE TABLE campaign_stats.report (
	id int8 GENERATED ALWAYS AS IDENTITY( INCREMENT BY 1 MINVALUE 1 MAXVALUE 9223372036854775807 START 1 CACHE 1 NO CYCLE) NOT NULL, -- Уникальный идентификатор
	user_id int4 NOT NULL, -- Связь с юзером из БД dit-services
	created_datetime timestamp DEFAULT now() NOT NULL, -- Время создание заявки
	status_id int4 DEFAULT 0 NOT NULL, -- Айди статуса заявки
	product_id int4 NOT NULL, -- Айди продукта
	global_campaign_id int4 NOT NULL, -- Айди глобальной кампании
	specification_action_id int4 NULL, -- Айди справочника действий
	specification_purpose_id int4 NULL, -- Айди справочника целей
	from_datetime timestamp NOT NULL, -- Дата-время начала периода
	to_datetime timestamp NOT NULL, -- Дата-время окончания периода
	filepath text NULL, -- Путь/ссылка к файлу отчёта
	previous_filepath text NULL, -- Путь/ссылка к файлу предыдущего отчёта
	to_delete bool DEFAULT false NOT NULL, -- Флаг об удалении, выставляемый пользователем
	content_report_filepath text NULL,
	CONSTRAINT chk_report_dates CHECK ((to_datetime > from_datetime)),
	CONSTRAINT report_pkey PRIMARY KEY (id)
);
CREATE INDEX idx_report_created_datetime ON campaign_stats.report USING btree (created_datetime);
CREATE INDEX idx_report_from_datetime ON campaign_stats.report USING btree (from_datetime);
CREATE INDEX idx_report_global_campaign_id ON campaign_stats.report USING btree (global_campaign_id);
CREATE INDEX idx_report_product_id ON campaign_stats.report USING btree (product_id);
CREATE INDEX idx_report_specification_action_id ON campaign_stats.report USING btree (specification_action_id);
CREATE INDEX idx_report_specification_purpose_id ON campaign_stats.report USING btree (specification_purpose_id);
CREATE INDEX idx_report_status_id ON campaign_stats.report USING btree (status_id);
CREATE INDEX idx_report_to_datetime ON campaign_stats.report USING btree (to_datetime);
CREATE INDEX idx_report_user_id ON campaign_stats.report USING btree (user_id);
COMMENT ON TABLE campaign_stats.report IS 'Таблица отчётов';

-- Column comments

COMMENT ON COLUMN campaign_stats.report.id IS 'Уникальный идентификатор';
COMMENT ON COLUMN campaign_stats.report.user_id IS 'Связь с юзером из БД dit-services';
COMMENT ON COLUMN campaign_stats.report.created_datetime IS 'Время создание заявки';
COMMENT ON COLUMN campaign_stats.report.status_id IS 'Айди статуса заявки';
COMMENT ON COLUMN campaign_stats.report.product_id IS 'Айди продукта';
COMMENT ON COLUMN campaign_stats.report.global_campaign_id IS 'Айди глобальной кампании';
COMMENT ON COLUMN campaign_stats.report.specification_action_id IS 'Айди справочника действий';
COMMENT ON COLUMN campaign_stats.report.specification_purpose_id IS 'Айди справочника целей';
COMMENT ON COLUMN campaign_stats.report.from_datetime IS 'Дата-время начала периода';
COMMENT ON COLUMN campaign_stats.report.to_datetime IS 'Дата-время окончания периода';
COMMENT ON COLUMN campaign_stats.report.filepath IS 'Путь/ссылка к файлу отчёта';
COMMENT ON COLUMN campaign_stats.report.previous_filepath IS 'Путь/ссылка к файлу предыдущего отчёта';
COMMENT ON COLUMN campaign_stats.report.to_delete IS 'Флаг об удалении, выставляемый пользователем';


-- campaign_stats.report внешние включи

ALTER TABLE campaign_stats.report ADD CONSTRAINT report_product_id_fkey FOREIGN KEY (product_id) REFERENCES campaign_stats.product(id);
ALTER TABLE campaign_stats.report ADD CONSTRAINT report_status_id_fkey FOREIGN KEY (status_id) REFERENCES campaign_stats.status(id);


-- заполнение campaign_stats.status --
INSERT INTO campaign_stats.status
(id, "name", description)
VALUES(3, 'failed', 'Ошибка обработки');
INSERT INTO campaign_stats.status
(id, "name", description)
VALUES(4, 'cancelled', 'Отменен');
INSERT INTO campaign_stats.status
(id, "name", description)
VALUES(0, 'in process', 'В процессе первичного сбора данных (значение по умолчанию) ');
INSERT INTO campaign_stats.status
(id, "name", description)
VALUES(1, 'creating', 'В процессе формирования отчёта');
INSERT INTO campaign_stats.status
(id, "name", description)
VALUES(5, 'completed', 'Завершен успешно');
INSERT INTO campaign_stats.status
(id, "name", description)
VALUES(2, 'stage 1 ready', 'Готов к формированию docx-отчета');


-- тестовая запись в campaign_stats.product --
INSERT INTO campaign_stats.product
("name", ym_counter, yd_login, links, user_id, created_at, updated_at, to_delete)
VALUES('тестовый продукт', 'test_counter', 'test_login', '{link1,link2}', 1, '2026-01-31 18:19:28.316', NULL, false);

-- тестовая запись в campaign_stats.report --
INSERT INTO campaign_stats.report
(user_id, created_datetime, status_id, product_id, global_campaign_id, specification_action_id, specification_purpose_id, from_datetime, to_datetime, filepath, previous_filepath, to_delete)
VALUES(1, '2025-11-18 07:20:01.670', 2, 1, 73, 40, NULL, '2025-06-10 00:00:00.000', '2025-08-11 00:00:00.000', 'products_report_generator/1/excel_report/Отчет_пример_10.06.2025 - 11.08.2025.xlsx', 'products_report_generator/92/Отчет_пример_10.06.2025 - 11.08.2025.xlsx', false);