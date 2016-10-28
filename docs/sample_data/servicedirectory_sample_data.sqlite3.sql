PRAGMA foreign_keys = ON;
PRAGMA temp_store = 2;

BEGIN;

CREATE TEMP TABLE _vars("Name" TEXT PRIMARY KEY, "Value" INTEGER);

--category
INSERT INTO "servicedirectory_category" (name,show_on_home_page) VALUES('Health',1);
INSERT INTO "_vars" VALUES ('health_category_id', last_insert_rowid());

INSERT INTO "servicedirectory_category" (name,show_on_home_page) VALUES('Education',0);
INSERT INTO "_vars" VALUES ('education_category_id', last_insert_rowid());

--keyword
INSERT INTO "servicedirectory_keyword" (name,show_on_home_page) VALUES('Test',1);
INSERT INTO "_vars" VALUES ('test_keyword_id', last_insert_rowid());

INSERT INTO "servicedirectory_keyword" (name,show_on_home_page) VALUES('HIV',1);
INSERT INTO "_vars" VALUES ('hiv_keyword_id', last_insert_rowid());

INSERT INTO "servicedirectory_keyword" (name,show_on_home_page) VALUES('Tutoring',1);
INSERT INTO "_vars" VALUES ('tutoring_keyword_id', last_insert_rowid());

--keyword_category
INSERT INTO "servicedirectory_keywordcategory" (keyword_id,category_id) VALUES((SELECT Value FROM _vars WHERE Name = 'test_keyword_id'),(SELECT Value FROM _vars WHERE Name = 'health_category_id'));
INSERT INTO "servicedirectory_keywordcategory" (keyword_id,category_id) VALUES((SELECT Value FROM _vars WHERE Name = 'test_keyword_id'),(SELECT Value FROM _vars WHERE Name = 'education_category_id'));
INSERT INTO "servicedirectory_keywordcategory" (keyword_id,category_id) VALUES((SELECT Value FROM _vars WHERE Name = 'hiv_keyword_id'),(SELECT Value FROM _vars WHERE Name = 'health_category_id'));
INSERT INTO "servicedirectory_keywordcategory" (keyword_id,category_id) VALUES((SELECT Value FROM _vars WHERE Name = 'tutoring_keyword_id'),(SELECT Value FROM _vars WHERE Name = 'education_category_id'));

--country
INSERT INTO "servicedirectory_country" (name,iso_code) VALUES('South Africa','ZA');
INSERT INTO "_vars" VALUES ('sa_country_id', last_insert_rowid());

--organisation
INSERT INTO "servicedirectory_organisation" (name,about,address,telephone,emergency_telephone,email,web,verified_as,opening_hours,country_id,location,facility_code) VALUES('Healthcare Co','Something about them','202 The Gatehouse, Century Way, Century City','0215522159','','blueteam@labs.ws','http://www.afrolabs.co.za','','',(SELECT Value FROM _vars WHERE Name = 'sa_country_id'),'{"type":"Point","coordinates":[18.505496,-33.891937]}','');
INSERT INTO "_vars" VALUES ('healthcareco_org_id', last_insert_rowid());

--organisation_category
INSERT INTO "servicedirectory_organisationcategory" (organisation_id,category_id) VALUES((SELECT Value FROM _vars WHERE Name = 'healthcareco_org_id'),(SELECT Value FROM _vars WHERE Name = 'health_category_id'));
INSERT INTO "servicedirectory_organisationcategory" (organisation_id,category_id) VALUES((SELECT Value FROM _vars WHERE Name = 'healthcareco_org_id'),(SELECT Value FROM _vars WHERE Name = 'education_category_id'));

--organisation_keyword
INSERT INTO "servicedirectory_organisationkeyword" (organisation_id,keyword_id) VALUES((SELECT Value FROM _vars WHERE Name = 'healthcareco_org_id'),(SELECT Value FROM _vars WHERE Name = 'test_keyword_id'));
INSERT INTO "servicedirectory_organisationkeyword" (organisation_id,keyword_id) VALUES((SELECT Value FROM _vars WHERE Name = 'healthcareco_org_id'),(SELECT Value FROM _vars WHERE Name = 'hiv_keyword_id'));

DROP TABLE _vars;

COMMIT;
