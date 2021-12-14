"""
Purpose of this class is to interface with the SQL database where our labels are stored.
"""

from sqlite3 import connect, Error

class DatasetManager:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = self.create_connection(self.db_name)
        print("Connection to {} opened!".format(self.db_name))

    def close(self):
        print("Connection to {} closed!".format(self.db_name))
        self.conn.close()

    def create_label(self, location, import_dt, cam, vid, frame, c, start_x, start_y, end_x, end_y):
        """
        Adds a label to the label table.
        :param location: The geographical location of the trail camera. I.e. caddo
        :param import_dt: Date of import. Example 'dec4-2021'
        :param cam: Camera number. Example 1-6 [one-indexed]
        :param vid: Video Number. Example 1-30+ [one-indexed]
        :param frame: Frame number. [zero indexed]
        :param c: Classification. [zero indexed]
        :param start_x: starting x-pixel [zero indexed]
        :param start_y: starting y-pixel [zero indexed]
        :param end_x: ending x-pixel
        :param end_y: ending y-pixel
        :return: N/a
        """

        sql = """insert into labels (location, import_dt, cam, vid, frame, class, start_x, start_y, end_x, end_y) 
                values ({}, '{}', {}, {}, {}, {}, {}, {}, {}, {});""".format(
            location, import_dt, cam, vid, frame, c, start_x, start_y, end_x, end_y
        )

        self.conn.execute(sql)
        self.conn.commit()

        print("Added record: l={} d={} c={} v={} f={} cls={} x1={} y1={} x2={} y2={}".format(
            location, import_dt, cam, vid, frame, c, start_x, start_y, end_x, end_y)
        )

    def create_connection(self, db_file):
        """ create a database connection to the SQLite database
            specified by db_file
        :param db_file: database file
        :return: Connection object or None
        """
        conn = None
        try:
            conn = connect(db_file)
            return conn
        except Error as e:
            print(e)

        return conn

    def create_table(self, conn, create_table_sql):
        """ create a table from the create_table_sql statement
        :param conn: Connection object
        :param create_table_sql: a CREATE TABLE statement
        :return:
        """
        try:
            c = conn.cursor()
            c.execute(create_table_sql)
        except Error as e:
            print(e)

    def create_object_label_table(self, conn):
        sql = """CREATE TABLE IF NOT EXISTS labels (
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
        ); """

        self.create_table(conn, sql)