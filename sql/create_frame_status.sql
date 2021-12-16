CREATE TABLE IF NOT EXISTS frame_status (
        id integer primary key,
        location integer,
        import_dt text,
        cam integer,
        vid integer,
        frame integer,
        is_labeled integer
);