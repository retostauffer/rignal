#!/usr/bin/python3


if __name__ == "__main__":

    import sys
    import argparse

    parser = argparse.ArgumentParser(description = "signal send messages")
    parser.add_argument("-s", "--sender", type = str,
                        dest = "sender",
                        help = "Number of the user who sends the message")
    parser.add_argument("-r", "--receiver", type = str,
                        dest = "receiver",
                        help = "Number of the user who should get the message")
    parser.add_argument("-m", "--message", type = str,
                        dest = "message",
                        help = "Message")

    args = parser.parse_args()


    import json
    def escape(x):
        import html
        return("\"{0:s}\"".format(html.escape(x)))

    # TODO FIX PATH !!!
    cmd = ["/home/retos/.signal/bin/signal-cli", "-u", args.sender,
           "send", "-m", escape(args.message),
           args.receiver]
    #print(json.dumps({"return":" ".join(cmd)}))

    import subprocess as sub
    p = sub.Popen(cmd, stdout = sub.PIPE, stderr = sub.PIPE)
    out,err = p.communicate()

    out = out.decode("utf-8")
    err = err.decode("utf-8")

    print(json.dumps({"cmd": " ".join(cmd),
                      "out": out if len(out) > 0 else None,
                      "err": err if len(err) > 0 else None,
                      "code": p.returncode}))
    sys.exit(0)

