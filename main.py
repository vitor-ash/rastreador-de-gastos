import click
from rich.table import Table
from rich.console import Console
import csv
from datetime import datetime
import unicodedata
from pathlib import Path

# ID,Date,Description,Amount,Category

# forma de achar o id atual
current_id: int = 0
lista_ids = []
lista_backup = []
fieldnames = ["ID", "Date", "Description", "Amount", "Category"]
categorias = ("Alimentacao", "Transporte", "Moradia", "Saúde", "Outros")

#caminho
base = Path(__file__).resolve().parent
CSV_PATH = base / "expenses.csv"

try:
    with open(CSV_PATH, "r", newline="", encoding="utf-8") as arquivo_csv:
        leitor = csv.DictReader(arquivo_csv)
        for line in leitor:
            lista_backup.append(line)
            lista_ids.append(int(line['ID']))
            if int(line['ID']) > current_id: current_id = int(line['ID'])
except FileNotFoundError:
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as create_new_file:
        writer = csv.writer(create_new_file)
        writer.writerow(fieldnames)

# functions
def checar_data(data: str) -> bool:
    try:
        testa_data = datetime.strptime(data, "%d/%m/%Y")
        return True
    except ValueError:
        return False

def checar_valor(valor: float) -> bool:
    try:
        valor = float(valor)
        return valor > 0
    except ValueError:
        return False


def tabela_categoria():
    # blueprint da tabela
    tabela_add = Table(title="Escolha a categoria: ", title_justify="left")
    tabela_add.add_column("Categorias", justify="left", style="cyan")

    #criando a tabela
    for index, tipo in enumerate(categorias):
        tabela_add.add_row(f"{index + 1}. {tipo}")
    console = Console()
    console.print(tabela_add)

def checar_categoria(categoria: int) -> bool:
    try:
        categoria = int(categoria)
        return categoria >= 1 and categoria <= 5
    except ValueError:
        return False
    
def normalizar_categoria(categoria: str) -> str:
    categoria = categoria.upper().strip()
    categoria = unicodedata.normalize("NFD", categoria)
    categoria = "".join(char for char in categoria if unicodedata.category(char) != "Mn")
    return categoria
       

@click.group()
def options():
    pass

@options.command()
def add():
    """Adicionar uma nova despesa""" # info que aparece no --help


    # pega a data e verifica se está correta
    while True:
        entrada = input("Digite a data (DD/MM/YYYY): ")
        if checar_data(entrada): 
            data: str = entrada
            break
        else:
            click.echo("Formato inválido! Use o formato DD/MM/YYYY.")

    # pega a descrição do produto
    descricao: str = input("Digite a descrição: ")

    # pega o valor do produto
    while True:
        entrada = input("Digite o valor: ")
        if checar_valor(entrada):
            valor: float = float(entrada)
            break
        else:
            click.echo("Valor inválido! Digite um número positivo.")

    # escolhe a categoria
    tabela_categoria()
    while True:
        entrada = input("Digite o número correspondete: ")
        if checar_categoria(entrada):
            categoria: int = int(entrada)
            break
        else:
            click.echo("Valor inválido! Digite um número de 1 a 5.")
    
    #adicioando a despesa
    global lista_backup
    global current_id
    global lista_ids
    current_id += 1
    lista_ids.append(current_id)
    lista_backup.append({
        'ID': current_id, 
        'Date': data, 
        'Description': descricao, 
        'Amount': valor, 
        'Category': categorias[categoria-1]
        })
    

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as adicionar:
        arquivo = csv.DictWriter(adicionar, fieldnames=fieldnames)
        arquivo.writeheader()
        arquivo.writerows(lista_backup)
    
    click.echo(f"Despesa com ID {current_id} adicionada com sucesso!")

@options.command()
@click.argument("id_escolhido", type=int)
def edit(id_escolhido: int):
    """Editar uma despesa"""

    flag = False

    if id_escolhido not in lista_ids:
        click.echo("Nenhuma despesa encontrada com o ID fornecido.")
        return
    

    for item in lista_backup:
        if int(item['ID']) == id_escolhido:

            
            #tenta mudar a data
            while True:
                entrada = input(f"Data atual: {item['Date']}. Digite a nova data (DD/MM/YYYY) ou pressione Enter para manter: ")
                if entrada.strip() != "":
                    if checar_data(entrada): 
                        nova_data: str = entrada
                        item['Date'] = nova_data
                        flag = True
                        break
                    else:
                        click.echo("Formato inválido! Use o formato DD/MM/YYYY.")
                else:
                    nova_data = item['Date']
                    break
            
            #tenta mudar a descrição
            entrada = input(f"Descrição atual: {item['Description']}. Digite a nova descrição ou pressione Enter para manter: ")
            if entrada.strip() != "":
                nova_descricao: str = entrada
                item['Description'] = nova_descricao
                flag = True
            else:
                nova_data = item['Description']

            #tenta mudar o valor
            while True:
                entrada = input(f"Valor atual: {float(item['Amount']):.2f}. Digite o novo valor ou pressione Enter para manter: ")
                if entrada.strip() != "":
                    if checar_valor(entrada): 
                        novo_valor: float = float(entrada)
                        item['Amount'] = novo_valor
                        flag = True
                        break
                    else:
                        click.echo("Valor inválido! Digite um número positivo.")
                else:
                    novo_valor = item['Amount']
                    break

            
            click.echo(f"Categoria atual: {item['Category']}")
            tabela_categoria()
            while True:
                entrada = input("Escolha uma nova categoria ou pressione Enter para manter a atual: ")
                if entrada.strip() != "":
                    if checar_categoria(entrada):
                        nova_categoria: int = int(entrada)
                        item['Category'] = categorias[nova_categoria-1]
                        flag = True
                        break
                    else:
                        click.echo("Valor inválido! Digite um número de 1 a 5.")
                else:
                    nova_categoria = item['Category']
                    break
    
    if flag:
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as edit_file:
            arquivo = csv.DictWriter(edit_file, fieldnames=fieldnames)
            arquivo.writeheader()
            arquivo.writerows(lista_backup)

        click.echo("Despesa editada com sucesso!")
    else:
        click.echo("Despesa não foi alterada.")

@options.command()
@click.argument("id_escolhido", type=int)
def delete(id_escolhido: int):
    """Deletar uma despesa"""

    global lista_backup
    global lista_ids

    if id_escolhido not in lista_ids:
        click.echo("Nenhuma despesa encontrada com o ID fornecido.")
        return
    
    ids_tpm = []
    lista_tpm = []
    for item in lista_backup:
        if id_escolhido == int(item['ID']):
            pass
        else:
            ids_tpm.append(int(item['ID']))
            lista_tpm.append(item)

    
    lista_backup = lista_tpm
    lista_ids = ids_tpm

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as delete_file:
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
        if normalizar_categoria(category) not in ["ALIMENTACAO", "TRANSPORTE", "MORADIA", "SAUDE", "OUTROS"]:
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
        categoria_ok = category == None or normalizar_categoria(category) == normalizar_categoria(compra['Category'])
        data_ok = month_year == None or month_year == "/".join(compra['Date'].split("/")[1:])
        if (categoria_ok and data_ok):
            tabela_despesas.add_row(str(compra['ID']), compra['Date'], compra['Description'], str(compra['Amount']), compra['Category'])
            valor_total += float(compra['Amount'])
    tabela_despesas.add_section()
    tabela_despesas.add_row("Total", "***", "***", f"{valor_total:.2f}", "***")

    console = Console()
    console.print(tabela_despesas)
@options.command()
@click.argument("month_year", required=True)
def resume(month_year):
    """Exibir o registro financeiro mensal"""

    #testar se a data está no formato adequado
    try:
        testa_data = datetime.strptime(month_year, "%m/%Y")
    except ValueError:
        click.echo("Formato inválido! Use o formato MM/YYYY.")
        return

    # criar a tabela
    tabela_resume = Table(title=f"Resumo de {month_year}")
    tabela_resume.add_column("Categoria", justify="center", style="blue")
    tabela_resume.add_column("Valor (R$)", justify="center", style="green")
    tabela_resume.add_column("Percentual", justify="center", style="bright_black")


    lista_mensal: dict[str, float]= dict()
    valor_total: float = 0.0
    #agrupa as categorias
    for compra in lista_backup:
        if month_year == "/".join(compra['Date'].split("/")[1:]):
            if compra['Category'] not in lista_mensal.keys():
                lista_mensal[compra['Category']] = 0.0

            lista_mensal[compra['Category']] += float(compra['Amount'])
            valor_total += float(compra['Amount'])
    #cria a tabela
    for categoria, valor in lista_mensal.items():
        if valor_total != 0:
            percentual: float = (valor / valor_total) * 100
        else: 
            percentual = 0    
        tabela_resume.add_row(str(categoria), str(valor), f"{percentual:.1f}%")

    tabela_resume.add_section()

    tabela_resume.add_row("Total Geral", f"{valor_total:.2f}", f"100%")

    console = Console()
    console.print(tabela_resume)

if __name__ == "__main__":
    options()