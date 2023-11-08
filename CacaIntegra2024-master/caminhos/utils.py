from gerencial.models import Gerencial
from gerencial.utils import SendTelegramMessage

def check_corte(papel):
    cortes = papel.caminho.cortes.all()
    for corte in cortes:
        caminhos_do_corte_safes = [x for x in corte.caminhos_afetados.all() if x.progresso >= corte.nivel]
        if len(caminhos_do_corte_safes) == corte.quantidade:
            for x in corte.caminhos_afetados.all():
                if x.progresso < corte.nivel:
                    print('Caminho '+x.nome+' foi cortado.')
                    SendTelegramMessage('Caminho '+x.nome+' foi cortado.')
                    x.ativo = False
                    x.save()
        