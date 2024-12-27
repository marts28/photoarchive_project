import pytest
from archive.models import Document, DocumentPhoto
from django.urls import reverse

@pytest.mark.django_db
def test_document_creation(user):
    document = Document.objects.create(
        title="Test Document",
        description="Test Description",
        author=user,
        doc_date="2023-01-01T12:00:00Z"
    )

    assert Document.objects.count() == 1
    assert document.title == "Test Document"

@pytest.mark.django_db
def test_document_with_multiple_photos(user):
    document = Document.objects.create(
        title="Document with Photos",
        description="Test description",
        author=user,
        doc_date="2023-01-01T12:00:00Z"
    )

    photo1 = DocumentPhoto.objects.create(document=document, image="photo1.png")
    photo2 = DocumentPhoto.objects.create(document=document, image="photo2.png")

    assert document.photos.count() == 2
    assert photo1 in document.photos.all()
    assert photo2 in document.photos.all()

@pytest.mark.django_db
def test_document_delete_with_photos(user):
    document = Document.objects.create(
        title="Document to Delete",
        description="This document will be deleted",
        author=user,
        doc_date="2023-01-01T12:00:00Z"
    )

    photo1 = DocumentPhoto.objects.create(document=document, image="photo1.png")
    photo2 = DocumentPhoto.objects.create(document=document, image="photo2.png")

    assert Document.objects.filter(id=document.id).exists()
    assert DocumentPhoto.objects.filter(document=document).count() == 2

    document.delete()

    assert not Document.objects.filter(id=document.id).exists()
    assert not DocumentPhoto.objects.filter(document=document).exists()


@pytest.mark.django_db
def test_document_date_filter(user):
    Document.objects.create(
        title="Document 1",
        description="Test description 1",
        author=user,
        doc_date="2023-01-01T12:00:00Z"
    )
    Document.objects.create(
        title="Document 2",
        description="Test description 2",
        author=user,
        doc_date="2023-02-01T12:00:00Z"
    )

    documents = Document.objects.filter(doc_date__gte="2023-01-15", doc_date__lte="2023-02-15")

    assert documents.count() == 1
    assert documents.first().title == "Document 2"

@pytest.mark.django_db
def test_document_list_pagination(client, user):
    client.force_login(user)

    for i in range(15):
        Document.objects.create(
            title=f"Document {i+1}",
            description=f"Description for document {i+1}",
            author=user,
            doc_date="2023-01-01T12:00:00Z"
        )

    response = client.get(reverse('archive:index'))

    assert response.status_code == 200

    assert response.context['is_paginated'] is True

    assert len(response.context['page_obj'].object_list) == 12

    assert response.context['page_obj'].has_next() is True


