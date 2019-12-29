

import re
import logging
logger = logging.getLogger("rignal")

class msgparser:

    def __init__(self, msg):
        """
        Deparsing an envelop message.

        Parameters
        ==========
        msg : str
            The message (full message)

        Returns
        =======
        No return, stores message information internally.
        """

        import sys
        import os

        self.msg = msg

        logger.debug("--------------------")
        [logger.debug(x) for x in msg.split("\n")]
        logger.debug("--------------------")

        # Sent or received message? From/to whom?
        self._sent,self._number       = self._get_sent_and_number()

        # Rest ...
        self._action       = self._get_action()
        self._receiver     = 0;
        self._timestamp    = self._get_timestamp()
        self._msgtimestamp = self._get_msgtimestamp()
        if self._action in ["RECEIPT", "STARTED", "STOPPED", "DELIVER"]:
            self._body = "No body (no message body)"
        else:
            self._body = self._get_body()
        self._group        = self._get_group()
        self._attachments  = self._get_attachments()


    def __repr__(self):

        if self.get("receiver") == 0:
            res = "Message to you from {:>18s}\n".format(self.get("number"))
        else:
            res = "Message from {:>18s}\n".format(self.get("number"))
        # Add action
        res += "  Action: {:s}\n".format("None" if self.get("action") is None else self.get("action"))
        # Adding body
        body = self.get("body")
        if body is None:
            res += "  Body is empty"
        elif len(body) > 30:
            res += "  Body:   {:s} ...\n".format(body[0:30])
        else:
            res += "  Body:   {:s}\n".format(body)
        # Adding attachment count
        att = self.get("attachments")
        if att is not None:
            res += "  Attachments: {:d}\n".format(len(att))

        return(res)

    def get(self, key):
        """
        Get message information.

        Parameters
        ==========
        key : str
            string, name of the key/infomation.

        Returns
        =======
        Returns the value of the key/information OR None
        if the key cannot be found.
        """

        try:
            res = getattr(self, "_{:s}".format(key))
        except:
            res = None
        return(res)


    def _get_action(self):
        """Extract action from envelope"""

        tmp = re.findall("-\sAction:\s+(.*)", self.msg)
        if len(tmp) == 0:

            # TODO: there must be a saver way
            if len(re.findall("(-\sIs\sread\sreceipt)", self.msg)) > 0:
                return("RECEIPT")
            elif len(re.findall("(Got\sreceipt.)", self.msg)) > 0:
                return("RECEIPT")
            else:
                return None
        if not len(tmp) == 1:
            logger.error(self.msg)
            raise Exception("Found \"from\" (sender) != 1 times!")
        logger.debug("---------------------- {:s}\n".format(tmp[0].strip()))
        return(tmp[0].strip())

    def _get_sent_and_number(self):
        """self._get_sent_and_number()
        
        Extract number from envelope

        Return
        ======
        Returns a list with a boolean (True if this is a message sent to
        someone, False if received) and the number of the receiver.
        """
        #if re.findall("Envelope to:\s+(\+[0-9]+)", self.msg):
        tmp = re.findall("Envelope (from|to):\s+([^\s]+)", self.msg)

        if not len(tmp) == 1:
            logger.error(self.msg)
            raise Exception("Found \"from\" (sender) {0:d} times (expected: once)".format(len(tmp)))
        return([True if tmp[0][0] == "to" else False, tmp[0][1]])

    def _get_timestamp(self):
        """Extract timestamp from envelope"""
        tmp = re.findall("\nTimestamp:\s+([0-9]+)", self.msg)
        if not len(tmp) == 1:
            logger.error(tmp)
            logger.error(self.msg)
            raise Exception("Found \"Timestamp\" != 1 times!")
        return(int(tmp[0]))

    def _get_msgtimestamp(self):
        """Extract message timestamp from envelope"""
        tmp = re.findall("\nMessage\stimestamp:\s+([0-9]+)", self.msg)
        if len(tmp) == 0: return([])
        if not len(tmp) == 1:
            logger.error(tmp)
            logger.error(self.msg)
            raise Exception("Found \"Message timestamp\" != 1 times!")
        return(int(tmp[0]))

    def _get_body(self):
        """Extract body timestamp from envelope"""
        tmp = re.findall("\nBody: (.*)(?=(Group\sinfo|Profile))", self.msg, re.S)
        #if len(tmp) == 0: return("No body (cares)")
        if not len(tmp) == 1:
            logger.error(tmp)
            logger.error(self.msg)
            raise Exception("Not found body")
        res = tmp[0][0].replace("\"", "\\\"")
        if res.endswith("\n"): res = res[:-1]
        return(res)

    def _get_attachments(self):
        """Extract attachment from body (if there is any)"""
        tmp = re.findall("Attachments:(.*)", self.msg, re.S)
        if len(tmp) == 0: return(None)
        # Else decode attachment
        att = []
        for rec in tmp:
            att.append(self._parse_attachment(rec))

        return(att)

    def _parse_attachment(self, att):
        """Parsing attachments: mime type and path (on disc)"""
        import re
        # Mime file type
        mime = re.findall("-\s(.*?)\s+\(Pointer\)", att)
        # Location
        path = re.findall("Stored\splaintext\sin:\s+(.*?)(?=\n)", att)

        return(msgattachment(mime[0] ,path[0]))

    def _get_group(self):
        """Extracting group information.

        Return
        ======
        If not a group message None will be returned, else an
        object of class msgroupinfo.
        """

        import re

        pattern = re.compile("Group\sinfo:\n(.*?)(?=^-)", re.M|re.DOTALL)
        pattern = re.compile("Group\sinfo:\n(.*?)(?=(^Profile\skey|^$))", re.M|re.DOTALL)
        info    = pattern.findall(self.msg)

        # No group info: return None
        if len(info) == 0: return None
        info = info[0][0]

        # Decoding group information
        res = msggroupinfo(info)

        return(res)

class msgattachment:
    def __init__(self, mime, path):

        self._mime = mime
        self._path = path

    def get(self, key):
        try:
            res = getattr(self, "_{0:}".format(key))
        except:
            res = None
        return(res)

    def __repr__(self):
        res = "Attachment information:\n"
        res += "  Mime:    {:s}\n".format(self._mime)
        res += "  Path:    {:s}\n".format(self._path)
        return(res)


class msggroupinfo:

    def __init__(self, msg):

        self.msg = msg
        self._id = self._get_id() 
        self._name = self._get_name() 
        self._type = self._get_type() 

        if self._type == "UPDATE":
            self._members = self._get_members() 
            self._avatar = self._get_avatar() 

    def get(self, what):

        fn = getattr(self, "_get_{0:s}".format(what.lower()))
        if not callable(fn):
            raise Exception("No method _get_{0:s} to get {1:s}".format(what.lower(), what))
        return(fn())

    def _get_id(self):
        from re import findall
        tmp = findall("Id:\s(.*==)", self.msg)
        if len(tmp) != 1:
            print(self.msg)
            raise Exception("problems to extract group ID")
        return(tmp[0])

    def _get_name(self):
        from re import findall
        tmp = findall("Name:\s(.*)", self.msg)
        if len(tmp) != 1:
            print(msg)
            raise Exception("problems to extract group name")
        return(tmp[0].strip())

    def _get_type(self):
        from re import findall
        tmp = findall("Type:\s(.*)", self.msg)
        if len(tmp) != 1:
            print(msg)
            raise Exception("problems to extract group type")
        return(tmp[0].strip())

    def _get_members(self):
        from re import findall
        tmp = findall("Member:\s(\+[0-9]+)", self.msg)
        return(tmp)

    def _get_avatar(self):
        from re import findall, compile

        pattern = "Avatar:\n.*?-\s(.*?)\s\(Pointer\).*?Id:\s([0-9]+).*?Filename:\s([^$.]?)"
        pattern = compile(pattern, re.M|re.DOTALL)
        tmp = pattern.findall(self.msg)
        tmp = tmp[0]

        return({"mime": tmp[0], "id": tmp[1], "name": tmp[2]})


    def __repr__(self):
        res = "Group information:\n"
        res += "  Id:      {:s}\n".format(self._id)
        res += "  Name:    {:s}\n".format(self._name)
        res += "  Type:    {:s}\n".format(self._type)
        if self._type == "UPDATE":
            res += "  Members: {:d}\n".format(len(self._members))
            res += "  Avatar:  {:s}\n".format(self._avatar["id"])
        return(res)










