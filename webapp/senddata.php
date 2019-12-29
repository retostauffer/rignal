<?php

// if started from commandline, wrap parameters to $_POST and $_GET.
// Allows to test the php script from console calling:
// php getdata.php "key1=arg1&key2=arg2" or what you need.
//
// php senddata.php "receiver=+436803328544&sender=+436803328544&message=phptest&attachment=343434"
if (!isset($_SERVER["HTTP_HOST"])) {
    if (count($argv) > 1) { parse_str($argv[1], $_POST); }
}
if (!isset($_POST)) { $_POST = array(); }
$_POST = (object)$_POST;

// Check if only users are requested
$sender      = (property_exists($_POST, "sender"))   ? $_POST->sender : False;
$receiver    = (property_exists($_POST, "receiver")) ? $_POST->receiver : False;
$message     = (property_exists($_POST, "message"))  ? $_POST->message : False;
$attachment  = (property_exists($_POST, "attachment"))  ? $_POST->attachment : False;

$message = htmlspecialchars($message);

if ($message && $sender && $receiver) {
    error_log(json_encode(array("status" => "sent",

                  "sender" => $sender,
                  "attachment" => $attachment,
                  "receiver" => $receiver,
                  "message" => $message)));
    $cmd = sprintf("cd ../bin && ./send.py -s \"%s\" -r \"%s\" -m \"%s\"",
                  $sender, $receiver, $message);
    if ($attachment) {
        $cmd .= sprintf(" -a %s", $attachment);
    }

    system($cmd);
}
