class PageSimple(object):

    def __init__(self, page_title = '', page_template='pages/PageSimple.html'):
        self.__page_title = page_title
        self.__page_template = page_template
        self.__subcontrols=[]
        self.__need_css = []
        self.__need_js = []
        self.__blocks = {}
        return super().__init__()

    def change_title(self, page_title):
        self.__page_title = page_title
        return self

    def change_template(self, page_template):
        self.__page_template = page_template
        return self

    def need_css(self, name):
        assert name not in self.__need_css, "duplicate css"
        self.__need_css.append(name)
        return self

    def need_js(self, name):
        assert name not in self.__need_js, "duplicate js"
        self.__need_js.append(name)
        return self

    def add_control(self, name, control, forward=False):
        assert name not in ([c[0]] for c in self.__subcontrols), "duplicate control name"
        if forward:
            self.__subcontrols.insert(0, (name, control))
        else:
            self.__subcontrols.append((name, control))
        return self

    def add_block(self, block_name, control):
        assert block_name not in self.__blocks
        self.__blocks[block_name] = control
        return self

    def __render_control(self, prefix, name, control, request, controls):
        render = {}
        for c in controls:
            if (prefix + name).endswith(c):
                context = RequestContext(request)
                subcontrol = {'name':name}
                control.publish(subcontrol, [], [])
                context['control'] = subcontrol
                template = get_template(control.get_template())
                render[c] = template.render(context)
        for c in control.get_subcontrols():
            render.update(self.__render_control(prefix + name + '.', c[0], c[1], request, controls))
        return render

    def render_controls_html(self, request, controls):
        render = {}
        for c in self.__subcontrols:
            render.update(self.__render_control('', c[0], c[1], request, controls))
        r = ''
        for name, text in render.items():
            r += text
        return HttpResponse(r)

    def render_controls_json(self, request, controls):
        render = {}
        for c in self.__subcontrols:
            render.update(self.__render_control('', c[0], c[1], request, controls))
        return HttpResponse(json.dumps(render))

    def render(self, request, add_params={}):
        context = {}
        context['page_title'] = self.__page_title
        context['controls'] = []
        context['blocks'] = {}
        context['js'] = self.__need_js
        context['css'] = self.__need_css
        context.update(add_params)

        for name, c in self.__blocks.items():
            subcontrol = {}
            c.publish(subcontrol, context['js'], context['css'])
            context['blocks'][name] = subcontrol

        for c in self.__subcontrols:
            subcontrol = {'name':c[0]}
            c[1].publish(subcontrol, context['js'], context['css'])
            context['controls'].append(subcontrol)

        template = get_template(self.__page_template)
        return HttpResponse(template.render(context, request))
