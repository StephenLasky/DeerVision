CREATE TABLE IF NOT EXISTS labels (
        id integer primary key,
        location integer,
        import_dt text,
        cam integer,
        vid integer,
        frame integer,
        class integer,
        start_x integer,
        start_y integer,
        end_x integer,
        end_y integer
);