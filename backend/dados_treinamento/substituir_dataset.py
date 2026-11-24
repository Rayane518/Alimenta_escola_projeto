import argparse
import csv
import sys
from pathlib import Path
from datetime import date
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.infrastructure.database.connection import get_connection

TURMAS = {'MANHÃ': [1, 2, 5, 7], 'TARDE': [3, 4, 8, 9]}
ESCOLA = 1

def exigir(condicao, mensagem):
    if not condicao:
        raise ValueError(mensagem)

def executar(arquivo, confirmar):
    registros = {}
    menus = {}
    with open(arquivo, encoding='utf-8-sig', newline='') as f:
        for r in csv.DictReader(f, delimiter=';'):
            d = date.fromisoformat(r['data'])
            t = r['turno'].strip().upper()
            exigir(t in TURMAS and int(r['id_escola_demo']) == ESCOLA, 'Escola ou turno inválido')
            exigir(d <= date(2026,8,31) and d.weekday() < 5, f'Data inválida: {d}')
            n,p,a,s,b = [int(r[k]) for k in ('alunos_previstos','alunos_presentes','refeicoes_preparadas','refeicoes_servidas','sobras')]
            exigir(n == 100 and 0 <= s <= p <= n and a >= s and b == a-s, f'Quantidades inválidas: {d} {t}')
            m = r['cardapio'].strip()
            exigir(bool(m) and menus.get(d,m)==m, f'Cardápio inconsistente: {d}')
            exigir((d,t) not in registros, f'Duplicidade: {d} {t}')
            menus[d]=m
            registros[d,t]=(p,a,s,b)
    exigir(len(registros)==3000 and len(menus)==1500 and all((d,t) in registros for d in menus for t in TURMAS), 'Quantidade de registros/datas incorreta')
    print(f'CSV validado: {len(registros)} registros, {min(menus)} a {max(menus)}')
    con=get_connection()
    cur=None
    try:
        con.start_transaction()
        cur=con.cursor()
        cur.execute("SELECT TABLE_NAME, ENGINE FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME IN ('presencas','cardapios','registros_merenda')")
        exigir(len([x for x in cur.fetchall() if x[1]=='InnoDB'])==3, 'Tabelas não são todas InnoDB')
        cur.execute('SELECT id_turma, turno, quantidade_alunos FROM turmas WHERE id_escola=%s AND ativa=1 FOR UPDATE',(ESCOLA,))
        exigir(set(cur.fetchall())=={(i,t,25) for t,ids in TURMAS.items() for i in ids}, 'Turmas ativas diferentes do esperado')
        for tabela in ('cardapios','registros_merenda','presencas'):
            if tabela=='presencas':
                sql='SELECT COUNT(*) FROM presencas p JOIN turmas t ON t.id_turma=p.id_turma WHERE t.id_escola=%s AND p.data BETWEEN %s AND %s'
            else:
                sql=f'SELECT COUNT(*) FROM {tabela} WHERE id_escola=%s AND data BETWEEN %s AND %s'
            cur.execute(sql,(ESCOLA,min(menus),max(menus)))
            exigir(cur.fetchone()[0]=={'cardapios':1500,'registros_merenda':3000,'presencas':12000}[tabela], f'Quantidade anterior inesperada em {tabela}')
        exigir(min(menus)==date(2020,12,1) and max(menus)==date(2026,8,31), 'Período inesperado')
        cur.execute('SELECT data, turno FROM registros_merenda WHERE id_escola=%s AND data BETWEEN %s AND %s FOR UPDATE',(ESCOLA,min(menus),max(menus)))
        exigir(set(cur.fetchall())==set(registros), 'Datas ou turnos anteriores divergem do CSV')
        cur.execute('SELECT data FROM cardapios WHERE id_escola=%s AND data BETWEEN %s AND %s FOR UPDATE',(ESCOLA,min(menus),max(menus)))
        exigir(set(x[0] for x in cur.fetchall())==set(menus), 'Datas de cardápios divergem')
        cur.execute('SELECT p.id_turma,p.data FROM presencas p JOIN turmas t ON t.id_turma=p.id_turma WHERE t.id_escola=%s AND p.data BETWEEN %s AND %s FOR UPDATE',(ESCOLA,min(menus),max(menus)))
        exigir(set(cur.fetchall())=={(i,d) for d,t in registros for i in TURMAS[t]}, 'Presenças anteriores divergem')
        # Atualizar no lugar, preservando IDs e chaves estrangeiras.
        cur.executemany('UPDATE cardapios SET descricao=%s WHERE id_escola=%s AND data=%s',[(m,ESCOLA,d) for d,m in menus.items()])
        pres=[]; mer=[]
        for (d,t),(p,a,ser,b) in sorted(registros.items()):
            q,r=divmod(p,4)
            for j,i in enumerate(TURMAS[t]):
                pres.append((25,q+int((j-d.toordinal())%4<r),i,d))
            mer.append((a,ser,b,ESCOLA,d,t))
        cur.executemany('UPDATE presencas SET alunos_previstos=%s, alunos_presentes=%s WHERE id_turma=%s AND data=%s',pres)
        cur.executemany('UPDATE registros_merenda SET refeicoes_preparadas=%s, refeicoes_servidas=%s, sobras=%s WHERE id_escola=%s AND data=%s AND turno=%s',mer)
        cur.execute('''WITH pt AS (SELECT t.id_escola,p.data,t.turno,SUM(p.alunos_previstos) n,SUM(p.alunos_presentes) p,COUNT(*) qtd FROM presencas p JOIN turmas t ON t.id_turma=p.id_turma WHERE t.id_escola=%s AND p.data BETWEEN %s AND %s GROUP BY t.id_escola,p.data,t.turno) SELECT pt.data,pt.turno,pt.n,pt.p,pt.qtd,c.descricao,rm.refeicoes_preparadas,rm.refeicoes_servidas,rm.sobras FROM pt JOIN cardapios c ON c.id_escola=pt.id_escola AND c.data=pt.data JOIN registros_merenda rm ON rm.id_escola=pt.id_escola AND rm.data=pt.data AND rm.turno=pt.turno AND rm.id_cardapio=c.id_cardapio''',(ESCOLA,min(menus),max(menus)))
        rows=cur.fetchall()
        exigir(len(rows)==3000,'Agregação não retornou 3000 registros')
        for d,t,n,p,q,m,a,s,b in rows:
            exigir(n==100 and q==4 and m==menus[d] and (p,a,s,b)==registros[d,t],f'Divergência após inserção: {d} {t}')
        print('Validação SQL aprovada: 1500 cardápios, 12000 presenças, 3000 registros de merenda; 3000 exemplos agregados.')
        if confirmar:
            con.commit()
            print('COMMIT: substituição concluída.')
        else:
            con.rollback()
            print('ROLLBACK: simulação concluída. Nenhuma alteração salva.')
    except BaseException:
        con.rollback()
        raise
    finally:
        if cur is not None: cur.close()
        con.close()

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('csv')
    parser.add_argument('--confirmar',action='store_true')
    args=parser.parse_args()
    executar(args.csv,args.confirmar)
