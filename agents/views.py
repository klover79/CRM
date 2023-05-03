from django.views import generic
from django.shortcuts import reverse, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from leads.models import Agent, User, Lead
from .forms import AgentModelForm, AgentUserUpdateForm
from .mixins import OrganiserAndLoginRequiredMixin
from django.core.mail import send_mail
import random

class AgentListView(OrganiserAndLoginRequiredMixin, generic.ListView):
    template_name = "agents/agent_list.html"
    context_object_name = "agents"
    
    def get_queryset(self) :
        organisation = self.request.user.userprofile
        return Agent.objects.filter(organisation=organisation)

class AgentLeadListView(OrganiserAndLoginRequiredMixin, generic.ListView):
    template_name = "agents/agent_lead_list.html"
    context_object_name = "agent_leads"

    def get_queryset(self) :
        organisation = self.request.user.userprofile
        leads = Lead.objects.filter(organisation=organisation, agent__id=self.kwargs["pk"])
        print(leads)
        return leads
    
    def get_context_data(self, **kwargs):
        context = super(AgentLeadListView, self).get_context_data(**kwargs)
        queryset = Agent.objects.get(organisation=self.request.user.userprofile, id=self.kwargs["pk"])
        context.update(
            { "agent": queryset}
        )
        return context


    
class AgentCreateView(OrganiserAndLoginRequiredMixin, generic.CreateView):
    template_name = "agents/agent_create.html"
    form_class = AgentModelForm
    # overide the default function of the class
    def get_success_url(self) -> str:
        return reverse("agents:agent-list")
    
    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_agent = True
        user.is_organiser = False
        user.set_password(f"{random.randint(0,1000000)}")
        user.save()
        Agent.objects.create(
            user=user,
            organisation = self.request.user.userprofile
        )
        send_mail(
            subject="You are invited to be an Agent",
            message="You were added to be an agent on DJCRM. Please come and start working",
            from_email="djcrm@gmail.com",
            recipient_list=["agentoso@gmail.com"]
        )

        # agent.organisation = self.request.user.userprofile
        # agent.save()
        return super(AgentCreateView,self).form_valid(form)

class AgentDetailView(OrganiserAndLoginRequiredMixin, generic.DetailView):
    template_name = "agents/agent_detail.html"
    context_object_name = "agent"

    def get_queryset(self):
        organisation = self.request.user.userprofile
        return Agent.objects.filter(organisation=organisation)    
    
class AgentUpdateView(OrganiserAndLoginRequiredMixin, generic.UpdateView):
    template_name = "agents/agent_update.html"
    form_class =  AgentModelForm
    # overide the default function of the class
    
    def get_success_url(self) -> str:
        return reverse("agents:agent-detail", kwargs={"pk":self.get_object().id})
    
    def get_queryset(self):
        organisation = self.request.user.userprofile
        # return Agent.objects.filter(organisation=organisation)
        # user = User.objects.filter(agent__id=self.kwargs["pk"])
        print(Agent.objects.filter(user__id=self.kwargs["pk"]))
        return Agent.objects.filter(user__id=self.kwargs["pk"])
    
class AgentDeleteView(OrganiserAndLoginRequiredMixin, generic.DeleteView):
    template_name = "agents/agent_delete.html"
    context_object_name = "agent"

    def get_queryset(self):
        organisation = self.request.user.userprofile
        return Agent.objects.filter(organisation=organisation)
    
    def get_success_url(self):
        return reverse("agents:agent-list")
    

#TODO: Decorative filter for login users only
def AgentUserUpdateView(request, pk):
    user = User.objects.get(agent__id=pk)
    agent = Agent.objects.get(id=pk,organisation=request.user.userprofile)
    form = AgentUserUpdateForm(instance=user)
    if request.method == "POST":
        form = AgentUserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('agents:agent-list')
    context = {
    "user": user,
    "form" : form,
    "agent" : agent,
    }
    return render(request, 'agents/agent_update.html',context)
   

