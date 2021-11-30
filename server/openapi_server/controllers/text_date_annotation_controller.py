import connexion
from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.text_date_annotation_request import \
    TextDateAnnotationRequest  # noqa: E501
from openapi_server.models.text_date_annotation import TextDateAnnotation
from openapi_server.models.text_date_annotation_response import \
    TextDateAnnotationResponse  # noqa: E501


def create_text_date_annotations():  # noqa: E501
    """Annotate dates in a clinical note

    Return the date annotations found in a clinical note # noqa: E501

    :rtype: TextDateAnnotations
    """
    res = None
    status = None
    if connexion.request.is_json:
        try:
            annotation_request = TextDateAnnotationRequest.from_dict(
                connexion.request.get_json())  # noqa: E501
            note = annotation_request._note
            note = note.text
            annotations = []
            res = TextDateAnnotationResponse(annotations)
            status = 200
        except Exception as error:
            status = 500
            res = Error("Internal error", status, str(error))
    return res, status


def add_date_annotation(annotations, matches, date_format):
    """
    Converts matches to TextDateAnnotation objects and adds them to the
    annotations array specified.
    """
    for match in matches:
        annotations.append(TextDateAnnotation(
            start=match.start(),
            length=len(match[0]),
            text=match[0],
            date_format=date_format,
            confidence=95.5
        ))
