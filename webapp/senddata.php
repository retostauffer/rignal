<?php

// if started from commandline, wrap parameters to $_POST and $_GET.
// Allows to test the php script from console calling:
// php getdata.php "key1=arg1&key2=arg2" or what you need.
if (!isset($_SERVER["HTTP_HOST"])) {
    if (count($argv) > 1) { parse_str($argv[1], $_POST); }
}
if (!isset($_POST)) { $_POST = array(); }
$_POST = (object)$_POST;

// Check if only users are requested
$sender   = (property_exists($_POST, "sender"))   ? $_POST->sender : False;
$receiver = (property_exists($_POST, "receiver")) ? $_POST->receiver : False;
$message  = (property_exists($_POST, "message"))  ? $_POST->message : False;

$message = htmlspecialchars($message);

if ($message && $sender && $receiver) {
    #print(json_encode(array("status" => "sent",
    #              "sender" => $sender,
    #              "receiver" => $receiver,
    #              "message" => $message)));
    #die(0);
    system(sprintf("cd ../bin && send.py -s %s -r %s -m \"%s\"",
           $sender, $receiver, $message));
}
