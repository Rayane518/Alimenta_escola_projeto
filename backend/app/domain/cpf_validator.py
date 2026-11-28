import re


def validar_cpf(cpf):
    if not isinstance(cpf, str):
        return False

    
    cpf = re.sub(r"[.-]", "", cpf)

   
    if not re.fullmatch(r"[0-9]{11}", cpf):
        return False

   
    if cpf == cpf[0] * 11:
        return False

    
    soma = sum(
        int(cpf[i]) * (10 - i)
        for i in range(9)
    )

    resto = (soma * 10) % 11
    primeiro_digito = 0 if resto == 10 else resto

    if primeiro_digito != int(cpf[9]):
        return False

    
    soma = sum(
        int(cpf[i]) * (11 - i)
        for i in range(10)
    )

    resto = (soma * 10) % 11
    segundo_digito = 0 if resto == 10 else resto

    return segundo_digito == int(cpf[10])
