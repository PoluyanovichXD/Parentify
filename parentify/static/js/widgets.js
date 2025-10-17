$(window).on('load', function () {
    const labels_RU = {
        labelIdle: 'Перетащите или выберите <span class="filepond--label-action"> Изображение </span>',
        labelFileAdded: "Добавить",
        labelFileCountPlural: "Файлов в списке",
        labelFileCountSingular: "Файл в списке",
        labelInvalidField: 'Поле содержит недопустимые файлы',
        labelFileWaitingForSize: 'Укажите размер',
        labelFileSizeNotAvailable: 'Размер не поддерживается',
        labelFileLoading: 'Ожидание',
        labelFileLoadError: 'Ошибка при ожидании',
        labelFileProcessing: 'Загрузка',
        labelFileProcessingComplete: 'Загрузка завершена',
        labelFileProcessingAborted: 'Загрузка отменена',
        labelFileProcessingError: 'Ошибка при загрузке',
        labelFileProcessingRevertError: 'Ошибка при возврате',
        labelFileRemoveError: 'Ошибка при удалении',
        labelTapToCancel: 'нажмите для отмены',
        labelTapToRetry: 'нажмите, чтобы повторить попытку',
        labelTapToUndo: 'нажмите для отмены последнего действия',
        labelButtonRemoveItem: 'Удалить',
        labelButtonAbortItemLoad: 'Прекращено',
        labelButtonRetryItemLoad: 'Повторите попытку',
        labelButtonAbortItemProcessing: 'Отмена',
        labelButtonUndoItemProcessing: 'Отмена последнего действия',
        labelButtonRetryItemProcessing: 'Повторите попытку',
        labelButtonProcessItem: 'Загрузка',
        labelMaxFileSizeExceeded: 'Файл слишком большой',
        labelMaxFileSize: 'Максимальный размер файла: {filesize}',
        labelMaxTotalFileSizeExceeded: 'Превышен максимальный размер',
        labelMaxTotalFileSize: 'Максимальный размер файла: {filesize}',
        labelFileSizeBytes: 'байт',
        labelFileSizeKilobytes: 'КБ',
        labelFileSizeGigabytes: 'ГБ',
        labelFileSizeMegabytes: 'МБ',
        labelFileTypeNotAllowed: 'Файл неверного типа',
        fileValidateTypeLabelExpectedTypes: 'Tipos de arquivo suportados são {allButLastType} ou {lastType}',
        imageValidateSizeLabelFormatError: 'Тип изображения не поддерживается',
        imageValidateSizeLabelImageSizeTooSmall: 'Изображение слишком маленькое',
        imageValidateSizeLabelImageSizeTooBig: 'Изображение слишком большое',
        imageValidateSizeLabelExpectedMinSize: 'Минимальный размер: {minWidth} × {minHeight}',
        imageValidateSizeLabelExpectedMaxSize: 'Максимальный размер: {maxWidth} × {maxHeight}',
        imageValidateSizeLabelImageResolutionTooLow: 'Разрешение слишком низкое',
        imageValidateSizeLabelImageResolutionTooHigh: 'Разрешение слишком высокое',
        imageValidateSizeLabelExpectedMinResolution: 'Минимальное разрешение: {minResolution}',
        imageValidateSizeLabelExpectedMaxResolution: 'Максимальное разрешение: {maxResolution}'
    };
    FilePond.setOptions(labels_RU)
    $.fn.filepond.registerPlugin(
        FilePondPluginFileValidateType,
        FilePondPluginImagePreview,
        FilePondPluginImageEdit
    );
    document.querySelectorAll('[filepond]').forEach((item)=>{
        filepondCreate(item);
    })
    document.querySelectorAll('.grid_pager').forEach(grid => {
        grid.innerHTML = '';
        
        for (let i = 0; i < 5; i++) {
            const pageBtn = document.createElement('button');
            pageBtn.className = 'w-8 h-8 flex items-center justify-center bg-gray-100 hover:bg-primary hover:text-white rounded-lg text-sm font-medium transition-colors duration-200';
            pageBtn.textContent = i + 1;
            pageBtn.onclick = ClickBtn(`?p=${i + 1}`);
            grid.appendChild(pageBtn);
        }
    });
})
function isDict(d) {
    return !!d && typeof d==='object' && d!==null && !(d instanceof Array) && !(d instanceof Date) && isJsonable(d);
}
function isJsonable(d) {
    try{
        return JSON.stringify(d) === JSON.stringify(JSON.parse(JSON.stringify(d)));
    } catch(e){
        return false;
    }
}
function isNumeric(str) {
    return !isNaN(str) && !isNaN(parseFloat(str))
}


$('#file_upload').on('drop', (e)=>{
    e.preventDefault()
    e.stopPropagation()
    uploadFile(e)
    if(e.originalEvent.dataTransfer){
        if(e.originalEvent.dataTransfer.files.length) {
            window['file'] = e.originalEvent.dataTransfer.files[0];
            $("#fileinput").prop("files", e.originalEvent.dataTransfer.files);
        }
    }
});
$('#fileinput').change((e)=>{
    if(e.target.files[0]){
        window['file'] = e.target.files[0]           
    }
})
function filepondCreate(element,name=null){
    if(element){
        element = $(element)
        var props = {
            storeAsFile: true,
            fileValidateTypeDetectType: (source, type) =>
            new Promise((resolve, reject) => {
                var types = element.attr('accepted-file-types')
                if (typeof types === typeof undefined || types === false) {
                    return resolve(type);
                } else {
                    types = types.split(',')
                    for (let i = 0; i < types.length; i++) {
                        if (source.name.toLowerCase().endsWith(types[i].toLowerCase())) return resolve(types[i].toLowerCase());
                    }
                }
                return reject(type)
            }),
            onaddfile:(error, file)=>{
                console.log(error, file)
            }
        }
        if(name){
            props['name']=name
        }
        if(typeof element.attr('server-url') !== 'undefined' && element.attr('server-url') !== false){
            props['server'] = {
                process: (fieldName, file, metadata, load, error, progress, abort, transfer, options) => {
                    const formData = new FormData();
                    formData.append('file', file, file.name);
                    
                    const request = new XMLHttpRequest();
                    request.open('POST', element.attr('server-url'));
                    request.setRequestHeader('X-CSRFToken', get_csrftoken('csrftoken'))
                    request.upload.onprogress = (e) => {
                        progress(e.lengthComputable, e.loaded, e.total);
                    };
                    request.onload = function () {
                        if (request.status >= 200 && request.status < 300) {
                            load(request.responseText);
                        } else {
                            error('oh no');
                        }
                    };
                    request.send(formData);
                    return {
                        abort: () => {
                            request.abort();
                            abort();
                        },
                    };
                },
                load: (source, load, error, progress, abort, headers) => {
                    console.log('attempting to load', source);
                },
            }
        }
        if(typeof element.attr('files') !== 'undefined' && element.attr('files') !== false){
            props['files'] = []
            element.attr('files').split(',').forEach(item => {
                if(item != ''){
                    props['files'].push({
                        source: item
                    });
                }
            });
        }
        var pond = element.filepond(props)
        element.on('FilePond:addfile', (event)=>{});
        return pond
    } else{
        return null;
    }
}

function ClickBtn(action='click',type=null,...args){
    var evnt = null
    var btn = null
    if(event){
        event.preventDefault()
        evnt = event
        btn = event.target.closest('button')
    }
    if(type==null){
        if(btn){
            type = btn.getAttribute('type')
        }
    } else{
        type = type
    }
    if(type=='submit'){
        var form = btn.closest('form');
        FormSubmit(form,action);
    } else if(type=='submit_downoload'){
        var form = btn.closest('form');
        FormSubmit(form,action,false);
    } else if(type=='submit_noloader'){
        var form = btn.closest('form');
        FormSubmit(form,action,false);
    } else if(type=='submit_iframe'){
        var form = btn.closest('form')
        FormSubmit(form,action);
        //window.parent.location.reload()
    } else if(type=='download'){
        const link = document.createElement('a')
        link.setAttribute('href', action)
        var filename = action.substring(action.lastIndexOf('/')+1);
        link.setAttribute('download', filename)
        link.style.display = 'none'
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
    } else{
        if(action instanceof Function || type=="function"){
            action.call(this,...args)
        } 
        else if((typeof action == 'string' && action != 'click') || type=="redirect"){
            LinkRedirect(action,evnt?evnt.ctrlKey:false)
        } else{
            console.log(action)
        }
    }
}
function FormSubmit(selector,cmds=null){
    var form = typeof selector == "string"?document.querySelector(selector):selector;
    if(selector instanceof Event){
        form = selector.target.closest('form');
    } else if(form.tagName != 'FORM'){
        form = form.closest('form')
    }
    if(!form){return false;}
    cmds = !Array.isArray(cmds)?[cmds]:cmds
    cmds.forEach(cmd => {
        if(isDict(cmd)){
            for (const [key, value] of Object.entries(cmd)) {
                $("<input />").attr("type", "hidden").attr("name", key).attr("value", value).appendTo($(form));
            }
        } else{
            $("<input />").attr("type", "hidden").attr("name", cmd).attr("value", cmd).appendTo($(form));
        }
    });
    form.dispatchEvent(new Event('submit',{
        'bubbles': true
    }))
    form.submit()
}
function LinkRedirect(url='',blank=false){
    try {
        logo_event('unload')
    } catch (error) {
        
    }
    if(event){
        event.preventDefault()
        if(event.ctrlKey){
            blank = true
        }
    }
    if(blank){
        window.open(url, "_blank")
    } else{
        window.location.href = url
    }
}