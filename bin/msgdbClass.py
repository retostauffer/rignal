

import sqlite3

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
        self._check_groupstable()
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

        sql1 = "INSERT OR IGNORE INTO groups (id, name, timestamp) VALUES ('{0:s}', '{1:s}', {2:d});"
        sql2 = "UPDATE groups SET name = '{1:s}', timestamp = {2:d} WHERE id = '{0:s}';"
        sql1 = sql1.format(grp.get("id"), grp.get("name"), msg.get("timestamp"))
        sql2 = sql2.format(grp.get("id"), grp.get("name"), msg.get("timestamp"))

        cur = self.con.cursor()
        try:
            cur.execute(sql1)
            cur.execute(sql2)
            self.con.commit()
        except Exception as e:
            print(e)
            raise Exception("Problems adding new message")

        # Members?
        if len(grp.get("members")) > 0:
            groupID = cur.execute("SELECT groupID FROM groups WHERE id = '{0:s}';".format(grp.get("id")))
            groupID = groupID.fetchone()[0]

            for mem in grp.get("members"):
                userID = self.get_userID(mem)
                sql = "INSERT OR IGNORE INTO groupmembers VALUES ({0:d}, {1:d})".format(groupID, userID)
                print(sql)
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

        # Else add to database.
        userID = self.get_userID(msg.get("number"))
        self._add_message(userID, msg)


    def _add_message(self, userID, msg):

        import sys
        att  = msg.get("attachments")
        att  = len(att) if not att is None else 0
        sql  = "INSERT OR IGNORE INTO messages (userID, receiver, timestamp, body, attachments) VALUES "
        sql += "({:d}, {:d}, {:d}, \"{:s}\", {:d});".format(userID, msg.get("receiver"), msg.get("timestamp"),
                   msg.get("body"), att)
        sql  = "INSERT OR IGNORE INTO messages (userID, timestamp, body, attachments) VALUES "
        sql += "(?, ?, ?, ?);"
        
        data = (userID, msg.get("timestamp"), msg.get("body"), att)

        
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
            if self.verbose: print("Create messages database table")

            sql = """CREATE TABLE messages (
                    userID INTEGER NOT NULL,
                    receiver INTEGER, timestamp INTEGER NOT NULL, body text,
                    attachments INTEGER,
                    CONSTRAINT msg UNIQUE (userID, timestamp)
                  )"""
            try:
                cur.execute(sql)
            except Exception as e:
                print(e)
                raise Exception("Problems creating messages table!")


    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    def _check_groupstable(self):

        cur = self.con.cursor()
        try:
            cur.execute("SELECT * FROM groups LIMIT 1;")
            exists = True
        except:
            exists = False

        if not exists:
            if self.verbose: print("Create groups database table")

            sql = """CREATE TABLE groups (
                    groupID INTEGER PRIMARY KEY AUTOINCREMENT,
                    id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    timestamp INTEGER NOT NULL,
                    avatar TEXT,
                    CONSTRAINT gid UNIQUE (id)
                  )"""
            try:
                cur.execute(sql)
            except Exception as e:
                print(e)
                raise Exception("Problems creating groups table!")
            

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
    def get_userID(self, number, create = True):
        """get_user_id(number)

        Get userID for a specific phone number.

        Parameters
        ==========
        number : str
            string, phone number (with leading +)
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
            sql = "INSERT INTO users (number) VALUES (\"{:s}\");".format(number)
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

        return(res)



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

        data = msgs()
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
    def __init__(self):
        self._data = []
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






