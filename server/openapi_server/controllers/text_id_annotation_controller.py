import connexion

from openapi_server.huggingface import huggingFace
from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.text_id_annotation_request import TextIdAnnotationRequest  # noqa: E501
from openapi_server.models.text_id_annotation import TextIdAnnotation
from openapi_server.models.text_id_annotation_response import TextIdAnnotationResponse  # noqa: E501


ID_TYPES = {
    'USERNAME': 'other',
    'IDNUM': 'id_number',
    'BIOID': 'bio_id',
    'HEALTHPLAN': 'health_plan',
    'MEDICALRECORD': 'medical_record',
    'DEVICE': 'device'
}


def create_text_id_annotations(text_id_annotation_request=None):  # noqa: E501
    """Annotate IDs in a clinical note

    Return the ID annotations found in a clinical note # noqa: E501

    :param text_id_annotation_request:
    :type text_id_annotation_request: dict | bytes

    :rtype: TextIdAnnotationResponse
    """
    res = None
    status = None
    if connexion.request.is_json:
        try:
            annotation_request = TextIdAnnotationRequest.from_dict(connexion.request.get_json())  # noqa: E501
            note = annotation_request._note  # noqa: E501
            annotations = []
            id_annotations = huggingFace.get_entities(
                note.text, ID_TYPES.keys())
            add_id_annotation(annotations, id_annotations)
            res = TextIdAnnotationResponse(annotations)
            status = 200
        except Exception as error:
            status = 500
            print(error)
            res = Error("Internal error", status, str(error))
    return res, status


def add_id_annotation(annotations, matches):
    """
    Converts matches to TextIdAnnotation objects and adds them to the
    annotations array specified.
    """
    for match in matches:
        annotations.append(TextIdAnnotation(
            start=int(match['start']),
            length=len(match['word']),
            text=match['word'],
            confidence=float(match['score'] * 100),
            id_type=ID_TYPES[match['entity_group']]
        ))
