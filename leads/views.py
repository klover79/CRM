from django.core.mail import send_mail
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from .models import Lead, Category
from .forms import (
LeadModelForm, 
CustomUserCreationForm, 
AgentAssignForm, 
LeadCategoryUpdateForm,
CategoryForm,
) 
from agents.mixins import OrganiserAndLoginRequiredMixin

class SignupView(generic.CreateView):
    template_name = "registration/signup.html"
    form_class = CustomUserCreationForm
    def get_success_url(self) -> str:
        return reverse("login")

class LandingPageView(generic.TemplateView):
    template_name = "landing.html"

class LeadListView(LoginRequiredMixin,generic.ListView):
    template_name = "leads/lead_list.html"
    context_object_name = "leads"

    def get_queryset(self):
        user = self.request.user
        if user.is_organiser:
            queryset = Lead.objects.filter(organisation=user.userprofile, agent__isnull=False)
        else:
            queryset = Lead.objects.filter(organisation=user.agent.organisation)
            queryset = queryset.filter(agent__user=user) 
        return queryset
    
    def get_context_data(self, **kwargs):
        user = self.request.user 
        context = super(LeadListView, self).get_context_data(**kwargs)
        if user.is_organiser:
            queryset = Lead.objects.filter(organisation=user.userprofile, agent__isnull=True)
            context.update(
                {"unassigned_leads": queryset}
            )
        return context

class LeadDetailView(OrganiserAndLoginRequiredMixin,generic.DetailView):
    template_name = "leads/lead_detail.html"
    context_object_name = "lead"

    def get_queryset(self):
        user = self.request.user
        if user.is_organiser:
            queryset = Lead.objects.filter(organisation=user.userprofile)
        else:
            queryset = Lead.objects.filter(organisation=user.agent.organisation)
            queryset = queryset.filter(agent__user=user)
        return queryset

class LeadCreateView(OrganiserAndLoginRequiredMixin,generic.CreateView):
    template_name ="leads/lead_create.html"
    form_class = LeadModelForm
    def get_success_url(self) -> str:
        return reverse("leads:lead-list")
    
    def form_valid(self, form: LeadModelForm):
        lead_organisation = self.request.user.userprofile 
        lead = form.save(commit=False)
        lead.organisation = lead_organisation
        lead.save()
        send_mail(
            subject="A lead has been created",
            message="Go to the side to see the new lead",
            from_email="localDjangoEmail@noreply.com",
            recipient_list=["faiz.kadir.ismail@gmail.com"]
        )
        return super(LeadCreateView, self).form_valid(form)
  
class LeadUpdateView(OrganiserAndLoginRequiredMixin,generic.UpdateView):
    template_name = "leads/lead_update.html"
    form_class = LeadModelForm

    def get_success_url(self) -> str:
        return reverse("leads:lead-list")
    
    def get_queryset(self):
        user = self.request.user
        return Lead.objects.filter(organisation=user.userprofile)
    
class LeadDeleteView(LoginRequiredMixin,generic.DeleteView):
    template_name = "leads/lead_delete.html"
    def get_success_url(self) -> str:
        return reverse("leads:lead-list")
    
    def get_queryset(self):
        user = self.request.user
        return Lead.objects.filter(organisation=user.userprofile)

class AssignAgentView(OrganiserAndLoginRequiredMixin,generic.FormView):
    template_name="leads/assign_agent.html"
    form_class=AgentAssignForm

    def get_form_kwargs(self, **kwargs):
        kwargs =super(AssignAgentView, self).get_form_kwargs(**kwargs)
        kwargs.update(
        {
            "request": self.request
        }
        )
        return kwargs

    def get_success_url(self):
        return reverse("leads:lead-list")
    
    def form_valid(self, form):
        agent = form.cleaned_data["agent"]
        lead = Lead.objects.get(id=self.kwargs["pk"])
        lead.agent = agent
        lead.save()
        return super(AssignAgentView, self).form_valid(form)

class CategoryListView(LoginRequiredMixin,generic.ListView):
    template_name = "leads/category_list.html"
    context_object_name = "categories"
    

    def get_context_data(self, **kwargs) :
        user = self.request.user
        context = super(CategoryListView, self).get_context_data(**kwargs)
        if user.is_organiser:
            queryset = Lead.objects.filter(organisation=user.userprofile)
        else:
            queryset = Lead.objects.filter(organisation=user.agent.organisation)

        context.update(
            {
                "unassigned_lead_count": queryset.filter(category__isnull=True).count()
            }
        )
        return context

    def get_queryset(self):
        user = self.request.user
        if user.is_organiser:
            queryset = Category.objects.filter(organisation=user.userprofile)
        else:
            queryset = Category.objects.filter(organisation=user.agent.organisation)
        return queryset
    
class CategoryDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = "leads/category_detail.html"
    context_object_name = "category"

    def get_context_data(self, **kwargs):
        context = super(CategoryDetailView, self).get_context_data(**kwargs)
        leads = self.get_object().leads.all()
        context.update(
            {
                "leads": leads
            }
        )
        return context

    def get_queryset(self):
        user = self.request.user
        if user.is_organiser:
            queryset = Category.objects.filter(organisation=user.userprofile)
        else:
            queryset = Category.objects.filter(organisation=user.agent.organisation)
        return queryset
    
class LeadCategoryUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "leads/lead_category_update.html"
    form_class = LeadCategoryUpdateForm

    def get_success_url(self) -> str:
        return reverse("leads:lead-detail", kwargs={"pk":self.get_object().id})
    
    def get_queryset(self):
        user = self.request.user
        if user.is_organiser:
            queryset = Lead.objects.filter(organisation=user.userprofile)
        else:
            queryset = Lead.objects.filter(organisation=user.agent.organisation)
            queryset = queryset.filter(agent__user=user)
        return queryset
    
class CategoryCreateView(OrganiserAndLoginRequiredMixin,generic.CreateView):
    template_name ="leads/category_create.html"
    form_class = CategoryForm
    def get_success_url(self) -> str:
        return reverse("leads:category-list")
    
    def form_valid(self, form: LeadModelForm):
        category_organisation = self.request.user.userprofile 
        category = form.save(commit=False)
        category.organisation = category_organisation
        category.save()
        return super(CategoryCreateView, self).form_valid(form)

class CategoryUpdateView(OrganiserAndLoginRequiredMixin,generic.UpdateView):
    template_name ="leads/category_update.html"
    form_class = CategoryForm
    def get_success_url(self) -> str:
        return reverse("leads:category-list")
    
    def get_queryset(self):
        user = self.request.user
        if user.is_organiser:
            queryset = Category.objects.filter(organisation=user.userprofile)
        else:
            queryset = Category.objects.filter(organisation=user.agent.organisation)
            queryset = queryset.filter(agent__user=user)
        return queryset

class CategoryDeleteView(LoginRequiredMixin,generic.DeleteView):
    template_name = "leads/category_delete.html"
    def get_success_url(self) -> str:
        return reverse("leads:category-list")
    
    def get_queryset(self):
        user = self.request.user
        return Category.objects.filter(organisation=user.userprofile)

def lead_list(request):
    leads = Lead.objects.all()
    
    context = {
        "leads" : leads
    }
        
    return render(request, "leads/lead_list.html", context)

def lead_detail(request, pk):   
    lead = Lead.objects.get(id=pk)
    context = {
        "lead":lead
    }
    return render(request, 'leads/lead_detail.html', context)

def lead_create(request):
    form = LeadModelForm()
    if request.method == "POST":
        form = LeadModelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/leads")
    context = {
        "form": form
    }
    return render(request, "leads/lead_create.html", context)

def lead_update(request,pk):
    lead = Lead.objects.get(id=pk)
    form = LeadModelForm(instance=lead)
    if request.method == "POST":
        form = LeadModelForm(request.POST, instance=lead)
        if form.is_valid():
            form.save()
            return redirect("/leads")
    context = {
        "lead": lead,
        "form" : form ,
    }
    return render(request, 'leads/lead_update.html', context)

def lead_delete(request,pk):
    lead = Lead.objects.get(id=pk)
    lead.delete()
    return redirect("/leads")
