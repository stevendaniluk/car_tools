# obd
Tools for interacting with OBD-II systems via an ELM327 OBD-II adapter.

Scripts:
* `check_DTCs.py`: Lists all present diagnostic trouble codes
* `obd_query.py`: Runs a specific OBD command and displays the response

Run any of the above scripts with `-h` to display more info about the usage and arguments.

## Notes
* The OBD library `python-OBD` is submoduled here because this requires a more recent version than the latest release 0.7.1 available via `pip`. 0.7.1 does not have as many OBD commands/modes.
