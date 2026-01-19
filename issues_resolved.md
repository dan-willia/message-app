[DATABASE] Development (1/19/26)
  - Add fake users and message history to have more robust demo of capabilities and look and feel.
  - **6 Fake accounts added using Faker library; can be added using Flask CLI command 'seed-db'.**

[BACKEND] Maintenance (1/19/26)
  - _Add logger to make operations of the app more transparent._
  - **Added logger, replaced print stmts with logging to logs folder.**

[BACKEND] Structure (1/19/26)
  - _Configuration is spread out over several files. Should consolidate into config.py_
    - **Created configuration file with dev, testing, deploy configs**

Status reporting (1/18/26)
  - _No error messages reported to user on failed registration or login, only messages in console. Add a message below the black text input bars._
  - **Informative Error messages now reported as red text at bottom of container.**