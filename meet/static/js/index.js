//插件中自带，直接复制粘贴：
    // 对Date的扩展，将 Date 转化为指定格式的String
    // 月(M)、日(d)、小时(h)、分(m)、秒(s)、季度(q) 可以用 1-2 个占位符，
    // 年(y)可以用 1-4 个占位符，毫秒(S)只能用 1 个占位符(是 1-3 位的数字)
    // 例子：
    // (new Date()).Format("yyyy-MM-dd hh:mm:ss.S") ==> 2006-07-02 08:09:04.423
    // (new Date()).Format("yyyy-M-d h:m:s.S")      ==> 2006-7-2 8:9:4.18
    Date.prototype.Format = function (fmt) { //author: zhaishuaishuai
        var o = {
            "M+": this.getMonth() + 1, //月份
            "d+": this.getDate(), //日
            "h+": this.getHours(), //小时
            "m+": this.getMinutes(), //分
            "s+": this.getSeconds(), //秒
            "q+": Math.floor((this.getMonth() + 3) / 3), //季度
            "S": this.getMilliseconds() //毫秒
        };
        if (/(y+)/.test(fmt)) fmt = fmt.replace(RegExp.$1, (this.getFullYear() + "").substr(4 - RegExp.$1.length));
        for (var k in o)
            if (new RegExp("(" + k + ")").test(fmt)) fmt = fmt.replace(RegExp.$1, (RegExp.$1.length == 1) ? (o[k]) : (("00" + o[k]).substr(("" + o[k]).length)));
        return fmt;
    };

//自定义的全局变量：
    SELECTED_ROOM = {del: {}, add: {}};
    CHOSEN_DATE = '';//转成字符串格式后的今日日期
    CHANGE_ID = '';
    CHANGE_NAME='';
    UPDATE_NAME = false;
    DISPLAY = false;
    SELECT = new Array();
    BACKGROUND_COLOR = ['#FFFACD',
                        '#E0FFFF',
                        '#FFE4E1',
                        '#FFE4B5',
                        '#7FFFD4',
                        '#90EE90',
                        '#FFB6C1',
                        '#98FB98',
                        '#E6E6FA',
                        '#AFEEEE']
    //网页加载完成后执行的js脚本内容：
    $(function () {
        initDatepicker();//初始化日期插件
//初始化房间信息，将今日日期发给后端,利用ajax从后台获得房间预订信息
        initBookingInfo(CHOSEN_DATE, DISPLAY);
        bindTdEvent();//绑定预定会议室事件
        bindSaveEvent();//保存按钮
    });
//处理csrftoken:
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'));
            }
        }
    });
//初始化日期插件内容：
    function initDatepicker() {
        $('#datetimepicker').datetimepicker({
            minView: "month",//最小可视是到月份，即最小选择是到day
            language: "zh-CN",
            sideBySide: true,
            format: 'yyyy-mm-dd',
            bootcssVer: 3,//bootstrap3必写
            autoclose: true,//自动关闭，不需要可删
        });//绑定改日期后的事件
    }
//初始化房间信息（利用ajax从后台获得房间预订信息）
    function initBookingInfo(date, display) {
        $('#shade,#loading').removeClass('hide');//遮罩层
        device = document.getElementById('device').value;
        $.ajax({
            url: '/booking/',
            type: 'get',
            data: {date: date, device: device, display:display},//字符串转义后的今日日期
            dataType: 'JSON',
            success: function (arg) {
                $('#shade,#loading').addClass('hide');//遮罩层去除
                if (arg.code === 1000) {//表示后台操作成功
                    $('#tBody').empty();
                    var rowIndex=0;
                    $.each(arg.data, function (i, item) {
                        var tr = document.createElement('tr');//此为js操作，等同于jQuery的$('<tr>')
                        $.each(item, function (j, row) {
                            var td = document.createElement('td');
                            if(row.id==='device'){
                                td.id = 'device_name';
                                td.style='white-space:nowrap;font-weight:bold;font-size:14px;color:#FF4500;background:#D8BFD8;vertical-align: middle;'
                                $(td).attr('ondblclick', 'changeName(this)');
                            }
                            $(td).text(row.text);
                            if(row.id==='data'){
                                $(td).text(row.text).attr('style','font-weight:bold');
                                if(row.status==='scheduling'){
                                td.id = "scheduling";
                                }else if(row.status === "scheduled"){
                                td.id = "scheduled";
                                }else{
                                    td.id="N/A";
                                }
                            }
                            if(row.id==='date'){
                                td.style = "white-space:nowrap;";
                            }
                            
                            $.each(row.attrs, function (k, v) {
                                $(td).attr(k, v);
                            });
                            $(tr).append(td)
                        });
                        $('#tBody').append(tr);
                        rowIndex++;
                    });
                    var tbody = document.getElementById('tBody');
                    mergeCells(tbody);
                } else {
                    alert(arg.msg);
                }
            },
            error: function () {
                $('#shade,#loading').addClass('hide');
                alert('请求异常');
            }
        })
    }

    /*
     绑定预定会议室事件，事件委派
     */
    function bindTdEvent() {
        $('#tBody').on('mousedown', 'td[time-id][disable!="true"]', function () {
            var roomId = $(this).attr('room-id');
            var timeId = parseInt($(this).attr('time-id'));
            var span = parseInt($(this).attr('colspan'));
            var arr = [];
            $(this).closest('tr').children().map(function(el){ 
               arr.push($(this)[0].innerText); 
               bookingdate=arr[1];
               device = arr[0]
            });
            bookingdate = bookingdate.split(' (')[0];
            $(this).closest('tr').off('mouseup');
            // 取消原来的预定：
            if ($(this).attr('style') && $(this).attr('id') == 'scheduled') {
                $(this).removeAttr("style").empty();
                $(this).closest('tr').off('mouseover');
                $(this).closest('tr').off('mouseout');
                SELECT.pop();
                for(var i = 0; i < span; i++){
                    if (SELECTED_ROOM.del[roomId]) {
                        SELECTED_ROOM.del[roomId].push([timeId+i,bookingdate]);
                    } else {
                        SELECTED_ROOM.del[roomId] = [[timeId+i,bookingdate]];
                    }
                }
            }
            else if ($(this).attr('style') && $(this).attr('id') == 'scheduling') {
                    $(this).closest('tr').on('mouseup','td[time-id][disable!="true"]',function () {
                    $(this).removeAttr("style").empty();
                    $(this).closest('tr').off('mouseover');
                    $(this).closest('tr').off('mouseout');
                    SELECT.pop();
                    var roomId = $(this).attr('room-id');
                        var timeId = parseInt($(this).attr('time-id'));
                        $(this).closest('tr').children().map(function(el){ 
                           arr.push($(this)[0].innerText); 
                           bookingdate=arr[1];
                           device = arr[0];
                        });
                    bookingdate = bookingdate.split(' (')[0];
                    // 取消选择
                    for(var i = 0; i < span; i++){
                    if (SELECTED_ROOM.del[roomId]) {
                            SELECTED_ROOM.del[roomId].push([timeId+i,bookingdate]);
                        } else {
                            SELECTED_ROOM.del[roomId] = [[timeId+i,bookingdate]];
                        }
                    }
                    cancelScheduling(SELECTED_ROOM, device);
                    $(this).closest('tr').off('mouseup');
                    })
            }
            else {
                    if($(this).attr('id') != 'scheduled'){
                        $(this).addClass('selected')
                        SELECT.push(true);
                        $(this).closest('tr').on('mouseover','td[time-id][disable!="true"]',function () {
                            $(this).addClass('mycolor');
                        })
                        $(this).closest('tr').on('mouseout','td[time-id][disable!="true"]',function () {
                            if($(this).hasClass('mycolor')){
                                $(this).removeClass('mycolor');
                            }
                        $(this).addClass('selected');
                        SELECT.push(true);
                        var roomId = $(this).attr('room-id');
                        var timeId = parseInt($(this).attr('time-id'));
                        $(this).closest('tr').children().map(function(el){ 
                           arr.push($(this)[0].innerText); 
                           bookingdate=arr[1];
                        });
                        bookingdate = bookingdate.split(' (')[0];
                        // 选择
                        if (SELECTED_ROOM.add[roomId]) {
                            SELECTED_ROOM.add[roomId].push([timeId,bookingdate]);
                        } else {
                            SELECTED_ROOM.add[roomId] = [[timeId,bookingdate]];
                        }
                        })
                        $(this).closest('tr').on('mouseup','td[time-id][disable!="true"]',function () {
                            $(this).closest('tr').off('mouseover');
                            $(this).closest('tr').off('mouseout');
                            $(this).removeClass('mycolor');
                            $(this).addClass('selected');
                            var roomId = $(this).attr('room-id');
                            var timeId = parseInt($(this).attr('time-id'));
                            $(this).closest('tr').children().map(function(el){ 
                               arr.push($(this)[0].innerText); 
                               bookingdate=arr[1];
                               device = arr[0];
                            });
                            bookingdate = bookingdate.split(' (')[0];
                            // 选择
                            if (SELECTED_ROOM.add[roomId]) {
                                SELECTED_ROOM.add[roomId].push([timeId,bookingdate]);
                            } else {
                                SELECTED_ROOM.add[roomId] = [[timeId,bookingdate]];
                            }
                            if(window.confirm('确认选中的时间段')){
                                var task = window.prompt('请输入事务项:');
                                if(task !== null && task !== ""){
                                    for(var i = 0; i < SELECTED_ROOM.add[roomId].length; i++){
                                        if(SELECTED_ROOM.add[roomId][i][1]==bookingdate){
                                            SELECTED_ROOM.add[roomId][i].push(task);
                                        };
                                    }
                                    console.log(SELECTED_ROOM);
                                    scheduling(SELECTED_ROOM, device);
                                    }else{
                                        SELECTED_ROOM = {del: {}, add: {}};
                                        initBookingInfo(date, true);
                                        bindTdEvent();
                                        $(this).closest('tr').off('mouseup');
                                        $(this).closest('tr').off('mousedown');
                                        }
                            }else{
                                SELECTED_ROOM = {del: {}, add: {}};
                                initBookingInfo(date, true);
                                bindTdEvent();
                                $(this).closest('tr').off('mouseup');
                                $(this).closest('tr').off('mousedown');
                            }
                        })
                }
            }
        })
    }
function scheduling(data, device){
    document.getElementById('device').value = device;
    $.ajax({
            url: '/booking/',
            type: 'POST',
            data: {data: JSON.stringify(data),
                   status: 'scheduling'},
            dataType: 'JSON',
            success: function (arg) {
                if (arg.code == 1000) {
                    date = document.getElementById('datetimepicker').value;
                    if(!date){
                        date = new Date().Format('yyyy-MM-dd');
                        }
                    initBookingInfo(date, true);
                    bindTdEvent();
                } else {
                    $('#errors').text(arg.msg);
                }
            }
        });
}

function cancelScheduling(data, device){
    console.log(data);
    document.getElementById('device').value = device;
    $.ajax({
        url: '/booking/',
        type: 'POST',
        data: {data: JSON.stringify(data),
               status: 'cancel'},
        dataType: 'JSON',
        success: function (arg) {
            if (arg.code == 1000) {
                date = document.getElementById('datetimepicker').value;
                if(!date){
                    date = new Date().Format('yyyy-MM-dd');
                    }
                initBookingInfo(date, true);
                bindTdEvent();
                SELECTED_ROOM = {del: {}, add: {}};
            } else {
                $('#errors').text(arg.msg);
            }
        }
        });
}
    /*
     保存按钮
     */
    function bindSaveEvent() {
        $('#errors').text('');
        $('#save').click(function () {
            $('#shade,#loading').removeClass('hide');
            if(UPDATE_NAME){
                if(window.confirm('确定更改设备名称？')){
                    task = '';
                 }else{
                    UPDATE_NAME = false;
                 }
             }
            $.ajax({
                url: '/booking/',
                type: 'POST',
                data: {device:CHANGE_NAME, 
                       device_id:CHANGE_ID, 
                       data: JSON.stringify(SELECTED_ROOM),
                       flag: UPDATE_NAME,
                       status:'scheduled'},
                dataType: 'JSON',
                success: function (arg) {
                    $('#shade,#loading').addClass('hide');
                    if (arg.code == 1000) {
                        document.getElementById('device').value = '';
                        initBookingInfo(CHOSEN_DATE,false);
                        if(UPDATE_NAME){
                            UPDATE_NAME = false;
                            swal({
                                title: '更新成功',
                                type: 'success',
                                text: '设备名字已更新'
                            })
                        }else{
                            swal({
                              title: '保存成功',
                              text: '设备排期已刷新',
                              type: 'success'
                            })
                            setTimeout(refresh, 1000);
                        }
                        
                    } else {
                        $('#errors').text(arg.msg);
                    }
                }
            });
            
    })
    }

    /*
    添加设备
    */
    function adDevice() {
        $('#errors').text('');
        $('#shade,#loading').removeClass('hide');
        device = document.getElementById('device').value;
        date = document.getElementById('datetimepicker').value;
        if(!date){
            if(window.confirm('未选择排期日期，则默认今天')){
                date = new Date().Format('yyyy-MM-dd');
            }
        }
        if (device){
            $.ajax({
                url: '/addevice/',
                type: 'POST',
                data:  {date: date, device: device},
                dataType: 'JSON',
                success: function (arg) {
                    if (arg.code == 200){
                        swal({
                                title: '添加成功',
                                text: '设备已添加到排期系统',
                                type: 'success'
                            })
                        initBookingInfo(date, true);
                        bindTdEvent();
                    }else{
                        swal({
                                title: '设备已存在',
                                text: '添加失败',
                                type: 'error'
                            })
                        setTimeout(refresh, 2000);
                    }
                }
            });
        }else{
            swal({
                  title: '添加失败',
                  type: 'error',
                  text: '请输入设备名称',
                })
            setTimeout(refresh, 1000);
        }
    }

    /*
    搜索排期
    */
    function onSearch() {
        $('#errors').text('');
        $('#shade,#loading').removeClass('hide');
        device = document.getElementById('device').value;
        date = document.getElementById('datetimepicker').value;
        $.ajax({
            url: '/booking/',
            type: 'get',
            data: {date: date, device: device, display:false},//字符串转义后的今日日期
            dataType: 'JSON',
            success: function (arg) {
                $('#shade,#loading').addClass('hide');//遮罩层去除
                if (arg.code === 1000) {//表示后台操作成功
                    initBookingInfo(date, false);
                } else {
                    alert(arg.msg);
                }
            },
            error: function () {
                $('#shade,#loading').addClass('hide');
                alert('请输入查询信息！');
            }
        });
    }

    function refresh() {
        location.reload();
    }
    function changeName(element){

        var oldhtml = element.innerHTML;
        $.ajax({
                url: '/addevice/',
                type: 'GET',
                data:  {device: oldhtml},
                dataType: 'JSON',
                success: function (arg) {
                    if (arg.code == 200){
                        UPDATE_NAME=true;
                        CHANGE_ID = arg.data;
                    } else {
                        $('#errors'.text(arg.msg));
                    }
                }
            });
        var newobj = document.createElement('input');//创建一个input元素
        newobj.type = 'text';//为newobj元素添加类型
        newobj.value=oldhtml;
        element.innerHTML = '';　　 //设置元素内容为空
        element.appendChild(newobj);//添加子元素
        newobj.focus();//获得焦点
        //设置newobj失去焦点的事件
        newobj.onblur = function(){
        //当触发时判断newobj的值是否为空，为空则不修改，并返回oldhtml
        CHANGE_NAME = element.innerHTML = this.value ? this.value : oldhtml;
        }
}


function mergeCells(tab) {
    var maxRow = tab.rows.length;
    var maxCol = 26, val, count, start;
    for (var row = maxRow-1; row >= 0; row--) {
        count = 1;
        val = "";
        for (var i = 2; i < maxCol; i++) {
            var txt = tab.rows[row].cells[i].innerHTML;
            if (txt!='' && val == txt) {
                count++;           
            } else {
                if (count > 1) { //合并
                    start = i - count;
                    tab.rows[row].cells[start].colSpan = count;
                    tab.rows[row].cells[start].style.background = BACKGROUND_COLOR[Math.floor(Math.random()*10)];

                    SELECT=[];
                    SELECT.push(true);
                    for (var j = start+1; j < i; j++) {
                        tab.rows[row].cells[j].style.display = "none";
                    }
                    count = 1;
                }else{
                    if(txt!=''){
                        tab.rows[row].cells[i].colSpan = 1;
                        tab.rows[row].cells[i].style.background = BACKGROUND_COLOR[Math.floor(Math.random()*10)];
                        SELECT=[];
                        SELECT.push(true);
                }
            }
                val = tab.rows[row].cells[i].innerHTML;
            }
        }
        if (count > 1 && txt != '') { //合并
            start = i - count;
            tab.rows[row].cells[start].colSpan = count;
            tab.rows[row].cells[start].style.background = BACKGROUND_COLOR[Math.floor(Math.random()*10)];
            SELECT=[];
            SELECT.push(true);
            for (var j = start+1; j < i; j++) {
                tab.rows[row].cells[j].style.display = "none";
            }
            count = 1;
            }
        }
        mergeRow(tab);
    }

function mergeRow(tab){
    var maxCol = 2, val, count, start;  //maxCol：合并单元格作用到多少列    
    for (var col = maxCol - 1; col >= 0; col--) {
        count = 1;
        val = "";
        for (var i = 0; i < tab.rows.length; i++) {
            var txt = tab.rows[i].cells[col].innerHTML;
            if (val == txt) {
                count++;
            } else {
                if (count > 1) { //合并
                    start = i - count;
                    tab.rows[start].cells[col].rowSpan = count;
                    for (var j = start + 1; j < i; j++) {
                        tab.rows[j].cells[col].style.display = "none";
                    }
                    count = 1;
                }
                val = tab.rows[i].cells[col].innerHTML;
            }
        }
        if (count > 1) { //合并，最后几行相同的情况下
            start = i - count;
            tab.rows[start].cells[col].rowSpan = count;
            for (var j = start + 1; j < i; j++) {
                tab.rows[j].cells[col].style.display = "none";
            }
        }
    }
}