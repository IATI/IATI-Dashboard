# End to end tests of IATI-Stats and IATI-Dashboard repos

Tests to be run on a predictable set of mock IATI data: end_to_end_tests/fixtures

To run these tests, we must first run the xml through the code in the
IATI-Stats repo, and then import it into the database in this IATI-Dashboard
repo. The script `end_to_end_tests/run.sh` will do all these steps. It is also
used in the github action
`.github/workflows/stats-and-dashboard-end-to-end.yml`.

The last step of `end_to_end_tests/run.sh` is to run pytest on
`end_to_end_tests/test.py`. These are currently selenium tests that run against
a runserver instance.
