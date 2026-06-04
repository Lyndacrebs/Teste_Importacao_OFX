# Teste de importação do OFX
Teste de upload do arquivo OFX (é um formato digital padronizado usado pelos bancos para exportar extratos bancários), leitura, categorização e salvamento no banco de dados usando python.

<br>

### Bibliotecas usadas:

- ***Flask*** - usado para criar o servidor web, gerenciar as rotas (/ e /upload), renderizar os templates HTML e enviar as mensagens flash para o usuário.

- ***ofxparse*** - usada para ler e interpretar arquivos no formato OFX (Open Financial Exchange), extraindo dados da conta, extrato e transações bancárias.

- ***Werkzeug*** (instalada automaticamente junto com o Flask) - a função usada foi a `secure_filename` para limpar o nome dos arquivos enviados e evitar ataques de injeção de caminho.
