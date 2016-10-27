ver: 0.2
date: 01-04-2016

Welcome to the wonderful world of Service Directory CSV based data imports/exports!

As of this iteration, importing data into Service Directory is done in stages. Starting with base data and building towards the more complicated models.
This means that there will be multiple csv imports to do, each relying on the other.

The CSV import/export functionality can be found by accessing the Service Directory admin CMS and selecting any of the model types.
Then the import and export buttons should be at the top right.


Examples of the formats of these files can be found in this folder.


The import order is:
Countries
Categories
Keywords (which rely on Categories)
Organisations (which rely on Countries, Categories & Keywords)


All model types can be referred to by their natural identifier (ie: 'name') rather than a numeric ID, however the numeric ID is included in some exports.
The importer will use the appropriate identifier to both
 - Determine if the thing being imported is New or being Updated
 - Find models associated with the thing being imported and create appropriate relationships between them

Boolean (true/false) fields are set using 0 or 1 where 1 is true. NOT the text 'true', 'false', 'yes', 'no', etc...


When importing, after selecting the CSV file, you will see a preview of the changes that will be made by the import.


Some model types accept lists of things to be associated with. These must be quoted and comma seperated in the CSV, eg: for importing a keyword with multiple categories:

name,categories,show_on_home_page
HIV,"Health,Education,Teenager",1

NOTE THAT IN THIS EXAMPLE THE CATEGORIES ('Health' & 'Education') MUST ALREADY HAVE BEEN IMPORTED. This applies to all models that are referred to during the import.
eg: Countries must already exist before they can be referred to by Organisations. That is why the import order is necessary for the moment.


An Organisation import would look like this:

name,about,address,telephone,emergency_telephone,email,web,verified_as,age_range_min,age_range_max,opening_hours,country,location,categories,keywords,facility_code
"Healthcare Co","Something about them","202 The Gatehouse, Century Way, Century City","0215522159","0215522159","blueteam@labs.ws","http://www.afrolabs.co.za","Healthcare Provider",0,99,"9am to 5pm on weekdays","South Africa","-33.891937,18.505496","Health,Education","HIV,Test","AL"

Note that the location is quoted, comma seperated, decimal, latitude and longitude.
