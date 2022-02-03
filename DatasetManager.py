"""
Purpose of this class is to interface with the SQL database where our labels are stored.
"""

from sqlite3 import connect, Error
from enums import *

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

        # Check to see if this record exists already
        sql = """select id from labels where location={} and import_dt='{}' and cam={} and vid={}
                and frame={} and start_x={} and start_y={} and end_x={} and end_y={}""".format(
            location, import_dt, cam, vid, frame, start_x, start_y, end_x, end_y
        )
        existing = self.conn.execute(sql).fetchall()

        if len(existing) > 1:           # CASE multiple labels for one object? This is an error!
            assert False, "ERROR: Multiple labels for this object!"
        elif len(existing) == 1:        # CASE label already here? Update this label with a new class.
            id = existing[0][0]
            sql = "update labels set class={} where id={}".format(c, id)
            self.conn.execute(sql)
            self.conn.commit()

            print("Updated record {} with class {}".format(id, c))
        else:                           # CASE no label existing? Create entirely new label!
            sql = """insert into labels (location, import_dt, cam, vid, frame, class, start_x, start_y, end_x, end_y) 
                    values ({}, '{}', {}, {}, {}, {}, {}, {}, {}, {});""".format(
                location, import_dt, cam, vid, frame, c, start_x, start_y, end_x, end_y
            )

            self.conn.execute(sql)
            self.conn.commit()

            print("Added record: l={} d={} c={} v={} f={} cls={} x1={} y1={} x2={} y2={}".format(
                location, import_dt, cam, vid, frame, c, start_x, start_y, end_x, end_y)
            )

    def retrieve_labels(self, location, import_dt, cam, vid, frame):
        sql = """select class, start_x, start_y, end_x, end_y from labels 
        where location={} and import_dt='{}' and cam={} and vid={} and frame={}""".format(
            location, import_dt, cam, vid, frame
        )

        return self.conn.execute(sql).fetchall()

    def retrieve_frame_state(self, location, import_dt, cam, vid, frame):
        """
        Retrieves the state of the frame from the DB. If no record is found, then it will create a generic record.
        :param location: location where it was taken
        :param import_dt: date which it was imported
        :param cam: camera number
        :param vid: video number
        :param frame: frame number
        :return: status - is_labeled
        """

        sql = "select is_labeled from frame_status where " \
              "location={} and import_dt='{}' and cam={} and vid={} and frame={}".format(
            location, import_dt, cam, vid, frame
        )

        self.conn.execute(sql)
        res = self.conn.execute(sql).fetchall()

        if len(res) == 1: return res[0][0]
        elif len(res) > 1:
            assert False, "Found more than 1 record for : {}".format(sql)
        elif len(res) == 0:
            sql = """insert into frame_status (location, import_dt, cam, vid, frame, is_labeled)
                    values ({}, '{}', {}, {}, {}, {})""".format(
                location, import_dt, cam, vid, frame, LABEL_STATUS_UNLABELED
            )

            self.conn.execute(sql)
            self.conn.commit()

            return LABEL_STATUS_UNLABELED

    def update_frame_state(self, location, import_dt, cam, vid, frame, new_label):
        sql = """update frame_status set is_labeled={} where 
        location={} and import_dt='{}' and cam={} and vid={} and frame={};""".format(
            new_label, location, import_dt, cam, vid, frame
        )

        self.conn.execute(sql)
        self.conn.commit()

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
        ); """

        self.create_table(conn, sql)

    def get_labeled_frames(self):
        """
        Will get a list of frames that have been labeled.
        However, a label could include nothing being in that frame at all.
        :return: list of frames that have a label
        """

        sql = """select location, import_dt, cam, vid, frame from frame_status where is_labeled=1
                order by location, import_dt, cam, vid, frame"""

        return self.conn.execute(sql).fetchall()

    def get_frames_with_objects(self):
        """
        Purpose of this is to get a list of frames that have an object as being labeled inside of them
        :return: List of frames with an object inside of them
        """

        sql = "select distinct location, import_dt, cam, vid, frame from labels"

        return self.conn.execute(sql).fetchall()