


class msghandler:

    def __init__(self, dir, verbose = False):

        import sys
        import os

        if not os.path.isdir(dir):
            raise Exception("Directory \"{0:s}\" not found!".format(dir))
        self.dir = dir
        self.verbose = verbose

        # Loading available message files
        self.files = self._get_files()
        if self.verbose: print("Found {:d} messasge files".format(len(self.files)))

        # Parse messages
        from msgparserClass import msgparser

        envelops = []
        for file in self.files:
            envelops += self._import_file(file)

        self._messages = []
        for rec in envelops:
            self._messages.append(msgparser(rec))


    def __repr__(self):

        res  = "\nMessage handler object:\n"
        res += " - Number of messages (envelops): {:d}".format(len(self.envelops))
        return(res)


    def _get_files(self):

        from glob import glob
        import os
        import re
        tmp = glob(os.path.join(self.dir, "*"))
        # Filter messages 
        files = []
        pat   = re.compile("^get_[0-9]+\\.msg$")
        for x in tmp:
            x = os.path.basename(x)
            if pat.match(x): files.append(x)

        files.sort()

        return(files)


    def _import_file(self, file):
        """
        Import the raw text files and extract envelops.

        Parameter
        =========
        file : str
            name of the file to be read (basename!)

        Returns
        =======
        Returns a list, either an empty list (if no envelop was
        found) or a list with all envelops.
        """

        import os
        import re

        # full file name
        file = os.path.join(self.dir, file)
        fid = open(file, "r", encoding = "utf-8")
        tmp = fid.readlines()
        fid.close()

        #pat = re.compile("(Envelop.{1}.*?)(?=Envelop|$)", re.M)
        return(re.findall("(Envelop.{1}.*?)(?=Envelop|$)", "".join(tmp), re.S))

    def messages(self):
        """messages()

        Returns
        =======
        Returns a list of all loaded messages (msgparser objects).
        """
        return(self._messages)

    def iteritems(self):
        return self._messages


