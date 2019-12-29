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
    parser.add_argument("-a", "--attachment", type = str, default = None,
                        dest = "attachment",
                        help = "Attachment (name of file in upload directory)")


    args = parser.parse_args()


    import json
    def escape(x):
        import html
        return("\"{0:s}\"".format(html.escape(x)))

    # TODO FIX PATH !!!
    from re import match
    if match("^\\+[0-9]+$", args.receiver):
        cmd = ["/home/retos/.signal/bin/signal-cli", "-u", args.sender,
               "send", "-m", escape(args.message),
               args.receiver]
    else:
        cmd = ["/home/retos/.signal/bin/signal-cli", "-u", args.sender,
               "send", "-m", escape(args.message),
               "-g", args.receiver]

    # TODO FIX PATH !!!
    att = None # Default
    if args.attachment is not None:
        import os
        att = os.path.join("/home/retos/.local/share/signal-cli/uploads", args.attachment)
        cmd += ["-a", att]

        # Does the attachment exist?
        if not os.path.isfile(att):
            print(json.dumps({"cmd": " ".join(cmd),
                              "out": None,
                              "err": "Error, attachment not found on disc! Path wrong?",
                              "code": 999}))
            import sys; sys.exit(9)



    # ------------------------------------------
    # Send information
    # ------------------------------------------
    from subprocess import run, PIPE, TimeoutExpired
    from threading import Timer

    # Timeout for sending via signal-cli
    timeout_secs = 10
    try:
        p = run(cmd, timeout = timeout_secs, stdout = PIPE, stderr = PIPE)
        out = p.stdout.decode("utf-8")
        err = p.stderr.decode("utf-8")
        returncode = p.returncode
    except TimeoutExpired:
        out = ""
        err = "Run into timeout while sending message"
        returncode = 888 # Timeout flag 888
    except Exception as e:
        log.error(e)
        out = ""
        err = "subprocess.run ran into an exception!"
        returncode = 999 # Error flag

    # Create output message file
    from datetime import datetime as dt
    now = dt.now()
    timestamp  = int(now.strftime("%s")) * 1000 + now.microsecond
    timestring = now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    # Create output string (message information)
    res = """
Envelope to: {0:s} (device: -9)
Timestamp: {2:d} ({3:s})
Sender: {1:s} (device: -9)
Message timestamp: {2:d} ({3:s})
Body: {4:s}
Profile whatever
"""
    res = res.format(args.receiver, args.sender, timestamp, timestring, args.message)


    # ------------------------------------------
    # If we have an attachment
    # ------------------------------------------
    if att:

        from os.path import basename, getsize
        from magic import Magic
        import re

        # File mime type
        m = Magic(mime = True)
        mime = m.from_file(att)

        # Image aggachment?
        if re.match("^image", mime):
            tmp = """Attachments:
- {0:s} (Pointer)
  Id: {1:s} Key length: 64
  Filename: -
  Size: {2:d} bytes
  Voice note: no
  Dimensions: {3:d}x{4:d}
  Stored plaintext in: {5:s}

"""

            # Image dimension
            from PIL import Image
            im = Image.open(att)
            width,height = im.size
            
            tmp = tmp.format(mime,
                             basename(att),
                             getsize(att),
                             width,
                             height,
                             att)
            res += tmp
        else:

            print(json.dumps({"cmd": " ".join(cmd),
                              "out": None,
                              "err": "Non-image attachment, not yet coded!",
                              "code": 999}))
            import sys; sys.exit(9)


    # ------------------------------------------
    # Write output file
    # ------------------------------------------
    outfile = "sentmessages/sent_{0:d}.msg".format(timestamp)
    with open(outfile, "w") as fid:
        fid.write(res)
        fid.close()


    # ------------------------------------------
    # Ajax return
    # ------------------------------------------
    print(json.dumps({"cmd": " ".join(cmd),
                      "out": out if len(out) > 0 else None,
                      "err": err if len(err) > 0 else None,
                      "devel": args.attachment,
                      "code": returncode}))
    sys.exit(0)
















