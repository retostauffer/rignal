<!DOCTYPE html>
<html lang="en">
<head>
  <title>Bootstrap Example</title>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="css/bootstrap.min.css">
  <link rel="stylesheet" href="css/rignal.css">
  <script src="js/jquery.min.js"></script>
  <script src="js/jquery-ui.min.js"></script>
  <script src="js/popper.min.js"></script>
  <script src="js/bootstrap.min.js"></script>
  <script src="js/rignal.js"></script>
  <script>
  $(document).ready(function() {
    $("body").rignal();
  });
  </script>
</head>
<body>

<div class="container" id="header">
  <h1>Rignal; Retos Signal Client</h1>
</div>

<div class="container">
    <div id="rignal" class="row">
        <div class="col-3" id="users"></div>
        <div class="col-9" id="chat">
            <div id="messages"></div>
            <div id="send"></div>
        </div>
    </div>
</div>
<div id="disable"></div>

</body>
</html>
