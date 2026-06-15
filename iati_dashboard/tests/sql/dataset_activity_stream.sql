CREATE TABLE dataset_activity_stream (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_type text NOT NULL,
    display_category text,
    message_date TIMESTAMPTZ NOT NULL,
    dataset_id UUID NOT NULL,
    payload JSON NOT NULL
);
