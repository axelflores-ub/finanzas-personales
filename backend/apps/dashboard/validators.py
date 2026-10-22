from rest_framework.exceptions import ValidationError

MES_MINIMO = 1
MES_MAXIMO = 12
ANIO_MINIMO = 2000
ANIO_MAXIMO = 2100


def parse_periodo(params):
    """Valida y devuelve (mes, anio) a partir de los query params.

    Lanza ValidationError (-> 400) ante cualquier parámetro faltante,
    no numérico o fuera de rango.
    """
    mes_raw = params.get("mes")
    anio_raw = params.get("anio")

    errores = {}
    if not mes_raw:
        errores["mes"] = "El parámetro mes es obligatorio."
    if not anio_raw:
        errores["anio"] = "El parámetro anio es obligatorio."
    if errores:
        raise ValidationError(errores)

    try:
        mes = int(mes_raw)
    except ValueError:
        raise ValidationError({"mes": "mes debe ser un número entero."})

    try:
        anio = int(anio_raw)
    except ValueError:
        raise ValidationError({"anio": "anio debe ser un número entero."})

    if not (MES_MINIMO <= mes <= MES_MAXIMO):
        raise ValidationError({"mes": f"mes debe estar entre {MES_MINIMO} y {MES_MAXIMO}."})
    if not (ANIO_MINIMO <= anio <= ANIO_MAXIMO):
        raise ValidationError(
            {"anio": f"anio debe estar entre {ANIO_MINIMO} y {ANIO_MAXIMO}."}
        )

    return mes, anio
