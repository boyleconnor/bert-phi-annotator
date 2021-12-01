import connexion

from openapi_server.huggingface import huggingFace
from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.text_contact_annotation_request import TextContactAnnotationRequest  # noqa: E501
from openapi_server.models.text_contact_annotation import TextContactAnnotation
from openapi_server.models.text_contact_annotation_response import TextContactAnnotationResponse  # noqa: E501


CONTACT_TYPES = {
    'EMAIL': 'email',
    'FAX': 'fax',
    'PHONE': 'phone',
    'URL': 'url'
}


def create_text_contact_annotations(text_contact_annotation_request=None):  # noqa: E501
    """Annotate contacts in a clinical note
    Return the Contact annotations found in a clinical note # noqa: E501
    :param text_contact_annotation_request:
    :type text_contact_annotation_request: dict | bytes
    :rtype: TextContactAnnotationResponse
    """
    res = None
    status = None
    if connexion.request.is_json:
        try:
            annotation_request = TextContactAnnotationRequest.from_dict(
                connexion.request.get_json())  # noqa: E501
            note = annotation_request._note  # noqa: E501
            annotations = []
            name_annotations = huggingFace.get_entities(
                note.text, CONTACT_TYPES.keys())
            add_contact_annotation(annotations, name_annotations)
            res = TextContactAnnotationResponse(annotations)
            status = 200
        except Exception as error:
            status = 500
            print(error)
            res = Error("Internal error", status, str(error))
    return res, status


def add_contact_annotation(annotations, matches):
    """
    Converts matches to TextContactAnnotation objects and adds them to the
    annotations array specified.
    """
    for match in matches:
        annotations.append(TextContactAnnotation(
            start=int(match['start']),
            length=int(match['end']) - int(match['start']),
            text=match['word'],
            contact_type=CONTACT_TYPES[match['entity_group']],
            confidence=float(match['score'] * 100)
        ))
