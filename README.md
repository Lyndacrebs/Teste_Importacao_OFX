# Teste de importação do OFX
Teste de upload do arquivo OFX (é um formato digital padronizado usado pelos bancos para exportar extratos bancários), leitura, categorização e salvamento no banco de dados usando python.

<br>

### Bibliotecas usadas:

- ***Flask*** - usado para criar o servidor web, gerenciar as rotas (/ e /upload), renderizar os templates HTML e enviar as mensagens flash para o usuário.

- ***ofxparse*** - usada para ler e interpretar arquivos no formato OFX (Open Financial Exchange), extraindo dados da conta, extrato e transações bancárias.

- ***Werkzeug*** (instalada automaticamente junto com o Flask) - a função usada foi a `secure_filename` para limpar o nome dos arquivos enviados e evitar ataques de injeção de caminho.

<br>

### Arquitetura do Banco de Dados:
Nesse projeto o SQLite foi usado como banco de dados local, sendo assim o arquivo `meu_banco.db` é apenas um ambiente de simulação (mock) para validar a modelagem dos dados e garantir que a lógica do sistema está correta

<br>

## Próximos passos para integração em Produção (MySQL):
A arquitetura do código já foi estruturada para suportar a migração para o MySQL com o objetivo de levar o sistema a um ambiente de produção real.
Para isso serão necessárias as seguintes adaptações: <br> 
<br>
#### **1.** Configuração do Servidor: Instalação e configuração de um servidor MySQL (local ou em nuvem). <br>
#### **2.** Credenciais e Segurança: Criação de usuários, senhas e definição de permissões de acesso ao banco. <br>
#### **3.** Alteração da Conexão: Substituição da biblioteca sqlite3 por um conector MySQL (como mysql-connector-python ou SQLAlchemy) e atualização da string de conexão no arquivo de configuração. <br>
#### **4.** Ajustes de Sintaxe SQL: Adaptação de pequenos detalhes de sintaxe entre o SQLite e o MySQL (como tipos de dados e funções de data). <br>
