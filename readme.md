# collectd-borgbase

collectd-borgbase is a CollectD Python plugin to get the Repo Usage from Borgbase GraphQL API

## Dependencies

Python Module: Requests [https://pypi.org/project/requests/](https://pypi.org/project/requests/)

## Configuration

1. Get an Borgbase API Key from [https://www.borgbase.com/account?tab=2](https://www.borgbase.com/account?tab=2)
2. Configure the Plugin
  ```
  LoadPlugin python
  <Plugin python>
    ModulePath "<Path to Folder>"
    Import "borgbase"
    <Module borgbase>
        apikey "<API-KEY>"
    </Module>
  </Plugin>
  ```
3. Done
