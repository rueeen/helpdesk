from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, FormMixin
from .forms import TicketForm, HistoryForm
from django.urls import reverse_lazy
from .models import Ticket, Status, Tech
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse

@method_decorator(login_required, name='dispatch')
class TicketListView(ListView):
    # Esta clase define una vista de lista para los objetos Ticket.
    # Utiliza el decorador login_required para requerir que el usuario esté autenticado para acceder a esta vista.

    model = Ticket  # Se especifica el modelo de datos que se utilizará en esta vista (Ticket).
    template_name = 'tickets/ticket_list.html'  # Se especifica la plantilla HTML que se utilizará para renderizar la vista.
    context_object_name = 'tickets'  # Se establece el nombre de la variable en el contexto de la plantilla que contendrá la lista de tickets.

    def get_queryset(self):
        # Este método se utiliza para obtener la lista de objetos Ticket que se mostrarán en la vista.

        # Filtra los tickets para mostrar solo los asignados al técnico que ha iniciado sesión.
        return Ticket.objects.filter(tech=Tech.objects.get(user=self.request.user))
        # Esto se logra filtrando los objetos Ticket en función del técnico (tech) que ha iniciado sesión, utilizando el usuario actual (self.request.user).


@method_decorator(login_required, name='dispatch')
class TicketDetailView(FormMixin, DetailView):
    # Esta clase define una vista de detalle para un objeto Ticket.
    # Utiliza el decorador login_required para requerir que el usuario esté autenticado para acceder a esta vista.

    model = Ticket  # Se especifica el modelo de datos que se utilizará en esta vista (Ticket).
    form_class = HistoryForm  # Se especifica el formulario que se utilizará en la vista (HistoryForm).
    template_name = 'tickets/ticket_detail.html'  # Se especifica la plantilla HTML que se utilizará para renderizar la vista.
    context_object_name = 'ticket'  # Se establece el nombre del objeto en el contexto de la plantilla.

    def get_object(self, queryset=None):
        """ Sobrescribe el método estándar para asegurarse de que el ticket pertenece al técnico. """
        # Este método se utiliza para obtener el objeto Ticket que se mostrará en la vista.

        ticket = super(TicketDetailView, self).get_object(queryset)

        # Verifica si el ticket está asignado al usuario actual.
        if ticket.tech.user == self.request.user:
            return ticket
        else:
            raise Http404("No tienes permiso para ver este ticket.")
        # Si el ticket no está asignado al usuario actual, se lanza una excepción Http404, indicando que el usuario no tiene permiso para ver el ticket.

        
    def get_context_data(self, **kwargs):
        # Primero llama a la implementación base para obtener el contexto
        context = super(TicketDetailView, self).get_context_data(**kwargs)
        # Agrega el formulario de Historial al diccionario de contexto
        context['form'] = self.get_form()
        # Devuelve el contexto actualizado que contiene el formulario
        return context

    def post(self, request, *args, **kwargs):
        # Recupera el objeto asociado con esta vista
        self.object = self.get_object()
        # Obtiene la instancia del formulario con los datos del POST
        form = self.get_form()
        # Verifica si el formulario es válido
        if form.is_valid():
            # Si el formulario es válido, procesa los datos del formulario
            return self.form_valid(form)
        else:
            # Si el formulario no es válido, regresa al formulario con los errores de validación
            return self.form_invalid(form)

    def form_valid(self, form):
        # Crea una instancia de Historial pero no la guarda en la BD aún
        history = form.save(commit=False)
        # Guarda la instancia de Historial en la BD
        history.save()
        # Añade la instancia de Historial guardada al historial del objeto Ticket asociado
        self.object.history.add(history)
        # Llama a la implementación base para redirigir a la URL de éxito
        return super(TicketDetailView, self).form_valid(form)

    def get_success_url(self):
        # Define la URL a la cual redirigir después de manejar exitosamente el formulario
        # La URL será la vista 'ticket_detail' con la clave primaria del objeto
        return reverse_lazy('ticket_detail', kwargs={'pk': self.object.pk})


# El decorador 'login_required' asegura que solo los usuarios autenticados puedan acceder a esta vista.
@method_decorator(login_required, name='dispatch')
class TicketCreateView(CreateView):
    # La vista hereda de 'CreateView', que es una vista genérica para crear objetos.

    model = Ticket  # 'model' especifica el modelo que se va a crear.
    form_class = TicketForm  # 'form_class' indica el formulario a usar para crear el objeto.
    template_name = 'tickets/ticket_form.html'  # 'template_name' define la plantilla HTML a utilizar.
    success_url = reverse_lazy('ticket_list')  # 'success_url' es la URL a la que se redirige después de una creación exitosa.

    def form_valid(self, form):
        # Este método se llama cuando se valida el formulario de manera exitosa.
        
        # Asigna el técnico actual al ticket antes de guardarlo en la base de datos.
        form.instance.tech = Tech.objects.get(user=self.request.user)
        
        # Guarda el objeto Ticket en la base de datos.
        self.object = form.save()
        
        # Comprueba si la petición es una solicitud AJAX.
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Si es una solicitud AJAX, prepara la respuesta JSON.
            data = {
                'status': 'success',
                'message': 'El ticket se ha creado con éxito.'
            }
            # Devuelve una respuesta JSON con el estado y el mensaje.
            return JsonResponse(data)
        else:
            # Si no es una solicitud AJAX, sigue el flujo normal de redirección.
            return super().form_valid(form)
        
    def form_invalid(self, form):
        # Este método se llama si el formulario enviado no es válido.
        
        # Comprueba si la petición es una solicitud AJAX.
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Si es una solicitud AJAX, prepara la respuesta JSON con los errores.
            data = {
                'status': 'error',
                'message': 'El formulario contiene errores.',
                'errors': form.errors.as_json()  # Convierte los errores del formulario a JSON.
            }
            # Devuelve una respuesta JSON con el estado de error y los mensajes correspondientes.
            return JsonResponse(data, status=400)
        else:
            # Si no es una solicitud AJAX, sigue el flujo normal de mostrar el formulario con errores.
            return super().form_invalid(form)

# Se asegura de que solo los usuarios autenticados puedan acceder a esta vista.
@method_decorator(login_required, name='dispatch')
class StatusUpdateView(UpdateView):
    # Indica el modelo que se va a actualizar.
    model = Ticket
    # URL a la que se redirige al usuario después de una actualización exitosa.
    success_url = reverse_lazy('ticket_list')
    # Especifica los campos del formulario que se van a incluir en la vista.
    fields = ['status']

    # Obtiene el objeto que se está actualizando.
    def get_object(self, queryset=None):
        # Obtiene el objeto del modelo Ticket utilizando la implementación base.
        ticket = super().get_object(queryset)
        # Actualiza el estado del ticket al estado 'Cerrado'.
        ticket.status = Status.objects.get(name='Cerrado')
        # Guarda el cambio en la base de datos.
        ticket.save()
        # Retorna el objeto ticket actualizado.
        return ticket
    
    # Se llama si los datos del formulario son válidos.
    def form_valid(self, form):
        # Guarda el objeto form y actualiza self.object con el objeto guardado.
        self.object = form.save()
        
        # Verifica si la petición es AJAX.
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Prepara los datos para la respuesta JSON.
            data = {
                'status': 'success',
                'message': 'El ticket se ha cerrado con éxito.'
            }
            # Envía una respuesta JSON con los datos.
            return JsonResponse(data)
        else:
            # Si no es una petición AJAX, continúa con el comportamiento normal.
            return super().form_valid(form)
        
    # Se llama si los datos del formulario no son válidos.
    def form_invalid(self, form):
        # Verifica si la petición es AJAX.
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Prepara los datos del error para la respuesta JSON.
            data = {
                'status': 'error',
                'message': 'Error al cerrar ticket.',
                'errors': form.errors.as_json()  # Convierte los errores del formulario a JSON.
            }
            # Envía una respuesta JSON con los datos de error.
            return JsonResponse(data, status=400)
        else:
            # Si no es una petición AJAX, continúa con el comportamiento normal de error.
            return super().form_invalid(form)
              

