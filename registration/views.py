from django.http import JsonResponse
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from tickets.models import Tech
from tickets.forms import TechForm
from django.contrib.auth.forms import UserCreationForm
from django import forms

# Create your views here.
class SignUpView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/sign_up.html'

    def get_success_url(self):
        return reverse_lazy('login')
    
    def get_form(self, form_class = None):
        form = super(SignUpView, self).get_form()

        form.fields['username'].widget = forms.TextInput(attrs={'class':'form-control'})
        form.fields['password1'].widget = forms.PasswordInput(attrs={'class':'form-control'})
        form.fields['password2'].widget = forms.PasswordInput(attrs={'class':'form-control'})
        
        return form

    def form_valid(self, form):
        self.object = form.save()
        # Si la petición es AJAX, se devuelve una respuesta JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            data = {
                'status': 'success',
                'message': 'Usuario creado exitosamente'
            }
            return JsonResponse(data)
        else:
            return super().form_valid(form)
    
        
    def form_invalid(self, form):
        # Si la petición es AJAX y el formulario no es válido, se devuelve un error
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            data = {
                'status': 'error',
                'message': 'El formulario contiene errores.',
                'errors': form.errors.as_json()  # Esto devuelve los errores del formulario en formato JSON
            }
            return JsonResponse(data, status=400)
        else:
            return super().form_invalid(form)

    
class ProfileUpdate(UpdateView):
    form_class = TechForm
    success_url = reverse_lazy('profile')
    template_name = 'registration/profile_form.html'

    def get_object(self):
        profile, created = Tech.objects.get_or_create(user = self.request.user)
        return profile
    


    