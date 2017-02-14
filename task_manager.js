/**
 * Created by kolu4ka on 07/01/17.
 */

var  aTask;
var idC=0;
var hashId="epmty";
var pageIs="empty";
var aUser = "aUser"
var isDone;
subTask = ""
isHeadCreated=false
isCommited=false
aTask=""

    //editing event attach to button and edit values of this field
   $(document).on('click','#btn',function() {
       // for editing
       cell = $(this.parentElement).siblings("#taskText,#taskTime")
       chBox = $(this).parent().prev().children()



       if (this.innerHTML == "edit") {
           isEdited = true;
           //awaiting for done
           //set red color as state is under editing
           color = "red"
           chBox.prop('checked',false)
           chBox.attr('disabled',true)
           this.innerHTML = "done"
       //    alert("in edit")
           // $("#isDone").checked == false
       }else{
           color = "yellow"
          // alert("in else")
           isEdited = false;
           this.innerHTML = "edit"
           chBox.attr('disabled',false)
           id = $(this.parentElement).siblings("#idT")
           //alert("in else2")
           taskTextL = $(cell[0]).children().html().replace(/(\r\n|\n|\r |<br>|&nbsp;)/gm,"")
          // alert("in else3")
           taskTimeL = cell[1].innerHTML.replace(/(\r\n|\n|\r |<br>|&nbsp;)/gm,"")
           console.log("pageIs: " + pageIs)

           aHash =  $(this.parentElement.parentElement).children("#taskText").attr('value')
            // alert(hashValue)
            //alert(aHash)
             if (pageIs == "mainPage") {
                 aTask = '{"aTask": [{' + '"hashId":' + '"' + aHash + '",' + '"state":"edit",' + '"pageIs":"' + pageIs + '"' + ',"taskText":' + '"' + taskTextL + '"' + ',"taskTime":"' + taskTimeL + '"'  + ',"aUser":"aUser"' + '}]}';
             }else {
                 aTask = '{"aTask": [{' + '"hashId":' + '"' + hashId + '",' + '"subTaskHash":' + '"' + aHash + '",' + '"state":"edit",' + '"pageIs":"' + pageIs + '"' + ',"taskText":' + '"' + taskTextL + '"' + ',"taskTime":"' + taskTimeL + '"'  + ',"aUser":"aUser"' + '}]}';
             }
            ajaxRequest()
       }
       $(this.parentElement).prevAll().css("background-color","yellow");
       $(this.parentElement).siblings("#taskText,#taskTime").css("background-color",color);


       for (i = 0; i < 2; i++) {
               cell[i].contentEditable = isEdited
       }

      });

     $(document).on('click','#rm',function() {
         if (confirm("Please,confirm deletion") == true) {
             $(this.parentElement.parentElement).fadeOut(350)

             aHash =  $(this.parentElement.parentElement).children("#taskText").attr('value')
            // alert(hashValue)

             if (pageIs == "mainPage") {
                 aTask = '{"aTask": [{' + '"hashId":' + '"' + aHash + '",' + '"state":"remove",' + '"pageIs":"' + pageIs + '"' + ',"aUser":"aUser"' + '}]}';
             }else {
                 aTask = '{"aTask": [{' + '"hashId":' + '"' + hashId + '",' + '"subTaskHash":' + '"' + aHash + '",' + '"state":"remove",' + '"pageIs":"' + pageIs + '"' + ',"aUser":"aUser"' + '}]}';
             }
             console.log("update: " + aTask)
             ajaxRequest()
         }else {
       alert("You pressed Cancel!")
    }
    });

    $(document).on('click','#isDone',function() {
        id = $(this.parentElement).siblings("#idT").text()
   //     alert(id)
        aHash =  $(this.parentElement.parentElement).children("#taskText").attr('value')
      //  alert("click method: " + aHash)
        if(this.checked == true) {
            $(this.parentElement).next().prevAll().css("background-color", "green");
            isDone = "true"
        }else{
            $(this.parentElement).next().prevAll().css("background-color", "yellow");
            isDone = "false"
        }
      //  alert(isDone)
       if (pageIs == "mainPage") {
             aTask = '{"aTask": [{' + '"hashId":' + '"' + aHash + '",' + '"state":"done",' + '"pageIs":"' + pageIs + '"' + ',"aUser":"aUser"' + "," + '"isDone":' + '"' + isDone + '"' + '}]}';
         }else {
             //hashId = window.location.href.match("aTask=(.*)")[1]
           //  alert("main hash:" + hashId)
             aTask = '{"aTask": [{' + '"hashId":' + '"' + hashId + '",' + '"subTaskHash":' + '"' + aHash + '",' + '"state":"done",' + '"pageIs":"' + pageIs + '"' + ',"aUser":"aUser"' + ',"isDone":' + '"' + isDone + '"' +'}]}';
         //    alert(aTask)
       }
         ajaxRequest()
    });

function getLtime(){
    lDate = new Date()
    lTime = lDate.getFullYear() + "-" + (lDate.getMonth() + 1) + "-" + lDate.getDate() + "; " + lDate.getHours() + ":" + lDate.getMinutes()

    return lTime;
}



function getFromServer(getTableFor){

    pageIs = getTableFor;
   // alert(hey.parentElement.innerHTML)
    console.log("getFromServer: " + pageIs)

    if (pageIs == "mainPage") {

        aTask = '{"aTask": [{' + '"state":"pageHasLoaded",' + '"pageIs":"mainPage",' + '"aUser":"' + aUser + '"' + '}]}';
   //     alert("getFromServer triggered:" + aTask)
    } else {
        // need to go to the subtask and open another table
        hashId = window.location.href.match("aTask=(.*)")[1]
        aTask = '{"aTask": [{' + '"state":"pageHasLoaded",' + '"pageIs":"aSubTask",' + '"aUser":"' + aUser + '"' + ',"hashId":"' + hashId + '"' + '}]}';
        //alert(subTask)

    //    alert("getFromServer triggered:" + aTask)
    }
    console.log("getFromServer: ajaxRequest")
    ajaxRequest();
}


function
ajaxRequest(){

console.log("ajaxRequest aTask is : " + aTask)
//alert(aTask)
    $.ajax({
        url: "./serverScript.py",
        type: "post",
        data: JSON.stringify(aTask),
        //async: false,
        contentType: "application/json;charset=utf-8",
        dataType: "json",
        success: function someCallBack(aTask) {

            decodedJsonATask = JSON.parse(aTask)
            lastElement = decodedJsonATask.aTask.length
            try{
                state = decodedJsonATask.aTask[lastElement-1]['answer']
                console.log("state is : " + state)
                console.log("last element : " + lastElement)
                console.log(decodedJsonATask.aTask[1])
            }catch (e){
                alert(e);
            }

            if(isHeadCreated != true){

                createHeadOfTable()
                $("#invite").hide()
            }
            if (state == "written" || state == "get") {

                idC = decodedJsonATask.aTask.length - 1
                console.log("ajax idC:" + idC)
                isDone = ""
                //  console.log("check isDone:" + decodedJsonATask.aTask[i]['isDone'])

                console.log(decodedJsonATask.aTask)

                for (i = 0; i < lastElement - 1; i++) {
                    console.log("check isDone:" + decodedJsonATask.aTask[0]['isDone'])
                    color = "yellow"
                    isDone = ""
                    if (decodedJsonATask.aTask[i]['isDone'] == '1') {
                        color = "green"
                        isDone = "checked"

                    }
                    createTable(color, decodedJsonATask.aTask[i]['ID'],
                        decodedJsonATask.aTask[i]['taskText'],
                        decodedJsonATask.aTask[i]['taskTime'],
                        decodedJsonATask.aTask[i]['lTime'],
                        isDone,
                        decodedJsonATask.aTask[i]['hashId'])
                }
            }
        },
        error: function (e) {
            alert("Error: save task before reload of page " + e.responseText)
            createTable("yellow ",idC, $("#textinput").val(), $("#textinput2").val(),lTime, false)

        }

    });



}

function createHeadOfTable () {
        $("#tbl").append(
		'<tr id="stop">' +
			'<td><h4 style="background-color:grey">id</h4></td>' +
			'<td><h4 style="background-color:grey">Task description</h4></td>' +
			'<td><h4 style="background-color:grey">Task time(hours)</h4></td>' +
			'<td><h4 style="background-color:grey">Time(yyyy-mm-dd;hh:mm)</h4></td>' +
			'<td><h4 style="background-color:grey">Done</h4></td>' +
		'</tr>'
    )
    isHeadCreated=true;
}

function register() {



    
   // alert($("#psw").val())

    aTask = '{"aTask": [{' + '"state":"register",' + '"aUser":'  + '"' + $("#usr").val() + '"' + ',"password":' + '"' + $("#psw").val() + '"' + '}]}'

    ajaxRequest()
   // return JSON.stringify(aTask)
}


function createTable(color,idCount,taskText,taskTime,lTime,isDoneSt,hashId){
idC = idCount
//alert(isDoneSt)
   // console.log("createTable")
        hrBegin = '<ttt id="hre">'
        hrEnd = '</ttt>'

    if (pageIs == "mainPage"){
        hrBegin =  '<a id="hre" href="./tasks.html?aTask=' + hashId + '" target="_blank" >'
        hrEnd = '</a>'
    }


    $("#tbl").append(
            '<tr id="rt">' +
                 '<td id="idT"  style="background-color:' + color + '">'  + idCount + '</td>' +
                 '<td id="taskText" value="' + hashId + '"' + 'style="background-color:' + color + '">' +
                  hrBegin + taskText  + hrEnd + '</td>' +
                 '<td id="taskTime" style="background-color:' + color + '">' +  taskTime + '</td>' +
                 '<td align="center" id="time1" style="background-color:' + color + '">'  +  lTime + '</td>'+
                 '<td id ="isDP" style="background-color:' + color + '">' + '<INPUT type="checkbox" id="isDone" ' + isDoneSt + '>' + '</INPUT>' + '</td>' +
             '<td><button id="btn">edit</button></td>' +
             '<td><button id="rm">remove</button></td>' +
            '</tr>'
    )
    idC++;
    console.log("tableCreated: id : " + idC)
}


//first task is writted here
function writeTasks(taskOrSubTask){
console.log("writT")
   // alert(taskOrSubTask)
    pageIs = taskOrSubTask;
    if (isHeadCreated != true ){
         console.log("writT condition")
         createHeadOfTable()
         idC=1
         writeTasks(taskOrSubTask)
     }else {
         console.log("writT:else")
         console.log("writT:test")
         //lTime = lDate.getFullYear() + "-" + addNull(lDate.getMonth() + 1) + "-" + addNull(lDate.getDate()) + "; " + addNull(lDate.getHours()) + ":" + addNull(lDate.getMinutes())
         // lTime="test"
       //  console.log("yellow" + "," + idC + "," + $("#textinput").val() + "," + $("#taskTime").val() + "," + getLtime() + "," + false)
         lTime = getLtime()
         taskText = $("#textinput").val()
         taskTime = $("#textinput2").val()


         console.log("yellow" + "," + idC + "," + taskText + "," + taskTime + "," + getLtime() + "," + false)

    if (pageIs == "mainPage"){

        aTask = '{"aTask": [{' + '"id":' + '"' + idC + '"' + ',"taskText":' + '"' + taskText + '"' + ',"taskTime":"' + taskTime + '"' + ',"lTime":"' + lTime + '"' + ',"isDone":"false"' +
             ',"state":"write"' + ',"pageIs":"' + pageIs + '"' + ',"aUser":"' + aUser + '"' + '}]}';
    }else {
        aTask = '{"aTask": [{' + '"id":' + '"' + idC + '"' + ',"taskText":' + '"' + taskText + '"' + ',"taskTime":"' + taskTime + '"' + ',"lTime":"' + lTime + '"' + ',"isDone":"false"' +
            ',"state":"write"' + ',"pageIs":"' + pageIs + '"' + ',"aUser":"' + aUser + '","hashId":"' + hashId + '"' + '}]}';
    }

         console.log("before ajax req")

         //client goes to create page
        ajaxRequest()

        console.log("ajax request succesfully sent")
         console.log("table done")

    }
}