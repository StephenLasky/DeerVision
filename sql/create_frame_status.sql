CREATE TABLE IF NOT EXISTS labels (
        id integer primary key,
        location integer,
        import_dt text,
        cam integer,
        vid integer,
        frame integer,
        is_labeled integer
);