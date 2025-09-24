class ControlBase(object):
    """default control, derive other from it"""

    def __init__(self, control_template='controls/ControlBase.html',classname=None):
        self.__controlTemplate = control_template
        self.__subcontrols = []
        self.__btn_controls = []
        self.__need_css = []
        self.__need_js = []
        self.__context = {}
        self.__classname = classname
        super().__init__()

    def get_template(self):
        return self.__controlTemplate

    def get_subcontrols(self):
        return self.__subcontrols

    def need_css(self, name):
        assert name not in self.__need_css, "duplicate css"
        self.__need_css.append(name)

    def need_js(self, name):
        assert name not in self.__need_js, "duplicate js"
        self.__need_js.append(name)

    def add_control(self, name, control,classname=None):
        assert name not in ([c[0]] for c in self.__subcontrols), "duplicate control name"
        if classname == None:
            classname = name
        self.__subcontrols.append((name, control,classname))
    
    def add_botton_control(self,name,control):
        assert name not in ([c[0]] for c in self.__btn_controls), "duplicate control name"
        self.__btn_controls.append((name, control))
    
    def add_context(self,context):
        self.__context.update(context)

    def publish(self, context_branch, js, css):
        for v in self.__need_js:
            if v not in js:
                js.append(v)
        for v in self.__need_css:
            if v not in css:
                css.append(v)
        if len(self.__subcontrols) > 0:
            context_branch['controls'] = []
            context_branch['btn_controls'] = []
            for c in self.__subcontrols:
                subcontrol = {'name': c[0],'classname': c[2]}
                c[1].publish(subcontrol, js, css)
                context_branch['controls'].append(subcontrol)
            
            for c in self.__btn_controls:
                subbtncontrol = {'name': c[0]}
                c[1].publish(subbtncontrol, js, css)
                context_branch['btn_controls'].append(subbtncontrol)
        if self.__context:
            context_branch.update(self.__context)
        context_branch['template'] = self.__controlTemplate
