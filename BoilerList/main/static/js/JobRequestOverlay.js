/**
 * Created by mattchiou1 on 10/2/16.
 */
    $(document).ready(function(){
        jrIDStr = getQueryVariable('jobrequestID');
        if (jrIDStr) {
            jrID = parseInt(jrIDStr);
            showOverlay(jrID)
        }
    });
    var ESC_KEY = 27; // ecs key value

    function closeOverlay() {
        $(".jobrequest-overlay:visible").hide();
        $(".jobrequest-overlay-contain").hide();
        jrIDStr = getQueryVariable('jobrequestID');
        if (getQueryVariable('jobrequestID')) {
            window.history.replaceState(null,null,'dash');
        }
    }
    function showOverlay(jobrequestID) { // jobrequestID should be an integer instead of a string here
        $(".jobrequest-overlay-contain").show();
        $('[overlayID="'+jobrequestID+'"]').show();
        window.history.replaceState(null,null,'dash?jobrequestID='+jobrequestID);
    }
    function showEventOverlay(event){
        event.preventDefault();
        event.stopPropagation();
        var jobrequestID;
        if ($(event.target).hasClass("jobrequest-overlay-trigger")) {
            jobrequestID = $(event.target).attr("jobrequestID");
        } else {
            jobrequestID = $(event.target).parent().attr("jobrequestID");
        }
        showOverlay(jobrequestID)
    }

    $(".jobrequest-overlay-trigger").click(showEventOverlay);

    $(".jobrequest-overlay-contain").click(function(event){
        event.stopPropagation();

        // this prevent the event getting triggered when clicking overlay
        if ($(event.target).hasClass("jobrequest-overlay-contain") || $(event.target).hasClass("exit-overlay")) {
            closeOverlay();
        }
    }).css({ // set the height and width to fit
        height: $(window).height(),
        width: $(window).width()
    });

    $(window).resize(function (event) { // handle the window resize
       $(".jobrequest-overlay-contain").css({
           height: $(window).height(),
           width: $(window).width()
       }) ;
    });

    $(document).keydown(function (event) {
        // if the key pressed is ESC or jobrequest-overlay-contain is visible
        if (event.which == ESC_KEY && $(".jobrequest-overlay-contain:visible")[0]) {
            closeOverlay();
        }
    });