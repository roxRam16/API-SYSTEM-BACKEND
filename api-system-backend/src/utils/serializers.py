from bson import ObjectId
from datetime import datetime
from typing import Any, Dict, List, Type, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def serialize_doc(
    doc: Dict[str, Any],
    model: Type[T],
    id_alias: str = "_id",
    defaults: Dict[str, Any] = None
) -> T:
    """
    Convierte un documento MongoDB a un modelo Pydantic genérico.

    Args:
        doc: Documento MongoDB.
        model: Modelo Pydantic destino.
        id_alias: Campo del ObjectId en MongoDB (default '_id').
        defaults: Campos y valores por defecto si no existen en el documento.

    Returns:
        Instancia del modelo Pydantic validada.
    """
    # Convierte ObjectId → str
    if id_alias in doc:
        doc[id_alias] = str(doc[id_alias])

    # Aplica valores por defecto
    if defaults:
        for key, value in defaults.items():
            doc.setdefault(key, value)

    return model.model_validate(doc)


def serialize_docs(
    docs: List[Dict[str, Any]],
    model: Type[T],
    id_alias: str = "_id",
    defaults: Dict[str, Any] = None
) -> List[T]:
    """
    Convierte una lista de documentos MongoDB a una lista de modelos Pydantic.

    Args:
        docs: Lista de documentos.
        model: Modelo Pydantic destino.
        id_alias: Campo del ObjectId.
        defaults: Valores por defecto para cada documento.

    Returns:
        Lista de modelos validados.
    """
    return [serialize_doc(doc, model, id_alias, defaults) for doc in docs]
