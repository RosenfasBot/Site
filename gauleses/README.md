# XLII IntegraPoli

Repositório com todo o site do caça e Integrapoli, feito usando o framework Django.

Neste README você encontra um guia de como rodar ele e colocar em produção.

Recomendo usar PyCharm ou VSCode com python 3.10.6 para o desenvolvimento.

### Conhecimentos Necessários
- Python, HTML, javascript, Bootstrap CSS
- Git
- [Django](https://www.djangoproject.com/start/)

### Rodando Localmente

**Clonar este repositório**

Se é a primeira vez que você está usando git, instale ele e configure chaves SSH usando [este guia](https://docs.github.com/en/authentication/connecting-to-github-with-ssh).
Depois clone o repositório com:
```
git clone git@github.com:berocco/CacaIntegra2024.git
cd CacaIntegra2024
```

**Instalar requirements**
 
```commandline 
pip install -r requirements.txt 
```

**Instalar postgresql**

O usuário, senha e port que você configurar no postgres devem ser as mesmas que você encontrar no arquivo .env na raíz dessa pasta.
Estas serão as credenciais do seu banco de dados de desenvolvimento local.

- [Ubuntu](https://www.cherryservers.com/blog/how-to-install-and-setup-postgresql-server-on-ubuntu-20-04)
  - só até a parte de configurar a senha
  - entre no psql e rode o comando `CREATE DATABASE [[nome]];` 
- [Windows](https://www.postgresql.org/download/windows/)
  - depois de instalar, entre no programa pgAdmin e crie uma database com o nome desejado


#### Como rodar:
```
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py runserver
```

O migrate precisa ser executado toda vez que existir uma alteração que afeta bancos de dados.
O runserver vai fazer com que a aplicação rode no navegador.


### Subindo e rodando na DigitalOcean

#### Github

Crie um github com o código do site.

#### Conta e créditos

Digital Ocean é uma plataforma que tem tudo o que precisamos pra hostear o site.
Até jan/2023, eles tinham uma promoção com créditos de 200 dólares para os dois primeiros meses de uso, então dá pra hostear o site sem pagar.

#### Configurando o projeto

Depois de criar sua conta na Digital Ocean, crie um projeto.
Pule a seção de adicionar resources.

Clique em Create -> Apps, em Service Provider escolha "GitHub".
Em "Manage Acess", dê acesso do seu repositório do GitHub ao Digital Ocean.
Deixe "Autodeploy" selecionado.

Clique em "Edit Plan", recomendo ter 2 containers de 1 GB de RAM.

Clique em "Add Resource" -> "Database", dê um nome como "db-integrapoli", confirme.

Pule environment variables.

Espere o build do aplicativo terminar (pode levar até 10 minutos).

Agora, na aba Settings, selecione o segundo componente (de banco de dados), veja os detalhes da conexão.
Crie no banco um usuário e uma base. Anote o host e a senha destes.
Nas configurações, adicione o app como "trusted sources".

Selecione o primeiro componente (de website) e edite as environment variables.
No modo "Bulk Editor", cole o seguinte, substituindo a senha e o host pelo que você anotou:
```
DATABASE_URL=${db-integrapoli.DATABASE_URL}
DATABASE_USER=[seu usuario]
DATABASE_PASSWORD=[sua senha]
DATABASE_HOST=[seu host]
DATABASE_NAME=[sua base]
DATABASE_PORT=25060
DEBUG=FALSE
ARQUIVOS_PISTAS=arquivosPistas
```
Salve. Espere um novo build. Vá na aba "Console" e rode o comando `python manage.py migrate`

Seu site deve estar no ar logo em seguida.

#### reCaptcha
Criar chaves recaptcha e colocar na .env e nos lugares com a propriedade data-sitekey (login e validar papel)

### Google service account
O site tem um botão para puxar pistas a partir de uma planilha do google docs.
Para poder usar isso, você precisa criar
[credenciais de google service account](https://mljar.com/blog/authenticate-python-google-sheets-service-account-json-credentials/).
Depois que você tiver o .json com as credenciais, coloque ele na raiz da pasta e atualize a constante GOOGLE_SERVICE_ACCOUNT_ARQUIVO no arquivo settings.py com o nome do novo arquivo de credenciais.
<br>Obs: a conta de serviço que você criou precisa ter acesso à planilha

### Bucket S3
Bucket é um serviço da amazon feito para armazenar e entregar arquivos para uma rede mundial.
É a melhor opção para armazenar arquivos não estáticos e que são upados por usuários, como os arquivos de pistas.

No DigitalOcean, um bucket chama Spaces, que é o que você precisa criar.
Crie uma pasta 'media' na raiz.
Vá em API e gere uma chave de acesso ao spaces.
Coloque os dados dessa chave na .env

### Troubleshooting
- Erro do tipo: relation "gerencial_websitelock" does not exist

Abrir o app no Digital Ocean, ir pra aba "Console" e rodar:
```commandline
python manage.py migrate
```

- Problemas com static files

```commandline
python manage.py collectstatic --dry-run --noinput
```


- [Ubuntu] pip install -r requirements falha em instalar psycopg2 
```commandline
sudo apt install python3-dev libpq-dev
```

### Domínio
Comprar na cloudflare, configurar CNAME, A;

Add domain no DigitalOcean

### Diretórios

- artefatos, caminhos, desejos, fila, gerencial, logs, pistas, users
  - cada um desses contém os tipos de objetos que tem sua tabela no banco de dados, suas propriedades e funções
  - os arquivos dessas pastas são inicialmente gerados pelo django, então você precisa aprender django pra entender melhor eles.
- CaçaWebApp
  - contém configurações do aplicativo, como as variáveis de ambiente em settings.py, e as URLs do site em urls.py 
- static
  - tem os assets públicos do site, como imagens, áudios, pdfs
  - tudo que está nessa pasta por padrão é acessível em [endereço do site]/static/[nome do arquivo]
- templates
  - aqui você faz sua programação HTML
  - arquivos aqui são templates, ou seja, pedaços de HTML que podem ser colocados dentro de outros e podem ter outros pedaços dentro de si