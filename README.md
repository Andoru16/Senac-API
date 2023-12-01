# Senac-API
API desenvolvida para o Projeto Integrador de Integração Aplicação - Zabbix

Para quem estiver com vontade de utilizar este programa, ele já está dockerizado no rep https://hub.docker.com/repository/docker/andoru20/senac-api/general

Só precisa configurar a porta 5555 do Docker para a porta desejada para funcionamento


# API

Existe 3 APIs dentro do programa

1. #/api-comprar
   É necessário ser enviado como POST e com um Body JSON
   {"compra": {
      "produto": "(Nome do produto)",
      "preco": (preço do produto)
     }
   }

2. #/monthly
   É necessário ser enviado como GET e pode ou não ter um Body JSON
   Caso não tenha um body, o mesmo vai retornar com os status mensais do mês atual da máquina
   Com o Body JSON, é possível retornar com o status do mês indicado
   {"Y_M": "(ANO-MÊS)(Ex. 2023-11)"}
   
3. #/last
   É necessário ser enviado como GET e ele retorna as informações da ultima transação realizada



