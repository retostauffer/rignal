<?php

$config = (object)include("config.inc.php");

if (!is_dir($config->uploaddir)) {
    $res = array("success" => false, "message" => "Upload directory does not exist");
    print(json_encode($res));
    die(0);
} else if (!is_writeable($config->uploaddir)) {
    $res = array("success" => false, "message" => "Upload directory not writeable");
    print(json_encode($res));
    die(0);
}


$new = sprintf("%s/%d", $config->uploaddir, (int)(microtime(true) * 1000.));
#error_log(var_export($_FILES, true));
$success = move_uploaded_file($_FILES["upload"]["tmp_name"], $new);


// $output will be converted into JSON
if ($success) {
    $output = array("success" => true, "message" => "Success!",
                    "filename" => basename($new));
} else {
	$output = array("success" => false, "error" => "Upload failure!");
}


header("Content-Type: application/json; charset=utf-8");
echo json_encode($output);


