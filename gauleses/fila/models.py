from django.db import models
from pistas.models import Pista
from gerencial.models import SingletonModel
from django.contrib.postgres.fields import ArrayField
 
class Fila(SingletonModel):
    # Fila é uma lista de ints, com os números das pistas

    fila = ArrayField(models.IntegerField(), default=list)

    @property
    def ordem_fila(self):
        return [models.Case(*[models.When(numero=numero, then=posicao) for posicao, numero in enumerate(self.fila)])]

    @property
    def pistas_livres(self):
        return Pista.objects.order_by(*self.ordem_fila)
        #return Pista.objects.filter(caminho__isnull=True).order_by(*self.ordem_fila)

    @property
    def all_pistas(self):
        if self.fila!=[]:
            return Pista.objects.order_by(*self.ordem_fila)
        else:
            return []

    def get_proxima_pista(self, caminho):        
        # prioridades de qual atribuir:
        # 0. Atribuída ao caminho
        # 1. Caminho pode pegar, plantada
        # 2. Caminho pode pegar, nao plantada
        # 3. Caminho não pode pegar, plantada
        # 4. Caminho nao pode pegar, nao plantada

        # resumo da ordenação: CA pode pegar, plantada, posição na fila
        pistas_livres = self.pistas_livres
        
        print(type(caminho))
        print(caminho)


        # P0 plantadas, no caminho do CA
        p0 = pistas_livres.filter(status='plantada',  caminho=caminho).first()
        pista = p0
        if not pista:
            print("----------------------not p0----------------------")
        # P1 plantadas e disponiveis pro CA
            p1 = pistas_livres.filter(status='plantada', caminho__isnull=True, caminhos_possiveis__in=[caminho], usuarios_possiveis__in=[caminho.CA_ativo]).first()
            pista = p1
            if not pista:
                print("----------------------not p1----------------------")
                # P2 não plantadas e disponiveis 
                p2 = pistas_livres.filter(caminhos_possiveis__in=[caminho], usuarios_possiveis__in=[caminho.CA_ativo]).first()
                pista = p2
                if not pista: 
                    print("----------------------not p2----------------------")            
                    # P3 plantada e não disponivel
                    p3 = pistas_livres.filter(status='plantada').first()
                    pista = p3
                    if not pista:
                        print("----------------------not p3---------------------------------")             
                        # P4 plantada e não disponivel
                        p4 = pistas_livres.first()
                        pista = p4
        return pista

    def manda_pro_fim(self, pista_numero):
        self.fila.remove(pista_numero)
        self.fila.append(pista_numero)
        super().save()

    def index_pista(self, pista):
        print(pista)
        all = self.all_pistas.exclude(status='recolhida')
        ind = (*all,).index(pista)+1
        return ind

    @property
    def pistas_a_plantar(self):
        todas_sem_caminho = self.all_pistas.exclude(status__in=['plantada', 'recolhida']).exclude(caminho__isnull=False).order_by(*self.ordem_fila)
        
        todas_com_caminho = self.all_pistas.exclude(status__in=['plantada', 'recolhida']).filter(caminho__isnull=False).order_by(*self.ordem_fila)   
        
        print(todas_sem_caminho, todas_com_caminho)
        return [*todas_com_caminho] + [*todas_sem_caminho]
 