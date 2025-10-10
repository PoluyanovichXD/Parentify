let editors = [],editorsIds = [];
document.addEventListener("DOMContentLoaded", function () {
    MultiplySetHTMLEditors(document.querySelectorAll('[html_editor]'));
});
function MultiplySetHTMLEditors(selectors){
    if(typeof selectors == 'string'){
        selectors = document.querySelectorAll(selectors)
    }
    selectors.forEach(html_editor => {
        GenerateHTMLEditor(html_editor,html_editor.getAttribute('label'))
    });
}
async function GenerateHTMLEditor(element,label=''){
    
    async function func(){
        if(element.nextElementSibling){
            if(element.nextElementSibling.classList){
                if(element.nextElementSibling.classList.contains('sun-editor')){
                    element.nextElementSibling.remove()
                }
            }
        }
        var editor = SUNEDITOR.create((element),{
            placeholder: label,
            katex: katex,
            lang: SUNEDITOR_LANG['ru'],
            height: 550,
            width:'100%',
            buttonList: [
                ['undo', 'redo'],
                ['font', 'fontSize', 'formatBlock'],
                ['paragraphStyle', 'blockquote'],
                ['bold', 'underline', 'italic', 'strike', 'subscript', 'superscript'],
                ['fontColor', 'hiliteColor', 'textStyle'],
                ['removeFormat'],
                ['outdent', 'indent'],
                ['align', 'horizontalRule', 'list', 'lineHeight'],
                ['table', 'link', 'image', 'video', 'audio' ,'math' ],
                ['fullScreen', 'showBlocks', 'codeView'],
                ['preview', 'print'],
                ['template'],
            ],
            templates:  [
                {
                    name: 'Шаблон для оповещений',
                    html: '<h3 style="text-align:center;">Оповещение</h3>'
                },
                {
                    name: 'Шаблон для тренажора',
                    html: '<h3 style="text-align:center;">Тренажор</h3>'
                }
              ],
        });
        editor.onChange = function (contents, core) { 
            editor.save();
        }
        return editor
    }
    
    if(hasScript('/static/katex/katex.min.js')&&hasScript('/static/suneditor/suneditor.min.js')&&hasScript('/static/suneditor/lang_ru.js')){
        setTimeout(async ()=>{
            editor = await func()
        }, 2000)
    } else{
        setTimeout(async ()=>{
            editor = await func()
        }, 2000)
    }
    return editor
}

async function GenerateHTMLReadOnly(element){
    async function func(){
        if(element.nextElementSibling){
            if(element.nextElementSibling.classList){
                if(element.nextElementSibling.classList.contains('sun-editor')){
                    element.nextElementSibling.remove()
                }
            }
        }
        var editor = SUNEDITOR.create((element),{
            lang: SUNEDITOR_LANG['ru'],
            width:'100%',
            buttonList: [],
            templates:  [],
            previewTemplate :"preview",
            onlyContents:true,
            contenteditable: true
        });
        editor.readOnly(true)
        editor.toolbar.disable();
        editor.toolbar.hide();
        // editor.getFullContents({
        //     onlyContents:true,
        //     contenteditable: true
        // });
    }
    if(hasScript('/static/katex/katex.min.js')&&hasScript('/static/suneditor/suneditor.min.js')&&hasScript('/static/suneditor/lang_ru.js')){
        setTimeout(async ()=>{
            editor = await func()
        }, 2000)
    } else{
        loadScript('/static/katex/katex.min.js')
        loadScript('/static/suneditor/suneditor.min.js')
        loadScript('/static/suneditor/lang_ru.js')
        setTimeout(async ()=>{
            editor = await func()
        }, 2000)
    }
    return editor
}