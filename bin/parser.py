#!/usr/bin/python3


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description='signal parser')
    parser.add_argument("-g", "--get", action = "store_true",
                        help = "If set, try to recieve messages.")
    parser.add_argument("-j", "--json", action = "store_true",
                        help = "Get json array in return (I/O)")
    parser.add_argument("-f", "--from", type = int, default = None,
                        dest = "time_from",
                        help = "UNIX time stamp (integer)")
    parser.add_argument("-t", "--to", type = int, default = None,
                        dest = "time_to",
                        help = "UNIX time stamp (integer)")
    parser.add_argument("-u", "--userID", type = int, default = None,
                        help = "userID if messages for a specific user should be loaded")
    parser.add_argument("--userlist", action = "store_true",
                        help = "only return userlist if used in combination with -j/--json")
    parser.add_argument("-l", "--loglevel", type = str, default = "DEBUG",
                        help = "Logger level. 0/ERROR, 1/INFO, 2/DEBUG")

    args = parser.parse_args()

    # JSON: always set logger to ERROR
    if args.json:
        args.loglevel = "ERROR"
    else:
        loglevels_allowed = ["0", "1", "2", "ERROR", "INFO", "DEBUG"]
        if not args.loglevel in loglevels_allowed:
            raise ValueError("Input -l/--loglevel invalid. Allowed: " + \
                    "{0:s}".format(", ".join(loglevels_allowed)))
        elif args.loglevel in ["0", "1", "2", "3"]:
            args.loglevel = {"0":"ERROR", "1":"INFO", "2":"DEBUG", "3":"ALL"}[args.loglevel]
    # Initiate logger
    import logging
    logging.basicConfig(format = "%(levelname)s: %(message)s")
    logger = logging.getLogger("rignal")
    logger.setLevel(getattr(logging, args.loglevel))

    # Checking from/to time stamps
    if args.time_from and args.time_to:
        if args.time_from >= args.time_to:
            raise ValueError("from has to be smaller than to")

    verbose = True
    if args.json: verbose = False

    # Main script part ...
    from msgdbClass import msgdb
    from msghandlerClass import msghandler
    
    db  = msgdb(verbose = verbose)
    obj = msghandler("messages", verbose)

    # Loading all users from the database
    users = db.get_users()
    if args.userlist and args.json:
        from json import dumps
        print(dumps(users.data()))
        import sys; sys.exit(0)

    # JSON
    elif args.userID and args.json:
        msgs = db.get_messages(args.userID, args.time_from, args.time_to)
        from json import dumps
        print(dumps(msgs.data()))
        import sys; sys.exit(0)

    # Currently ony one else condition
    else:
        ignore = ["STARTED", "DELIVERED", "STOPPED", "DELIVER"]
        for rec in obj.iteritems():
            if rec.get("action") in ignore:
                import sys
                #print(rec)
                sys.exit(3)
            ## Adding message to database
            #print("_______________________")
            #print("Adding message to db")
            #print(rec)
            db.add_message(rec)
    
    db.close()



