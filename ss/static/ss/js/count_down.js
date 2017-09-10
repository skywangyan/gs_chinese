$(document).ready(function(){
    window.setInterval(function() {
        $(".start_time_1").each(function(){
            var start_time = new Date($(this).text());
            var whole_time = Number($(this).siblings('.whole_time_1').text())*60000;
            var today = new Date();
            var dt = today.getTime() - start_time.getTime() + today.getTimezoneOffset()*60*1000;
//            var dt = today.getTime() - start_time.getTime();
            if (whole_time > -1){
                if (dt > whole_time){
                    $(this).siblings('.count_down').html("<span style='color:red;'> Timeout!</span>");
                }
                else {
                    dt = whole_time - dt;
                    var hh = Math.floor(dt/3600000);
                    var mm = Math.floor((dt%3600000)/60000);
                    var ss = Math.floor((dt%60000)/1000);
                    hh = checkTime(hh);
                    mm = checkTime(mm);
                    ss = checkTime(ss);
                    $(this).siblings('.count_down').text(hh+":"+mm+":"+ss);
                }
                }
        });
    }, 1000);
});
function checkTime(i) {
    if (i < 10) {i = "0" + i};  // add zero in front of numbers < 10
    return i;
}
$(document).ready(function(){
    window.setInterval(function(){
        var minutes = (new Date()).getMinutes();
        if ( minutes%5==0 ) {
            location.reload();
        }
    },60000);
});
