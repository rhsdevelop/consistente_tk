import argparse
import sqlite3

from config import *
from forms import App, Menu
from migrations import data_update
from modules.forms import (BankForm, CategoriasForm, GoogleDriveConn,
                           ImportCsvForm, MainPanel, MovimentosForm,
                           ParceirosForm, UserForm)


def mainpanel():
    main = MainPanel(app, conn)
    main.grid()

def importcsvform():
    app.clear_mainframe()
    main = ImportCsvForm(app, conn)
    main.grid()

def googledriveform():
    app.clear_mainframe()
    main = GoogleDriveConn(app, conn)
    main.grid()

def bankform():
    app.clear_mainframe()
    main = BankForm(app, conn)
    main.grid()
    main.cmd_seek()

def categoriasform():
    app.clear_mainframe()
    main = CategoriasForm(app, conn)
    main.grid()
    main.cmd_seek()

def parceirosform():
    app.clear_mainframe()
    main = ParceirosForm(app, conn)
    main.grid()
    main.cmd_seek()

def userform():
    app.clear_mainframe()
    main = UserForm(app, conn)
    main.grid()
    main.cmd_seek()

def receberform():
    app.clear_mainframe()
    main = MovimentosForm(app, conn, tipo_form='rec')
    main.grid()
    main.cmd_seek()

def pagarform():
    app.clear_mainframe()
    main = MovimentosForm(app, conn, tipo_form='pag')
    main.grid()
    main.cmd_seek()

def importgoogle():
    main = GoogleDriveConn(app, conn)
    main.get_data()

def exportgoogle():
    main = GoogleDriveConn(app, conn)
    main.set_data()
    
def implement():
    app.clear_mainframe()
    print('ERRO: Não existe rotina!')

def clear():
    app.clear_mainframe()

if __name__ == '__main__':
    menu = Menu()
    menu.add_menu('Cadastros')
    menu.add_menu('Configurações')
    menu.add_menu('Backup')
    menu.add_option('Cadastros', 'Bancos', cmd=bankform)
    menu.add_option('Cadastros', 'Categorias', cmd=categoriasform)
    menu.add_option('Cadastros', 'Parceiros', cmd=parceirosform)
    menu.add_option('Cadastros', 'Usuários', cmd=userform)
    #menu.add_submenu('abrir', 'Cadastros', 'Abrir')
    #menu.add_option('abrir', 'Contato', cmd=implement)
    menu.add_option('Configurações', 'Importar CSV', cmd=importcsvform)
    menu.add_option('Configurações', 'Configurar conta Google Drive', cmd=googledriveform)
    menu.add_option('Backup', 'Enviar dados ao Google Drive', cmd=exportgoogle)
    menu.add_option('Backup', 'Receber dados do Google Drive', cmd=importgoogle)
    conn = sqlite3.connect(SQLITE_DB)
    c = conn.cursor()
    data_update(conn, c)
    app = App(title='Consistente - Gestão financeira', backcolor=BGCOLOR, mainmenu=menu)
    parser = argparse.ArgumentParser(description='Executa rotinas específicas.')
    parser.add_argument('cmd', nargs='?')
    args = parser.parse_args()
    if args.cmd:
        for i in dir():
            if args.cmd == i:
                eval('%s()' % i)
    else:
        mainpanel()
    app.run()
