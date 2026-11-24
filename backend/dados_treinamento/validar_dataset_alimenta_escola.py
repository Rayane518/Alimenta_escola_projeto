import csv
import sys
from collections import Counter
from datetime import date
from pathlib import Path

CAMPOS = ('data','turno','alunos_previstos','alunos_presentes','cardapio','refeicoes_preparadas','refeicoes_servidas','sobras')

def validar(caminho):
    erros=[]; datas=set(); pares=set(); turnos=Counter(); total=0
    with open(caminho, newline='', encoding='utf-8-sig') as arq:
        leitor=csv.DictReader(arq,delimiter=';')
        ausentes=set(CAMPOS)-set(leitor.fieldnames or [])
        if ausentes:
            print('ERRO: colunas ausentes:', ', '.join(sorted(ausentes)));return 1
        for linha, r in enumerate(leitor, start=2):
            total+=1
            try:
                if any(not r[c].strip() for c in CAMPOS): raise ValueError('campo obrigatório vazio')
                d=date.fromisoformat(r['data']); t=r['turno']
                if t not in ('MANHÃ','TARDE'): raise ValueError('turno inválido')
                if d.weekday()>4: raise ValueError('data em fim de semana')
                chave=(d,t)
                if chave in pares: raise ValueError('data/turno duplicados')
                pares.add(chave);datas.add(d);turnos[t]+=1
                previstos,presentes,preparadas,servidas,sobras=(int(r[c]) for c in ('alunos_previstos','alunos_presentes','refeicoes_preparadas','refeicoes_servidas','sobras'))
                if not 0<=presentes<=previstos<=100: raise ValueError('presença/matrícula incoerentes com 100 por turno')
                if not 0<=servidas<=presentes: raise ValueError('refeições servidas acima da presença')
                if preparadas<servidas or sobras!=preparadas-servidas: raise ValueError('sobras inconsistentes')
            except (ValueError,TypeError) as e:
                erros.append(f'linha {linha}: {e}')
    print(f'Registros: {total}; datas: {len(datas)}; manhã: {turnos["MANHÃ"]}; tarde: {turnos["TARDE"]}')
    if total!=3000: erros.append(f'esperados 3000 registros, encontrados {total}')
    if len(datas)<5: erros.append('menos de 5 datas distintas')
    if erros:
        print(f'REPROVADO: {len(erros)} inconsistências')
        for erro in erros[:25]: print('-',erro)
        return 1
    print('APROVADO nas verificações estruturais. NÃO comprova qualidade estatística nem origem real de campos simulados.')
    return 0

if __name__=='__main__':
    if len(sys.argv)!=2:
        print('Uso: python validar_dataset_alimenta_escola.py arquivo.csv');sys.exit(2)
    sys.exit(validar(Path(sys.argv[1])))
