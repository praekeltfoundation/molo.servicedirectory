DO $$

DECLARE health_category_id integer;
DECLARE education_category_id integer;
DECLARE test_keyword_id integer;
DECLARE hiv_keyword_id integer;
DECLARE tutoring_keyword_id integer;
DECLARE sa_country_id integer;
DECLARE healthcareco_org_id integer;

BEGIN

-- to print a variable:
-- RAISE NOTICE 'health_category_id: %', health_category_id;

--category
INSERT INTO "api_category" (name,show_on_home_page) VALUES('Health',True) RETURNING id INTO health_category_id;
INSERT INTO "api_category" (name,show_on_home_page) VALUES('Education',False) RETURNING id INTO education_category_id;

--keyword
INSERT INTO "api_keyword" (name,show_on_home_page) VALUES('Test',True) RETURNING id INTO test_keyword_id;
INSERT INTO "api_keyword" (name,show_on_home_page) VALUES('HIV',True) RETURNING id INTO hiv_keyword_id;
INSERT INTO "api_keyword" (name,show_on_home_page) VALUES('Tutoring',True) RETURNING id INTO tutoring_keyword_id;

--keyword_category
INSERT INTO "api_keywordcategory" (keyword_id,category_id) VALUES(test_keyword_id,health_category_id);
INSERT INTO "api_keywordcategory" (keyword_id,category_id) VALUES(test_keyword_id,education_category_id);
INSERT INTO "api_keywordcategory" (keyword_id,category_id) VALUES(hiv_keyword_id,health_category_id);
INSERT INTO "api_keywordcategory" (keyword_id,category_id) VALUES(tutoring_keyword_id,education_category_id);

--country
INSERT INTO "api_country" (name,iso_code) VALUES('South Africa','ZA') RETURNING id INTO sa_country_id;

--organisation
INSERT INTO "api_organisation" (name,about,address,telephone,emergency_telephone,email,web,verified_as,opening_hours,country_id,location,facility_code) VALUES('Healthcare Co','Something about them','202 The Gatehouse, Century Way, Century City','0215522159','','blueteam@labs.ws','http://www.afrolabs.co.za','','',sa_country_id,'SRID=4326;POINT (18.5054960000000008 -33.8919369999999986)','') RETURNING id INTO healthcareco_org_id;

--organisation_category
INSERT INTO "api_organisationcategory" (organisation_id,category_id) VALUES(healthcareco_org_id,health_category_id);
INSERT INTO "api_organisationcategory" (organisation_id,category_id) VALUES(healthcareco_org_id,education_category_id);

--organisation_keyword
INSERT INTO "api_organisationkeyword" (organisation_id,keyword_id) VALUES(healthcareco_org_id,test_keyword_id);
INSERT INTO "api_organisationkeyword" (organisation_id,keyword_id) VALUES(healthcareco_org_id,hiv_keyword_id);

END $$;
