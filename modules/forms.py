import csv
import datetime
import os
from tkinter import (Button, Checkbutton, Entry, Frame, Image, IntVar, Label,
                     Listbox, Text, messagebox, Toplevel)
from tkinter.filedialog import askopenfilename
from tkinter.ttk import Combobox, Scrollbar, Treeview

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from config import *
from forms import Constructor, Widgets
from modules.helpers import (GenerateFatura, Numbers, cmd, cmd_data, cmd_desc,
                             cmd_fat, date_in, date_out, lastdaymonth,
                             query_id, query_list)

TIPOS_MOV = ['Dinheiro em mãos', 'Conta Bancária', 'Cartão de Crédito', 'Cartão Pré pago']
TIPOS_CONTA = ['Conta Corrente', 'Poupança', 'CDB/Outras']
TIPOS_CATEG = ['Receita', 'Despesa', 'Transferência']
TIPOS_DOC = ['Pessoa Física', 'Pessoa Jurídica']
TIPOS_RELAC = ['Ambos', 'Cliente', 'Fornecedor']
d = datetime

class MainPanel:
    def __init__(self, instance, conn, saved={}):
        self.bg = BGFORM
        self.conn = conn
        self.instance = instance
        self.mainframe = instance.mainframe
        self.frame = Frame(self.mainframe, bd=1, bg=self.bg, relief='sunken')
        self.icons = {
            '0': ['Bancos', 'static/images/bancos.png', self.cmd_bank],
            '1': ['Parceiros', 'static/images/users.png', self.cmd_parceiro],
            '2': ['Contas à Receber', 'static/images/salary.png', self.cmd_receber],
            '3': ['Contas à Pagar', 'static/images/buy.png', self.cmd_pagar],
            '4': ['Cartões de crédito', 'static/images/creditcard.png', self.cmd_cred],
            '5': ['Transferências', 'static/images/transference.png', self.cmd_transf],
            '6': ['Movimento Diário', 'static/images/calendar.png', self.cmd_report],
            '7': ['Fluxo de Caixa', 'static/images/cashmachine.png', self.cmd_cashflow],
            '8': ['Despesas Categoria', 'static/images/pag-categorias.png', self.cmd_fechamento],
            '9': ['Despesas Parceiro', 'static/images/compras.png', self.teste],
        }

    def grid(self):
        #Label(self.mainframe, text='', width=10, bg=BGCOLOR).grid(row=0, column=0)
        Label(self.mainframe, text='MENU INICIAL', width=60, bg=BGCOLOR, font=('Arial Bold', 16)).grid(row=1, column=0)
        image = Widgets(self.frame).image
        self.frame.grid(row=2, column=0)
        Label(self.frame, text='\n', width=0, height=10, bg=self.bg).grid(row=0, column=0, rowspan=5)
        Label(self.frame, text='', width=10, bg=self.bg).grid(row=0, column=1)
        row = 2
        col = 0
        for item in self.icons:
            Label(self.frame, text=self.icons[item][0], width=17, bg=self.bg).grid(row=row, column=col)
            image(field='', textwidth=70, imagefile=self.icons[item][1], row=row - 1, col=col, bg=self.bg, imagewidth=(64, 64), cmd=self.icons[item][2])
            col += 1
            if col == 5:
                Label(self.frame, text='', width=10, bg=self.bg).grid(row=row + 1, column=1)
                col = 0
                row += 3
        image('', 400, 'static/images/finance.png', row + 1, 0, colspam=5, bg=self.bg, imagewidth=(190, 190), cmd=self.cmd_sobre)
        image('', 70, 'static/images/exit.png', row + 2, 4, bg=self.bg, imagewidth=(64, 64), cmd=self.cmd_quit)
        Label(self.frame, text='', width=10, bg=self.bg).grid(row=row + 3, column=0)

    def teste(self, event=None):
        print('Renan')

    def cmd_bank(self, event=None):
        self.instance.clear_mainframe()
        main = BankForm(self.instance, self.conn)
        main.grid()
        main.cmd_seek()

    def cmd_parceiro(self, event=None):
        self.instance.clear_mainframe()
        main = ParceirosForm(self.instance, self.conn)
        main.grid()
        main.cmd_seek()

    def cmd_receber(self, event=None):
        self.instance.clear_mainframe()
        main = MovimentosForm(self.instance, self.conn, tipo_form='rec')
        main.grid()
        main.cmd_seek()

    def cmd_pagar(self, event=None):
        self.instance.clear_mainframe()
        main = MovimentosForm(self.instance, self.conn, tipo_form='pag')
        main.grid()
        main.cmd_seek()

    def cmd_cred(self, event=None):
        self.instance.clear_mainframe()
        main = MovimentosForm(self.instance, self.conn, tipo_form='cred')
        main.grid()
        main.cmd_seek()

    def cmd_transf(self, event=None):
        self.instance.clear_mainframe()
        main = MovimentosForm(self.instance, self.conn, tipo_form='transf')
        main.grid()
        main.cmd_seek()

    def cmd_cashflow(self, event=None):
        self.instance.clear_mainframe()
        main = CashflowForm(self.instance, self.conn)
        main.grid()
        main.cmd_seek()

    def cmd_report(self, event=None):
        self.instance.clear_mainframe()
        main = ReportForm(self.instance, self.conn)
        main.grid()
        main.cmd_seek()

    def cmd_fechamento(self, event=None):
        self.instance.clear_mainframe()
        main = FechamentoForm(self.instance, self.conn)
        main.grid()
        main.cmd_seek()

    def cmd_quit(self, event=None):
        resp = messagebox.askyesno(title='Informação', message='Tem certeza de que deseja fechar o app Consistente?')
        if resp:
            messagebox.showinfo(title='Bye', message='Aguardamos seu retorno. Tchau!')
            self.instance.destroy()

    def cmd_sobre(self, event=None):
        self.instance.clear_mainframe()
        main = SobreForm(self.instance, self.conn)
        main.grid()


class SobreForm:
    def __init__(self, instance, conn):
        self.instance = instance
        self.conn = conn
        self.mainframe = instance.mainframe
        self.frame = Frame(self.mainframe, bd=1, relief='sunken', bg=BGFORM)
        self.labels = Frame(self.frame, bd=1, bg=BGFORM)
        self.image1 = Widgets(self.labels).image('', 0,'static/images/finance.png', 1, 1, bg=BGFORM, rowspan=5, imagewidth=(64, 64))
        text1 = 'Consistente - Gerenciamento Financeiro'
        text2 = 'Cuidando bem de seus recursos!'
        text3 = 'Versão 1.0'
        text4 = '(c) 2020 RHS Desenvolvimento'
        text5 = 'Responsável: Renan Hernandes de Souza'
        self.text1 = Label(self.labels, anchor='e', text=text1, bg=BGFORM, width=40)
        self.text2 = Label(self.labels, anchor='e', text=text2, bg=BGFORM, width=40)
        self.text3 = Label(self.labels, anchor='e', text=text3, bg=BGFORM, width=40)
        self.text4 = Label(self.labels, anchor='e', text=text4, bg=BGFORM, width=40)
        self.text5 = Label(self.labels, anchor='e', text=text5, bg=BGFORM, width=40)
        self.buttons = Frame(self.frame, bg=BGFORM, width=80)
        self.fechar = Button(self.buttons, text='Ok', width=20, command=self.cmd_fechar)
        self.fechar.focus()

    def grid(self):
        #Label(self.mainframe, text='', width=10, bg=BGCOLOR).grid(row=0, column=0)
        Label(self.mainframe, text='SOBRE', width=50, bg=BGCOLOR, font=('Arial Bold', 16)).grid(row=1, column=0)
        self.frame.grid(row=2, column=0)
        Label(self.frame, text='', bg=BGFORM, width=10).grid(row=0, column=1)
        Label(self.labels, text='\n', height=8, bg=BGFORM).grid(row=0, column=0, rowspan=6)
        self.labels.grid(row=1, column=1)
        self.text1.grid(row=1, column=2)
        self.text2.grid(row=2, column=2)
        self.text3.grid(row=3, column=2)
        self.text4.grid(row=4, column=2)
        self.text5.grid(row=5, column=2)
        self.buttons.grid(row=2, column=1)
        Label(self.buttons, text='', bg=BGFORM, width=50).grid(row=0, column=1)
        Label(self.buttons, text='\n', height=3, bg=BGFORM).grid(row=0, column=0, rowspan=2)
        self.fechar.grid(row=1, column=1)
        Label(self.frame, text='', bg=BGFORM, width=5).grid(row=3, column=0)
        Label(self.frame, text='', bg=BGFORM, width=5).grid(row=3, column=3)

    def cmd_fechar(self):
        self.instance.clear_mainframe()
        MainPanel(self.instance, self.conn).grid()


class ImportCsvForm:
    def __init__(self, instance, conn, saved={}, data=None):
        self.instance = instance
        self.mainframe = instance.mainframe
        self.conn = conn
        self.saved = saved
        self.data = data
        self.frame = Frame(self.mainframe, bd=1, relief='sunken', bg=BGFORM)
        self.buscar_arquivo = Button(self.frame, text='Procura arquivo CSV', width=20, command=self.cmd_buscar_arquivo)
        self.nome_l = Label(self.frame, anchor='e', text='Arquivo ', bg=BGFORM, width=15)
        self.nome = Entry(self.frame, width=40)
        query = self.conn.execute('SELECT name FROM sqlite_master WHERE type = "table" ORDER BY name')
        self.tables = []
        for i in query:
            if i[0] != 'sqlite_sequence':
                self.tables.append(i[0])
        self.table_l = Label(self.frame, anchor='e', text='Tabela ', bg=BGFORM, width=15)
        self.table = Combobox(self.frame, width=20, values=self.tables)
        self.fields_l = Label(self.frame, anchor='e', text='Fields para CSV ', bg=BGFORM, width=15)
        self.fields = Entry(self.frame, width=40)
        self.observacao_l = Label(self.frame, anchor='e', text='Cabeçalho ', bg=BGFORM, width=15)
        self.observacao = Label(self.frame, anchor='w', text='Estrutura da tabela', relief='sunken', justify='left', width=40)
        self.buttons = Frame(self.frame, bg=BGFORM, width=50)
        self.cancel = Button(self.buttons, text='Cancelar', width=10, command=self.cmd_cancel)
        self.confirm = Button(self.buttons, text='Importar dados', width=15, command=self.cmd_confirm)
        self.commit = Button(self.buttons, text='Commit', width=9, command=self.cmd_commit)
        self.table.bind("<FocusOut>", self.cmd_table)
        self.nome.focus()
    
    def grid(self):
        #Label(self.mainframe, text='', width=10, bg=BGCOLOR).grid(row=0, column=0)
        Label(self.mainframe, text='IMPORTAR DADOS VIA ARQUIVOS CSV', width=60, bg=BGCOLOR, font=('Arial Bold', 16)).grid(row=1, column=0)
        self.frame.grid(row=2, column=0)
        Label(self.frame, text='\n', width=5, height=18, bg=BGFORM).grid(row=0, column=0, rowspan=7)
        Label(self.frame, text='', bg=BGFORM, width=10).grid(row=0, column=1)
        self.buscar_arquivo.grid(row=1, column=1, columnspan=2)
        self.nome_l.grid(row=2, column=1)
        self.nome.grid(row=2, column=2, sticky='w')
        self.table_l.grid(row=3, column=1)
        self.table.grid(row=3, column=2, sticky='w')
        self.fields_l.grid(row=4, column=1)
        self.fields.grid(row=4, column=2, sticky='w')
        self.observacao_l.grid(row=5, column=1)
        self.observacao.grid(row=5, column=2, sticky='w')
        self.buttons.grid(row=6, column=1, columnspan=2)
        Label(self.buttons, text='', bg=BGFORM, width=60).grid(row=0, column=1, columnspan=3)
        self.cancel.grid(row=1, column=1)
        self.confirm.grid(row=1, column=2)
        self.commit.grid(row=1, column=3)
        Label(self.frame, text='', bg=BGFORM, width=5).grid(row=7, column=1)
        Label(self.frame, text='', bg=BGFORM, width=5).grid(row=7, column=3)

    def cmd_buscar_arquivo(self):
        filename = askopenfilename(
            title='Importar arquivo CSV para tabela local',
            filetypes=[("Planilhas em CSV", "*.csv")]
        )
        if filename:
            self.nome.delete(0, 'end')
            self.nome.insert(0, filename)

    def cmd_table(self, event=None):
        if self.table.get() and self.table.get() not in self.tables:
            for i in self.tables:
                if self.table.get() in i:
                    self.table.delete(0, 'end')
                    self.table.insert(0, i)
                    self.observacao['text'] = ''
                    query = self.conn.execute('PRAGMA TABLE_INFO(%s)' % self.table.get())
                    itens = []
                    detail = []
                    for i in query:
                        itens.append(i[1])
                        detail.append('%s - %s: %s' % (i[0], i[1], i[2]))
                    self.fields.delete(0, 'end')
                    self.fields.insert(0, ';'.join(itens[1:]))
                    self.observacao['text'] = '\n'.join(detail)
                    break
            if self.table.get() not in self.tables:
                self.observacao['text'] = 'Estrutura da tabela'
                self.fields.delete(0, 'end')
                self.table.delete(0, 'end')
        elif self.table.get() in self.tables:
            self.observacao['text'] = ''
            query = self.conn.execute('PRAGMA TABLE_INFO(%s)' % self.table.get())
            itens = []
            detail = []
            for i in query:
                itens.append(i[1])
                detail.append('%s - %s: %s' % (i[0], i[1], i[2]))
            self.fields.delete(0, 'end')
            self.fields.insert(0, ';'.join(itens[1:]))
            self.observacao['text'] = '\n'.join(detail)

    def cmd_cancel(self):
        self.instance.clear_mainframe()
        MainPanel(self.instance, self.conn).grid()

    def cmd_confirm(self):
        filename = self.nome.get()
        table = Constructor('consistente.db', self.table.get(), self.table.get())
        f = open(filename, 'r')
        data = csv.DictReader(f, delimiter=';')
        c = self.conn.cursor()
        try:
            for i in data:
                values = []
                for item in table.fields[1:]:
                    if table.dict_fields[item] in ['VARCHAR']:
                        values.append('"%s"' % i[item])
                    else:
                        values.append('%s' % i[item])
                cmd = 'INSERT INTO %s (%s) VALUES (%s)' % (table.table, ', '.join(table.fields[1:]), ', '.join(values))
                c.execute(cmd)
            messagebox.showinfo(title='Aviso', message='Dados subiram com sucesso. Verifique e dê o commit para aceitar as mudanças.')
        except:
            messagebox.showerror(title='Aviso', message='Verifique seu arquivo. Houve alguma falha. Sugerido abrir e fechar o programa.')

    def cmd_commit(self):
        if messagebox.askokcancel(title='Empenhar dados', message='Deseja empenhar dados em definitivo no app?'):
            self.conn.commit()


class GoogleDriveConn:
    def __init__(self, instance, conn, saved={}, data=None):
        self.instance = instance
        self.mainframe = instance.mainframe
        self.conn = conn
        self.saved = saved
        self.data = data
        self.frame = Frame(self.mainframe, bd=1, relief='sunken', bg=BGFORM)
        text = 'Esse formulário permite configurar um backup automático com sua conta Google.\n\n'\
            'O primeiro botão permite configurar uma conexão. O browser será aberto e o usuário\n'\
            'deve estar logado e conceder a autorização para que o app Consistente faça a integração.\n\n'\
            'O segundo botão remove a conexão estabelecida. Caso o usuário queira fazer backup\n'\
            'usando uma conta do Google, deverá usar o primeiro botão novamente.'
        self.nome = Label(self.frame, anchor='e', text=text, bg=BGFORM, width=80)
        self.buttons = Frame(self.frame, bg=BGFORM, width=80)
        self.executar = Button(self.buttons, text='Configurar/trocar conexão com conta Google', width=40, command=self.cmd_executar)
        self.limpar = Button(self.buttons, text='Remover conexão com conta Google', width=40, command=self.cmd_limpar)
        self.fechar = Button(self.buttons, text='Sair da tela de configuração', width=40, command=self.cmd_fechar)
        #self.cancel = Button(self.buttons, text='Cancelar', width=10, command=self.cmd_cancel)
        #self.confirm = Button(self.buttons, text='Importar dados', width=15, command=self.cmd_confirm)
        #self.commit = Button(self.buttons, text='Commit', width=9, command=self.cmd_commit)
        self.executar.focus()

    def grid(self):
        #Label(self.mainframe, text='', width=10, bg=BGCOLOR).grid(row=0, column=0)
        Label(self.mainframe, text='CONFIGURAR BACKUP GOOGLE DRIVE', width=60, bg=BGCOLOR, font=('Arial Bold', 16)).grid(row=1, column=0)
        self.frame.grid(row=2, column=0)
        Label(self.frame, text='\n', height=18, bg=BGFORM).grid(row=0, column=0, rowspan=3)
        Label(self.frame, text='', bg=BGFORM, width=10).grid(row=0, column=1)
        self.nome.grid(row=1, column=1)
        self.buttons.grid(row=2, column=1)
        Label(self.buttons, text='', bg=BGFORM, width=80).grid(row=0, column=1)
        Label(self.buttons, text='\n', height=6, bg=BGFORM).grid(row=0, column=0, rowspan=3)
        self.executar.grid(row=1, column=1)
        self.limpar.grid(row=2, column=1)
        self.fechar.grid(row=3, column=1)
        Label(self.frame, text='', bg=BGFORM, width=5).grid(row=3, column=0)
        Label(self.frame, text='', bg=BGFORM, width=5).grid(row=3, column=3)

    def cmd_executar(self):
        c = self.conn.cursor()
        if os.path.exists('googledrive/consistente.dat'):
            c.execute('SELECT * FROM Drive WHERE Arquivo = "consistente.db"')
            fields = c.fetchone()
            if fields:
                messagebox.showinfo('Configurar conexão', 'Você já está vinculado a uma conta Google. Se deseja usar uma configuração em nova conta, primeiro remova a conexão já existente.', parent=self.form_child)
        else:
            try:
                if os.path.exists('googledrive'):
                    pass
                else:
                    os.mkdir('googledrive')
                gauth = GoogleAuth()
                gauth.LocalWebserverAuth()
                drive = GoogleDrive(gauth)
                file1 = drive.CreateFile()  # Initialize GoogleDriveFile instance with file id
                file1.SetContentFile('consistente.db') # Read file and set it as a content of this instance.
                file1.Upload() # Upload it
                commands = 'INSERT OR REPLACE INTO drive (arquivo, idgoogle) VALUES ('
                commands += '"consistente.db", "' + file1['id'] + '")'
                c.execute(commands)
                self.conn.commit()
                file1 = drive.CreateFile({'id': file1['id']})  # Initialize GoogleDriveFile instance with file id
                file1.SetContentFile('consistente.db')            # Download file as 'catlove.png'
                file1.Upload()                            # Upload it
                messagebox.showinfo('Configurar conexão', 'Configuração realizada com sucesso. Seus dados podem ser sincronizados com o Google Drive a qualquer momento.')
            except:
                messagebox.showerror('Configurar conexão', 'A configuração não foi realizada. Verifique se você está conectado à internet e se concedeu autorização no seu navegador.')

    def cmd_limpar(self):
        c = self.conn.cursor()
        if os.path.exists('googledrive/consistente.dat'):
            c.execute('SELECT * FROM drive WHERE arquivo = "consistente.db"')
            fields = c.fetchone()
            if fields:
                gauth = GoogleAuth()
                gauth.LocalWebserverAuth()
                drive = GoogleDrive(gauth)
                idfile = fields[2]
                file1 = drive.CreateFile({'id': idfile})  # Initialize GoogleDriveFile instance with file id
                file1.Delete()            # Download file as 'catlove.png'
                c.execute('DELETE FROM drive WHERE arquivo = "consistente.db"')
                self.conn.commit()
                os.remove('googledrive/consistente.dat')
                messagebox.showinfo('Configurar conexão', 'Seu vínculo de backup foi desabilitado e seu arquivo backup em nuvem foi apagado.')
        else:
            messagebox.showwarning('Configurar conexão', 'Ainda não há backup configurado para ser apagado.')

    def cmd_fechar(self):
        self.instance.clear_mainframe()
        MainPanel(self.instance, self.conn).grid()

    def get_data(self):
        c = self.conn.cursor()
        if messagebox.askyesno(parent=self.instance.root,
                            title="Importar registros do servidor",
                            message='Tem certeza que deseja importar os dados da última atualização do servidor? \
                                        Não será possível desfazer a operação!'):
            if 1==1:
                if os.path.exists('googledrive/consistente.dat'):
                    c.execute('SELECT * FROM drive WHERE arquivo = "consistente.db"')
                    fields = c.fetchone()
                    if fields:
                        gauth = GoogleAuth()
                        gauth.LocalWebserverAuth()
                        drive = GoogleDrive(gauth)
                        namefile = fields[1]
                        idfile = fields[2]
                        file1 = drive.CreateFile({'id': idfile})  # Initialize GoogleDriveFile instance with file id
                        file1.GetContentFile(namefile)            # Download file as 'catlove.png'
                        lastupdate = file1['modifiedDate'][0:10]
                        lastupdate = lastupdate.split('-')
                        lastupdate = [int(row) for row in lastupdate]
                        lasthour = file1['modifiedDate'][11:16]
                        lasthour = lasthour.split(':')
                        lasthour = [int(row) for row in lasthour]
                        international = d.datetime(lastupdate[0], lastupdate[1], lastupdate[2], lasthour[0], lasthour[1])
                        brasildate = international - d.timedelta(hours=3)
                        lastupdate = brasildate.strftime('%d/%m/%Y')
                        lasthour = brasildate.strftime('%H:%M')
                        message = 'Banco de dados sincronizado com atualização realizada em ' + lastupdate + ' às ' + lasthour + '.'
                        messagebox.showinfo(title="Receber dados de sua conta Google",
                                            message=message)
                else:
                    messagebox.showerror(title="Receber dados de sua conta Google",
                                        message="Há um problema de configuração que está impedindo o recebimento dos dados.")
            else:
                messagebox.showerror(title="Receber dados de sua conta Google",
                                         message="Erro de atualização! Verifique se você está conectado à internet.")
        else:
            pass

    def set_data(self):
        c = self.conn.cursor()
        if messagebox.askyesno(title="Enviar dados para sua conta",
                               message='Tem certeza que deseja exportar os dados em seu aplicativo para o servidor? \
                                        Não será possível desfazer a operação!'):
            try:
                gauth = GoogleAuth()
                gauth.LocalWebserverAuth()
                drive = GoogleDrive(gauth)
                c.execute('SELECT * FROM drive WHERE arquivo = "consistente.db"')
                fields = c.fetchone()
                if fields and os.path.exists('googledrive/consistente.dat'):
                    namefile = fields[1]
                    idfile = fields[2]
                    file1 = drive.CreateFile({'id': idfile})  # Initialize GoogleDriveFile instance with file id
                    file1.SetContentFile(namefile)            # Download file as 'catlove.png'
                    file1.Upload()                            # Upload it
                else:
                    messagebox.showerror(title="Enviar dados para sua conta",
                                        message="Há um problema de configuração que está impedindo o recebimento dos dados.")
            except:
                messagebox.showerror(title="Enviar dados para sua conta",
                                    message="Erro de atualização! Verifique se você está conectado à internet.")
            messagebox.showinfo(title="Enviar dados para sua conta",
                                message="Atividade concluída!")
        else:
            pass


class BankForm:
    def __init__(self, instance, conn, saved={}):
        self.conn = conn
        self.instance = instance
        self.mainframe = instance.mainframe
        self.frame = Frame(self.mainframe, bd=1, bg=BGFORM, relief='sunken')
        self.nome_l = Label(self.frame, anchor='e', text='Nome do banco ', bg=BGFORM, width=15)
        self.nome = Entry(self.frame, width=15)
        self.tipo_l = Label(self.frame, anchor='e', text='Tipo de movimento ', bg=BGFORM, width=20)
        self.tipo = Combobox(self.frame, width=15, values=TIPOS_MOV)
        self.fr1 = Frame(self.frame, bd=1, relief='sunken')
        self.fr1.configure(height=200, width=550)
        self.fr1.grid_propagate(0)
        self.fr1_place = Frame(self.fr1)
        self.table1 = Treeview(self.fr1_place, height=10)
        self.sb_y = Scrollbar(self.fr1_place, orient="vertical", command=self.table1.yview)
        self.sb_x = Scrollbar(self.fr1_place, orient="horizontal", command=self.table1.xview)
        self.table1.configure(yscroll=self.sb_y.set, xscroll=self.sb_x.set)
        self.buttons = Frame(self.frame, bg=BGFORM, width=30)
        self.new = Button(self.buttons, text='Novo', width=10, command=self.cmd_new)
        self.edit = Button(self.buttons, text='Editar', width=12, command=self.cmd_edit)
        self.quit = Button(self.buttons, text='Sair', width=10, command=self.cmd_quit)
        if 'nome' in saved and saved['nome']: self.nome.insert('end', saved['nome'])
        if 'tipo' in saved and saved['tipo']: self.tipo.insert('end', saved['tipo'])
        self.nome.bind("<FocusOut>", self.cmd_seek)
        self.tipo.bind("<FocusOut>", self.cmd_tipos)
        self.nome.focus()
    
    def grid(self):
        #Label(self.mainframe, text='', width=10, bg=BGCOLOR).grid(row=0, column=0)
        Label(self.mainframe, text='CADASTRO DE BANCOS', width=60, bg=BGCOLOR, font=('Arial Bold', 16)).grid(row=1, column=0)
        self.frame.grid(row=2, column=0)
        Label(self.frame, text='\n', width=0, height=10, bg=BGFORM).grid(row=0, column=0, rowspan=5)
        Label(self.frame, text='', width=10, bg=BGFORM).grid(row=0, column=1)
        self.nome_l.grid(row=1, column=1)
        self.nome.grid(row=1, column=2)
        self.tipo_l.grid(row=1, column=3)
        self.tipo.grid(row=1, column=4)
        Label(self.frame, text='', width=5, bg=BGFORM).grid(row=1, column=5)
        Label(self.frame, text='', width=5, bg=BGFORM).grid(row=2, column=1)
        self.fr1.grid(row=3, column=1, columnspan=5)
        self.fr1_place.place(bordermode='outside', height=200, width=550)
        self.sb_y.pack(side="right", fill='y')
        self.sb_x.pack(side="bottom", fill='x')
        self.table1.pack(expand=1)
        self.buttons.grid(row=4, column=1, columnspan=5)
        Label(self.buttons, text='', width=50, bg=BGFORM).grid(row=0, column=1, columnspan=3)
        self.new.grid(row=1, column=1)
        self.edit.grid(row=1, column=2)
        self.quit.grid(row=1, column=3)
        Label(self.frame, text='', width=5, bg=BGFORM).grid(row=5, column=1)
        Label(self.frame, text='', width=5, bg=BGFORM).grid(row=5, column=3)

    def data(self, filter='', order='nomebanco'):
        c = self.conn.cursor()
        cmd = 'SELECT id, nomebanco, tipomov, numero, diavenc FROM bancos'
        if filter: cmd += filter
        if order:
            cmd += ' ORDER BY %s' % order
        c.execute(cmd)
        dados = c.fetchall()
        _dados = []
        for i in dados:
            day = i[4]
            if not day:
                day = ''
            _dados.append([i[0], i[1], TIPOS_MOV[i[2]], i[3], day])
        dados = _dados
        # Preenche a tabela
        self.table1['columns'] = ['Nome Banco', 'Tipo', 'Número', 'Venc']
        self.table1.heading('#0', text='Id', anchor='center')
        self.table1.column('#0', anchor='w', width=40)
        self.table1.delete(*self.table1.get_children())
        self.table1.tag_configure('total', background='green yellow')
        columns = {
            'Nome Banco': 157, 'Tipo': 145, 'Número': 140, 'Venc': 50
        }
        for row in ['Nome Banco', 'Tipo', 'Número', 'Venc']:
            self.table1.heading(
                row, 
                text=row, 
                anchor='center' 
            )
            anchor = 'w'
            self.table1.column(row, anchor=anchor, width=columns[row])
        index = 1
        for row in dados:
            self.table1.insert('', 'end', text=str(row[0]), values=row[1:])
            index += 1

    def cmd_tipos(self, event=None):
        if self.tipo.get() and self.tipo.get() not in TIPOS_MOV:
            for i in TIPOS_MOV:
                if self.tipo.get().lower() in i.lower():
                    self.tipo.delete(0, 'end')
                    self.tipo.insert(0, i)
                    break
            if self.tipo.get() not in TIPOS_MOV:
                self.tipo.delete(0, 'end')
        self.cmd_seek()

    def cmd_seek(self, event=None):
        filt = ''
        pre = 'WHERE'
        if self.nome.get():
            filt += ' %s nomebanco LIKE "%s%s%s"' % (pre, "%", self.nome.get(), "%")
            pre = 'AND'
        if self.tipo.get():
            filt += ' %s tipomov = %s' % (pre, TIPOS_MOV.index(self.tipo.get()))
        self.data(filter=filt)
        
    def cmd_new(self):
        saved = {}
        if self.nome.get():
            saved['nome'] = self.nome.get()
        if self.tipo.get():
            saved['tipo'] = self.tipo.get()
        self.instance.clear_mainframe()
        main = BankEditForm(self.instance, self.conn, saved=saved)
        main.grid()

    def cmd_edit(self, event=None):
        saved = {}
        if self.nome.get():
            saved['nome'] = self.nome.get()
        if self.tipo.get():
            saved['tipo'] = self.tipo.get()
        try:
            region = self.table1.identify("region", event.x, event.y)
        except:
            region = 'cell'
        #column = form.fields['table'].identify("column", event.x, event.y)
        #cell = form.fields['table'].identify("row", event.x, event.y)
        _id = None
        if region == "cell":
            if self.table1.selection():
                for i in self.table1.selection():
                    _id = str(self.table1.item(i, 'text'))
                    self.instance.clear_mainframe()
                    main = BankEditForm(self.instance, self.conn, saved=saved, data=_id)
                    main.grid()
            else:
                messagebox.showerror(title='Atenção', message='Selecione um usuário para a edição.')

    def cmd_quit(self):
        self.instance.clear_mainframe()
        MainPanel(self.instance, self.conn).grid()


class BankEditForm:
    def __init__(self, instance, conn, saved={}, data=None):
        self.instance = instance
        self.mainframe = instance.mainframe
        self.conn = conn
        self.saved = saved
        self.data = data
        self.frame = Frame(self.mainframe, bd=1, relief='sunken', bg=BGFORM)
        self.datacadastro_l = Label(self.frame, anchor='e', text='Data Cadastro ', bg=BGFORM, width=25)
        self.datacadastro = Entry(self.frame, width=10)
        self.nomebanco_l = Label(self.frame, anchor='e', text='Nome do banco ', bg=BGFORM, width=25)
        self.nomebanco = Entry(self.frame, width=20)
        self.tipomov_l = Label(self.frame, anchor='e', text='Tipo de banco ', bg=BGFORM, width=25)
        self.tipomov = Combobox(self.frame, width=15, values=TIPOS_MOV)
        self.numero_l = Label(self.frame, anchor='e', text='Número do cartão ', bg=BGFORM, width=25)
        self.numero = Entry(self.frame, width=20)
        self.diavenc_l = Label(self.frame, anchor='e', text='Dia vencimento fatura ', bg=BGFORM, width=25)
        self.diavenc = Entry(self.frame, width=3)
        self.gerafatura_l = Label(self.frame, anchor='e', text='Gera fatura ', bg=BGFORM, width=25)
        self.gerafatura_v = IntVar()
        self.gerafatura = Checkbutton(self.frame, text='Sim  ', bg=BGFORM, width=5, variable=self.gerafatura_v)
        self.agencia_l = Label(self.frame, anchor='e', text='Agência ', bg=BGFORM, width=25)
        self.agencia = Entry(self.frame, width=7)
        self.conta_l = Label(self.frame, anchor='e', text='Conta ', bg=BGFORM, width=25)
        self.conta = Entry(self.frame, width=11)
        self.tipoconta_l = Label(self.frame, anchor='e', text='Tipo conta ', bg=BGFORM, width=25)
        self.tipoconta = Combobox(self.frame, width=15, values=TIPOS_CONTA)
        self.usuario_l = Label(self.frame, anchor='e', text='Usuário ', bg=BGFORM, width=25)
        self.usuario = Entry(self.frame, width=20)
        self.buttons = Frame(self.frame, bg=BGFORM, width=30)
        self.cancel = Button(self.buttons, text='Cancelar', width=10, command=self.cmd_cancel)
        self.confirm = Button(self.buttons, text='Confirmar', width=10, command=self.cmd_confirm)
        self.tipomov.bind("<FocusOut>", self.cmd_tipomov)
        self.tipoconta.bind("<FocusOut>", self.cmd_tipoconta)
        if self.data:
            self.fill_data()
        else:
            self.datacadastro.insert(0, datetime.date.today().strftime('%d/%m/%Y'))
            self.usuario.insert(0, '1')
        self.nomebanco.focus()
        self.usuario['state'] = 'disabled'
    
    def grid(self):
        #Label(self.mainframe, text='', width=10, bg=BGCOLOR).grid(row=0, column=0)
        Label(self.mainframe, text='EDIÇÃO DE BANCO', width=60, bg=BGCOLOR, font=('Arial Bold', 16)).grid(row=1, column=0)
        self.frame.grid(row=2, column=0)
        Label(self.frame, text='\n', width=5, height=18, bg=BGFORM).grid(row=0, column=0, rowspan=11)
        Label(self.frame, text='', width=10, bg=BGFORM).grid(row=0, column=1)
        self.datacadastro_l.grid(row=1, column=1)
        self.datacadastro.grid(row=1, column=2, sticky='w')
        self.nomebanco_l.grid(row=2, column=1)
        self.nomebanco.grid(row=2, column=2, sticky='w')
        self.tipomov_l.grid(row=3, column=1)
        self.tipomov.grid(row=3, column=2, sticky='w')
        self.diavenc_l.grid(row=4, column=1)
        self.diavenc.grid(row=4, column=2, sticky='w')
        self.gerafatura_l.grid(row=5, column=1)
        self.gerafatura.grid(row=5, column=2, sticky='w')
        self.agencia_l.grid(row=6, column=1)
        self.agencia.grid(row=6, column=2, sticky='w')
        self.conta_l.grid(row=7, column=1)
        self.conta.grid(row=7, column=2, sticky='w')
        self.tipoconta_l.grid(row=8, column=1)
        self.tipoconta.grid(row=8, column=2, sticky='w')
        self.usuario_l.grid(row=9, column=1)
        self.usuario.grid(row=9, column=2, sticky='w')
        self.buttons.grid(row=10, column=1, columnspan=2)
        Label(self.buttons, text='', bg=BGFORM, width=30).grid(row=0, column=1, columnspan=2)
        self.cancel.grid(row=1, column=1)
        self.confirm.grid(row=1, column=2)
        Label(self.frame, text='', bg=BGFORM, width=5).grid(row=11, column=1)
        Label(self.frame, text='', bg=BGFORM, width=5).grid(row=11, column=3)

    def fill_data(self):
        c = self.conn.cursor()
        c.execute('SELECT datacadastro, nomebanco, tipomov, numero, diavenc, gerafatura, agencia, conta, tipoconta, usuario FROM bancos WHERE id = %s' % self.data)
        data = c.fetchone()
        self.datacadastro.insert(0, datetime.datetime.strptime(data[0], '%Y-%m-%d').strftime('%d/%m/%Y'))
        self.nomebanco.insert(0, data[1])
        self.tipomov.insert(0, TIPOS_MOV[data[2]])
        self.numero.insert(0, data[3])
        field = data[4]
        if not field:
            field = ''
        self.diavenc.insert(0, str(field))
        if data[5]:
            self.gerafatura_v.set(1)
        self.agencia.insert(0, data[6])
        self.conta.insert(0, data[7])
        self.tipoconta.insert(0, TIPOS_CONTA[data[8]])
        usuario = data[9]
        if not usuario:
            usuario = 1
        self.usuario.insert(0, str(usuario))

    def cmd_tipomov(self, event=None):
        if self.tipomov.get() and self.tipomov.get() not in TIPOS_MOV:
            for i in TIPOS_MOV:
                if self.tipomov.get().lower() in i.lower():
                    self.tipomov.delete(0, 'end')
                    self.tipomov.insert(0, i)
                    break
            if self.tipomov.get() not in TIPOS_MOV:
                self.tipomov.delete(0, 'end')

    def cmd_tipoconta(self, event=None):
        if self.tipoconta.get() and self.tipoconta.get() not in TIPOS_CONTA:
            for i in TIPOS_CONTA:
                if self.tipoconta.get().lower() in i.lower():
                    self.tipoconta.delete(0, 'end')
                    self.tipoconta.insert(0, i)
                    break
            if self.tipoconta.get() not in TIPOS_CONTA:
                self.tipoconta.delete(0, 'end')

    def cmd_cancel(self):
        self.instance.clear_mainframe()
        main = BankForm(self.instance, self.conn, saved=self.saved)
        main.grid()
        main.cmd_seek()

    def cmd_confirm(self):
        if self.nomebanco.get() and self.tipomov.get():
            resp = messagebox.askyesno(title='Confirmação', message='Tem certeza que deseja confirmar os dados?')            
            if resp:
                c = self.conn.cursor()
                diavenc = self.diavenc.get()
                if not diavenc:
                    diavenc = '0'
                if not self.data:
                    cmd = '''INSERT INTO bancos 
                    (datacadastro, nomebanco, tipomov, numero, diavenc, gerafatura, agencia, conta, tipoconta, usuario)
                    VALUES ("%s", "%s", %s, "%s", %s, %s, "%s", "%s", %s, %s)''' % (
                        datetime.datetime.strptime(self.datacadastro.get(), '%d/%m/%Y').strftime('%Y-%m-%d'),
                        self.nomebanco.get(), TIPOS_MOV.index(self.tipomov.get()), self.numero.get(),
                        diavenc, self.gerafatura_v.get(), self.agencia.get(), self.conta.get(),
                        TIPOS_CONTA.index(self.tipoconta.get()), self.usuario.get()
                    )
                    c.execute(cmd)
                else:
                    cmd = '''UPDATE bancos
                    SET datacadastro = "%s", nomebanco = "%s", tipomov = %s, numero = "%s", diavenc = %s,
                    gerafatura = %s, agencia = "%s", conta = "%s", tipoconta = %s, usuario = %s
                    WHERE id = %s''' % (
                        datetime.datetime.strptime(self.datacadastro.get(), '%d/%m/%Y').strftime('%Y-%m-%d'),
                        self.nomebanco.get(), TIPOS_MOV.index(self.tipomov.get()), self.numero.get(),
                        diavenc, self.gerafatura_v.get(), self.agencia.get(), self.conta.get(),
                        TIPOS_CONTA.index(self.tipoconta.get()), self.usuario.get(), self.data
                    )
                    c.execute(cmd)
                self.conn.commit()
                messagebox.showinfo('Informação', 'Dados atualizados com sucesso!')
                self.instance.clear_mainframe()
                main = BankForm(self.instance, self.conn, saved=self.saved)
                main.grid()
                main.cmd_seek()
        else:
            messagebox.showerror(title='Aviso', message='Não é possível atualizar. Verifique os dados preenchidos.')


class CategoriasForm:
    # Objetivo: 
    def __init__(self, instance, conn, saved={}):
        self.conn = conn
        self.instance = instance
        self.mainframe = instance.mainframe
        self.frame = Frame(self.mainframe, bd=1, bg=BGFORM, relief='sunken')
        self.filter1_l = Label(self.frame, anchor='e', text='Filtro ', bg=BGFORM, width=10)
        self.filter1 = Entry(self.frame, width=20)
        self.filter1.bind("<FocusOut>", self.cmd_seek)
        self.fr1 = Frame(self.frame, bd=1, bg=BGFORM, relief='sunken')
        self.fr1.configure(height=200, width=400)
        self.fr1.grid_propagate(0)
        self.fr1_place = Frame(self.fr1)
        self.table1 = Treeview(self.fr1_place, height=10)
        self.sb_y = Scrollbar(self.fr1_place, orient="vertical", command=self.table1.yview)
        self.sb_x = Scrollbar(self.fr1_place, orient="horizontal", command=self.table1.xview)
        self.table1.configure(yscroll=self.sb_y.set, xscroll=self.sb_x.set)
        self.buttons = Frame(self.frame, bg=BGFORM, width=30)
        self.new = Button(self.buttons, text='Novo', width=10, command=self.cmd_new)
        self.edit = Button(self.buttons, text='Editar', width=12, command=self.cmd_edit)
        self.quit = Button(self.buttons, text='Sair', width=10, command=self.cmd_quit)
        if 'filter1' in saved and saved['filter1']: self.filter1.insert('end', saved['filter1'])
        self.filter1.focus()

    def grid(self):
        #Label(self.mainframe, text='', width=10, bg=BGCOLOR).grid(row=0, column=0)
        Label(self.mainframe, text='CADASTRO DE CATEGORIAS', width=60, bg=BGCOLOR, font=('Arial Bold', 16)).grid(row=1, column=0)
        self.frame.grid(row=2, column=0)
        Label(self.frame, text='\n', width=5, height=10, bg=BGFORM).grid(row=0, column=0, rowspan=5) # remover espaço para Enter.
        Label(self.frame, text='', bg=BGFORM, width=10).grid(row=0, column=1)
        self.filter1_l.grid(row=1, column=1)
        self.filter1.grid(row=1, column=2)
        Label(self.frame, text='', bg=BGFORM, width=5).grid(row=2, column=1)
        self.fr1.grid(row=3, column=1, columnspan=2, stick='w')
        self.fr1_place.place(bordermode='outside', height=200, width=400)
        self.sb_y.pack(side="right", fill='y')
        self.sb_x.pack(side="bottom", fill='x')
        self.table1.pack(expand=1)
        self.buttons.grid(row=4, column=1, columnspan=2)
        Label(self.buttons, text='', bg=BGFORM, width=50).grid(row=0, column=1, columnspan=3)
        self.new.grid(row=1, column=1)
        self.edit.grid(row=1, column=2)
        self.quit.grid(row=1, column=3)
        Label(self.frame, text='', bg=BGFORM, width=5).grid(row=5, column=1)
        Label(self.frame, text='', bg=BGFORM, width=5).grid(row=5, column=3)

    def data(self, filter='', order=''):
        c = self.conn.cursor()
        cmd = 'SELECT id, categoria, tipomov, classifica FROM categorias'
        if filter: cmd += filter
        if order:
            cmd += ' ORDER BY %s' % order
        c.execute(cmd)
        dados = c.fetchall()
        _dados = []
        consta = 'Não', 'Sim'
        for i in dados:
            _dados.append([i[0], i[1], TIPOS_CATEG[i[2]], consta[i[3]]])
        dados = _dados
        # Preenche a tabela
        self.table1['columns'] = ['Categoria', 'Tipo', 'Consta']
        self.table1.heading('#0', text='Id', anchor='center')
        self.table1.column('#0', anchor='w', width=60)
        self.table1.delete(*self.table1.get_children())
        self.table1.tag_configure('total', background='green yellow')
        columns = {
            'id': 60, 'Categoria': 181, 'Tipo': 80, 'Consta': 60
        }
        for row in ['Categoria', 'Tipo', 'Consta']:
            self.table1.heading(
                row, 
                text=row, 
                anchor='center' 
            )
            anchor = 'w'
            self.table1.column(row, anchor=anchor, width=columns[row])
        index = 1
        for row in dados:
            self.table1.insert('', 'end', text=str(row[0]), values=row[1:])
            index += 1

    def cmd_seek(self, event=None):
        # Esse código precisa ser ajustado de acordo com os fields do filtro.
        filt = ''
        pre = 'WHERE'
        if self.filter1.get():
            filt += ' %s filter1 LIKE "%s%s%s"' % (pre, "%", self.filter1.get(), "%")
            pre = 'AND'
        #if self.filter2.get():
        #    filt += ' %s filter2 = %s' % (pre, self.filter2.get())
        self.data(filter=filt)
        
    def cmd_new(self):
        saved = {}
        if self.filter1.get():
            saved['filter1'] = self.filter1.get()
        #if self.filter2.get():
        #    saved['filter2'] = self.filter2.get()
        self.instance.clear_mainframe()
        main = CategoriasEditForm(self.instance, self.conn, saved=saved)
        main.grid()

    def cmd_edit(self, event=None):
        saved = {}
        if self.filter1.get():
            saved['filter1'] = self.filter1.get()
        #if self.filter2.get():
        #    saved['filter2'] = self.filter2.get()
        try:
            region = self.table1.identify("region", event.x, event.y)
        except:
            region = 'cell'
        #column = form.fields['table'].identify("column", event.x, event.y)
        #cell = form.fields['table'].identify("row", event.x, event.y)
        _id = None
        if region == "cell":
            if self.table1.selection():
                for i in self.table1.selection():
                    _id = str(self.table1.item(i, 'text'))
                    self.instance.clear_mainframe()
                    main = CategoriasEditForm(self.instance, self.conn, saved=saved, data=_id)
                    main.grid()
            else:
                messagebox.showerror(title='Atenção', message='Selecione um registro para a edição.')

    def cmd_quit(self):
        self.instance.clear_mainframe()
        MainPanel(self.instance, self.conn).grid()

        
class CategoriasEditForm:
    def __init__(self, instance, conn, saved={}, data=None):
        self.instance = instance
        self.mainframe = instance.mainframe
        self.conn = conn
        self.saved = saved
        self.data = data
        self.frame = Frame(self.mainframe, bd=1, relief='sunken', bg=BGFORM)
        self.id_l = Label(self.frame, anchor='e', text='Id ', bg=BGFORM, width=18)
        self.id = Entry(self.frame, width=20)
        self.categoria_l = Label(self.frame, anchor='e', text='Categoria ', bg=BGFORM, width=18)
        self.categoria = Entry(self.frame, width=20)
        self.tipomov_l = Label(self.frame, anchor='e', text='Tipomov ', bg=BGFORM, width=18)
        self.tipomov = Combobox(self.frame, width=8, values=TIPOS_CATEG)
        self.classifica_l = Label(self.frame, anchor='e', text='Contempla no painel ', bg=BGFORM, width=18)
        self.classifica_v = IntVar()
        self.classifica = Checkbutton(self.frame, text='Sim  ', bg=BGFORM, width=5, variable=self.classifica_v)
        self.usuario_l = Label(self.frame, anchor='e', text='Usuario ', bg=BGFORM, width=18)
        self.usuario = Entry(self.frame, width=20)
        self.buttons = Frame(self.frame, bg=BGFORM, width=30)
        self.cancel = Button(self.buttons, text='Cancelar', width=10, command=self.cmd_cancel)
        self.confirm = Button(self.buttons, text='Confirmar', width=10, command=self.cmd_confirm)
        self.tipomov.bind("<FocusOut>", self.cmd_tipomov)
        # self.combo1.bind("<FocusOut>", self.cmd_combo1)
        # self.combo2.bind("<FocusOut>", self.cmd_combo2)
        if self.data:
            self.fill_data()
        else:
            # Instruções para dados default quando iniciar novo registro.
            # self.datacadastro.insert(0, datetime.date.today().strftime('%d/%m/%Y'))
            # self.usuario.insert(0, '1')
            pass
        self.id['state'] = 'disabled'
        self.categoria.focus()

    def grid(self):
        #Label(self.mainframe, text='', width=10, bg=BGCOLOR).grid(row=0, column=0)
        Label(self.mainframe, text='EDIÇÃO DE CATEGORIAS', width=60, bg=BGCOLOR, font=('Arial Bold', 16)).grid(row=1, column=0)
        self.frame.grid(row=2, column=0)
        Label(self.frame, text='\n', width=5, height=14, bg=BGFORM).grid(row=0, column=0, rowspan=7) # juntar o Enter
        Label(self.frame, text='', width=10, bg=BGFORM).grid(row=0, column=1)
        self.id_l.grid(row=1, column=1)
        self.id.grid(row=1, column=2, sticky='w')
        self.categoria_l.grid(row=2, column=1)
        self.categoria.grid(row=2, column=2, sticky='w')
        self.tipomov_l.grid(row=3, column=1)
        self.tipomov.grid(row=3, column=2, sticky='w')
        self.classifica_l.grid(row=4, column=1)
        self.classifica.grid(row=4, column=2, sticky='w')
        self.usuario_l.grid(row=5, column=1)
        self.usuario.grid(row=5, column=2, sticky='w')
        self.buttons.grid(row=6, column=1, columnspan=2)
        Label(self.buttons, text='', bg=BGFORM, width=30).grid(row=0, column=1, columnspan=2)
        self.cancel.grid(row=1, column=1)
        self.confirm.grid(row=1, column=2)
        Label(self.frame, text='', bg=BGFORM, width=5).grid(row=7, column=1)
        Label(self.frame, text='', bg=BGFORM, width=5).grid(row=7, column=3)

    def fill_data(self):
        c = self.conn.cursor()
        cmd = 'SELECT id, categoria, tipomov, classifica, usuario FROM categorias WHERE id = %s' % self.data
        c.execute(cmd)
        data = c.fetchone()
        self.id.insert(0, data[0])
        self.categoria.insert(0, data[1])
        self.tipomov.insert(0, TIPOS_CATEG[data[2]])
        self.classifica_v.set(data[3])
        self.usuario.insert(0, data[4])

    def cmd_tipomov(self, event=None):
        if self.tipomov.get() and self.tipomov.get() not in TIPOS_CATEG:
            for i in TIPOS_CATEG:
                if self.tipomov.get().lower() in i.lower():
                    self.tipomov.delete(0, 'end')
                    self.tipomov.insert(0, i)
                    break
            if self.tipomov.get() not in TIPOS_CATEG:
                self.tipomov.delete(0, 'end')

    def cmd_cancel(self):
        self.instance.clear_mainframe()
        main = CategoriasForm(self.instance, self.conn, saved=self.saved)
        main.grid()
        main.cmd_seek()

    def cmd_confirm(self):
        resp = messagebox.askyesno(title='Confirmação', message='Tem certeza que deseja confirmar os dados?')            
        if resp:
            c = self.conn.cursor()
            if not self.data:
                c.execute('''INSERT INTO categorias (categoria, tipomov, classifica, usuario)
                VALUES("%s", %s, %s, %s)''' % (
                    self.categoria.get(), TIPOS_CATEG.index(self.tipomov.get()), self.classifica_v.get(), self.usuario.get()
                ))
            else:
                c.execute('''UPDATE categorias
                SET categoria = "%s", tipomov = %s, classifica = %s, usuario = %s
                WHERE id = %s''' % (
                    self.categoria.get(), TIPOS_CATEG.index(self.tipomov.get()), self.classifica_v.get(), self.usuario.get(), self.data
                ))
            self.conn.commit()
            messagebox.showinfo('Informação', 'Dados atualizados com sucesso!')
            self.instance.clear_mainframe()
            main = CategoriasForm(self.instance, self.conn, saved=self.saved)
            main.grid()
            main.cmd_seek()


class UserForm:
    def __init__(self, instance, conn, saved={}):
        self.conn = conn
        self.instance = instance
        self.mainframe = instance.mainframe
        self.frame = Frame(self.mainframe, bd=1, bg=BGFORM, relief='sunken')
        self.nome_l = Label(self.frame, anchor='e', text='Nome ', bg=BGFORM, width=10)
        self.nome = Entry(self.frame, width=20)
        self.nome.bind("<FocusOut>", self.cmd_seek)
        self.fr1 = Frame(self.frame, bd=1, bg=BGFORM, relief='sunken')
        self.fr1.configure(height=200, width=400)
        self.fr1.grid_propagate(0)
        self.fr1_place = Frame(self.fr1)
        self.table1 = Treeview(self.fr1_place, height=10)
        self.sb_y = Scrollbar(self.fr1_place, orient="vertical", command=self.table1.yview)
        self.sb_x = Scrollbar(self.fr1_place, orient="horizontal", command=self.table1.xview)
        self.table1.configure(yscroll=self.sb_y.set, xscroll=self.sb_x.set)
        self.buttons = Frame(self.frame, bg=BGFORM, width=30)
        self.new = Button(self.buttons, text='Novo', width=10, command=self.cmd_new)
        self.edit = Button(self.buttons, text='Editar', width=12, command=self.cmd_edit)
        self.quit = Button(self.buttons, text='Sair', width=10, command=self.cmd_quit)
        if 'nome' in saved and saved['nome']: self.nome.insert('end', saved['nome'])
        self.nome.focus()
    
    def grid(self):
        #Label(self.mainframe, text='', width=10, bg=BGCOLOR).grid(row=0, column=0)
        Label(self.mainframe, text='CADASTRO DE USUÁRIOS', width=60, bg=BGCOLOR, font=('Arial Bold', 16)).grid(row=1, column=0)
        self.frame.grid(row=2, column=0)
        Label(self.frame, text='\n', width=5, height=10, bg=BGFORM).grid(row=0, column=0, rowspan=5)
        Label(self.frame, text='', bg=BGFORM, width=10).grid(row=0, column=1)
        self.nome_l.grid(row=1, column=1)
        self.nome.grid(row=1, column=2)
        Label(self.frame, text='', bg=BGFORM, width=5).grid(row=2, column=1)
        self.fr1.grid(row=3, column=1, columnspan=2, stick='w')
        self.fr1_place.place(bordermode='outside', height=200, width=400)
        self.sb_y.pack(side="right", fill='y')
        self.sb_x.pack(side="bottom", fill='x')
        self.table1.pack(expand=1)
        self.buttons.grid(row=4, column=1, columnspan=2)
        Label(self.buttons, text='', bg=BGFORM, width=50).grid(row=0, column=1, columnspan=3)
        self.new.grid(row=1, column=1)
        self.edit.grid(row=1, column=2)
        self.quit.grid(row=1, column=3)
        Label(self.frame, text='', bg=BGFORM, width=5).grid(row=5, column=1)
        Label(self.frame, text='', bg=BGFORM, width=5).grid(row=5, column=3)

    def data(self, filter=''):
        c = self.conn.cursor()
        cmd = 'SELECT id, nome, observacao FROM usuarios'
        if filter: cmd += filter
        cmd += ' ORDER BY nome'
        c.execute(cmd)
        dados = c.fetchall()
        # Preenche a tabela
        self.table1['columns'] = ['Nome', 'Observação']
        self.table1.heading('#0', text='Id', anchor='center')
        self.table1.column('#0', anchor='w', width=60)
        self.table1.delete(*self.table1.get_children())
        self.table1.tag_configure('total', background='green yellow')
        for row in ['Nome', 'Observação']:
            self.table1.heading(
                row, 
                text=row, 
                anchor='center' 
            )
            anchor = 'w'
            self.table1.column(row, anchor=anchor, width=161)
        index = 1
        #dados = [[1, 'Renan', 'Administrador'], [2, 'Outro', ''], [1, 'Renan', 'Administrador'], [2, 'Outro', ''], [1, 'Renan', 'Administrador'], [2, 'Outro', '']]
        for row in dados:
            self.table1.insert('', 'end', text=str(row[0]), values=row[1:])
            index += 1

    def cmd_seek(self, event=None):
        filt = ' '
        if self.nome.get():
            filt += 'WHERE nome LIKE "%s%s%s"' % ("%", self.nome.get(), "%")
        self.data(filter=filt)
        
    def cmd_new(self):
        saved = {}
        if self.nome.get():
            saved['nome'] = self.nome.get()
        self.instance.clear_mainframe()
        main = UserEditForm(self.instance, self.conn, saved=saved)
        main.grid()

    def cmd_edit(self, event=None):
        saved = {}
        if self.nome.get():
            saved['nome'] = self.nome.get()
        try:
            region = self.table1.identify("region", event.x, event.y)
        except:
            region = 'cell'
        #column = form.fields['table'].identify("column", event.x, event.y)
        #cell = form.fields['table'].identify("row", event.x, event.y)
        _id = None
        if region == "cell":
            if self.table1.selection():
                for i in self.table1.selection():
                    _id = str(self.table1.item(i, 'text'))
                    self.instance.clear_mainframe()
                    main = UserEditForm(self.instance, self.conn, saved=saved, data=_id)
                    main.grid()
            else:
                messagebox.showerror(title='Atenção', message='Selecione um usuário para a edição.')

    def cmd_quit(self):
        self.instance.clear_mainframe()
        MainPanel(self.instance, self.conn).grid()


class UserEditForm:
    def __init__(self, instance, conn, saved={}, data=None):
        self.instance = instance
        self.mainframe = instance.mainframe
        self.conn = conn
        self.saved = saved
        self.data = data
        self.frame = Frame(self.mainframe, bd=1, relief='sunken', bg=BGFORM)
        self.nome_l = Label(self.frame, anchor='e', text='Nome ', bg=BGFORM, width=10)
        self.nome = Entry(self.frame, width=20)
        self.senha_l = Label(self.frame, anchor='e', text='Senha ', bg=BGFORM, width=10)
        self.senha = Entry(self.frame, width=20, show='*')
        self.observacao_l = Label(self.frame, anchor='e', text='Observacao ', bg=BGFORM, width=10)
        self.observacao = Entry(self.frame, width=20)
        self.buttons = Frame(self.frame, bg=BGFORM, width=30)
        self.cancel = Button(self.buttons, text='Cancelar', width=10, command=self.cmd_cancel)
        self.confirm = Button(self.buttons, text='Confirmar', width=10, command=self.cmd_confirm)
        if self.data:
            self.fill_data()
        self.nome.focus()
    
    def grid(self):
        #Label(self.mainframe, text='', width=10, bg=BGCOLOR).grid(row=0, column=0)
        Label(self.mainframe, text='EDIÇÃO DE USUÁRIO', width=60, bg=BGCOLOR, font=('Arial Bold', 16)).grid(row=1, column=0)
        self.frame.grid(row=2, column=0)
        Label(self.frame, text='\n', width=5, height=10, bg=BGFORM).grid(row=0, column=0, rowspan=5)
        Label(self.frame, text='', bg=BGFORM, width=10).grid(row=0, column=1)
        self.nome_l.grid(row=1, column=1)
        self.nome.grid(row=1, column=2)
        self.senha_l.grid(row=2, column=1)
        self.senha.grid(row=2, column=2)
        self.observacao_l.grid(row=3, column=1)
        self.observacao.grid(row=3, column=2)
        self.buttons.grid(row=4, column=1, columnspan=2)
        Label(self.buttons, text='', bg=BGFORM, width=30).grid(row=0, column=1, columnspan=2)
        self.cancel.grid(row=1, column=1)
        self.confirm.grid(row=1, column=2)
        Label(self.frame, text='', bg=BGFORM, width=5).grid(row=5, column=1)
        Label(self.frame, text='', bg=BGFORM, width=5).grid(row=5, column=3)

    def fill_data(self):
        c = self.conn.cursor()
        c.execute('SELECT nome, senha, observacao FROM usuarios WHERE id = %s' % self.data)
        data = c.fetchone()
        self.nome.insert(0, data[0])
        self.senha.insert(0, data[1])
        self.observacao.insert(0, data[2])

    def cmd_cancel(self):
        self.instance.clear_mainframe()
        main = UserForm(self.instance, self.conn, saved=self.saved)
        main.grid()
        main.cmd_seek()

    def cmd_confirm(self):
        if self.nome.get() and self.senha.get() and self.observacao.get():
            resp = messagebox.askyesno(title='Confirmação', message='Tem certeza que deseja confirmar os dados?')            
            if resp:
                c = self.conn.cursor()
                if not self.data:
                    c.execute('''INSERT INTO usuarios (nome, senha, observacao)
                    VALUES ("%s", "%s", "%s")''' % (self.nome.get(), self.senha.get(), self.observacao.get()))
                else:
                    c.execute('''UPDATE usuarios
                    SET nome = "%s", senha = "%s", observacao = "%s"
                    WHERE id = %s''' % (self.nome.get(), self.senha.get(), self.observacao.get(), self.data))
                self.conn.commit()
                messagebox.showinfo('Informação', 'Dados atualizados com sucesso!')
                self.instance.clear_mainframe()
                main = UserForm(self.instance, self.conn, saved=self.saved)
                main.grid()
                main.cmd_seek()
        else:
            messagebox.showerror(title='Aviso', message='Não é possível atualizar. Verifique os dados preenchidos.')


class ParceirosForm:
    # Objetivo: 
    def __init__(self, instance, conn, saved={}):
        self.conn = conn
        self.instance = instance
        self.mainframe = instance.mainframe
        self.frame = Frame(self.mainframe, bd=1, bg=BGFORM, relief='sunken')
        self.filter1_l = Label(self.frame, anchor='e', text='Filtro ', bg=BGFORM, width=10)
        self.filter1 = Entry(self.frame, width=20)
        self.filter1.bind("<FocusOut>", self.cmd_seek)
        self.fr1 = Frame(self.frame, bd=1, bg=BGFORM, relief='sunken')
        self.fr1.configure(height=400, width=800)
        self.fr1.grid_propagate(0)
        self.fr1_place = Frame(self.fr1)
        self.table1 = Treeview(self.fr1_place, height=20)
        self.sb_y = Scrollbar(self.fr1_place, orient="vertical", command=self.table1.yview)
        self.sb_x = Scrollbar(self.fr1_place, orient="horizontal", command=self.table1.xview)
        self.table1.configure(yscroll=self.sb_y.set, xscroll=self.sb_x.set)
        self.buttons = Frame(self.frame, bg=BGFORM, width=30)
        self.new = Button(self.buttons, text='Novo', width=10, command=self.cmd_new)
        self.edit = Button(self.buttons, text='Editar', width=12, command=self.cmd_edit)
        self.quit = Button(self.buttons, text='Sair', width=10, command=self.cmd_quit)
        if 'filter1' in saved and saved['filter1']: self.filter1.insert('end', saved['filter1'])
        self.filter1.focus()

    def grid(self):
        #Label(self.mainframe, text='', width=10, bg=BGCOLOR).grid(row=0, column=0)
        Label(self.mainframe, text='CADASTRO DE PARCEIROS', width=60, bg=BGCOLOR, font=('Arial Bold', 16)).grid(row=1, column=0)
        self.frame.grid(row=2, column=0)
        Label(self.frame, text='\n', width=5, height=10, bg=BGFORM).grid(row=0, column=0, rowspan=5) # remover espaço para Enter.
        Label(self.frame, text='', bg=BGFORM, width=10).grid(row=0, column=1)
        self.filter1_l.grid(row=1, column=1)
        self.filter1.grid(row=1, column=2)
        Label(self.frame, text='', bg=BGFORM, width=5).grid(row=2, column=1)
        self.fr1.grid(row=3, column=1, columnspan=2, stick='w')
        self.fr1_place.place(bordermode='outside', height=400, width=800)
        self.sb_y.pack(side="right", fill='y')
        self.sb_x.pack(side="bottom", fill='x')
        self.table1.pack(expand=1)
        self.buttons.grid(row=4, column=1, columnspan=2)
        Label(self.buttons, text='', bg=BGFORM, width=50).grid(row=0, column=1, columnspan=3)
        self.new.grid(row=1, column=1)
        self.edit.grid(row=1, column=2)
        self.quit.grid(row=1, column=3)
        Label(self.frame, text='', bg=BGFORM, width=5).grid(row=5, column=1)
        Label(self.frame, text='', bg=BGFORM, width=5).grid(row=5, column=3)

    def data(self, filter='', order='nome'):
        c = self.conn.cursor()
        cmd = 'SELECT id, nome, nomecompleto, tipo, doc, endereco, telefone, observacao, modo, datacadastro FROM parceiros'
        if filter: cmd += filter
        if order:
            cmd += ' ORDER BY %s' % order
        c.execute(cmd)
        dados = c.fetchall()
        _dados = []
        consta = 'Não', 'Sim'
        for i in dados:
            _dados.append([i[0], i[1], i[2], TIPOS_DOC[i[3]], i[4], i[5], i[6], i[7], TIPOS_RELAC[i[8]], i[9]])
        dados = _dados
        # Preenche a tabela
        self.table1['columns'] = ['Nome', 'Nome Completo', 'tipo', 'doc', 'endereco', 'telefone', 'observacao', 'modo', 'Incluído em']
        self.table1.heading('#0', text='Id', anchor='center')
        self.table1.column('#0', anchor='w', width=60)
        self.table1.delete(*self.table1.get_children())
        self.table1.tag_configure('total', background='green yellow')
        columns = {
            'id': 60, 'Nome': 120, 'Nome Completo': 250, 'tipo': 120, 'doc': 140, 'endereco': 250, 'telefone': 120, 'observacao': 180, 'modo': 120, 'Incluído em': 120
        }
        for row in ['Nome', 'Nome Completo', 'tipo', 'doc', 'endereco', 'telefone', 'observacao', 'modo', 'Incluído em']:
            self.table1.heading(
                row, 
                text=row, 
                anchor='center' 
            )
            anchor = 'w'
            self.table1.column(row, anchor=anchor, width=columns[row])
        index = 1
        for row in dados:
            self.table1.insert('', 'end', text=str(row[0]), values=row[1:])
            index += 1

    def cmd_seek(self, event=None):
        # Esse código precisa ser ajustado de acordo com os fields do filtro.
        filt = ''
        pre = 'WHERE'
        if self.filter1.get():
            filt += ' %s filter1 LIKE "%s%s%s"' % (pre, "%", self.filter1.get(), "%")
            pre = 'AND'
        #if self.filter2.get():
        #    filt += ' %s filter2 = %s' % (pre, self.filter2.get())
        self.data(filter=filt)
        
    def cmd_new(self):
        saved = {}
        if self.filter1.get():
            saved['filter1'] = self.filter1.get()
        #if self.filter2.get():
        #    saved['filter2'] = self.filter2.get()
        self.instance.clear_mainframe()
        main = ParceirosEditForm(self.instance, self.conn, saved=saved)
        main.grid()

    def cmd_edit(self, event=None):
        saved = {}
        if self.filter1.get():
            saved['filter1'] = self.filter1.get()
        #if self.filter2.get():
        #    saved['filter2'] = self.filter2.get()
        try:
            region = self.table1.identify("region", event.x, event.y)
        except:
            region = 'cell'
        #column = form.fields['table'].identify("column", event.x, event.y)
        #cell = form.fields['table'].identify("row", event.x, event.y)
        _id = None
        if region == "cell":
            if self.table1.selection():
                for i in self.table1.selection():
                    _id = str(self.table1.item(i, 'text'))
                    self.instance.clear_mainframe()
                    main = ParceirosEditForm(self.instance, self.conn, saved=saved, data=_id)
                    main.grid()
            else:
                messagebox.showerror(title='Atenção', message='Selecione um registro para a edição.')

    def cmd_quit(self):
        self.instance.clear_mainframe()
        MainPanel(self.instance, self.conn).grid()

        
class ParceirosEditForm:
    def __init__(self, instance, conn, saved={}, data=None):
        self.instance = instance
        self.mainframe = instance.mainframe
        self.conn = conn
        self.saved = saved
        self.data = data
        self.frame = Frame(self.mainframe, bd=1, relief='sunken', bg=BGFORM)
        self.id_l = Label(self.frame, anchor='e', text='Id ', bg=BGFORM, width=18)
        self.id = Entry(self.frame, width=6)
        self.datacadastro_l = Label(self.frame, anchor='e', text='Data do Cadastro ', bg=BGFORM, width=18)
        self.datacadastro = Entry(self.frame, width=10)
        self.nome_l = Label(self.frame, anchor='e', text='Nome ', bg=BGFORM, width=18)
        self.nome = Entry(self.frame, width=15)
        self.nomecompleto_l = Label(self.frame, anchor='e', text='Nome Completo ', bg=BGFORM, width=18)
        self.nomecompleto = Entry(self.frame, width=35)
        self.tipo_l = Label(self.frame, anchor='e', text='Tipo ', bg=BGFORM, width=18)
        self.tipo = Combobox(self.frame, width=13, values=TIPOS_DOC)
        self.doc_l = Label(self.frame, anchor='e', text='CNPJ/CPF ', bg=BGFORM, width=18)
        self.doc = Entry(self.frame, width=17)
        self.endereco_l = Label(self.frame, anchor='e', text='Endereço ', bg=BGFORM, width=18)
        self.endereco = Entry(self.frame, width=35)
        self.telefone_l = Label(self.frame, anchor='e', text='Telefone ', bg=BGFORM, width=18)
        self.telefone = Entry(self.frame, width=20)
        self.observacao_l = Label(self.frame, anchor='e', text='Observação ', bg=BGFORM, width=18)
        self.observacao = Entry(self.frame, width=20)
        self.modo_l = Label(self.frame, anchor='e', text='Relacionamento ', bg=BGFORM, width=18)
        self.modo = Combobox(self.frame, width=13, values=TIPOS_RELAC)
        self.usuario_l = Label(self.frame, anchor='e', text='Usuario ', bg=BGFORM, width=18)
        self.usuario = Entry(self.frame, width=20)
        self.buttons = Frame(self.frame, bg=BGFORM, width=30)
        self.cancel = Button(self.buttons, text='Cancelar', width=10, command=self.cmd_cancel)
        self.confirm = Button(self.buttons, text='Confirmar', width=10, command=self.cmd_confirm)
        self.tipo.bind("<FocusOut>", self.cmd_tipo)
        self.modo.bind("<FocusOut>", self.cmd_modo)
        if self.data:
            self.fill_data()
        else:
            # Instruções para dados default quando iniciar novo registro.
            self.datacadastro.insert(0, datetime.date.today().strftime('%d/%m/%Y'))
            self.usuario.insert(0, '1')
            pass
        self.id['state'] = 'disabled'
        self.nome.focus()

    def grid(self):
        #Label(self.mainframe, text='', width=10, bg=BGCOLOR).grid(row=0, column=0)
        Label(self.mainframe, text='EDIÇÃO DE PARCEIROS', width=60, bg=BGCOLOR, font=('Arial Bold', 16)).grid(row=1, column=0)
        self.frame.grid(row=2, column=0)
        Label(self.frame, text='\n', width=5, height=18, bg=BGFORM).grid(row=0, column=0, rowspan=11) # juntar o Enter
        Label(self.frame, text='', width=10, bg=BGFORM).grid(row=0, column=1)
        self.id_l.grid(row=1, column=1)
        self.id.grid(row=1, column=2, sticky='w')
        self.datacadastro_l.grid(row=2, column=1)
        self.datacadastro.grid(row=2, column=2, sticky='w')
        self.nome_l.grid(row=3, column=1)
        self.nome.grid(row=3, column=2, sticky='w')
        self.nomecompleto_l.grid(row=4, column=1)
        self.nomecompleto.grid(row=4, column=2, sticky='w')
        self.tipo_l.grid(row=5, column=1)
        self.tipo.grid(row=5, column=2, sticky='w')
        self.doc_l.grid(row=6, column=1)
        self.doc.grid(row=6, column=2, sticky='w')
        self.endereco_l.grid(row=7, column=1)
        self.endereco.grid(row=7, column=2, sticky='w')
        self.telefone_l.grid(row=8, column=1)
        self.telefone.grid(row=8, column=2, sticky='w')
        self.observacao_l.grid(row=9, column=1)
        self.observacao.grid(row=9, column=2, sticky='w')
        self.modo_l.grid(row=10, column=1)
        self.modo.grid(row=10, column=2, sticky='w')
        self.usuario_l.grid(row=11, column=1)
        self.usuario.grid(row=11, column=2, sticky='w')
        self.buttons.grid(row=12, column=1, columnspan=2)
        Label(self.buttons, text='', bg=BGFORM, width=30).grid(row=0, column=1, columnspan=2)
        self.cancel.grid(row=1, column=1)
        self.confirm.grid(row=1, column=2)
        Label(self.frame, text='', bg=BGFORM, width=5).grid(row=13, column=1)
        Label(self.frame, text='', bg=BGFORM, width=5).grid(row=13, column=3)

    def fill_data(self):
        c = self.conn.cursor()
        cmd = 'SELECT id, datacadastro, nome, nomecompleto, tipo, doc, endereco, telefone, observacao, modo, usuario FROM parceiros WHERE id = %s' % self.data
        c.execute(cmd)
        data = c.fetchone()
        self.id.insert(0, data[0])
        self.datacadastro.insert(0, data[1])
        self.nome.insert(0, data[2])
        self.nomecompleto.insert(0, data[3])
        self.tipo.insert(0, TIPOS_DOC[data[4]])
        self.doc.insert(0, data[5])
        self.endereco.insert(0, data[6])
        self.telefone.insert(0, data[7])
        self.observacao.insert(0, data[8])
        self.modo.insert(0, TIPOS_RELAC[data[9]])
        self.usuario.insert(0, data[10])

    def cmd_tipo(self, event=None):
        if self.tipo.get() and self.tipo.get() not in TIPOS_DOC:
            for i in TIPOS_DOC:
                if self.tipo.get().lower() in i.lower():
                    self.tipo.delete(0, 'end')
                    self.tipo.insert(0, i)
                    break
            if self.tipo.get() not in TIPOS_DOC:
                self.tipo.delete(0, 'end')

    def cmd_modo(self, event=None):
        if self.modo.get() and self.modo.get() not in TIPOS_RELAC:
            for i in TIPOS_RELAC:
                if self.modo.get().lower() in i.lower():
                    self.modo.delete(0, 'end')
                    self.modo.insert(0, i)
                    break
            if self.modo.get() not in TIPOS_RELAC:
                self.modo.delete(0, 'end')

    def cmd_cancel(self):
        self.instance.clear_mainframe()
        main = ParceirosForm(self.instance, self.conn, saved=self.saved)
        main.grid()
        main.cmd_seek()

    def cmd_confirm(self):
        if self.datacadastro.get() and self.nome.get() and self.nomecompleto.get() and self.tipo.get():
            resp = messagebox.askyesno(title='Confirmação', message='Tem certeza que deseja confirmar os dados?')            
            if resp:
                c = self.conn.cursor()
                if not self.data:
                    c.execute('''INSERT INTO parceiros (datacadastro, nome, nomecompleto, tipo, doc, endereco, telefone, observacao, modo, usuario)
                    VALUES("%s", "%s", "%s", %s, "%s", "%s", "%s", "%s", %s, %s)''' % (
                        self.datacadastro.get(), self.nome.get(), self.nomecompleto.get(), TIPOS_DOC.index(self.tipo.get()), self.doc.get(), self.endereco.get(), self.telefone.get(), self.observacao.get(), TIPOS_RELAC.index(self.modo.get()), self.usuario.get()
                    ))
                else:
                    c.execute('''UPDATE parceiros
                    SET datacadastro = "%s", nome = "%s", nomecompleto = "%s", tipo = %s, doc = "%s", endereco = "%s", telefone = "%s", observacao = "%s", modo = %s, usuario = %s
                    WHERE id = %s''' % (
                        self.datacadastro.get(), self.nome.get(), self.nomecompleto.get(), TIPOS_DOC.index(self.tipo.get()), self.doc.get(), self.endereco.get(), self.telefone.get(), self.observacao.get(), TIPOS_RELAC.index(self.modo.get()), self.usuario.get(), self.data
                    ))
                self.conn.commit()
                messagebox.showinfo('Informação', 'Dados atualizados com sucesso!')
                self.instance.clear_mainframe()
                main = ParceirosForm(self.instance, self.conn, saved=self.saved)
                main.grid()
                main.cmd_seek()
        else:
            messagebox.showerror(title='Aviso', message='Não é possível atualizar. Verifique os dados preenchidos.')


class MovimentosForm:
    # Objetivo: 
    def __init__(self, instance, conn, saved={}, tipo_form='rec'):
        self.conn = conn
        self.instance = instance
        self.mainframe = instance.mainframe
        self.bg = BGFORM
        self.font = FONT
        if 'tipo_form' in saved:
            self.tipo_form = saved['tipo_form']
        else:
            self.tipo_form = tipo_form
        if self.tipo_form == 'rec':
            self.bg = 'aquamarine'
            self.tipomov = ['0']
        elif self.tipo_form == 'pag':
            self.bg = 'RosyBrown1'
            self.tipomov = ['1']
        elif self.tipo_form == 'transf':
            self.tipomov = ['3']
        else: # cred
            self.bg = 'RosyBrown1'
            self.tipomov = ['3']
        self.frame = Frame(self.mainframe, bd=1, bg=self.bg, relief='sunken')
        self.filter_frame = Frame(self.frame, bg=self.bg, width=30)
        if self.tipo_form == 'rec':
            text = 'Cliente '
            where = 'modo IN (0, 1)'
        else:
            text = 'Fornecedor '
            where = 'modo IN (0, 2)'
        values = query_list(self.conn, 'nome', 'parceiros', where=where, order_by='nome')
        self.parceiro_l = Label(self.filter_frame, anchor='e', text='Parceiro ', bg=self.bg, width=10)
        self.parceiro = Combobox(self.filter_frame, width=16, values=values)
        self.parceiro.bind("<FocusOut>", self.cmd_seek)
        values = query_list(self.conn, 'categoria, id', 'categorias', where='tipomov = %s' % self.tipomov[0], order_by='categoria')
        self.categoriamov_l = Label(self.filter_frame, anchor='e', text='Categoria ', bg=self.bg, width=10)
        self.categoriamov = Combobox(self.filter_frame, width=16, values=values)
        self.categoriamov.bind("<FocusOut>", self.cmd_seek)
        if self.tipo_form == 'cred':
            text = 'Cartão '
            where = 'tipomov = 2'
        else:
            text = 'Banco '
            where = ''
        values = query_list(self.conn, 'nomebanco', 'bancos', where=where, order_by='nomebanco')
        self.banco_l = Label(self.filter_frame, anchor='e', text=text, bg=self.bg, width=7)
        self.banco = Combobox(self.filter_frame, width=16, values=values)
        self.banco.bind("<FocusOut>", self.cmd_seek)
        self.fatura_l = Label(self.filter_frame, anchor='e', text='Fatura ', bg=self.bg, width=7)
        self.fatura = Entry(self.filter_frame, width=12)
        self.fatura.bind("<FocusOut>", self.cmd_seek)
        self.dataini_l = Label(self.filter_frame, anchor='e', text='Data Inicial ', bg=self.bg, width=12)
        self.dataini = Entry(self.filter_frame, width=10)
        self.dataini.bind("<FocusOut>", self.cmd_seek)
        self.datafin_l = Label(self.filter_frame, anchor='e', text='Data Final ', bg=self.bg, width=12)
        self.datafin = Entry(self.filter_frame, width=10)
        self.datafin.bind("<FocusOut>", self.cmd_seek)
        self.vencini_l = Label(self.filter_frame, anchor='e', text='Venc Inicial ', bg=self.bg, width=12)
        self.vencini = Entry(self.filter_frame, width=10)
        self.vencini.bind("<FocusOut>", self.cmd_seek)
        self.vencfin_l = Label(self.filter_frame, anchor='e', text='Venc Final ', bg=self.bg, width=12)
        self.vencfin = Entry(self.filter_frame, width=10)
        self.vencfin.bind("<FocusOut>", self.cmd_seek)
        self.height = int(instance.root.winfo_height() - 260)
        self.fr1 = Frame(self.frame, bd=1, bg=self.bg, relief='sunken')
        self.fr1.configure(height=self.height, width=820)
        self.fr1.grid_propagate(0)
        self.fr1_place = Frame(self.fr1)
        self.table1 = Treeview(self.fr1_place, height=20)
        self.sb_y = Scrollbar(self.fr1_place, orient="vertical", command=self.table1.yview)
        self.sb_x = Scrollbar(self.fr1_place, orient="horizontal", command=self.table1.xview)
        self.table1.configure(yscroll=self.sb_y.set, xscroll=self.sb_x.set)
        self.table1.bind("<Button-1>", self.cmd_table)
        self.table1.bind("<Double-1>", self.cmd_table)
        self.asc = True # Ordem ascendente ou descendente
        self.buttons = Frame(self.frame, bg=self.bg, width=30)
        self.new = Button(self.buttons, text='Novo', width=10, command=self.cmd_new)
        self.duplic = Button(self.buttons, text='Duplicar', width=10, command=self.cmd_duplic)
        self.edit = Button(self.buttons, text='Editar', width=12, command=self.cmd_edit)
        self.quit = Button(self.buttons, text='Sair', width=10, command=self.cmd_quit)
        if tipo_form == 'rec':
            fg = 'dark green'
        else:
            fg = 'red'
        self.amount = Label(self.buttons, text='Valor: 0,00', bg=self.bg, fg=fg, font=('Arial 12 bold'))
        if 'parceiro' in saved and saved['parceiro']: self.parceiro.insert('end', saved['parceiro'])
        if 'categoriamov' in saved and saved['categoriamov']: self.categoriamov.insert('end', saved['categoriamov'])
        if 'banco' in saved and saved['banco']: self.banco.insert('end', saved['banco'])
        if 'fatura' in saved and saved['fatura']: self.fatura.insert('end', saved['fatura'])
        if 'dataini' in saved and saved['dataini']: self.dataini.insert('end', saved['dataini'])
        if 'datafin' in saved and saved['datafin']: self.datafin.insert('end', saved['datafin'])
        if 'vencini' in saved and saved['vencini']: self.vencini.insert('end', saved['vencini'])
        if 'vencfin' in saved and saved['vencfin']: self.vencfin.insert('end', saved['vencfin'])
        if not self.dataini.get() and not saved: self.dataini.insert(0, '%s' % (date_out(str(d.date.today())[:-2] + '01')))
        if not self.datafin.get() and not saved: self.datafin.insert(0, '%s' % (date_out(str(lastdaymonth(d.date.today())))))
        self.new.focus()

    def grid(self):
        if self.tipo_form == 'rec':
            label = 'RECEBIMENTOS'
        elif self.tipo_form == 'pag':
            label = 'PAGAMENTOS'
        elif self.tipo_form == 'transf':
            label = 'TRANSFERÊNCIAS'
        else:
            label = 'CARTÕES DE CRÉDITO'
        #Label(self.mainframe, text='', width=10, bg=BGCOLOR).grid(row=0, column=0)
        Label(self.mainframe, text=label, width=60, bg=BGCOLOR, font=('Arial Bold', 16)).grid(row=1, column=0)
        self.frame.grid(row=2, column=0)
        Label(self.frame, text='\n', width=5, height=10, bg=self.bg).grid(row=0, column=0, rowspan=5) # remover espaço para Enter.
        Label(self.frame, text='', bg=self.bg, width=10).grid(row=0, column=1)
        self.filter_frame.grid(row=2, column=0, columnspan=9)
        Label(self.filter_frame, text='\n', width=0, height=6, bg=self.bg).grid(row=0, column=0, rowspan=4) # remover espaço para Enter.
        if self.tipo_form in ['rec', 'pag']:
            self.parceiro_l.grid(row=1, column=1)
            self.parceiro.grid(row=1, column=2, stick='w')
            self.categoriamov_l.grid(row=2, column=1)
            self.categoriamov.grid(row=2, column=2, stick='w')
        self.banco_l.grid(row=1, column=3)
        self.banco.grid(row=1, column=4, stick='w')
        self.fatura_l.grid(row=2, column=3)
        self.fatura.grid(row=2, column=4, stick='w')
        self.dataini_l.grid(row=1, column=5)
        self.dataini.grid(row=1, column=6, stick='w')
        self.datafin_l.grid(row=2, column=5)
        self.datafin.grid(row=2, column=6, stick='w')
        self.vencini_l.grid(row=1, column=7)
        self.vencini.grid(row=1, column=8, stick='w')
        self.vencfin_l.grid(row=2, column=7)
        self.vencfin.grid(row=2, column=8, stick='w')
        Label(self.filter_frame, text='', bg=self.bg, width=5).grid(row=3, column=9)
        self.fr1.grid(row=3, column=1, columnspan=2, stick='w')
        self.fr1_place.place(bordermode='outside', height=self.height, width=820)
        self.sb_y.pack(side="right", fill='y')
        self.sb_x.pack(side="bottom", fill='x')
        self.table1.pack(expand=1)
        self.buttons.grid(row=4, column=1, columnspan=2)
        Label(self.buttons, text='', bg=self.bg, width=50).grid(row=0, column=1, columnspan=3)
        self.new.grid(row=1, column=1)
        self.duplic.grid(row=1, column=2)
        self.edit.grid(row=1, column=3)
        self.quit.grid(row=1, column=4)
        self.amount.grid(row=1, column=5)
        Label(self.frame, text='', bg=self.bg, width=5).grid(row=5, column=1)
        Label(self.frame, text='', bg=self.bg, width=5).grid(row=5, column=3)

    def data(self, filter='', order_by='datadoc, datavenc'):
        c = self.conn.cursor()
        cmd = 'SELECT diario.id, datadoc, diario.parceiro, descricao, categoriamov, datavenc, valor, datapago, diario.banco, fatura, diario.usuario FROM diario '
        cmd += 'JOIN parceiros on parceiros.id = diario.parceiro '
        cmd += 'JOIN bancos on bancos.id = diario.banco '
        cmd += 'JOIN categorias on categorias.id = diario.categoriamov '
        if filter: cmd += filter
        if order_by:
            cmd += ' ORDER BY %s' % order_by
        c.execute(cmd)
        dados = c.fetchall()
        cmd = 'SELECT SUM(valor) FROM diario %s' % filter
        c.execute(cmd)
        valor = c.fetchone()
        if valor[0]:
            self.amount['text'] = ' Total: %s' % Numbers(abs(valor[0])).get_str()
        else:
            self.amount['text'] = ' Total: 0,00'
        _dados = []
        consta = 'Não', 'Sim'
        for i in dados:
            if self.tipo_form in ['rec', 'pag']:
                valor = Numbers(i[6]).get_str()
                if self.tipo_form == 'pag':
                    valor = Numbers(-float(i[6])).get_str()
                _dados.append([
                    i[0],
                    date_out(i[1]),
                    query_list(self.conn, 'nome', 'parceiros', 'id = %s' % i[2])[0],
                    i[3],
                    query_list(self.conn, 'categoria, id', 'categorias', 'id = %s' % i[4])[0],
                    date_out(i[5]),
                    valor,
                    date_out(i[7]),
                    query_list(self.conn, 'nomebanco', 'bancos', 'id = %s' % i[8])[0],
                    i[9],
                    i[10]
                ])
            elif self.tipo_form == 'transf':
                c.execute('SELECT banco FROM diario WHERE id = %s' % str(int(i[0]) - 1))
                banco_paga = query_list(self.conn, 'nomebanco', 'bancos', 'id = %s' % c.fetchone()[0])[0]
                _dados.append([
                    i[0],
                    date_out(i[1]),
                    banco_paga,
                    query_list(self.conn, 'nomebanco', 'bancos', 'id = %s' % i[8])[0],
                    i[3],
                    date_out(i[5]),
                    Numbers(i[6]).get_str(),
                    date_out(i[7]),
                    i[10]
                ])
            elif self.tipo_form == 'cred':
                c.execute('SELECT banco FROM diario WHERE id = %s' % str(int(i[0]) - 1))
                banco_paga = query_list(self.conn, 'nomebanco', 'bancos', 'id = %s' % c.fetchone()[0])[0]
                _dados.append([
                    i[0],
                    date_out(i[1]),
                    query_list(self.conn, 'nomebanco', 'bancos', 'id = %s' % i[8])[0],
                    banco_paga,
                    i[9],
                    date_out(i[5]),
                    Numbers(i[6]).get_str(),
                    date_out(i[7]),
                    i[10]
                ])
        dados = _dados
        # Preenche a tabela
        if self.tipo_form in ['rec', 'pag']:
            self.table1['columns'] = ['Data', 'Parceiro', 'Descrição', 'Categoria', 'Vencimento', 'Valor', 'Pagamento', 'Banco', 'Fatura', 'Usuario']
            columns = {
                'id': 60, 'Data': 80, 'Parceiro': 140, 'Descrição': 190, 'Categoria': 160, 'Vencimento': 100, 'Valor': 75, 'Pagamento': 120, 'Banco': 120, 'Fatura': 120, 'Usuario': 120
            }
        elif self.tipo_form == 'transf':
            self.table1['columns'] = ['Data', 'De banco', 'Para banco', 'Descrição', 'Vencimento', 'Valor', 'Pagamento', 'Usuario']
            columns = {
                'id': 60, 'Data': 80, 'De banco': 138, 'Para banco': 138, 'Descrição': 215, 'Vencimento': 100, 'Valor': 75, 'Pagamento': 120, 'Usuario': 120
            }
        elif self.tipo_form == 'cred':
            self.table1['columns'] = ['Data','Cartão', 'Banco',  'Fatura', 'Vencimento', 'Valor', 'Pagamento', 'Usuario']
            columns = {
                'id': 60, 'Data': 80, 'Banco': 138, 'Cartão': 138, 'Fatura': 100, 'Vencimento': 100, 'Valor': 75, 'Pagamento': 120, 'Usuario': 120
            }
        self.table1.heading('#0', text='Id', anchor='center')
        self.table1.column('#0', anchor='w', width=60)
        self.table1.delete(*self.table1.get_children())
        self.table1.tag_configure('total', background='green yellow')
        for row in self.table1['columns']:
            self.table1.heading(
                row, 
                text=row, 
                anchor='center' 
            )
            if row in ['Valor']:
                anchor = 'e'
            else:
                anchor = 'w'
            self.table1.column(row, anchor=anchor, width=columns[row])
        index = 1
        for row in dados:
            self.table1.insert('', 'end', text=str(row[0]), values=row[1:])
            index += 1

    def cmd_table(self, event=None):
        try:
            region = self.table1.identify("region", event.x, event.y)
        except:
            region = 'cell'
        #cell = form.fields['table'].identify("row", event.x, event.y)
        if self.tipo_form in ['rec', 'pag']:
            columns = ['diario.id', 'datadoc', 'parceiros.nome', 'descricao', 'categorias.categoria', 'datavenc', 'valor', 'datapago', 'banco', 'fatura', 'usuario']
        if region == 'heading':
            column = self.table1.identify("column", event.x, event.y)
            if self.asc:
                self.cmd_seek(order_by=columns[int(column[1:])])
                self.asc = False
            else:
                self.cmd_seek(order_by=columns[int(column[1:])] + ' DESC')
                self.asc = True

    def cmd_seek(self, event=None, order_by='datadoc, datavenc'):
        # Esse código precisa ser ajustado de acordo com os fields do filtro.
        cmd(self.parceiro)
        cmd(self.categoriamov)
        cmd(self.banco)
        cmd_data(self.dataini)
        cmd_data(self.datafin)
        cmd_data(self.vencini)
        cmd_data(self.vencfin)
        filt = ' WHERE diario.tipomov IN (%s)' % ', '.join(self.tipomov)
        pre = 'AND'
        if self.parceiro.get():
            filt += ' %s parceiro = %s' % (pre, query_id(self.conn, 'parceiros', ['nome'], [True], self.parceiro.get()))
            pre = 'AND'
        if self.categoriamov.get():
            filt += ' %s categoriamov = %s' % (pre, query_id(self.conn, 'categorias', ['categoria', 'id'], [True, False], self.categoriamov.get()))
            pre = 'AND'
        if self.banco.get():
            filt += ' %s banco = %s' % (pre, query_id(self.conn, 'bancos', ['nomebanco'], [True], self.banco.get()))
            pre = 'AND'
        if self.fatura.get():
            filt += ' %s fatura LIKE "%s%s%s"' % (pre, "%", self.fatura.get(), "%")
            pre = 'AND'
        if self.dataini.get():
            filt += ' %s datadoc >= "%s"' % (pre, date_in(self.dataini.get()))
            pre = 'AND'
        if self.datafin.get():
            filt += ' %s datadoc <= "%s"' % (pre, date_in(self.datafin.get()))
            pre = 'AND'
        if self.vencini.get():
            filt += ' %s datavenc >= "%s"' % (pre, date_in(self.vencini.get()))
            pre = 'AND'
        if self.vencfin.get():
            filt += ' %s datavenc <= "%s"' % (pre, date_in(self.vencfin.get()))
            pre = 'AND'
        #if self.filter2.get():
        #    filt += ' %s filter2 = %s' % (pre, self.filter2.get())
        if self.tipo_form == 'cred':
            filt += ' %s descricao = "<CRED.CARD>"' % (pre)
        elif self.tipo_form == 'transf':
            filt += ' %s descricao != "<CRED.CARD>"' % (pre)

        self.data(filter=filt, order_by=order_by)
        
    def cmd_new(self):
        saved = {}
        saved['tipo_form'] = self.tipo_form
        if self.parceiro.get():
            saved['parceiro'] = self.parceiro.get()
        if self.categoriamov.get():
            saved['categoriamov'] = self.categoriamov.get()
        if self.banco.get():
            saved['banco'] = self.banco.get()
        if self.fatura.get():
            saved['fatura'] = self.fatura.get()
        if self.dataini.get():
            saved['dataini'] = self.dataini.get()
        if self.datafin.get():
            saved['datafin'] = self.datafin.get()
        if self.vencini.get():
            saved['vencini'] = self.vencini.get()
        if self.vencfin.get():
            saved['vencfin'] = self.vencfin.get()
        self.instance.clear_mainframe()
        main = MovimentosEditForm(self.instance, self.conn, saved=saved, tipomov_d=self.tipomov, tipo_form=self.tipo_form)
        main.grid()

    def cmd_edit(self, event=None):
        saved = {}
        saved['tipo_form'] = self.tipo_form
        if self.parceiro.get():
            saved['parceiro'] = self.parceiro.get()
        if self.categoriamov.get():
            saved['categoriamov'] = self.categoriamov.get()
        if self.banco.get():
            saved['banco'] = self.banco.get()
        if self.fatura.get():
            saved['fatura'] = self.fatura.get()
        if self.dataini.get():
            saved['dataini'] = self.dataini.get()
        if self.datafin.get():
            saved['datafin'] = self.datafin.get()
        if self.vencini.get():
            saved['vencini'] = self.vencini.get()
        if self.vencfin.get():
            saved['vencfin'] = self.vencfin.get()
        try:
            region = self.table1.identify("region", event.x, event.y)
        except:
            region = 'cell'
        #column = form.fields['table'].identify("column", event.x, event.y)
        #cell = form.fields['table'].identify("row", event.x, event.y)
        _id = None
        if region == "cell":
            if self.table1.selection():
                for i in self.table1.selection():
                    _id = str(self.table1.item(i, 'text'))
                    self.instance.clear_mainframe()
                    main = MovimentosEditForm(self.instance, self.conn, saved=saved, data=_id, tipomov_d=self.tipomov, tipo_form=self.tipo_form)
                    main.grid()
            else:
                messagebox.showerror(title='Atenção', message='Selecione um registro para a edição.')

    def cmd_duplic(self, event=None):
        saved = {}
        saved['tipo_form'] = self.tipo_form
        if self.parceiro.get():
            saved['parceiro'] = self.parceiro.get()
        if self.categoriamov.get():
            saved['categoriamov'] = self.categoriamov.get()
        if self.banco.get():
            saved['banco'] = self.banco.get()
        if self.fatura.get():
            saved['fatura'] = self.fatura.get()
        if self.dataini.get():
            saved['dataini'] = self.dataini.get()
        if self.datafin.get():
            saved['datafin'] = self.datafin.get()
        if self.vencini.get():
            saved['vencini'] = self.vencini.get()
        if self.vencfin.get():
            saved['vencfin'] = self.vencfin.get()
        try:
            region = self.table1.identify("region", event.x, event.y)
        except:
            region = 'cell'
        #column = form.fields['table'].identify("column", event.x, event.y)
        #cell = form.fields['table'].identify("row", event.x, event.y)
        _id = None
        if region == "cell":
            if self.table1.selection():
                for i in self.table1.selection():
                    _id = str(self.table1.item(i, 'text'))
                    self.instance.clear_mainframe()
                    main = MovimentosEditForm(self.instance, self.conn, saved=saved, data=_id, tipomov_d=self.tipomov, tipo_form=self.tipo_form, duplic=True)
                    main.grid()
            else:
                messagebox.showerror(title='Atenção', message='Selecione um registro para a edição.')

    def cmd_quit(self):
        self.instance.clear_mainframe()
        MainPanel(self.instance, self.conn).grid()

        
class MovimentosEditForm:
    def __init__(self, instance, conn, saved={}, data=None, tipomov_d=None, tipo_form='rec', duplic=False):
        # tipomov_d >> se o movimento é entrada, saída ou transferência (lista)
        self.instance = instance
        self.mainframe = instance.mainframe
        self.conn = conn
        self.saved = saved
        self.data = data
        self.bg = BGFORM
        self.duplic = duplic
        c = self.conn.cursor()
        self.frame = Frame(self.mainframe, bd=1, relief='sunken', bg=self.bg)
        wd = 15 # width padrão dos labels
        self.id_l = Label(self.frame, anchor='e', text='Id ', bg=self.bg, width=wd)
        self.id = Entry(self.frame, width=6)
        self.datafirstupdate_l = Label(self.frame, anchor='e', text='Criado em ', bg=self.bg, width=wd)
        self.datafirstupdate = Entry(self.frame, width=10)
        self.datalastupdate_l = Label(self.frame, anchor='e', text='Editado em ', bg=self.bg, width=wd)
        self.datalastupdate = Entry(self.frame, width=10)
        self.datadoc_l = Label(self.frame, anchor='e', text='Data da compra ', bg=self.bg, width=wd)
        self.datadoc = Entry(self.frame, width=10)
        if tipo_form == 'rec':
            text = 'Cliente '
            where = 'modo IN (0, 1)'
        else:
            text = 'Fornecedor '
            where = 'modo IN (0, 2)'
        values = query_list(self.conn, 'nome', 'parceiros', where=where, order_by='nome')
        self.parceiro_l = Label(self.frame, anchor='e', text=text, bg=self.bg, width=wd)
        self.parceiro = Combobox(self.frame, width=20, values=values)
        values = query_list(self.conn, 'nomebanco', 'bancos')
        self.banco_l = Label(self.frame, anchor='e', text='Banco ', bg=self.bg, width=wd)
        self.banco = Combobox(self.frame, width=20, values=values)
        self.bancorec_l = Label(self.frame, anchor='e', text='Banco Recebedor', bg=self.bg, width=wd)
        self.bancorec = Combobox(self.frame, width=20, values=values)
        values = query_list(self.conn, 'categoria, id', 'categorias', where='tipomov = %s' % tipomov_d[0], order_by='categoria')
        self.categoriamov_l = Label(self.frame, anchor='e', text='Categoria ', bg=self.bg, width=wd)
        self.categoriamov = Combobox(self.frame, width=20, values=values)
        self.fatura_l = Label(self.frame, anchor='e', text='Fatura ', bg=self.bg, width=wd)
        self.fatura = Entry(self.frame, width=7)
        self.descricao_l = Label(self.frame, anchor='e', text='Descricao ', bg=self.bg, width=wd)
        self.descricao = Entry(self.frame, width=40)
        self.valor_l = Label(self.frame, anchor='e', text='Valor ', bg=self.bg, width=wd)
        self.valor = Entry(self.frame, width=8)
        self.datavenc_l = Label(self.frame, anchor='e', text='Vencimento ', bg=self.bg, width=wd)
        self.datavenc = Entry(self.frame, width=10)
        self.datapago_l = Label(self.frame, anchor='e', text='Pagamento ', bg=self.bg, width=wd)
        self.datapago = Entry(self.frame, width=10)
        self.tipomov_d = tipomov_d
        if self.tipomov_d == ['3']:
            self.tipomov_d = ['3', '4']
        self.tipo_form = tipo_form
        self.usuario_l = Label(self.frame, anchor='e', text='Usuario ', bg=self.bg, width=wd)
        self.usuario = Entry(self.frame, width=20)
        self.buttons = Frame(self.frame, bg=self.bg, width=30)
        self.cancel = Button(self.buttons, text='Cancelar', width=10, command=self.cmd_cancel)
        self.confirm = Button(self.buttons, text='Confirmar', width=10, command=self.cmd_confirm)
        # self.combo1.bind("<FocusOut>", self.cmd_combo1)
        # self.combo2.bind("<FocusOut>", self.cmd_combo2)
        if self.data:
            self.fill_data()
        else:
            self.datafirstupdate.insert(0, datetime.date.today().strftime('%d/%m/%Y'))
            self.datalastupdate.insert(0, datetime.date.today().strftime('%d/%m/%Y'))
            self.datadoc.insert(0, datetime.date.today().strftime('%d/%m/%Y'))
            self.datavenc.insert(0, datetime.date.today().strftime('%d/%m/%Y'))
            self.valor.insert(0, '0,00')
            self.usuario.insert(0, '1')
            if 'banco' in self.saved:
                self.banco.insert(0, self.saved['banco'])
            if 'categoriamov' in self.saved:
                self.categoriamov.insert(0, self.saved['categoriamov'])
            if 'parceiro' in self.saved:
                self.parceiro.insert(0, self.saved['parceiro'])
        self.datadoc.bind("<FocusOut>", self.cmd_datadoc)
        self.banco.bind("<FocusOut>", self.cmd_banco)
        self.bancorec.bind("<FocusOut>", self.cmd_bancorec)
        self.categoriamov.bind("<FocusOut>", self.cmd_categoriamov)
        self.fatura.bind("<FocusOut>", self.cmd_fatura)
        self.parceiro.bind("<FocusOut>", self.cmd_parceiro)
        self.valor.bind("<FocusOut>", self.cmd_valor)
        self.datavenc.bind("<FocusOut>", self.cmd_datavenc)
        self.datapago.bind("<FocusOut>", self.cmd_datapago)
        self.id['state'] = 'disabled'
        self.datafirstupdate['state'] = 'disabled'
        self.datalastupdate['state'] = 'disabled'
        self.usuario['state'] = 'disabled'
        if self.tipo_form == 'cred':
            self.descricao['state'] = 'disabled'
        self.datadoc.focus()

    def grid(self):
        #Label(self.mainframe, text='', width=10, bg=BGCOLOR).grid(row=0, column=0)
        if self.tipo_form == 'rec':
            text = 'EDIÇÃO DE RECEBIMENTO'
        elif self.tipo_form == 'pag':
            text = 'EDIÇÃO DE PAGAMENTO'
        elif self.tipo_form == 'transf':
            text = 'EDIÇÃO DE TRANSFERÊNCIA'
        else:
            text = 'FATURA DE CARTÃO DE CRÉDITO'
        Label(self.mainframe, text=text, width=60, bg=BGCOLOR, font=('Arial Bold', 16)).grid(row=1, column=0)
        self.frame.grid(row=2, column=0)
        Label(self.frame, text='\n', width=5, height=30, bg=self.bg).grid(row=0, column=0, rowspan=16) # juntar o Enter
        Label(self.frame, text='', width=10, bg=self.bg).grid(row=0, column=1)
        row = 1
        self.id_l.grid(row=row, column=1)
        self.id.grid(row=row, column=2, sticky='w')
        row += 1
        self.datafirstupdate_l.grid(row=row, column=1)
        self.datafirstupdate.grid(row=row, column=2, sticky='w')
        row += 1
        self.datalastupdate_l.grid(row=row, column=1)
        self.datalastupdate.grid(row=row, column=2, sticky='w')
        row += 1
        self.datadoc_l.grid(row=row, column=1)
        self.datadoc.grid(row=row, column=2, sticky='w')
        row += 1
        if self.tipo_form in ('rec', 'pag'):
            self.parceiro_l.grid(row=row, column=1)
            self.parceiro.grid(row=row, column=2, sticky='w')
            row += 1
        else:
            p = query_list(self.conn, 'nome', 'parceiros', where='id = 1')
            self.parceiro.delete(0, 'end')
            self.parceiro.insert(0, p[0])
            p = query_list(self.conn, 'categoria, id', 'categorias', where='tipomov = 2')
            self.categoriamov.delete(0, 'end')
            self.categoriamov.insert(0, p[0])
        self.banco_l.grid(row=row, column=1)
        self.banco.grid(row=row, column=2, sticky='w')
        row += 1
        if self.tipo_form in ('transf', 'cred'):
            self.bancorec_l.grid(row=row, column=1)
            self.bancorec.grid(row=row, column=2, sticky='w')
            row += 1
        if self.tipo_form in ('rec', 'pag'):
            self.categoriamov_l.grid(row=row, column=1)
            self.categoriamov.grid(row=row, column=2, sticky='w')
            row += 1
        if self.tipo_form in ('pag', 'cred'):
            self.fatura_l.grid(row=row, column=1)
            self.fatura.grid(row=row, column=2, sticky='w')
            row += 1
        self.descricao_l.grid(row=row, column=1)
        self.descricao.grid(row=row, column=2, sticky='w')
        row += 1
        self.valor_l.grid(row=row, column=1)
        self.valor.grid(row=row, column=2, sticky='w')
        row += 1
        self.datavenc_l.grid(row=row, column=1)
        self.datavenc.grid(row=row, column=2, sticky='w')
        row += 1
        self.datapago_l.grid(row=row, column=1)
        self.datapago.grid(row=row, column=2, sticky='w')
        row += 1
        self.usuario_l.grid(row=row, column=1)
        self.usuario.grid(row=row, column=2, sticky='w')
        row += 1
        self.buttons.grid(row=row, column=1, columnspan=2)
        row += 1
        Label(self.buttons, text='', bg=self.bg, width=30).grid(row=0, column=1, columnspan=2)
        self.cancel.grid(row=1, column=1)
        self.confirm.grid(row=1, column=2)
        Label(self.frame, text='', bg=self.bg, width=5).grid(row=row, column=1)
        Label(self.frame, text='', bg=self.bg, width=5).grid(row=row, column=3)

    def fill_data(self):
        c = self.conn.cursor()
        cmd = 'SELECT id, datafirstupdate, datalastupdate, datadoc, datavenc, datapago, parceiro, banco, fatura, descricao, valor, tipomov, categoriamov, usuario FROM diario WHERE id = %s' % self.data
        c.execute(cmd)
        data = c.fetchone()
        if data[11] == 4:
            self.data = str(int(self.data) + 1)
            cmd = 'SELECT id, datafirstupdate, datalastupdate, datadoc, datavenc, datapago, parceiro, banco, fatura, descricao, valor, tipomov, categoriamov, usuario FROM diario WHERE id = %s' % self.data
            c.execute(cmd)
            data = c.fetchone()
        if not self.duplic:
            self.id.insert(0, data[0])
            self.datafirstupdate.insert(0, date_out(data[1]))
            self.datalastupdate.insert(0, date_out(data[2]))
        else:
            self.datafirstupdate.insert(0, date_out(str(d.date.today())))
            self.datalastupdate.insert(0, date_out(str(d.date.today())))
        self.datadoc.insert(0, date_out(data[3]))
        if self.duplic:
            self.datavenc.insert(0, date_out(str(d.date.today())))
        elif not self.duplic:
            self.datavenc.insert(0, date_out(data[4]))
            self.datapago.insert(0, date_out(data[5]))
        self.parceiro.insert(0, query_list(self.conn, 'nome', 'parceiros', 'id = %s' % data[6])[0])
        if self.tipo_form in ('transf', 'cred'):
            values = query_list(self.conn, 'banco', 'diario', where='id = ' + str(int(self.data) - 1))
            self.banco.insert(0, query_list(self.conn, 'nomebanco', 'bancos', 'id = %s' % values[0])[0])
            self.bancorec.insert(0, query_list(self.conn, 'nomebanco', 'bancos', 'id = %s' % data[7])[0])
        else:
            self.banco.insert(0, query_list(self.conn, 'nomebanco', 'bancos', 'id = %s' % data[7])[0])
        self.descricao.insert(0, data[9])
        if self.tipo_form in ('pag', 'cred'):
            self.fatura.insert(0, data[8])
            if self.tipo_form == 'cred':
                self.descricao['state'] = 'normal'
                self.descricao.delete(0, 'end')
                self.descricao.insert(0, cmd_desc(self.conn, self.bancorec.get(), data[8]))
                self.descricao['state'] = 'disabled'
        if self.tipo_form != 'pag':
            self.valor.insert(0, Numbers(data[10]).get_str())
        else:
            self.valor.insert(0, Numbers(-data[10]).get_str())
        self.categoriamov.insert(0, query_list(self.conn, 'categoria, id', 'categorias', 'id = %s' % data[12])[0])
        self.usuario.insert(0, data[13])

    def cmd_datadoc(self, event=None):
        cmd_data(self.datadoc)

    def cmd_datavenc(self, event=None):
        cmd_data(self.datavenc)

    def cmd_datapago(self, event=None):
        cmd_data(self.datapago)

    def cmd_banco(self, event=None):
        cmd(self.banco)
        if self.tipo_form == 'pag':
            fatura = cmd_fat(self.conn, self.banco.get(), self.datadoc.get())
            self.fatura.delete(0, 'end')
            if fatura:
                self.fatura.insert(0, fatura['new_fat'])
                self.datavenc.delete(0, 'end')
                self.datavenc.insert(0, fatura['new_venc'])

    def cmd_bancorec(self, event=None):
        cmd(self.bancorec)

    def cmd_categoriamov(self, event=None):
        cmd(self.categoriamov)

    def cmd_fatura(self, event=None):
        if self.fatura.get() and self.tipo_form == 'pag':
            fatura = cmd_fat(self.conn, self.banco.get(), self.fatura.get(), True)
            self.datavenc.delete(0, 'end')
            if fatura and fatura['new_venc']:
                self.datavenc.insert(0, fatura['new_venc'])
            else:
                self.fatura.delete(0, 'end')

    def cmd_parceiro(self, event=None):
        cmd(self.parceiro)

    def cmd_valor(self, event=None):
        value = Numbers(self.valor.get())
        self.valor.delete(0, 'end')
        self.valor.insert(0, value.get_str())

    def cmd_cancel(self):
        self.instance.clear_mainframe()
        main = MovimentosForm(self.instance, self.conn, tipo_form=self.tipo_form, saved=self.saved)
        main.grid()
        main.cmd_seek()

    def cmd_confirm(self):
        descricao = self.descricao.get()
        if self.tipo_form == 'cred': descricao = '<CRED.CARD>'
        banco = self.banco.get()
        fatura = ''
        if self.tipo_form in ('pag', 'cred'):
            fatura = self.fatura.get()
            if self.tipo_form == 'pag':
                fat_g = GenerateFatura(self.conn, self.data, query_id(self.conn, 'bancos', ['nomebanco'], [True], banco), self.fatura.get())
                if fat_g.pago_anterior: descricao = None
                if fat_g.message: messagebox.showwarning(fat_g.message[0], fat_g.message[1])
        if self.parceiro.get() and self.banco.get() and descricao and self.valor.get() and self.categoriamov.get():
            resp = messagebox.askyesno(title='Confirmação', message='Tem certeza que deseja confirmar os dados?')            
            if resp:
                if self.tipo_form in ('pag', 'transf', 'cred'):
                    valor = str(-Numbers(self.valor.get()).get_val())
                else:
                    valor = str(Numbers(self.valor.get()).get_val())
                c = self.conn.cursor()
                if not self.data or self.duplic:
                    self.tipomov_d.reverse()
                    for tipomov in self.tipomov_d:
                        if tipomov == '3':
                            valor = str(-float(valor))
                            banco = self.bancorec.get()
                        elif tipomov == '4':
                            banco = self.banco.get()
                        c.execute('''INSERT INTO diario (datafirstupdate, datalastupdate, datadoc, datavenc, datapago, parceiro, banco, fatura, descricao, valor, tipomov, categoriamov, usuario)
                        VALUES("%s", "%s", "%s", "%s", "%s", %s, %s, "%s", "%s", %s, %s, %s, %s)''' % (
                            date_in(self.datafirstupdate.get()),
                            date_in(self.datalastupdate.get()),
                            date_in(self.datadoc.get()),
                            date_in(self.datavenc.get()),
                            date_in(self.datapago.get()),
                            query_id(self.conn, 'parceiros', ['nome'], [True], self.parceiro.get()),
                            query_id(self.conn, 'bancos', ['nomebanco'], [True], banco),
                            fatura,
                            descricao,
                            valor,
                            tipomov,
                            query_id(self.conn, 'categorias', ['categoria', 'id'], [True, False], self.categoriamov.get()),
                            self.usuario.get()
                        ))
                    # Compras parceladas.
                    if self.tipo_form == 'pag' and '/' in self.descricao.get():
                        test = self.descricao.get().split(' ')
                        descr = ' '.join(test[:-1])
                        parc = test[-1:]
                        parc = parc[0].split('/')
                        if len(parc) == 2:
                            try:
                                parcelas = int(parc[1])
                                new_venc = d.datetime.strptime(date_in(self.datavenc.get()), '%Y-%m-%d')
                                for p in range(2, parcelas + 1):
                                    try:
                                        new_venc = d.datetime(new_venc.year, new_venc.month + 1, new_venc.day)
                                    except:
                                        new_venc = d.datetime(new_venc.year + 1, 1, new_venc.day)
                                    descricao = '%s %s/%s' % (descr, p, parcelas)
                                    if fatura:
                                        new_fatura = str(new_venc)[0:7]
                                    else:
                                        new_fatura = ''
                                    c.execute('''INSERT INTO diario (datafirstupdate, datalastupdate, datadoc, datavenc, datapago, parceiro, banco, fatura, descricao, valor, tipomov, categoriamov, usuario)
                                    VALUES("%s", "%s", "%s", "%s", "%s", %s, %s, "%s", "%s", %s, %s, %s, %s)''' % (
                                        date_in(self.datafirstupdate.get()),
                                        date_in(self.datalastupdate.get()),
                                        date_in(self.datadoc.get()),
                                        str(new_venc)[0:10],
                                        '',
                                        query_id(self.conn, 'parceiros', ['nome'], [True], self.parceiro.get()),
                                        query_id(self.conn, 'bancos', ['nomebanco'], [True], banco),
                                        new_fatura,
                                        descricao,
                                        valor,
                                        tipomov,
                                        query_id(self.conn, 'categorias', ['categoria', 'id'], [True, False], self.categoriamov.get()),
                                        self.usuario.get()
                                    ))
                                    # Pra verificar lançar valores no cartão de crédito.
                                    if fatura:
                                        new_fat_g = GenerateFatura(self.conn, None, query_id(self.conn, 'bancos', ['nomebanco'], [True], banco), new_fatura)
                                        new_fat_g.run()
                            except:
                                pass
                else:
                    for tipomov in self.tipomov_d:
                        data = self.data
                        if tipomov == '3':
                            valor = str(-float(valor))
                            banco = self.bancorec.get()
                        elif tipomov == '4':
                            valor = str(-float(valor))
                            banco = self.banco.get()
                            data = str(int(data) - 1)
                        c.execute('''UPDATE diario
                        SET datafirstupdate = "%s", datalastupdate = "%s", datadoc = "%s", datavenc = "%s", datapago = "%s", parceiro = %s, banco = %s, fatura = "%s", descricao = "%s", valor = %s, tipomov = %s, categoriamov = "%s", usuario = %s
                        WHERE id = %s''' % (
                            date_in(self.datafirstupdate.get()),
                            date_in(self.datalastupdate.get()),
                            date_in(self.datadoc.get()),
                            date_in(self.datavenc.get()),
                            date_in(self.datapago.get()),
                            query_id(self.conn, 'parceiros', ['nome'], [True], self.parceiro.get()),
                            query_id(self.conn, 'bancos', ['nomebanco'], [True], banco),
                            fatura,
                            descricao,
                            valor,
                            tipomov,
                            query_id(self.conn, 'categorias', ['categoria', 'id'], [True, False], self.categoriamov.get()),
                            self.usuario.get(),
                            data
                        ))
                # Atualiza saldo de cartões
                if self.tipo_form == 'pag':
                    fat_g.run()
                if self.tipo_form == 'cred':
                    cmd = 'UPDATE diario SET datapago = "%s" WHERE banco = %s AND fatura = "%s" AND tipomov = 1' % (
                        date_in(self.datapago.get()),
                        query_id(self.conn, 'bancos', ['nomebanco'], [True], self.bancorec.get()),
                        fatura
                    )
                    print(cmd)
                    c.execute(cmd)
                self.conn.commit()
                messagebox.showinfo('Informação', 'Dados atualizados com sucesso!')
                self.instance.clear_mainframe()
                main = MovimentosForm(self.instance, self.conn, tipo_form=self.tipo_form, saved=self.saved)
                main.grid()
                main.cmd_seek()
        else:
            messagebox.showerror(title='Aviso', message='Não é possível atualizar. Verifique os dados preenchidos.')


class CashflowForm:
    # Objetivo: 
    def __init__(self, instance, conn, saved={}):
        self.conn = conn
        self.instance = instance
        self.bg = BGFORM
        self.mainframe = instance.mainframe
        self.frame = Frame(self.mainframe, bd=1, bg=BGFORM, relief='sunken')
        self.filter_frame = Frame(self.frame, bd=1, bg=BGFORM, width=60, relief='groove')
        values = query_list(self.conn, 'nomebanco', 'bancos', order_by='nomebanco')
        values = ['Todos os bancos'] + values
        self.banco_l = Label(self.filter_frame, anchor='e', text='Banco ', bg=BGFORM, width=12)
        self.banco = Combobox(self.filter_frame, width=20, values=values)
        self.banco.bind("<FocusOut>", self.cmd_seek)
        self.vencini_l = Label(self.filter_frame, anchor='e', text='Venc Inicial ', bg=self.bg, width=12)
        self.vencini = Entry(self.filter_frame, width=10)
        self.vencini.bind("<FocusOut>", self.cmd_seek)
        self.vencfin_l = Label(self.filter_frame, anchor='e', text='Venc Final ', bg=self.bg, width=12)
        self.vencfin = Entry(self.filter_frame, width=10)
        self.vencfin.bind("<FocusOut>", self.cmd_seek)
        self.dash_frame = Frame(self.frame, bd=1, bg=BGFORM, width=60, relief='groove')
        self.entradas_l = Label(self.dash_frame, anchor='e', text='Entradas no período: ', font='Arial 11 bold', bg=self.bg, width=25)
        self.entradas = Label(self.dash_frame, anchor='e', text='0,00', font='Arial 12 bold', bg='white', fg='blue', relief='sunken', width=10)
        self.saidas_l = Label(self.dash_frame, anchor='e', text='Saídas no período: ', font='Arial 11 bold', bg=self.bg, width=25)
        self.saidas = Label(self.dash_frame, anchor='e', text='0,00', font='Arial 12 bold', bg='white', fg='red', relief='sunken', width=10)
        self.saldo_l = Label(self.dash_frame, anchor='e', text='Confronto: ', font='Arial 11 bold', bg=self.bg, width=25)
        self.saldo = Label(self.dash_frame, anchor='e', text='0,00', font='Arial 12 bold', bg='white', relief='sunken', width=10)
        self.fr1 = Frame(self.frame, bd=1, bg=BGFORM, relief='sunken')
        self.height = int(instance.root.winfo_height() - 260)
        self.fr1.configure(height=self.height, width=820)
        self.fr1.grid_propagate(0)
        self.fr1_place = Frame(self.fr1)
        self.table1 = Treeview(self.fr1_place, height=20)
        self.sb_y = Scrollbar(self.fr1_place, orient="vertical", command=self.table1.yview)
        self.sb_x = Scrollbar(self.fr1_place, orient="horizontal", command=self.table1.xview)
        self.table1.configure(yscroll=self.sb_y.set, xscroll=self.sb_x.set)
        self.buttons = Frame(self.frame, bg=BGFORM, width=30)
        self.pagar = Button(self.buttons, text='Pagar compromissos selecionados', width=30, command=self.cmd_pagar)
        self.quit = Button(self.buttons, text='Sair', width=10, command=self.cmd_quit)
        if 'banco' in saved and saved['banco']: self.banco.insert('end', saved['banco'])
        if not self.vencini.get() and not saved: self.vencini.insert(0, '%s' % (date_out(str(d.date.today())[:-2] + '01')))
        if not self.vencfin.get() and not saved: self.vencfin.insert(0, '%s' % (date_out(str(lastdaymonth(d.date.today())))))
        self.banco.focus()

    def grid(self):
        #Label(self.mainframe, text='', width=10, bg=BGCOLOR).grid(row=0, column=0)
        Label(self.mainframe, text='FLUXO DE CAIXA - EXTRATO DE MOVIMENTO', width=60, bg=BGCOLOR, font=('Arial Bold', 16)).grid(row=1, column=0)
        self.frame.grid(row=2, column=0)
        Label(self.frame, text='\n', width=5, height=10, bg=BGFORM).grid(row=0, column=0, rowspan=5) # remover espaço para Enter.
        Label(self.frame, text='', bg=BGFORM, width=50).grid(row=0, column=1, columnspan=2)
        self.filter_frame.grid(row=1, column=1)
        Label(self.filter_frame, text='\n', width=0, height=5, bg=BGFORM).grid(row=0, column=0, rowspan=5) # remover espaço para Enter.
        self.banco_l.grid(row=1, column=1)
        self.banco.grid(row=1, column=2, stick='w')
        self.vencini_l.grid(row=2, column=1)
        self.vencini.grid(row=2, column=2, stick='w')
        self.vencfin_l.grid(row=3, column=1)
        self.vencfin.grid(row=3, column=2, stick='w')
        Label(self.filter_frame, text='', width=2, bg=BGFORM).grid(row=3, column=3) # remover espaço para Enter.
        self.dash_frame.grid(row=1, column=2)
        Label(self.dash_frame, text='\n', width=0, height=5, bg=BGFORM).grid(row=0, column=0, rowspan=5) # remover espaço para Enter.
        self.entradas_l.grid(row=1, column=1)
        self.entradas.grid(row=1, column=2, stick='w')
        self.saidas_l.grid(row=2, column=1)
        self.saidas.grid(row=2, column=2, stick='w')
        self.saldo_l.grid(row=3, column=1)
        self.saldo.grid(row=3, column=2, stick='w')
        Label(self.dash_frame, text='', width=2, bg=BGFORM).grid(row=3, column=3) # remover espaço para Enter.
        Label(self.frame, text='', bg=BGFORM, width=5).grid(row=2, column=1)
        self.fr1.grid(row=3, column=1, columnspan=2, stick='w')
        self.fr1_place.place(bordermode='outside', height=self.height, width=820)
        self.sb_y.pack(side="right", fill='y')
        self.sb_x.pack(side="bottom", fill='x')
        self.table1.pack(expand=1)
        self.buttons.grid(row=4, column=1, columnspan=2)
        Label(self.buttons, text='', bg=BGFORM, width=50).grid(row=0, column=1, columnspan=3)
        self.pagar.grid(row=1, column=1)
        self.quit.grid(row=1, column=3)
        Label(self.frame, text='', bg=BGFORM, width=5).grid(row=5, column=1)
        Label(self.frame, text='', bg=BGFORM, width=5).grid(row=5, column=3)

    def data(self, filter1='', filter2='', initial_date='', bank='', order=''):
        c = self.conn.cursor()
        valor1 = 0.0
        valor2 = 0.0
        if initial_date:
            cmd = 'SELECT SUM(valor) FROM diario JOIN bancos on bancos.id = banco WHERE datavenc < "%s" AND diario.tipomov in (0, 3)' % initial_date
            if bank:
                cmd += bank
            c.execute(cmd)
            valor = c.fetchone()
            if valor: valor1 = valor[0]
            cmd = 'SELECT SUM(valor) FROM diario JOIN bancos on bancos.id = banco WHERE datavenc < "%s" AND diario.tipomov in (1, 4)' % initial_date
            if bank:
                cmd += bank
            c.execute(cmd)
            valor = c.fetchone()
            if valor: valor2 = valor[0]
        if valor1 == None: valor1 = 0.0
        if valor2 == None: valor2 = 0.0
        _dados = [
            ['', '', '', 'Saldo Inicial', '0,00', '0,00', Numbers(round(valor2 + valor1, 2)).get_str(), '', '', '', '', '', '', '', '', '']
        ]
        amount = round(valor2 + valor1, 2)
        dados = []
        for r in range(2):
            cmd = 'SELECT diario.id, bancos.nomebanco, parceiros.nome, categorias.categoria, valor, datavenc, datapago, datafirstupdate, datalastupdate, datadoc, '
            cmd += 'fatura, descricao, diario.tipomov, diario.usuario FROM diario '
            cmd += 'JOIN parceiros on parceiros.id = diario.parceiro '
            cmd += 'JOIN bancos on bancos.id = diario.banco '
            cmd += 'JOIN categorias on categorias.id = diario.categoriamov '
            if r == 0:
                if filter1: cmd += filter1
                cmd += ' ORDER BY datapago'
            if r == 1:
                if filter2: cmd += filter2
                cmd += ' ORDER BY datavenc'
            c.execute(cmd)
            dados.append(c.fetchall())
        #_dados = []
        entradas = 0.0
        saidas = 0.0
        for dad in dados:
            for i in dad:
                valor = Numbers(i[6]).get_str()
                entra = ''
                sai = ''
                if i[12] in [0, 3]:
                    entra = Numbers(float(i[4])).get_str()
                    entradas += float(i[4])
                elif i[12] in [1, 4]:
                    sai = Numbers(-float(i[4])).get_str()
                    saidas += float(i[4])
                amount += float(i[4])
                saldo = Numbers(amount).get_str()
                _dados.append([
                    i[0],
                    i[1],
                    i[2],
                    i[3],
                    entra,
                    sai,
                    saldo,
                    date_out(i[5]),
                    date_out(i[6]),
                    date_out(i[7]),
                    date_out(i[8]),
                    date_out(i[9]),
                    i[10],
                    i[11],
                    i[12],
                    i[13],
                ])
            dados = _dados
        # Preenche a tabela
        self.table1['columns'] = ['Banco', 'Parceiro', 'Categoria', 'Entra', 'Sai', 'Saldo', 'Vence em', 'Pago em', 'datafirstupdate', 'datalastupdate', 'datadoc', 'fatura', 'descricao', 'tipomov', 'usuario']
        columns = {
            'id': 50, 'Banco': 130, 'Parceiro': 130, 'Categoria': 135, 'Entra': 65, 'Sai': 65, 'Saldo': 70, 'Vence em': 80, 'Pago em': 80, 'datafirstupdate': 120, 'datalastupdate': 120, 'datadoc': 120, 'fatura': 120, 'descricao': 120, 'tipomov': 120, 'usuario': 120
        }
        self.table1.heading('#0', text='Id', anchor='center')
        self.table1.column('#0', anchor='w', width=50)
        self.table1.delete(*self.table1.get_children())
        self.table1.tag_configure('positive', foreground='blue')
        self.table1.tag_configure('negative', foreground='red')
        for row in self.table1['columns']:
            self.table1.heading(
                row, 
                text=row, 
                anchor='center' 
            )
            if row in ['Entra', 'Sai', 'Saldo']:
                anchor = 'e'
            else:
                anchor = 'w'
            self.table1.column(row, anchor=anchor, width=columns[row])
        index = 1
        for row in dados:
            if Numbers(row[6]).get_val() < 0.0:
                self.table1.insert('', 'end', text=str(row[0]), values=row[1:], tag='negative')
            else:
                self.table1.insert('', 'end', text=str(row[0]), values=row[1:])
            index += 1
        self.entradas['text'] = Numbers(entradas).get_str()
        self.saidas['text'] = Numbers(-saidas).get_str()
        self.saldo['text'] = Numbers(entradas + saidas).get_str()
        self.saldo['fg'] = 'blue'
        if entradas + saidas < 0.0:
            self.saldo['fg'] = 'red'

    def cmd_seek(self, event=None):
        cmd(self.banco)
        cmd_data(self.vencini)
        cmd_data(self.vencfin)
        filter1 = ''
        filter2 = ''
        pre = 'WHERE'
        bank = None
        if self.banco.get() and self.banco.get() != 'Todos os bancos':
            filter1 += ' %s nomebanco = "%s"' % (pre, self.banco.get())
            filter2 += ' %s nomebanco = "%s"' % (pre, self.banco.get())
            bank = ' %s nomebanco = "%s"' % (' AND ', self.banco.get())
            pre = 'AND'
        elif self.banco.get() and self.banco.get() == 'Todos os bancos':
            filter1 += ' %s bancos.tipomov IN (0, 1)' % (pre)
            filter2 += ' %s bancos.tipomov IN (0, 1)' % (pre)
            bank = ' %s bancos.tipomov IN (0, 1)' % (' AND ')
            pre = 'AND'
        elif not self.banco.get():
            filter1 += ' %s nomebanco = "XXX"' % (pre)
            filter2 += ' %s nomebanco = "XXX"' % (pre)
            bank = ' %s nomebanco = "XXX"' % (' AND ')
            pre = 'AND'
        if self.vencini.get():
            filter1 += ' %s datapago >= "%s"' % (pre, date_in(self.vencini.get()))
            initial_date = date_in(self.vencini.get())
            filter2 += ' %s datavenc >= "%s" AND datapago = ""' % (pre, date_in(self.vencini.get()))
            pre = 'AND'
        if self.vencfin.get():
            filter1 += ' %s datapago <= "%s"' % (pre, date_in(self.vencfin.get()))
            filter2 += ' %s datavenc <= "%s" AND datapago = ""' % (pre, date_in(self.vencfin.get()))
            pre = 'AND'
        self.data(filter1=filter1, filter2=filter2, initial_date=initial_date, bank=bank)
        
    def cmd_pagar(self):
        resp = messagebox.askyesno('Aviso', 'Tem certeza que deseja realizar a baixa dos documentos selecionados?')
        if resp:
            c = self.conn.cursor()
            saved = {}
            if self.banco.get():
                saved['banco'] = self.banco.get()
            if self.vencini.get():
                saved['vencini'] = self.vencini.get()
            if self.vencfin.get():
                saved['vencfin'] = self.vencfin.get()
            try:
                region = self.table1.identify("region", event.x, event.y)
            except:
                region = 'cell'
            #column = form.fields['table'].identify("column", event.x, event.y)
            #cell = form.fields['table'].identify("row", event.x, event.y)
            _id = None
            if region == "cell":
                if self.table1.selection():
                    for i in self.table1.selection():
                        _id = str(self.table1.item(i, 'text'))
                        command = 'SELECT datapago, tipomov, descricao FROM diario WHERE id = %s' % (_id)
                        c.execute(command)
                        resp = c.fetchone()
                        if resp[2] == '<CRED.CARD>':
                            messagebox.showwarning('Aviso', 'Foi selecionada fatura de cartão de crédito entre os documnentos. Realize o pagamento na seção de Cartões de Crédito.')
                            continue
                        actual_date = str(d.datetime.now().date())
                        if not resp[0]:
                            if resp[1] == 3:
                                command = 'UPDATE diario SET datapago = "%s" WHERE id = %s AND datapago = ""' % (actual_date, _id)
                                c.execute(command)
                                command = 'UPDATE diario SET datapago = "%s" WHERE id = %s AND datapago = ""' % (actual_date, int(_id) - 1)
                                c.execute(command)
                            elif resp[1] == 4:
                                command = 'UPDATE diario SET datapago = "%s" WHERE id = %s AND datapago = ""' % (actual_date, _id)
                                c.execute(command)
                                command = 'UPDATE diario SET datapago = "%s" WHERE id = %s AND datapago = ""' % (actual_date, int(_id) + 1)
                                c.execute(command)
                            else:
                                command = 'UPDATE diario SET datapago = "%s" WHERE id = %s AND datapago = ""' % (actual_date, _id)
                                c.execute(command)
                    self.conn.commit()
                    self.cmd_seek()
                    messagebox.showinfo(title='Baixas realizadas', message='Documentos selecionados foram baixados com data de hoje.')
                else:
                    messagebox.showerror(title='Atenção', message='Selecione um registro para a baixa.')

    def cmd_quit(self):
        self.instance.clear_mainframe()
        MainPanel(self.instance, self.conn).grid()


class ReportForm:
    # Objetivo: 
    def __init__(self, instance, conn, saved={}):
        self.conn = conn
        self.instance = instance
        self.bg = BGFORM
        self.mainframe = instance.mainframe
        self.frame = Frame(self.mainframe, bd=1, bg=BGFORM, relief='sunken')
        self.filter_frame = Frame(self.frame, bd=1, bg=BGFORM, width=60, relief='groove')
        values = query_list(self.conn, 'nomebanco', 'bancos', order_by='nomebanco')
        self.banco_l = Label(self.filter_frame, anchor='e', text='Banco ', bg=BGFORM, width=12)
        self.banco = Combobox(self.filter_frame, width=18, values=values)
        self.banco.bind("<FocusOut>", self.cmd_seek)
        values = query_list(self.conn, 'categoria', 'categorias', where='tipomov = 1 AND classifica = 1', order_by='categoria')
        self.categoriamov_l = Label(self.filter_frame, anchor='e', text='Categoria ', bg=BGFORM, width=12)
        self.categoriamov = Combobox(self.filter_frame, width=18, values=values)
        self.categoriamov.bind("<FocusOut>", self.cmd_seek)
        values = query_list(self.conn, 'nome', 'parceiros', where='modo IN (0, 2)', order_by='nome')
        self.parceiro_l = Label(self.filter_frame, anchor='e', text='Parceiro ', bg=BGFORM, width=12)
        self.parceiro = Combobox(self.filter_frame, width=18, values=values)
        self.parceiro.bind("<FocusOut>", self.cmd_seek)
        self.dataini_l = Label(self.filter_frame, anchor='e', text='Data Inicial ', bg=self.bg, width=14)
        self.dataini = Entry(self.filter_frame, width=12)
        self.dataini.bind("<FocusOut>", self.cmd_seek)
        self.datafin_l = Label(self.filter_frame, anchor='e', text='Data Final ', bg=self.bg, width=14)
        self.datafin = Entry(self.filter_frame, width=12)
        self.datafin.bind("<FocusOut>", self.cmd_seek)
        self.valor_l = Label(self.filter_frame, anchor='e', text='Período em R$ ', font='Arial 11 bold', bg=self.bg, width=16)
        self.valor = Label(self.filter_frame, anchor='e', text='0,00', font='Arial 12 bold', bg='white', fg='blue', relief='sunken', width=10)
        #self.gerafatura_v = IntVar()
        #self.gerafatura_l = Label(self.filter_frame, anchor='e', text='Visualização ', bg=self.bg, width=12)
        #self.gerafatura = Checkbutton(self.frame, text='Resumo mensal', bg=BGFORM, width=5, variable=self.gerafatura_v)
        self.fr1 = Frame(self.frame, bd=1, bg=BGFORM, relief='sunken')
        self.height = int(instance.root.winfo_height() - 260)
        self.fr1.configure(height=self.height, width=500)
        self.fr1.grid_propagate(0)
        self.fr1_place = Frame(self.fr1)
        self.table1 = Treeview(self.fr1_place, height=20)
        self.sb_y = Scrollbar(self.fr1_place, orient="vertical", command=self.table1.yview)
        self.sb_x = Scrollbar(self.fr1_place, orient="horizontal", command=self.table1.xview)
        self.table1.configure(yscroll=self.sb_y.set, xscroll=self.sb_x.set)
        self.buttons = Frame(self.frame, bg=BGFORM, width=30)
        self.pagar = Button(self.buttons, text='Pagar compromissos selecionados', width=30, command=self.cmd_pagar)
        self.quit = Button(self.buttons, text='Sair', width=10, command=self.cmd_quit)
        if 'banco' in saved and saved['banco']: self.banco.insert('end', saved['banco'])
        if not self.dataini.get() and not saved: self.dataini.insert(0, '%s' % (date_out(str(d.date.today())[:-2] + '01')))
        if not self.datafin.get() and not saved: self.datafin.insert(0, '%s' % (date_out(str(lastdaymonth(d.date.today())))))
        self.banco.focus()

    def grid(self):
        #Label(self.mainframe, text='', width=10, bg=BGCOLOR).grid(row=0, column=0)
        Label(self.mainframe, text='RELATÓRIO DIÁRIO DE COMPRAS', width=60, bg=BGCOLOR, font=('Arial Bold', 16)).grid(row=1, column=0)
        self.frame.grid(row=2, column=0)
        Label(self.frame, text='\n', width=5, height=10, bg=BGFORM).grid(row=0, column=0, rowspan=5) # remover espaço para Enter.
        Label(self.frame, text='', bg=BGFORM, width=50).grid(row=0, column=1, columnspan=2)
        self.filter_frame.grid(row=1, column=1)
        Label(self.filter_frame, text='\n', width=0, height=5, bg=BGFORM).grid(row=0, column=0, rowspan=5) # remover espaço para Enter.
        self.banco_l.grid(row=1, column=1)
        self.banco.grid(row=1, column=2, stick='w')
        self.categoriamov_l.grid(row=2, column=1)
        self.categoriamov.grid(row=2, column=2, stick='w')
        self.parceiro_l.grid(row=3, column=1)
        self.parceiro.grid(row=3, column=2, stick='w')
        self.dataini_l.grid(row=1, column=3)
        self.dataini.grid(row=1, column=4, stick='w')
        self.datafin_l.grid(row=2, column=3)
        self.datafin.grid(row=2, column=4, stick='w')
        self.valor_l.grid(row=3, column=3)
        self.valor.grid(row=3, column=4, stick='w')
        Label(self.filter_frame, text='', width=2, bg=BGFORM).grid(row=3, column=5) # remover espaço para Enter.
        Label(self.frame, text='', bg=BGFORM, width=5).grid(row=2, column=1)
        self.fr1.grid(row=3, column=1, columnspan=2, stick='w')
        self.fr1_place.place(bordermode='outside', height=self.height, width=500)
        self.sb_y.pack(side="right", fill='y')
        self.sb_x.pack(side="bottom", fill='x')
        self.table1.pack(expand=1)
        self.buttons.grid(row=4, column=1, columnspan=2)
        Label(self.buttons, text='', bg=BGFORM, width=50).grid(row=0, column=1, columnspan=3)
        self.pagar.grid(row=1, column=1)
        self.quit.grid(row=1, column=3)
        Label(self.frame, text='', bg=BGFORM, width=5).grid(row=5, column=1)
        Label(self.frame, text='', bg=BGFORM, width=5).grid(row=5, column=3)

    def data(self, filter='', categ='', order='datadoc'):
        c = self.conn.cursor()
        acum = 0.0
        categs = {
            'MERCADO': 900,
            'CHURRASCO': 200,
            'SAÚDE': 150,
            'TELEFONE E INTERNET': 260
        }
        if categ:
            if categ in categs:
                meta = categs[categ]
            else:
                meta = 100.0
        else:
            meta = 5900.0
        dados = []
        cmd = 'SELECT datadoc, SUM(valor) FROM diario '
        cmd += 'JOIN parceiros on parceiros.id = diario.parceiro '
        cmd += 'JOIN bancos on bancos.id = diario.banco '
        cmd += 'JOIN categorias on categorias.id = diario.categoriamov '
        if filter: cmd += filter
        cmd += ' GROUP BY datadoc ORDER BY %s' % order
        c.execute(cmd)
        dados = c.fetchall()
        _dados = []
        count = 1
        for i in dados:
            acum -= float(i[1])
            meta += float(i[1])
            _dados.append([
                str(count),
                date_out(i[0]),
                Numbers(-i[1]).get_str(),
                Numbers(acum).get_str(),
                Numbers(meta).get_str(),
            ])
            count += 1
        dados = _dados
        # Preenche a tabela
        self.table1['columns'] = ['Data', 'Valor dia', 'Valor acumulado', 'Disponível']
        columns = {
            'id': 50, 'Data': 100, 'Valor dia': 100, 'Valor acumulado': 120, 'Disponível': 110
        }
        self.table1.heading('#0', text='Id', anchor='center')
        self.table1.column('#0', anchor='w', width=50)
        self.table1.delete(*self.table1.get_children())
        self.table1.tag_configure('total', background='green yellow')
        for row in self.table1['columns']:
            self.table1.heading(
                row, 
                text=row, 
                anchor='center' 
            )
            if row in ['Valor dia', 'Valor acumulado', 'Disponível']:
                anchor = 'e'
            else:
                anchor = 'w'
            self.table1.column(row, anchor=anchor, width=columns[row])
        index = 1
        for row in dados:
            self.table1.insert('', 'end', text=str(row[0]), values=row[1:])
            index += 1
        self.valor['text'] = Numbers(acum).get_str()
        if acum < 0.0:
            self.saldo['fg'] = 'red'

    def cmd_seek(self, event=None, order_by='datadoc, datavenc'):
        cmd(self.banco)
        cmd(self.categoriamov)
        cmd(self.parceiro)
        cmd_data(self.dataini)
        cmd_data(self.datafin)
        filter = ''
        pre = 'WHERE'
        filter += ' %s diario.tipomov = 1' % pre
        pre = 'AND'
        categ = None
        if self.banco.get():
            filter += ' %s nomebanco = "%s"' % (pre, self.banco.get())
            pre = 'AND'
        if self.categoriamov.get():
            filter += ' %s categorias.categoria = "%s"' % (pre, self.categoriamov.get())
            categ = self.categoriamov.get()
            pre = 'AND'
        if self.parceiro.get():
            filter += ' %s parceiros.nome = "%s"' % (pre, self.parceiro.get())
            pre = 'AND'
        if self.dataini.get():
            filter += ' %s datadoc >= "%s"' % (pre, date_in(self.dataini.get()))
            pre = 'AND'
        if self.datafin.get():
            filter += ' %s datadoc <= "%s"' % (pre, date_in(self.datafin.get()))
            pre = 'AND'
        self.data(filter=filter, categ=categ)
        
    def cmd_pagar(self):
        messagebox.showwarning(title='Informação', message='Ainda não está disponível.')

    def cmd_quit(self):
        self.instance.clear_mainframe()
        MainPanel(self.instance, self.conn).grid()


class FechamentoForm:
    # Objetivo: 
    def __init__(self, instance, conn, saved={}):
        self.conn = conn
        self.instance = instance
        self.bg = BGFORM
        self.mainframe = instance.mainframe
        self.frame = Frame(self.mainframe, bd=1, bg=BGFORM, relief='sunken')
        self.filter_frame = Frame(self.frame, bd=1, bg=BGFORM, width=60, relief='groove')
        self.mesini_l = Label(self.filter_frame, anchor='e', text='Mês Inicial ', bg=self.bg, width=11)
        self.mesini = Entry(self.filter_frame, width=12)
        self.mesini.bind("<FocusOut>", self.cmd_seek)
        self.mesfin_l = Label(self.filter_frame, anchor='e', text='Mês Final ', bg=self.bg, width=11)
        self.mesfin = Entry(self.filter_frame, width=12)
        self.mesfin.bind("<FocusOut>", self.cmd_seek)
        self.valor_l = Label(self.filter_frame, anchor='e', text='Período em R$ ', font='Arial 11 bold', bg=self.bg, width=16)
        self.valor = Label(self.filter_frame, anchor='e', text='0,00', font='Arial 12 bold', bg='white', fg='blue', relief='sunken', width=10)
        self.fr1 = Frame(self.frame, bd=1, bg=BGFORM, relief='sunken')
        self.height = int(instance.root.winfo_height() - 260)
        self.fr1.configure(height=self.height, width=800)
        self.fr1.grid_propagate(0)
        self.fr1_place = Frame(self.fr1)
        self.table1 = Treeview(self.fr1_place, height=20)
        self.sb_y = Scrollbar(self.fr1_place, orient="vertical", command=self.table1.yview)
        self.sb_x = Scrollbar(self.fr1_place, orient="horizontal", command=self.table1.xview)
        self.table1.configure(yscroll=self.sb_y.set, xscroll=self.sb_x.set)
        self.table1.bind("<Button-1>", self.cmd_table)
        self.table1.bind("<Double-1>", self.cmd_table)
        self.asc = True # Ordem ascendente ou descendente
        self.buttons = Frame(self.frame, bg=BGFORM, width=30)
        self.gerar = Button(self.buttons, text='Gerar resumo em CSV', width=30, command=self.cmd_gerar)
        self.quit = Button(self.buttons, text='Sair', width=10, command=self.cmd_quit)
        if not self.mesini.get() and not saved: self.mesini.insert(0, '%s-01' % d.date.today().year)
        if not self.mesfin.get() and not saved: self.mesfin.insert(0, '%s-12' % d.date.today().year)
        self.mesini.focus()

    def grid(self):
        #Label(self.mainframe, text='', width=10, bg=BGCOLOR).grid(row=0, column=0)
        Label(self.mainframe, text='DEMONSTRATIVO DESPESAS POR CATEGORIA', width=60, bg=BGCOLOR, font=('Arial Bold', 16)).grid(row=1, column=0)
        self.frame.grid(row=2, column=0)
        Label(self.frame, text='\n', width=5, height=10, bg=BGFORM).grid(row=0, column=0, rowspan=5) # remover espaço para Enter.
        Label(self.frame, text='', bg=BGFORM, width=80).grid(row=0, column=1, columnspan=2)
        self.filter_frame.grid(row=1, column=1, columnspan=2)
        Label(self.filter_frame, text='\n', width=0, height=5, bg=BGFORM).grid(row=0, column=0, rowspan=4) # remover espaço para Enter.
        self.mesini_l.grid(row=1, column=1)
        self.mesini.grid(row=1, column=2, stick='w')
        self.mesfin_l.grid(row=2, column=1)
        self.mesfin.grid(row=2, column=2, stick='w')
        Label(self.filter_frame, text='', width=2, bg=BGFORM).grid(row=2, column=3) # remover espaço para Enter.
        Label(self.frame, text='', bg=BGFORM, width=5).grid(row=2, column=1)
        self.fr1.grid(row=3, column=1, columnspan=2, stick='w')
        self.fr1_place.place(bordermode='outside', height=self.height, width=800)
        self.sb_y.pack(side="right", fill='y')
        self.sb_x.pack(side="bottom", fill='x')
        self.table1.pack(expand=1)
        self.buttons.grid(row=4, column=1, columnspan=2)
        Label(self.buttons, text='', bg=BGFORM, width=50).grid(row=0, column=1, columnspan=3)
        self.gerar.grid(row=1, column=1)
        self.quit.grid(row=1, column=3)
        Label(self.frame, text='', bg=BGFORM, width=5).grid(row=5, column=1)
        Label(self.frame, text='', bg=BGFORM, width=5).grid(row=5, column=3)

    def data(self, filter='', bank='', order=''):
        c = self.conn.cursor()
        cmd = 'SELECT SUBSTR(datadoc, 0, 8) AS mes FROM diario JOIN categorias on categorias.id = diario.categoriamov '
        if filter: cmd += filter
        cmd += ' GROUP BY mes ORDER BY mes'
        c.execute(cmd)
        dados = c.fetchall()
        months = []
        for i in dados:
            months.append(i[0])
        cmd = 'SELECT categorias.categoria FROM diario JOIN categorias on categorias.id = diario.categoriamov '
        if filter: cmd += filter
        cmd += ' GROUP BY categorias.categoria ORDER BY categorias.categoria'
        c.execute(cmd)
        dados = c.fetchall()
        categs = {}
        for i in dados:
            categs[i[0]] = {}
            for m in months:
                categs[i[0]][m] = 0.0
        cmd = 'SELECT categorias.categoria, SUBSTR(datadoc, 0, 8) AS mes, SUM(valor) FROM diario '
        cmd += 'JOIN parceiros on parceiros.id = diario.parceiro '
        cmd += 'JOIN bancos on bancos.id = diario.banco '
        cmd += 'JOIN categorias on categorias.id = diario.categoriamov '
        if filter: cmd += filter
        cmd += ' GROUP BY categorias.categoria, mes ORDER BY mes, categorias.categoria'
        c.execute(cmd)
        dados = c.fetchall()
        for i in dados:
            categs[i[0]][i[1]] = round(i[2], 2)
        categs_list = list(categs.keys())
        if order:
            order = order.split(' ')
            if order[0] == 'Categoria':
                reverse = False
                if order[1] == 'DESC': reverse = True
                categs_list.sort(reverse=reverse)
            else:
                if order[0] in months:
                    sorter = []
                    for i in categs:
                        if categs[i][order[0]] < 0:
                            signal = '-'
                        sorter.append('%s %s' % (str(round(abs(categs[i][order[0]] * 100))).zfill(10), i))
                        # Presume-se que aqui só entra números negativos. Se houver positivos, é necessário mudar a regra
                reverse = False
                if order[1] == 'DESC': reverse = True
                sorter.sort(reverse=reverse)
                categs_list = []
                for i in sorter:
                    categs_list.append(i[11:])
        _dados = []
        count = 1
        for i in categs_list:
            new_line = [str(count), i]
            for m in months:
                new_line.append(Numbers(-float(categs[i][m])).get_str())
            _dados.append(new_line)
            count += 1
        dados = _dados
        # Preenche a tabela
        new_cols = {}
        tam = int(580 / len(months))
        if tam <= 80: tam = 80
        for i in months:
            new_cols[i] = tam
        self.table1['columns'] = ['Categoria'] + months
        columns = {
            'id': 50, 'Categoria': 170
        }
        columns.update(new_cols)
        self.table1.heading('#0', text='Id', anchor='center')
        self.table1.column('#0', anchor='w', width=50)
        self.table1.delete(*self.table1.get_children())
        self.table1.tag_configure('total', background='green yellow')
        for row in self.table1['columns']:
            self.table1.heading(
                row, 
                text=row, 
                anchor='center' 
            )
            if row in ['Categoria']:
                anchor = 'w'
            else:
                anchor = 'e'
            self.table1.column(row, anchor=anchor, width=columns[row])
        index = 1
        for row in dados:
            self.table1.insert('', 'end', text=str(row[0]), values=row[1:])
            index += 1

    def cmd_seek(self, event=None, order=''):
        #cmd(self.banco)
        #cmd(self.categoriamov)
        filter = ''
        pre = 'WHERE'
        filter += ' %s diario.tipomov = 1 AND categorias.classifica = 1' % pre
        pre = 'AND'
        if self.mesini.get():
            _date = self.mesini.get() + '-01'
            filter += ' %s datadoc >= "%s"' % (pre, _date)
            pre = 'AND'
        if self.mesfin.get():
            _date = str(lastdaymonth(self.mesfin.get() + '01'))
            filter += ' %s datadoc <= "%s"' % (pre, _date)
            pre = 'AND'
        self.data(filter=filter, order=order)

    def cmd_table(self, event=None):
        try:
            region = self.table1.identify("region", event.x, event.y)
        except:
            region = 'cell'
        #cell = form.fields['table'].identify("row", event.x, event.y)
        if region == 'heading':
            column = self.table1.identify("column", event.x, event.y)
            try:
                if self.asc:
                    self.cmd_seek(order=self.table1.column(int(column[1:])-1)['id'] + ' ASC')
                    self.asc = False
                else:
                    self.cmd_seek(order=self.table1.column(int(column[1:])-1)['id'] + ' DESC')
                    self.asc = True
            except:
                pass

    def cmd_gerar(self):
        messagebox.showwarning(title='Informação', message='Ainda não está disponível.')

    def cmd_quit(self):
        self.instance.clear_mainframe()
        MainPanel(self.instance, self.conn).grid()
