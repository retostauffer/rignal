

import sqlite3
import logging
logger = logging.getLogger("rignal")


class msgdb:

    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    def __init__(self, dbname = "signal.sqlite3", verbose = False):

        self.verbose = verbose

        import sqlite3
        try:
            self.con = sqlite3.connect(dbname)
        except:
            raise Exception("Cannot open sqlite3 connection to \"{:s}\"".format(dbname))

        self._check_usertable()
        self._check_messagetable()
        self._check_attachmenttable()
        self._check_groupmemberstable()

    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    def close(self):
        """close()

        Close sqlite3 database connection.
        """
        self.con.close() 


    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    def update_group(self, msg):
        """update_group(msg)

        Update group information, triggered if we have group information
        in a message.

        Parameters
        ==========
        msg : msgparser object

        Returns
        =======
        No return, updates database.
        """

        from msgparserClass import msgparser
        if not isinstance(msg, msgparser):
            raise ValueError("input to update_group needs to be a msgparser instance")

        grp = msg.get("group")
        # groups are handled as users.
        groupID = self.get_userID(grp.get("id"), grp.get("name"))

        cur = self.con.cursor()
        # Members?
        if len(grp.get("members")) > 0:
            for mem in grp.get("members"):
                userID = self.get_userID(mem)
                sql = "INSERT OR IGNORE INTO groupmembers VALUES ({0:d}, {1:d})".format(groupID, userID)
                cur.execute(sql)
        self.con.commit()

    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    def add_message(self, msg):
        """add_message(msg)

        Add a message to the database.

        Parameters
        ==========
        msg : msgparser object

        Returns
        =======
        No return (raises an exception if something goes wrong)
        """

        from msgparserClass import msgparser
        if not isinstance(msg, msgparser):
            raise ValueError("input to add_message needs to be a msgparser instance")

        # If this message has group information the message is related
        # to a specific group (not a single user). Instead of using the
        # number of the sender/receiver, use group ID to store the message.
        if not msg.get("group") is None:
            userID = self.get_userID(msg.get("group").get("id"))
        # Else single user message
        else:
            userID = self.get_userID(msg.get("number"))
        self._add_message(userID, msg)


    def _add_attachments(self, att, sent):
        """self._add_attachment(att, sent)

        Parameters
        ==========
        att : list of msgattachment object
            The attachment information object.
        sent : bool
            True for sent attachemnts, False for received ones.

        Return
        ======
        Saves attachment information into database and returns
        the attachment ID's as integer list.
        """

        from os.path import basename
        from msgparserClass import msgattachment

        if not isinstance(sent, bool):
            raise ValueError("sent must be boolean True or False")

        cur = self.con.cursor()
        sql = "INSERT OR IGNORE INTO attachments (mime, sent, name) VALUES (\"{0:s}\", {1:d}, \"{2:s}\")"
        for rec in att:
            if not isinstance(rec, msgattachment):
                raise ValueError("att must be of instance msgattachment")
            cur.execute(sql.format(rec.get("mime"), 1 if sent else 0, basename(rec.get("path"))))

        # Fetch ID's
        sql = "SELECT attachmentID FROM attachments WHERE sent = {0:d} AND name IN ({1:s})"
        names = ["\"{0:s}\"".format(basename(rec.get("path"))) for rec in att]
        cur.execute(sql.format(1 if sent else 0, ", ".join(names)))
        res = [x[0] for x in cur.fetchall()]

        return(res)


    def _add_message(self, userID, msg):

        from json import dumps
        att  = msg.get("attachments")

        # Attachment ID's are stored as json array
        if att is not None:
            att = self._add_attachments(att, msg.get("sent"))
        else:
            att = []

        sql  = "INSERT OR IGNORE INTO messages (userID, sent, timestamp, body, attachments) VALUES "
        sql += "(?, ?, ?, ?, ?);"
        
        data = (userID, msg.get("sent"), msg.get("timestamp"), msg.get("body"), dumps(att))
        
        cur = self.con.cursor()
        cur.execute(sql, data)
        try:
            cur.execute(sql, data)
            self.con.commit()
        except Exception as e:
            print(e)
            raise Exception("Problems adding new message")


    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    def _check_usertable(self):

        cur = self.con.cursor()
        try:
            cur.execute("SELECT * FROM users LIMIT 1;")
            exists = True
        except:
            exists = False

        if not exists:
            if self.verbose: print("Create users database table")

            sql = """CREATE TABLE users (
                    userID INTEGER PRIMARY KEY AUTOINCREMENT,
                    number TEXT NOT NULL,
                    name TEXT
                  )"""
            try:
                cur.execute(sql)
            except:
                raise Exception("Problems creating users table!")


    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    def _check_messagetable(self):

        cur = self.con.cursor()
        try:
            cur.execute("SELECT * FROM messages LIMIT 1;")
            exists = True
        except:
            exists = False

        if not exists:
            logger.debug("Create messages database table")

            sql = """CREATE TABLE messages (
                    userID INTEGER NOT NULL,
                    sent INTEGER NOT NULL,
                    receiver INTEGER, timestamp INTEGER NOT NULL, body text,
                    attachments TEXT DEFAULT NULL,
                    CONSTRAINT msg UNIQUE (userID, timestamp)
                  )"""
            try:
                cur.execute(sql)
            except Exception as e:
                print(e)
                raise Exception("Problems creating messages table!")

    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    def _check_attachmenttable(self):

        cur = self.con.cursor()
        try:
            cur.execute("SELECT * FROM attachments LIMIT 1;")
            exists = True
        except:
            exists = False

        if not exists:
            logger.debug("Create attachments database table")

            sql = """CREATE TABLE attachments (
                    attachmentID INTEGER PRIMARY KEY AUTOINCREMENT,
                    mime TEXT NOT NULL,
                    sent INT NOT NULL,
                    name TEXT NOT NULL,
                    CONSTRAINT att UNIQUE (sent, name)
                  )"""
            try:
                cur.execute(sql)
            except Exception as e:
                print(e)
                raise Exception("Problems creating attachment table!")



    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    def _check_groupmemberstable(self):

        cur = self.con.cursor()
        try:
            cur.execute("SELECT * FROM groupmembers LIMIT 1;")
            exists = True
        except:
            exists = False

        if not exists:
            if self.verbose: print("Create groupmembers database table")

            sql = """CREATE TABLE groupmembers (
                    groupID INTEGER NOT NULL,
                    userID INTEGER NOT NULL,
                    CONSTRAINT gm UNIQUE (groupID, userID)
                  )"""
            try:
                cur.execute(sql)
            except Exception as e:
                print(e)
                raise Exception("Problems creating groupmembers table!")


    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    def get_userID(self, number, name = None, create = True):
        """get_userID(number, name = None, create = True)

        Get userID for a specific phone number.

        Parameters
        ==========
        number : str
            string, phone number (with leading +)
        name : str
            string, name of the person/group. Default is None (no name).
        create : bool
            whether or not the user should be created if not yet existing.

        Returns
        =======
        Returns the userID (integer) if found. If create is set to True (default)
        the user will be created if not yet existing and the new ID will be returned.
        If create is set to False and the user does not exist an error will be raised.
        """

        cur = self.con.cursor()
        sql = "SELECT userID FROM users WHERE number = \"{:s}\";".format(number)
        try:
            res = cur.execute(sql)
        except:
            raise Exception("Problems reading number from users database.")

        res = res.fetchall()
        # If create is False and user does not exist: stop.
        if len(res) == 0 and not create:
            raise Exception("Cannot find user for \"{:s}\"".format(number))
        # user not found? Add!
        elif len(res) == 0:
            if name is None:
                sql = "INSERT INTO users (number) VALUES (\"{:s}\");".format(number)
            else:
                sql = "INSERT INTO users (number, name) VALUES (\"{:s}\", \"{:s}\");".format(number, name)
            try:
                cur.execute(sql)
                self.con.commit()
            except Exception as e:
                print(e)
                raise Exception("Problems adding new user {:s}".format(number))

            if self.verbose: print("Added user \"{:s}\" to users table".format(number))
            res = self.get_userID(number)
        else:
            res = res[0][0]

        return(int(res))



    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    def _add_user(self, number):
        cur = self.con.cursor()
        sql = "INSERT INTO users (number) VALUES (\"{:s}\");".format(number)
        try:
            cur.execute(sql)
        except:
            raise Exception("Problems adding new user \"%s\".".format(number))
        if self.verbose: print("Added new user \"{:s}\"".format(number))


    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    def get_messages(self, number, time_from = None, time_to = None):
        """get_messages(number, time_from = None, time_to = None)

        Parameters
        ==========
        number : str or int
            phone number of the user (string) or userID (integer)
        time_from : None or integer
            if integer: unix time stamp, messages from this timestamp will be loaded
        time_to : None or integer
            if integer: unix time stamp, messages up to this timestamp will be loaded

        Returns
        =======
        Returns a msgs object containing the messages.
        """

        if not isinstance(number, str) and not isinstance(number, int):
            raise ValueError("number must be either string (phone number) or integer (userID)")
        if not isinstance(time_from, type(None)) and not isinstance(time_from, int):
            raise ValueError("time_from has to be None or an integer!")
        if not isinstance(time_to, type(None)) and not isinstance(time_to, int):
            raise ValueError("time_to has to be None or an integer!")

        # Loading user ID
        if isinstance(number, str):
            userID = self.get_userID(number, create = False)
        else:
            userID = number

        ##sql = "SELECT timestamp, body, attachments FROM messages WHERE userID = {:d}".format(userID)
        ##if time_from: sql += " AND timestamp >= {:d}".format(time_from)
        ##if time_to:   sql += " AND timestamp >= {:d}".format(time_to)
        ##sql += " ORDER BY timestamp ASC;"
        sql = "SELECT * FROM messages WHERE userID = {:d}".format(userID)
        if time_from: sql += " AND timestamp >= {:d}".format(time_from)
        if time_to:   sql += " AND timestamp >= {:d}".format(time_to)
        sql += " ORDER BY timestamp ASC;"

        # Loading messages
        res = self.con.cursor().execute(sql)
        col = [x[0] for x in res.description]

        data = msgs(self.con)
        for rec in res.fetchall():
            msg = {}
            for i in range(0, len(rec)): msg[col[i]] = rec[i]
            data.add(msg)

        return(data)


    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    def get_users(self):
        """get_users()

        Returns
        =======
        Returns a users object containing the registered users
        """

        sql = "SELECT u.userID, u.number, u.name, m.timestamp FROM users AS u " + \
              "LEFT JOIN (" + \
              "    SELECT userID, max(timestamp) AS timestamp FROM messages " + \
              "    GROUP BY userID) AS m " + \
              "ON u.userID = m.useRID " + \
              "ORDER BY timestamp DESC"

        # Loading messages
        res = self.con.cursor().execute(sql)
        col = [x[0] for x in res.description]

        data = users()
        for rec in res.fetchall():
            user = {}
            for i in range(0, len(rec)): user[col[i]] = rec[i]
            data.add(user)

        return(data)

# --------------------------------------------------------------------
# --------------------------------------------------------------------
class msgs:
    """msgs(con)

    Parameters
    ==========
    con : sqlite3 connection handler
    """

    def __init__(self, con):
        self._data = []
        self.con = con

    def __repr__(self):
        return("Message list, contains {:d} messages.".format(len(self._data)))

    def add(self, msg):
        """add(msg)

        Parameters
        ==========
        msg : dict
        """
        if not isinstance(msg, dict):
            raise ValueError("input must be a (well defined) dict!")

        from json import JSONDecoder
        d = JSONDecoder()
        att = d.decode(msg.get("attachments"))

        # Loading file information from database
        if len(att) > 0:
            sql = "SELECT * FROM attachments WHERE attachmentID IN ({0:s})".format(
                    ", ".join(["{:d}".format(x) for x in att]))
            cur = self.con.cursor()
            cur.execute(sql)
            desc = [x[0] for x in cur.description]
            msg["attachments"] = []
            for row in cur.fetchall():
                tmp = {}
                for i in enumerate(desc): tmp[i[1]] = row[i[0]]
                msg["attachments"].append(tmp)
        else:
            msg["attachments"] = []

        self._data.append(msg)
        ### TODO some checks
        ##for key in self._data.keys():
        ##    self._data[key].append(msg.get(key))

    def data(self):
        """data()

        Returns
        =======
        Returns the messages stored on this object, as list of dicts.
        """
        return(self._data)
    #def json(self):
    #    from json import dumps
    #    from re import match
    #    res = dumps(self._data, ensure_ascii = False)
    #    print(res)


# --------------------------------------------------------------------
# --------------------------------------------------------------------
class users:

    def __init__(self):
        self._data = []

    def __repr__(self):
        return("User list, contains {:d} messages.".format(len(self._data)))

    def add(self, user):
        """add(user)

        Parameters
        ==========
        user : dict
        """
        if not isinstance(user, dict):
            raise ValueError("input must be a (well defined) dict!")

        self._data.append(user)

    def data(self):
        """data()

        Returns
        =======
        Returns the users stored on this object, as list of dicts.
        """
        return(self._data)






