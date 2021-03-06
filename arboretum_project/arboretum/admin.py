from functools import update_wrapper

from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.core.urlresolvers import reverse
from django.template.response import TemplateResponse

from django.contrib import admin

from django.contrib.admin.options import csrf_protect_m
from django.contrib.admin.views.main import ChangeList
from django.contrib.admin.util import unquote, quote
from django.conf.urls import url

from . import utility


from django.http import HttpResponse


# Voorlopig: moet op termijn  naar util gebracht
import json

new_title_default = "new"

class FancytreeMpttAdmin(admin.ModelAdmin):
    tree_auto_open = 1
  #  tree_load_on_demand = 1
    # Geef hier aan of heel de boom geladen moet worden ?
    tree_load_on_demand = 10
    trigger_save_after_move = False

    change_list_template = 'fancytree_mptt/grid_view.html'

    @csrf_protect_m
    def changelist_view(self, request, extra_context=None):
        if not self.has_change_permission(request, None):
            raise PermissionDenied()

        change_list = self.get_change_list_for_tree(request)



# prepare the context to pass ths information from the server to the client browser
        context = dict(
            title=change_list.title,
            app_label=self.model._meta.app_label,
            cl=change_list,
            media=self.media,
            has_add_permission=self.has_add_permission(request),
            tree_auto_open=utility.get_javascript_value(self.tree_auto_open),
            tree_json_url=self.get_admin_url('tree_json'),
            tree_services_url = self.get_admin_url('change_tree'),
            tree_model_name = utility.get_model_name(self.model),
            grid_url=self.get_admin_url('grid'),
            new_title = new_title_default,
        )

        if extra_context:
            context.update(extra_context)

        return TemplateResponse(
            request,
            'fancytree_mptt/change_list.html',
            context
        )

    def get_urls(self):
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        urlpatterns = super(FancytreeMpttAdmin, self).get_urls()

        def add_url(regex, url_name, view):
            # Prepend url to list so it has preference before 'change' url
            urlpatterns.insert(
                0,
                url(
                    regex,
                    wrap(view),
                    name='%s_%s_%s' % (
                        self.model._meta.app_label,
                        utility.get_model_name(self.model),
                        url_name
                    )
                )
            )

        add_url(r'^(.+)/move/$', 'move', self.move_view)


        add_url(r'^tree_json/$', 'tree_json', self.tree_json_view)


        add_url(r'^change_tree/$', 'change_tree', self.tree_service)

        add_url(r'^grid/$', 'grid', self.grid_view)
        return urlpatterns


    @csrf_protect_m
    @utility.django_atomic()
    def move_view(self, request, object_id):
        instance = self.get_object(request, unquote(object_id))

        if not self.has_change_permission(request, instance):
            raise PermissionDenied()

        if request.method != 'POST':
            raise SuspiciousOperation()

        target_id = request.POST['target_id']
        position = request.POST['position']
        target_instance = self.get_object(request, target_id)

        if position == 'before':
            instance.move_to(target_instance, 'left')
        elif position == 'after':
            instance.move_to(target_instance, 'right')
        elif position == 'inside':
            instance.move_to(target_instance)
        else:
            raise Exception('Unknown position')

        if self.trigger_save_after_move:
            instance.save()

        return utility.JsonResponse(
            dict(success=True)
        )

    def get_change_list_for_tree(self, request):
        kwargs = dict(
            request=request,
            model=self.model,
            list_display=(),
            list_display_links=(),
            list_filter=(),
            date_hierarchy=None,
            search_fields=(),
            list_select_related=(),
            list_per_page=100,
            list_editable=(),
            model_admin=self,
            list_max_show_all=200,
        )

        return ChangeList(**kwargs)

    def get_changelist(self, request, **kwargs):
        if utility.get_short_django_version() >= (1, 5):
            return super(FancytreeMpttAdmin, self).get_changelist(request, **kwargs)
        else:
            return FixedChangeList

    def get_admin_url(self, name, args=None):
        opts = self.model._meta
        url_name = 'admin:%s_%s_%s' % (opts.app_label, utility.get_model_name(self.model), name)

        return reverse(
            url_name,
            args=args,
            current_app=self.admin_site.name
        )









    def get_tree_data(self, qs, max_level):
        pk_attname = self.model._meta.pk.attname

        def handle_create_node(instance, node_info):
            pk = quote(getattr(instance, pk_attname))

            node_info.update(
                url=self.get_admin_url('change', (quote(pk),)),
                move_url=self.get_admin_url('move', (quote(pk),))
            )

        return utility.get_tree_from_queryset(qs, handle_create_node, max_level)

    def tree_json_view(self, request):
        node_id = request.GET.get('node')

        if node_id:
            node = self.model.objects.get(id=node_id)
            max_level = node.level + 1
        else:
            max_level = self.tree_load_on_demand

        qs = utility.get_tree_queryset(
            model=self.model,
            node_id=node_id,
            selected_node_id=request.GET.get('selected_node'),
            max_level=max_level,
        )

        tree_data = self.get_tree_data(qs, max_level)
        return utility.JsonResponse(tree_data)

    def grid_view(self, request):
        return super(FancytreeMpttAdmin, self).changelist_view(
            request,
            dict(tree_url=self.get_admin_url('changelist'))
        )



    def tree_service(self,request):

        model = self.model

        try:
            data = json.loads(request.body)
            source_nodes = data['source_nodes']
            target_node = data['target_node']
            method = data['method']
            hitmode = data['hitmode']
            new_id = data['new_id']
            response = data['response']







            if method=="CHANGETITLE":
                node_to_change = model.objects.get(pk=target_node['node_id'])
                node_to_change.title = target_node['node_title']
                node_to_change.save()
                return HttpResponse('OK')



            elif method=="GETALLNODES":
                return



        # def get_tree_data(self, qs, max_level):
        #     pk_attname = self.model._meta.pk.attname
        #
        #     def handle_create_node(instance, node_info):
        #         pk = quote(getattr(instance, pk_attname))
        #
        #         node_info.update(
        #             url=self.get_admin_url('change', (quote(pk),)),
        #             move_url=self.get_admin_url('move', (quote(pk),))
        #         )
        #
        #     return utility.get_tree_from_queryset(qs, handle_create_node, max_level)



            elif method=="PASTE":

                node_to_move = model.objects.get(pk=source_nodes[0].get('node_id'))
                target_node = model.objects.get(pk=target_node['node_id'])
                model.objects.move_node(node_to_move, target_node, position='last-child')

                return HttpResponse('OK')


            elif method=="DROP":

                node_to_move = model.objects.get(pk=source_nodes[0].get('node_id'))



                if hitmode == 'over':
                    target_node = model.objects.get(pk=target_node['node_id'])
                    model.objects.move_node(node_to_move, target_node, position='first-child')
                elif hitmode == 'before':
                    target_node = model.objects.get(pk=target_node['node_id'])
                    model.objects.move_node(node_to_move, target_node, position='left')
                elif hitmode == 'after':
                    target_node = model.objects.get(pk=target_node['node_id'])
                    model.objects.move_node(node_to_move, target_node, position='right')



                return HttpResponse('OK')

            elif method=="ADD":

                target_node = model.objects.get(pk=target_node['node_id'])
                new_node = model()
                new_node.title= new_title_default
                new_node.insert_at(target_node,position='last-child',save=True)
                data['new_id']=new_node.id
                dataresponse = json.dumps(data)
                resp = HttpResponse( dataresponse)
                return resp


            elif method=="DELETE":
                target_node = model.objects.get(pk=target_node['node_id'])
                target_node.delete()
                dataresponse = json.dumps(data)
                resp = HttpResponse( dataresponse)
                return resp

            elif method=="REBUILD":
                #target_node = model.objects.get(pk=target_node['node_id'])
                model.objects.rebuild()
                dataresponse = json.dumps(data)
                resp = HttpResponse( dataresponse)
                return resp

        except (KeyError):
            # Redisplay the poll voting form.
            return
        else:

            return HttpResponse('OK')












        def get_admin_url(self, name, args=None):
            opts = self.model._meta
            url_name = 'admin:%s_%s_%s' % (opts.app_label, utility.get_model_name(self.model), name)

            return reverse(
                url_name,
                args=args,
                current_app=self.admin_site.name
            )

        def get_tree_data(self, qs, max_level):
            pk_attname = self.model._meta.pk.attname

            def handle_create_node(instance, node_info):
                pk = quote(getattr(instance, pk_attname))

                node_info.update(
                    url=self.get_admin_url('change', (quote(pk),)),
                    move_url=self.get_admin_url('move', (quote(pk),))
                )

            return utility.get_tree_from_queryset(qs, handle_create_node, max_level)

        def tree_json_view(self, request):
            node_id = request.GET.get('node')

            if node_id:
                node = self.model.objects.get(id=node_id)
                max_level = node.level + 1
            else:
                max_level = self.tree_load_on_demand

            qs = utility.get_tree_queryset(
                model=self.model,
                node_id=node_id,
                selected_node_id=request.GET.get('selected_node'),
                max_level=max_level,
            )

            tree_data = self.get_tree_data(qs, max_level)
            return utility.JsonResponse(tree_data)

        def grid_view(self, request):
            return super(FancytreeMpttAdmin, self).changelist_view(
                request,
                dict(tree_url=self.get_admin_url('changelist'))
            )


class FixedChangeList(ChangeList):
    """
    Fix issue 1: the changelist must have a correct link to the edit page
    """
    def url_for_result(self, result):
        pk = getattr(result, self.pk_attname)

        return reverse(
            'admin:%s_%s_change' % (self.opts.app_label, self.opts.module_name),
            args=[quote(pk)],
            current_app=self.model_admin.admin_site.name
        )
