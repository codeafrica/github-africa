github-africa
=============

a collection of scripts to gather data about african users of github.


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

