function findRadioSelected(){
    var  result = document.querySelector('input[type="radio"]:checked').value;
    if (result==1){
        document.getElementById("id_whole_time").readOnly = false;
        document.getElementById("id_whole_tickets").readOnly = false;
        document.getElementById("id_whole_tickets").style.backgroundColor = "";
        document.getElementById("id_whole_time").style.backgroundColor = "";
        document.getElementById("id_whole_time").style.color = "black";
        document.getElementById("id_whole_tickets").style.color = "black";
        document.getElementById("id_whole_tickets").value = "";
        document.getElementById("id_whole_time").value = "";
    }
    else if (result==2){
        document.getElementById("id_whole_time").readOnly = false;
        document.getElementById("id_whole_tickets").readOnly = true;
        document.getElementById("id_whole_time").style.backgroundColor = "";
        document.getElementById("id_whole_tickets").style.backgroundColor = "grey";
        document.getElementById("id_whole_time").style.color = "black";
        document.getElementById("id_whole_tickets").style.color = "grey";
        document.getElementById("id_whole_tickets").value = "-1";
        document.getElementById("id_whole_time").value = "";
    }
    else if(result==3){
        document.getElementById("id_whole_time").readOnly = true;
        document.getElementById("id_whole_tickets").readOnly = false;
        document.getElementById("id_whole_time").style.backgroundColor = "grey";
        document.getElementById("id_whole_time").style.color = "grey";
        document.getElementById("id_whole_tickets").style.backgroundColor = "";
        document.getElementById("id_whole_tickets").style.color = "black";
        document.getElementById("id_whole_time").value = "-1";
        document.getElementById("id_whole_tickets").value = "";

    }
}