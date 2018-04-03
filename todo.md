* better faq/assistance commands system
* list of auto-approved servers, and auto-remove ones not approved
* list words that triggered a filter action
* things I forgot...

technical stuff:
* mod/server logs base
* replace connwrap, not necessary as the Connection is already a context manager
* move warn features to a separate class/file (makes it easier for any cmd to add a warn)
