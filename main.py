import click
from rich.table import Table
from rich.console import Console
import csv
from datetime import datetime

# forma de achar o id atual
current_id: int = 0
lista_backup = []
fieldnames = ["id", "data", "descricao", "valor", "categoria"]
categorias = ("Alimentação", "Transporte", "Moradia", "Saúde", "Outros")
#esse categorias_test só é usado uma vez
categorias_test = ("ALIMENTACAO", "TRANSPORTE", "MORADIA", "SAUDE", "OUTROS")

try:
    with open("despesas.csv", "r", newline="", encoding="utf-8") as arquivo_csv:
        leitor = csv.DictReader(arquivo_csv)
        for line in leitor:
            lista_backup.append(line)
            if int(line['id']) > current_id: current_id = int(line['id'])
except FileNotFoundError:
    with open("despesas.csv", "w", newline="", encoding="utf-8") as create_new_file:
        writer = csv.writer(create_new_file)
        writer.writerow(fieldnames)

@click.group()
def options():
    pass

@options.command()
def add():
    """Adicionar uma nova despesa""" # info que aparece no --help

    # pega a data e verifica se está correta
    data: str = input("Digite a data (DD/MM/YYYY): ")
    try:
        testa_data = datetime.strptime(data, "%d/%m/%Y")
    except ValueError:
        click.echo("Formato inválido! Use o formato DD/MM/YYYY.")
        return

    # pega a descrição do produto
    descricao: str = input("Digite a descrição: ")

    # pega o valor do produto
    valor: float = float(input("Digite o valor: "))
    if valor < 0:
        click.echo("Valor inválido! Digite um número positivo.")
        return

    # escolhe a categoria
    click.echo("Escolha a categoria: ")

    tabela_add = Table(title="Escolha a categoria: ", title_justify="left")
    tabela_add.add_column("Categorias", justify="left", style="cyan")

    for index, tipo in enumerate(categorias):
        tabela_add.add_row(f"{index + 1}. {tipo}")
    console = Console()
    console.print(tabela_add)
    escolha: int = int(input("Digite o número correspondete: "))
    if escolha not in [1, 2, 3, 4, 5]:
        click.echo("Escolha inválida!")
        return 
    
    global lista_backup
    lista_backup.append({
        'id': current_id + 1, 
        'data': data, 
        'descricao': descricao, 
        'valor': valor, 
        'categoria': categorias[escolha-1]
        })
    
    current_id += 1
    
    with open("despesas.csv", "w", newline="", encoding="utf-8") as adicionar:
        arquivo = csv.DictWriter(adicionar, fieldnames=fieldnames)
        arquivo.writeheader()
        arquivo.writerows(lista_backup)
    
    click.echo(f"Despesa com ID {current_id + 1} adicionada com sucesso!")

@options.command()
@click.argument("id_escolhido", type=int)
def edit(id_escolhido: int):
    """Editar uma despesa"""

    ids_existentes = [int(item["id"]) for item in lista_backup]

    if id_escolhido not in ids_existentes:
        click.echo("Nenhuma despesa encontrada com o ID fornecido.")
        return
    

    for item in lista_backup:
        if int(item['id']) == id_escolhido:
            #tenta mudar a data
            nova_data: str = input(f"Data atual: {item['data']}. Digite a nova data (DD/MM/YYYY) ou pressione Enter para manter: ") or item['data']
            if nova_data.strip() != "":
                try:
                    testa_data = datetime.strptime(nova_data, "%d/%m/%Y")
                except ValueError:
                    click.echo("Formato inválido! Use o formato DD/MM/YYYY.")
                    return
            
            #tenta mudar a descrição
            nova_descricao: str = input(f"Descrição atual: {item['descricao']}. Digite a nova descrição ou pressione Enter para manter: ") or item['descricao']

            #tenta mudar o valor
            novo_valor: str = str(input(f"Valor atual: {float(item['valor']):.2f}. Digite o novo valor ou pressione Enter para manter: ")) or item['valor']
        
            try:
                novo_valor_float = float(novo_valor)
                if novo_valor_float < 0:
                    print("Valor inválido! Digite um número positivo.")
                    return
            except ValueError:
                print("Valor inválido! Digite um número positivo.")
                return
            novo_valor_float = float(item['valor'])


            nova_categoria: str = item['categoria']
            click.echo(f"Categoria atual: {item['categoria']}. Escolha uma nova categoria ou pressione Enter para manter:")

            tabela_add = Table(title="Escolha a categoria: ", title_justify="left")
            tabela_add.add_column("Categorias", justify="left", style="cyan")

            for index, tipo in enumerate(categorias):
                tabela_add.add_row(f"{index + 1}. {tipo}")
            console = Console()
            console.print(tabela_add)
            escolha = input("Digite o número correspondente: ")
            if escolha not in ["1", "2", "3", "4", "5", ""]:
                click.echo("Escolha inválida!")
                return 
            if escolha != "": nova_categoria = categorias[int(escolha) - 1]

            item['data'] = nova_data
            item['descricao'] = nova_descricao
            item['valor'] = float(novo_valor_float)
            item['categoria'] = nova_categoria

    with open("despesas.csv", "w", newline="", encoding="utf-8") as edit_file:
        arquivo = csv.DictWriter(edit_file, fieldnames=fieldnames)
        arquivo.writeheader()
        arquivo.writerows(lista_backup)

    click.echo("Despesa editada com sucesso!")

@options.command()
@click.argument("id_escolhido", type=int)
def delete(id_escolhido: int):
    """Deletar uma despesa"""

    if id_escolhido > current_id or id_escolhido < 1:
        click.echo("Nenhuma despesa encontrada com o ID fornecido.")
        return
    
    global lista_backup

    lista_tpm = []
    for item in lista_backup:
        if id_escolhido == int(item['id']):
            pass
        else:
            lista_tpm.append(item)

    
    lista_backup = lista_tpm

    with open("despesas.csv", "w", newline="", encoding="utf-8") as delete_file:
        arquivo_remove = csv.DictWriter(delete_file, fieldnames=fieldnames)
        arquivo_remove.writeheader()
        arquivo_remove.writerows(lista_backup)
        

    click.echo(f"Despesa com ID {id_escolhido} removida com sucesso!")
            
@options.command()
@click.option("--category", type=str, help="Filtra as despesas por categoria.")
@click.option("--month-year", type=str, help="Filtra as despesas de um mês/ano específico (formato MM/YYYY).")
def list(category, month_year):
    """Listar todas as despesas registradas"""

    if category != None:
        if category.upper() not in categorias_test:
            click.echo("Categoria não encontrada!")
            return
        
    if month_year != None:
        try:
            testa_data = datetime.strptime(month_year, "%m/%Y")
        except ValueError:
            click.echo("Formato inválido! Use o formato MM/YYYY.")
            return

    # criando a tabela
    tabela_despesas = Table(title="Lista de Despesas")
    tabela_despesas.add_column("ID", justify="center", style="bright_black")
    tabela_despesas.add_column("Data", justify="center", style="yellow", no_wrap=True)
    tabela_despesas.add_column("Descrição", justify="center", style="magenta")
    tabela_despesas.add_column("Valor (R$)", justify="center", style="green")
    tabela_despesas.add_column("Categoria", justify="center", style="blue")
    
    valor_total: float = 0.0
    for compra in lista_backup:
        # verifica se a categoria e data passam
        categoria_ok = category == None or category == compra['categoria']
        data_ok = month_year == None or month_year == "/".join(compra['data'].split("/")[1:])
        if (categoria_ok and data_ok):
            tabela_despesas.add_row(str(compra['id']), compra['data'], compra['descricao'], str(compra['valor']), compra['categoria'])
            valor_total += float(compra['valor'])
    tabela_despesas.add_section()
    tabela_despesas.add_row("Total", "***", "***", f"{valor_total:.2f}", "***")

    console = Console()
    console.print(tabela_despesas)
@options.command()
@click.argument("month_year", required=True)
def resume(month_year):
    """Exibir o registro financeiro mensal"""

    try:
        testa_data = datetime.strptime(month_year, "%m/%Y")
    except ValueError:
        click.echo("Formato inválido! Use o formato MM/YYYY.")
        return

    tabela_resume = Table(title=f"Resumo de {month_year}")
    tabela_resume.add_column("Categoria", justify="center", style="blue")
    tabela_resume.add_column("Valor (R$)", justify="center", style="green")
    tabela_resume.add_column("Percentual", justify="center", style="bright_black")


    lista_resumo = []
    valor_total: float = 0
    for compra in lista_backup:
        if month_year == "/".join(compra['data'].split("/")[1:]):
            lista_resumo.append(compra)
            valor_total += float(compra['valor'])

    for item in lista_resumo:
        percentual: float = (float(item['valor']) / valor_total) * 100
        tabela_resume.add_row(item['categoria'], item['valor'], f"{percentual:.1f}%")

    tabela_resume.add_section()

    tabela_resume.add_row("Total Geral", f"{valor_total:.2f}", f"100%")

    console = Console()
    console.print(tabela_resume)

if __name__ == "__main__":
    options()