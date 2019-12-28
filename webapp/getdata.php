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
$getaction = (property_exists($_POST, "get")) ? $_POST->get : False;
$userID    = (property_exists($_POST, "userID")) ? $_POST->userID : False;

// Call parser (python3), print json
// If we have a userID: load messages
if ($userID) {
    system(sprintf("cd ../bin && ./parser.py -j -u %d", $userID));
} else if ($getaction == "userlist") {
    system("cd ../bin && ./parser.py -j --userlist", $res);
} else {
    system("cd ../bin && ./parser.py -j", $res);
}


