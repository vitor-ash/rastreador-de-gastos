import click
from rich.table import Table
from rich.console import Console
import csv
from datetime import datetime

# forma de achar o id atual
current_id: int
categorias = ("Alimentação", "Transporte", "Moradia", "Saúde", "Outros")
categorias_test = ("ALIMENTACAO", "TRANSPORTE", "MORADIA", "SAUDE", "OUTROS")

with open("despesas.csv", "r") as arquivo_csv:
    next(arquivo_csv)
    total_linhas: int = 0
    for line in arquivo_csv:
        total_linhas += 1
    
current_id: int = total_linhas

fieldnames = ["id", "data", "descricao", "valor", "categoria"]

lista_backup = []

with open("despesas.csv", "r", newline="", encoding="utf-8") as copy:
    arquivo = csv.DictReader(copy)
    for i in arquivo:
        lista_backup.append(i)

tabela_despesas = Table(title="Lista de Despesas")
tabela_despesas.add_column("ID", justify="center", style="bright_black")
tabela_despesas.add_column("Data", justify="center", style="yellow", no_wrap=True)
tabela_despesas.add_column("Descrição", justify="center", style="magenta")
tabela_despesas.add_column("Valor (R$)", justify="center", style="green")
tabela_despesas.add_column("Categoria", justify="center", style="blue")


@click.group()
def options():
    pass

@options.command()
def add():
    """Adicionar uma nova despesa"""
    # usar rich module, mas funciona
    data: str = input("Digite a data (DD/MM/YYYY): ")
    descricao: str = input("Digite a descrição: ")
    valor: float = float(input("Digite o valor: "))

    click.echo("Escolha a categoria: ")
    for index, tipo in enumerate(categorias):
        click.echo(f"{index + 1}. {tipo}")
    escolha: int = int(input("Digite o número correspondete: "))

    with open("despesas.csv", "a", newline="", encoding="utf-8") as adicionar:
        write = csv.writer(adicionar)
        write.writerow([current_id + 1, data, descricao, valor, categorias[escolha]])
    
    click.echo(f"Despesa com ID {current_id + 1} adicionada com sucesso!")



@options.command()
@click.argument("id_escolhido", type=int)
def edit(id_escolhido: int):
    """Editar uma despesa"""

    if id_escolhido > current_id or id_escolhido < 1:
        click.echo("Nenhuma despesa encontrada com o ID fornecido.")
        return
    
    with open("despesas.csv", "w", newline="", encoding="utf-8") as edit_file:
        arquivo = csv.DictWriter(edit_file, fieldnames=fieldnames)
        arquivo.writeheader()
        for item in lista_backup:
            if int(item['id']) == id_escolhido:
                nova_data: str = input(f"Data atual: {item['data']}. Digite a nova data (DD/MM/YYYY) ou pressione Enter para manter: ") or item['data']
                nova_descricao: str = input(f"Descrição atual: {item['descricao']}. Digite a nova descrição ou pressione Enter para manter: ") or item['descricao']
                novo_valor: str = str(input(f"Valor atual: {float(item['valor']):.2f}. Digite o novo valor ou pressione Enter para manter: ")) or item['valor']
                nova_categoria: str = item['categoria']
                click.echo(f"Categoria atual: {item['categoria']}. Escolha uma nova categoria ou pressione Enter para manter:")
                for index, tipo in enumerate(categorias):
                    click.echo(f"{index + 1}. {tipo}")
                escolha = input("Digite o número correspondete: ")
                if escolha != "": nova_categoria = categorias[int(escolha) - 1]

                item['data'] = nova_data
                item['descricao'] = nova_descricao
                item['valor'] = float(novo_valor)
                item['categoria'] = nova_categoria

            arquivo.writerow(item)

    click.echo("Despesa editada com sucesso!")

@options.command()
@click.argument("id_escolhido", type=int)
def delete(id_escolhido: int):
    """Deletar uma despesa"""

    if id_escolhido > current_id or id_escolhido < 1:
        click.echo("Nenhuma despesa encontrada com o ID fornecido.")
        return

    with open("despesas.csv", "w", newline="", encoding="utf-8") as delete_file:
        arquivo_remove = csv.DictWriter(delete_file, fieldnames=fieldnames)

        arquivo_remove.writeheader()
        for item in lista_backup:
            if id_escolhido == int(item['id']):
                pass
            else:
                arquivo_remove.writerow(item)

    click.echo(f"Despesa com ID {id_escolhido} removida com sucesso!")
            
@options.command()
@click.option("--category", type=str, help="Filtra as despesas por categoria.")
@click.option("--month_year", type=str, help="Filtra as despesas de um mês/ano específico (formato MM/YYYY).")
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

    global tabela_despesas
    valor_total: float = 0.0
    for compra in lista_backup:
        if (category == None or category == compra['categoria']) and (month_year == None or month_year == "/".join(compra['data'].split("/")[1:])):
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