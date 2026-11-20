import re


def validar_cpf(cpf):
    if not isinstance(cpf, str):
        return False

    # Remove apenas os caracteres de formatação
    cpf = re.sub(r"[.-]", "", cpf)

    # Deve conter exatamente 11 dígitos
    if not re.fullmatch(r"[0-9]{11}", cpf):
        return False

    # Rejeita CPFs com todos os dígitos iguais
    if cpf == cpf[0] * 11:
        return False

    # Calcula o primeiro dígito verificador
    soma = sum(
        int(cpf[i]) * (10 - i)
        for i in range(9)
    )

    resto = (soma * 10) % 11
    primeiro_digito = 0 if resto == 10 else resto

    if primeiro_digito != int(cpf[9]):
        return False

    # Calcula o segundo dígito verificador
    soma = sum(
        int(cpf[i]) * (11 - i)
        for i in range(10)
    )

    resto = (soma * 10) % 11
    segundo_digito = 0 if resto == 10 else resto

    return segundo_digito == int(cpf[10])
