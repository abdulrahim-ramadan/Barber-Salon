from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import MultipleObjectMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, CreateView, UpdateView, DeleteView , DetailView, TemplateView
from .models import Owner, Barber, Review, GalleryItem, Appointment, Message, Service, Category
from .forms import OwnerForm, BarberForm, GalleryItemForm, ReviewCreateForm, AppointmentForm, MessageForm, ServiceForm
from django.http import Http404
from django.http import HttpResponseRedirect
from django.db import IntegrityError
from django.db.models import Q
from django.contrib import messages
import uuid
import logging
import hashlib
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


# Owner

class OwnerProfileRequiredMixin(LoginRequiredMixin):
    # def dispatch(self, request, *args, **kwargs):
    #     owner_profile = request.user.owner_user_profile
    #     if not owner_profile:
    #         raise Http404(_("Sie dürfen diese Seite nicht anzeigen."))
    #     return super().dispatch(request, *args, **kwargs)
    pass

    
class OwnerCreateView(LoginRequiredMixin, CreateView):
    model = Owner
    form_class = OwnerForm
    template_name = 'contact/owner/owner_create.html'
    success_url = reverse_lazy('contact:owner_list') 

    def form_valid(self, form):
        # Check if the user is authenticated
        if not self.request.user.is_authenticated:
            return self.handle_no_permission()

        # Check if an owner already exists
        if Owner.objects.exists():
            messages.error(self.request, _('Es kann nur einen Eigentümer geben.'))
            return self.handle_no_permission()

        # Assign the user to the user attribute of the form instance
        form.instance.user = self.request.user

        try:
            # Attempt to save the form
            return super().form_valid(form)
        except IntegrityError:
            # Handle integrity error
            messages.error(self.request, _('Ein Fehler ist aufgetreten.'))
            return self.handle_no_permission()

    def handle_no_permission(self):
        raise Http404(_("Sie sind nicht berechtigt, diese Seite zu sehen."))


class OwnerUpdateView(OwnerProfileRequiredMixin, UpdateView):
    model = Owner
    fields = ['name', 'email', 'phone', 'address', 'logo', 'website', 'about', 'social_media_links']
    template_name = 'owner_form.html'
    success_url = reverse_lazy('owner_list')

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        owner_profile = obj.owner
        if (
            request.user != owner_profile.user
            or Owner.objects.filter(user=request.user).exclude(pk=obj.pk).exists()
        ):
            raise Http404(_("Sie dürfen dieses Eigentümerprofil nicht bearbeiten."))
        return super().dispatch(request, *args, **kwargs)
        
        
class OwnerDeleteView(OwnerProfileRequiredMixin, DeleteView):
    model = Owner
    template_name = 'owner_confirm_delete.html'
    success_url = reverse_lazy('owner_list')

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if request.user != obj.user:
            raise Http404(_("Sie dürfen dieses Eigentümerprofil nicht löschen."))
        return super().dispatch(request, *args, **kwargs)

class OwnerListView(OwnerProfileRequiredMixin, DetailView):
    model = Owner
    template_name = 'owner_detail.html'
    
    
def contact_view(request):
    template_name = 'contact/contact.html'
    owner = Owner.objects.first()  
    message_form = MessageForm()
    if request.method == 'POST':
        message_form = MessageForm(request.POST)
        if message_form.is_valid():
            # Get form data
            name = message_form.cleaned_data['name']
            email = message_form.cleaned_data['email']
            phone = message_form.cleaned_data['phone']
            message = message_form.cleaned_data['message']
            
            
            Message.objects.create(name=name, email=email, phone=phone, message=message)
            
            
            # Send email
            # send_mail(
            #     phone,
            #     f'Name: {name}\nEmail: {email}\n\n{message}\n\n{phone}',  
            #     'admin@gmail.com',  
            #     ['your@example.com'],  # Replace with recipient email address
            #     fail_silently=False,
            # )

            
            return redirect('contact:contact')  
    else:
        message_form = MessageForm() 

    context = {
        'owner': owner,
        'message_form': message_form,
    }
    return render(request, 'contact/contact.html', context)

def contact_success(request):
    return render(request, 'contact.html')

# Barber
class BarberCreateView(OwnerProfileRequiredMixin, CreateView):
    model = Barber
    form_class = BarberForm
    template_name = 'contact/barber/barber_create.html'
    success_url = reverse_lazy('contact:barber_list')

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.user = self.request.user
            name = form.cleaned_data.get('name')
            existing_barber = Barber.objects.filter(name=name).first()

            if existing_barber:
                messages.error(self.request, _('A barber with this name already exists.'))
                return self.form_invalid(form)
            else:
                return super().form_valid(form)
        else:
            raise Http404(_("You must be logged in to create a barber profile."))
        
        
class BarberUpdateView(OwnerProfileRequiredMixin, UpdateView):
    model = Barber
    form_class = BarberForm
    template_name = 'contact/barber/barber_update.html'
    
    def get_success_url(self):
        return reverse('contact:barber_list')


class BarberDeleteView(OwnerProfileRequiredMixin, DeleteView):
    model = Barber
    template_name = 'contact/barber/barber_delete.html'
    success_url = reverse_lazy('contact:barber_list')
    

    def get_object(self, queryset=None):
        return get_object_or_404(Barber, pk=self.kwargs['pk'])

    def delete(self, request, *args, **kwargs):
        barber = self.get_object()
        barber.delete()
        return HttpResponseRedirect(self.get_success_url())



class BarberListView(OwnerProfileRequiredMixin, ListView):
    model = Barber
    template_name = 'contact/barber/barber_list.html'
    
    def get_queryset(self):
        return Barber.objects.all()
    
class BarberManagementView(OwnerProfileRequiredMixin, ListView):
    model = Barber
    template_name = 'contact/barber/barber_management.html'
    
    def get_queryset(self):
        return Barber.objects.all()
    
    


# GalleryItem
class GalleryItemCreateView(OwnerProfileRequiredMixin, CreateView):
    model = GalleryItem
    form_class = GalleryItemForm
    template_name = 'contact/gallery/item_create.html'
    success_url = reverse_lazy('contact:item_list')

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.user = self.request.user
            try:
                return super().form_valid(form)
            except IntegrityError:
                messages.error(self.request, _('Ein Element mit diesem Titel existiert bereits.'))
                return self.form_invalid(form)
        else:
            raise Http404(_("Sie dürfen kein Galerieelement erstellen."))

class GalleryItemUpdateView(OwnerProfileRequiredMixin, UpdateView):
    model = GalleryItem
    form_class = GalleryItemForm
    template_name = 'contact/gallery/item_update.html'
    success_url = reverse_lazy('contact:item_list')



class GalleryItemDeleteView(OwnerProfileRequiredMixin, DeleteView):
    model = GalleryItem
    template_name = 'contact/gallery/item_delete.html'
    success_url = reverse_lazy('contact:item_list')

    # def get_success_url(self):
    #     return reverse('contact:item_list')

    def get_object(self, queryset=None):
        return get_object_or_404(GalleryItem, pk=self.kwargs['pk'])

    def delete(self, request, *args, **kwargs):
        item = self.get_object()
        item.delete()
        return HttpResponseRedirect(self.get_success_url())


class GalleryItemListView(OwnerProfileRequiredMixin, ListView):
    model = GalleryItem
    template_name = 'contact/gallery/item_list.html'
    
    def get_queryset(self):
        return GalleryItem.objects.all()
    
    
class GalleryItemManagementView(OwnerProfileRequiredMixin, ListView):
    model = GalleryItem
    template_name = 'contact/gallery/item_management.html'
    
    def get_queryset(self):
        return GalleryItem.objects.all()

# Review
class ReviewCreateView(OwnerProfileRequiredMixin, CreateView):
    model = Review
    form_class = ReviewCreateForm
    template_name = 'contact/review/review_create.html'
    success_url = reverse_lazy('contact:review_list')

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.user = self.request.user
            form.instance.rating = form.cleaned_data['rating']
            try:
                return super().form_valid(form)
            except IntegrityError:
                messages.error(self.request, _('Eine Bewertung von diesem Benutzer für denselben Friseur existiert bereits.'))
                return self.form_invalid(form)
        else:
            raise Http404(_("Sie dürfen keine Bewertung erstellen."))

class ReviewUpdateView(OwnerProfileRequiredMixin, UpdateView):
    model = Review
    form_class = ReviewCreateForm
    template_name = 'contact/review/review_update.html'
    success_url = reverse_lazy('contact:review_list')



class ReviewDeleteView(OwnerProfileRequiredMixin, DeleteView):
    model = Review
    template_name = 'contact/review/review_delete.html'
    success_url = reverse_lazy('contact:review_list')


    def get_object(self, queryset=None):
        return get_object_or_404(Review, pk=self.kwargs['pk'])

    def delete(self, request, *args, **kwargs):
        review = self.get_object()
        review.delete()
        return HttpResponseRedirect(self.get_success_url())


class ReviewListView(OwnerProfileRequiredMixin, ListView):
    model = Review
    template_name = 'contact/review/review_list.html'
    context_object_name = 'object_list'
    
    def get_queryset(self):
        return Review.objects.all()
    
class ReviewManagementView(OwnerProfileRequiredMixin, ListView):
    model = Review
    template_name = 'contact/review/review_management.html'
    context_object_name = 'object_list'
    
    def get_queryset(self):
        return Review.objects.all()

# Appointment
class AppointmentCreateView(OwnerProfileRequiredMixin, CreateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = 'contact/appointment/appointment_create.html'
    # success_url = reverse_lazy('contact:appointment_list')

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.user = self.request.user
            self.submitted = True
            return super().form_valid(form)
        else:
            raise Http404(_("Sie müssen angemeldet sein, um einen Termin zu erstellen."))

    
    def form_invalid(self, form):
        self.submitted = False
        return self.render_to_response(self.get_context_data(form=form))
    
    def get_success_url(self):
        return reverse('contact:appointment_list')

class AppointmentUpdateView(OwnerProfileRequiredMixin, UpdateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = 'contact/appointment/appointment_update.html'

    def get_success_url(self):
        return reverse('contact:appointment_list')
    


class AppointmentDeleteView(OwnerProfileRequiredMixin, DeleteView):
    model = Appointment
    template_name = 'contact/appointment/appointment_delete.html'
    
    def get_success_url(self):
        return reverse('contact:appointment_list')

    def get_object(self, queryset=None):
        return get_object_or_404(Appointment, pk=self.kwargs['pk'])

    def delete(self, request, *args, **kwargs):
        appointment = self.get_object()
        appointment.delete()
        return HttpResponseRedirect(self.get_success_url())



class AppointmentListView(OwnerProfileRequiredMixin, ListView):
    model = Appointment
    template_name = 'contact/appointment/appointment_list.html'
    context_object_name = 'object_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['verbose_name'] = self.model._meta.verbose_name.title()
        return context
    
    
class AppointmentManagementView(OwnerProfileRequiredMixin, ListView):
    model = Appointment
    template_name = 'contact/appointment/appointment_management.html'
    context_object_name = 'object_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['verbose_name'] = self.model._meta.verbose_name.title()
        return context


def pricing_view(request):
    categories = Category.objects.prefetch_related('service_category').all()
    services = Service.objects.all()
    return render(request, 'contact/pricing.html', {'categories': categories, 'services': services})

class ServiceCreateView(CreateView):
    model = Service
    fields = ['name', 'price', 'category']
    template_name = 'prices/service_create.html'
    success_url = reverse_lazy('contact:management')

class ServiceUpdateView(UpdateView):
    model = Service
    fields = ['name', 'price', 'category']
    template_name = 'prices/service_update.html'
    success_url = reverse_lazy('contact:management')

class ServiceDeleteView(DeleteView):
    model = Service
    template_name = 'prices/service_delete.html'
    success_url = reverse_lazy('contact:management')

# Visitor Views
class VisitorIdMixin:
    def get_visitor_id(self):
        visitor_id = self.request.session.get('visitor_id', None)
        if not visitor_id:
            visitor_id = str(uuid.uuid4())
            self.request.session['visitor_id'] = visitor_id
        return visitor_id
    
    
class VisitorAppointmentCreateView(CreateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = 'contact/appointment/visitor_appointment_create.html'
    success_url = reverse_lazy('contact:visitor_appointment_list')

    def form_valid(self, form):
        # Get visitor information (IP address and user-agent)
        visitor_info = self.request.META.get('REMOTE_ADDR', '') + self.request.META.get('HTTP_USER_AGENT', '')
        # Hash visitor information
        visitor_hash = hashlib.sha256(visitor_info.encode()).hexdigest()
        
        # Check for existing appointment with same visitor hash, date, and time
        existing_appointment = Appointment.objects.filter(visitor_hash=visitor_hash, date=form.instance.date, time=form.instance.time).first()
        
        if existing_appointment:
            messages.error(self.request, _('Sie haben bereits einen Termin für dieses Datum und diese Uhrzeit.'))
            return self.form_invalid(form)
        
        # Save the appointment with visitor hash
        form.instance.visitor_hash = visitor_hash
        try:
            self.object = form.save()
            messages.success(self.request, _('Termin erfolgreich hinzugefügt.'))
            return super().form_valid(form)
        except IntegrityError:
            messages.error(self.request, _('Ein Fehler ist aufgetreten. Bitte versuchen Sie es erneut.'))
            return self.form_invalid(form)


class VisitorReviewCreateView(CreateView):
    model = Review
    form_class = ReviewCreateForm
    template_name = 'contact/review/visitor_review_create.html'
    success_url = reverse_lazy('contact:visitor_review_list')

    def form_valid(self, form):
        # Get visitor information (IP address and user-agent)
        visitor_info = self.request.META.get('REMOTE_ADDR', '') + self.request.META.get('HTTP_USER_AGENT', '')
        # Hash visitor information
        visitor_hash = hashlib.sha256(visitor_info.encode()).hexdigest()
        
        # Check for existing review with same visitor hash, barber, and name
        existing_review = Review.objects.filter(visitor_hash=visitor_hash, barber=form.instance.barber, customer_name=form.instance.customer_name).first()
        
        if existing_review:
            messages.error(self.request, _('Sie haben bereits eine Bewertung für diesen Friseur mit dem gleichen Namen abgegeben.'))
            return self.form_invalid(form)
        
        # Save the review with visitor hash
        form.instance.visitor_hash = visitor_hash
        try:
            self.object = form.save()
            messages.success(self.request, _('Bewertung erfolgreich hinzugefügt.'))
            print(form.cleaned_data)
            return super().form_valid(form)
        except IntegrityError:
            messages.error(self.request, _('Ein Fehler ist aufgetreten. Bitte versuchen Sie es erneut.'))
            return self.form_invalid(form)

class VisitorAppointmentListView(ListView):
    model = Appointment
    template_name = 'contact/appointment/appointment_list.html'
   

    def get_queryset(self):
        # Get visitor information (IP address and user-agent)
        visitor_info = self.request.META.get('REMOTE_ADDR', '') + self.request.META.get('HTTP_USER_AGENT', '')
        # Hash visitor information
        visitor_hash = hashlib.sha256(visitor_info.encode()).hexdigest()

        # Check if the visitor has any appointments
        appointments = Appointment.objects.filter(visitor_hash=visitor_hash)
        if appointments.exists():
            return appointments
        else:
            # If no appointments found for the visitor, search appointments by email
            email = self.request.POST.get('email', '')  # Get email from the appointment form
            if email:
                return Appointment.objects.filter(Q(email=email) | Q(visitor_hash=visitor_hash))
            else:
                return Appointment.objects.none()
        

class VisitorReviewListView(VisitorIdMixin, ListView):
    model = Review
    template_name = 'contact/review/visitor_review_list.html'

    def get_queryset(self):

            visitor_info = self.request.META.get('REMOTE_ADDR', '') + self.request.META.get('HTTP_USER_AGENT', '')
            visitor_hash = hashlib.sha256(visitor_info.encode()).hexdigest()
            visitor_reviews = Review.objects.filter(visitor_hash=visitor_hash)

            return list(visitor_reviews)



class ManagementView(TemplateView):
    template_name = 'contact/management.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['appointment_list'] = Appointment.objects.all()
        context['barber_list'] = Barber.objects.all()
        context['review_list'] = Review.objects.all()
        context['gallery_item_list'] = GalleryItem.objects.all()
        context['category_list'] = Category.objects.all()
        context['service_list'] = Service.objects.all()
        context['service_form'] = ServiceForm()
        return context
