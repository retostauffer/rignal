
(function ( $ ) {
 
    $.fn.rignal = function() {

        function timestamp_to_str(ts) {
            var ts = new Date(ts);
            var date = $.datepicker.formatDate("yy-mm-dd", ts);
            var hour = ts.getHours();
            var mins = ts.getMinutes();
            if (hour < 10) { hour = "0" + hour; }
            if (mins < 10) { mins = "0" + mins; }
            return(date + " " + hour + ":" + mins);
        }

        /* Show users */
        function show_users(users) {
            $("#users").empty().append("<ul></ul>");
            var ul = $("#users").find("ul");
            $.each(users, function(k, user) {
                if (user.name !== null) {
                    var name = "<div>" + user.name + "</div>" + user.number
                } else {
                    var name = user.number
                }
                $(ul).append("<li number=\"" + user.number + "\" userid=\"" +
                             user.userID + "\">" + name + "</li>");
            });

            // Add interaction
            $(ul).on("click", "li", function() {
                var userID = $(this).attr("userid");
                var number = $(this).attr("number");
                load_messages(userID, number);
            });
        }

        /* Show messages */
        function show_messages(msgs) {
            console.log(msgs)
            $("#messages").empty().append("<ul></ul>");
            var cls = "undefined";
            $.each(msgs, function(k, msg) {

                var time = timestamp_to_str(msg.timestamp);

                if (msg.sent != "1") { cls = "received"; } else { cls = "sent"; }

                /* Crete attachments output */
                var attachments = ""
                if (msg.attachments.length > 0) {
                    $.each(msg.attachments, function(k, att) {
                        if (parseInt(att.sent) == 1) {
                            var dir = "uploads";
                        } else {
                            var dir = "attachments";
                        }
                        if (att.mime == "image/jpeg") {
                            tmp = "<img src=\"" + dir + "/" + att.name + "\" />"
                            attachments += tmp
                        }
                    });
                    /* Final html markup */
                    attachments = "<span class=\"message-attachments\">"
                                + attachments
                                + "</span><br>"

                }

                /* Create final markup */
                $("#messages ul").append("<li class=\"" + cls + "\">"
                    +"<span class=\"message-text\">" + msg.body + "</span><br>"
                    +attachments
                    +"<span class=\"time\">" + time + "</span></li>");
            });
        }

        /* Show send form */
        function show_send(userID, number) {
            $("#send").empty().append("<form />")
            // Create form
            $("#send > form")
                .append("<input type=\"text\" name=\"message\" value=\"retos signal client test message\" />")
                .append("<input type=\"hidden\" name=\"receiver\" value=\"" + number + "\" />")
                .append("<input type=\"hidden\" name=\"receiverID\" value=\"" + userID + "\" />")
                .append("<input type=\"button\" name=\"send\" value=\"SEND\" />")
                .append("<input style=\"margin-left: 1em;\" type=\"checkbox\" name=\"hot\" value=\"hot\" /> hot?")
                .append("<div>Receiver: " + number + "</div>")
                .append("<input type = \"file\" name = \"upload\" />")
                .append("<span id = \"attached-file\" />")

            // simpleUpload functionality
            $("#send > form > input[name='upload']").on("change", function() {
                $(this).simpleUpload("fileupload.php", {
                    start: function(file){
                        //upload started
                        console.log("upload started");
                    },
                    //progress: function(progress){
                    //    //received progress
                    //    console.log("upload progress: " + Math.round(progress) + "%");
                    //},
                    success: function(data){
                        //upload successful
                        console.log("upload successful!");
                        console.log(data);
                        console.log(data.success)
                        if (data.success) {
                            $("#attached-file").html("<b>Attached file: <i>" + data.filename + "</i></b>")
                            $("#attached-file").attr("filename", data.filename)
                        } else {
                            alert("Whoops, problem with file upload (got non-success return from php)");
                        }
                    },
                    //error: function(error){
                    //    //upload failed
                    //    console.log("upload error: " + error.name + ": " + error.message);
                    //}
                });
            });

            // Show form
            $("#send").show();

            // Add interaction
            $("#send > form > input[name='send']").on("click", function() {
                var message    = $(this).closest("form").find("input[name=\"message\"]").val();
                var receiverID = $(this).closest("form").find("input[name=\"receiverID\"]").val();
                var receiver   = $(this).closest("form").find("input[name=\"receiver\"]").val();
                var sender     = "+436803328544";

                if (!$(this).closest("form").find("input[name=\"hotr\"]").is(":checked")) {
                    receiver = sender
                }

                send_data(sender, receiver, message);
            });
        }


        /* Loading user messages */
        function load_messages(userID, number) {
            get_data({"userID":userID})
            var div = $("#messages");
            var window_height = parseInt($(window).height());
            var header_height = parseInt($("#header").height());
            var height = window_height - header_height - 100;

            div.css("height", height).animate({scrollTop: div.height() + 10000});
            console.log(height)

            show_send(userID, number)
        }

        /* Send message to user
         * Returns
         * =======
         * TODO: development JSON
         */
        function send_data(sender, receiver, message) {

            // Check if we have an attachment
            if ($("#attached-file").length == 1) {
                var attachment = $("#attached-file").attr("filename")
            } else {
                var attachment = null
            }
            var data = {sender: sender, receiver: receiver, message: message,
                        attachment: attachment}
            $("#disable").show()
            $.ajax({
                url: "senddata.php",
                data: data,
                type: "post",
                dataType: "JSON",
                success: function(res) {
                    if (res.err !== null) {
                        alert(res.err)
                    } else {
                        console.log(res)
                    }
                    $("#disable").hide()
                }, error: function(xhr, ajaxOptions, thrownError) {
                    console.log(xhr.status);
                    console.log(thrownError);
                }
            });
        }

        /* Loading data (via ajax php/python)
         * Returns
         * =======
         * No return, calls the functions who set up the UI.
         */
        function get_data(data = {}) {
            console.log(data)
            $.ajax({
                url: "getdata.php",
                data: data,
                type: "post",
                dataType: "JSON",
                success: function(res) {
                    console.log(res)
                    if (data.get == "userlist") {
                        show_users(res);
                    } else {
                        // Show messages ...
                        show_messages(res);
                    }
                }, error: function(xhr, ajaxOptions, thrownError) {
                    console.log(data)
                    console.log(xhr.status);
                    console.log(thrownError);
                }
            });
        }

        /* On initialization: load/show users */
        get_data({"get": "userlist"})
        var userID = $("#users ul li:first-child").attr("userid");
        get_data({"userID":parseInt(userID)});
    };
 
}( jQuery ));
