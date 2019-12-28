
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
                if (msg.receiver == null) { cls = "received"; } else { cls = "sent"; }
                $("#messages ul").append("<li class=\"" + cls + "\">"
                    +"<span class=\"message-text\">" + msg.body + "</span><br>"
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
            var data = {sender: sender, receiver: receiver, message: message}
            $("#disable").show()
            $.ajax({
                url: "senddata.php",
                data: {sender: sender, receiver: receiver, message:message},
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
