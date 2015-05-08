from demoapp.forms import TreeForm
from django.shortcuts import render
from django.views.generic.edit import FormView



# def TreeView(request, template_name=  "fancytree.html"):


class TreeView(FormView):
    template_name = 'demoapp/demo.html'
    form_class = TreeForm




    # form = TreeForm(request.POST or None)
    # if request.method == "POST":
    #     if form.is_valid():
    #         print form.cleaned_data
    #     else:
    #         print form.errors
    # return render(request, template_name, {'form': form})

