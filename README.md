GitHub Africa
=============

Project to help highlight GitHub usage in Africa

Methodology
-----------

Using GitHub API's we searched for all GitHub user's who had an African country or city listed in their profile.  This is obviously an imperfect method but does help illustrate where GitHub usage in Africa is occuring.  We feel this provides a good proxy where opensource and modern software practices is growing in Africa. 

These scripts in this repo where used to generate the [github-africa-users](https://github.com/codeafrica/github-africa/blob/master/data/github-africa-users-20141231.csv) list.  We used this data to create the GitHub Africa User's Map at: [codeafrica.org](http://codeafrica.org)

About
-----

This is part of the [CodeAfrica](http://codeafrica.org) initiative supported by [Ona](http://company.ona.io) and [Yeleman](http://yeleman.com) - software companies building world class open source software in Nairobi, Kenya and Bamako, Mali.  

Usage
-----

* Create a virtualenv and `pip install -r requirements.pip` inside.
* Copy `secret.py.example` to `secret.py`
* Edit `secret.py` with a `clientID` and `secretID` from your github profile/auth page
* Add your username and password (in clear) to `secret.py`
* Launch `./auth.py` and export the `GITHUB_TOKEN` variable as suggested.
* You can now clear/remove `secret.py`
* Launch `step1_search_by_location.py`
* Launch `step2_cleanup_users.py`
* Launch `step3_extend_users.py`
* Launch `step4_cleanup_dates.py`
* Launch `step5_export_for_map.py`

Main per-user data is located in `step4.json`.
The Step5 creates a CSV file usable with Mapbox Studio to create a simple map based on number of users per country/city.
