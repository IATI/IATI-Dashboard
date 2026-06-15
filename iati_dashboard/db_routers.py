class ActivityStreamRouter:
    """The activity_stream database is externally managed.

    Django must never run migrations against it (or load fixtures into it);
    its only model here is the managed=False DatasetHistoricEvent, which is
    queried with explicit .using("activity_stream").
    """

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return db != "activity_stream"
