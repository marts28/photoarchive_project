import tempfile
import zipfile

from django.forms import inlineformset_factory
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from wsgiref.util import FileWrapper
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.http import FileResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, CreateView, DeleteView, UpdateView
from .forms import DocumentForm, PhotoForm
from .models import Document, DocumentPhoto

DocumentPhotoFormSet = inlineformset_factory(
    Document,
    DocumentPhoto,
    form=PhotoForm,
    extra=1,
    can_delete=True
)


class DocumentChangeMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        post = self.get_object()
        return redirect('blog:post_detail', post_id=post.id)


class IndexView(LoginRequiredMixin, ListView):
    model = Document
    template_name = 'archive/index.html'
    paginate_by = 12

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        s = self.request.GET
        query = s.get('q')
        date_from = s.get('from')
        date_to = s.get('to')
        context['q'] = query
        context['date_from'] = date_from
        context['date_to'] = date_to

        return context

    def get_queryset(self):
        s = self.request.GET
        query = s.get('q')
        date_from = s.get('from')
        date_to = s.get('to')
        if not date_from:
            date_from = None
        if not date_to:
            date_to = timezone.now()

        filters = Q()
        if query:
            filters &= Q(title__icontains=query) | Q(description__icontains=query)
        if date_from:
            filters &= Q(doc_date__gte=date_from)
        if date_to:
            filters &= Q(doc_date__lte=date_to)

        return Document.objects.filter(filters).prefetch_related('photos')


class DocumentDetailView(LoginRequiredMixin, DetailView):
    model = Document


class DocumentCreateView(LoginRequiredMixin, CreateView):
    template_name = 'archive/create.html'
    form_class = DocumentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['photo_formset'] = DocumentPhotoFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            context['photo_formset'] = DocumentPhotoFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        photo_formset = context['photo_formset']
        if photo_formset.is_valid():
            self.object = form.save(commit=False)
            self.object.author = self.request.user
            self.object = form.save()
            photo_formset.instance = self.object
            photo_formset.save()
            return redirect(reverse('archive:document_detail', kwargs={'pk': self.object.pk}))
        else:
            return self.form_invalid(form)


class DocumentDeleteView(LoginRequiredMixin, DocumentChangeMixin, DeleteView):
    model = Document
    form_class = DocumentForm
    template_name = 'archive/create.html'
    success_url = reverse_lazy('archive:index')


class DocumentUpdateView(LoginRequiredMixin, UpdateView):
    model = Document
    form_class = DocumentForm
    template_name = 'archive/create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['photo_formset'] = DocumentPhotoFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            context['photo_formset'] = DocumentPhotoFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        photo_formset = context['photo_formset']
        if photo_formset.is_valid():
            self.object = form.save()
            photo_formset.instance = self.object
            photo_formset.save()
            return redirect(reverse('archive:document_detail', kwargs={'pk': self.object.pk}))
        else:
            return self.form_invalid(form)


@login_required
def download_document(request, document_pk, image_pk):
    document = get_object_or_404(Document, id=document_pk)
    images = document.photos.filter(document=document)
    if image_pk > 0:
        images = document.photos.filter(id=image_pk)
    temp = tempfile.TemporaryFile()
    archive = zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED)
    for index in range(images.count()):
        filename = images[index].image.path
        archive.write(filename, f'{document.title}_{index + 1}.png')
    archive.close()
    temp.seek(0)
    wrapper = FileWrapper(temp)
    response = HttpResponse(wrapper, content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename={document.title}.zip'

    return response
