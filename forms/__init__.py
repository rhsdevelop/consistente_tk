#!/usr/bin/python3.5
import base64
import platform
import random
import sqlite3
import sys
import tkinter
from datetime import date, datetime, timedelta
from tkinter import messagebox, ttk
from unicodedata import normalize

from config import *
from ttkcalendar import Calendar


class FalseRoutine():
    ''' Classe que instancia objetos fakes '''
    def __init__ (self):
        pass
    
    def get(self, value=None):
        return value


class Widgets():
    ''' Classe que instancia os widgets nos formulários. '''
    def __init__(self, instance, color=''):
        self.instance = instance
        self.color = color

    def button(self, field, cmd, textwidth, height, row, col, colspan=0, fontwidth=9):
        ''' Inserir button em formulários. '''
        text = tkinter.Button(self.instance, text=field, width=textwidth, command=cmd, font=(fonte, fontwidth, 'bold'))
        if colspan:
            text.grid(row=row, column=col, columnspan=colspan)
        else:
            text.grid(row=row, column=col)
        return text

    def label(self, field, textwidth, row, col, colspan=1, rowspan=1, fg='', height=0, stick=None, fontwidth=10):
        ''' Inserir texto livre em formulários. '''
        label = tkinter.Label(self.instance, text=field, width=textwidth, font=(fonte, fontwidth))
        if self.color:
            label['bg'] = self.color
        if height:
            label['height'] = height
        if stick:
            label.grid(row=row, column=col, columnspan=colspan, rowspan=rowspan, sticky=stick)
        else:
            label.grid(row=row, column=col, columnspan=colspan, rowspan=rowspan)
        return label

    def textbox(self, field, textwidth, row, col, default='', show='', cmd='', fontwidth=10):
        ''' Inserir textbox em formulários. '''
        label = tkinter.Label(self.instance, text=field, font=(fonte, fontwidth))
        text = tkinter.Entry(self.instance, width=textwidth, font=(fonte, fontwidth))
        if self.color:
            label['bg'] = self.color
        if show:
            text['show'] = show
        if cmd:
            text.bind("<FocusOut>", cmd)
            #text['validate'] = 'focusout'
            #text['validatecommand'] = cmd
        label.grid(row=row, column=col, sticky='E')
        text.grid(row=row, column=col + 1, sticky='W')
        text.insert(0, default)
        return text

    def calendar(self, row, col, default='', rowspan=1, columnspan=1, command=False, fontwidth=10):
        ''' Inserir calendário em formulários. '''
        try:
            calendar = Calendar(self.instance, locale='pt_BR.utf8')
        except:
            calendar = Calendar(self.instance, locale='ptb_bra')
        if command:
            calendar.bind("<1>", command)
        calendar.grid(row=row, column=col, rowspan=rowspan, columnspan=columnspan, stick='W')
        return calendar

    def check(self, field, textwidth, checktext, row, col, selected=False, seek='', fontwidth=10):
        ''' Inserir checkbox em formulários. '''
        label = tkinter.Label(self.instance, text=field, font=(fonte, fontwidth))
        var = tkinter.IntVar()
        checkbox = tkinter.Checkbutton(self.instance, text=checktext,
                                       width=textwidth, variable=var, font=(fonte, fontwidth))
        # var = True
        if self.color:
            label['bg'] = self.color
            checkbox['bg'] = self.color
        label.grid(row=row, column=col, stick='E')
        checkbox.grid(row=row, column=col + 1, sticky='W')
        if selected:
            checkbox.select()
        else:
            checkbox.deselect()
        if seek:
            checkbox.bind("<FocusOut>", seek)
        return var

    def combobox(self, field, textwidth, combolist, row, col, default='', cmd='', seek='', fontwidth=10):
        ''' Inserir combobox em formulários. '''
        label = tkinter.Label(self.instance, text=field, font=(fonte, fontwidth))
        text = ttk.Combobox(self.instance, values=combolist, width=textwidth, font=(fonte, fontwidth))
        if self.color:
            label['bg'] = self.color
        if cmd:
            text.bind("<<ComboboxSelected>>", cmd)
        if seek:
            text.bind("<FocusOut>", seek)
        label.grid(row=row, column=col, stick='E')
        text.grid(row=row, column=col + 1, sticky='W')
        text.insert(0, default)
        return text

    def combobox_return(self, field, lista=[]):
        if field.get():
            value = ''
            for row in lista:
                if field.get().lower() == row.lower():
                    value = row
                    break
            if not value:
                for row in lista:
                    if field.get().lower() in row.lower():
                        value = row
                        break
            field.delete(0, 'end')
            field.insert(0, value)
        
    def listbox(self, field, textwidth, height, combolist, row, col, cmd=None, fontwidth=10):
        ''' Inserir combobox em formulários. '''
        label = tkinter.Label(self.instance, text=field, font=(fonte, fontwidth))
        text = tkinter.Listbox(self.instance, height=height, width=textwidth, font=(fonte, fontwidth))
        for rowl in combolist:
            text.insert('end', rowl)
        if self.color:
            label['bg'] = self.color
        if cmd:
            text.bind("<Double-1>", cmd)
        label.grid(row=row, column=col, stick='E')
        text.grid(row=row, column=col + 1, sticky='W')
        return text

    def grid(self, columns, headers, combolist, ordlist, height, row, col, colspan=1, rowspan=1, cmd=None, order=True):
        ''' Inserir gridbox em formulários. 
        columns é uma tupla.
        headers é um dicionário de dicionário.
        combolist é um dicionario de tupla.
        ordlist é a lista ordenada de preenchimento.'''

        def treeview_sort_column(tv, col, reverse):
            l = [(tv.set(k, col), k) for k in tv.get_children('')]
            indice = columns
            if 'format' in headers[indice[col]]:
                if headers[indice[col]]['format'] == 'float':
                    l.sort(key=lambda t: float(num_usa(t[0])), reverse=reverse)
                if headers[indice[col]]['format'] == 'int':
                    l.sort(key=lambda t: int(num_usa(t[0])), reverse=reverse)
                if headers[indice[col]]['format'] == 'date/time':
                    try:
                        l.sort(key=lambda t: datetime.strptime(t[0], '%d/%m/%Y %H:%M:%S'), reverse=reverse)
                    except:
                        l.sort(key=lambda t: datetime.strptime(t[0], '%d/%m/%Y %H:%M'), reverse=reverse)
                if headers[indice[col]]['format'] == 'date':
                    l.sort(key=lambda t: datetime.strptime(t[0], '%d/%m/%Y'), reverse=reverse)
            else:
                l.sort(key=lambda t: t[0].lower(), reverse=reverse)
                # l.sort(reverse=reverse)

            # rearrange items in sorted positions
            for index, (val, k) in enumerate(l):
                tv.move(k, '', index)

            # reverse sort next time
            tv.heading(col, command=lambda: \
                    treeview_sort_column(tv, col, not reverse))

        def orderable(event):
            region = text.identify("region", event.x, event.y)
            if region == "heading":
                cabec = {'0-60': 1}
                last = 60
                ind = 0
                for row in headers:
                    cabec[str(last + 1) + '-' + str(headers[row]['width'] + last)] = ind
                    ind += 1
                    last += headers[row]['width']
                for row in cabec:
                    verif = row.split('-')
                    if event.x >= int(verif[0]) and event.x <= int(verif[1]):
                        treeview_sort_column(text, cabec[row], grid_order[0])
                if grid_order[0]:
                    grid_order[0] = False
                else:
                    grid_order[0] = True

        text = ttk.Treeview(self.instance, columns=columns, height=height)
        style = ttk.Style()
        style.configure(".", font=(fonte, 10))
        style.configure("Treeview.Heading", font=(fonte, 10, 'bold'))
        text.heading('#0', text='Id', anchor='center')
        text.column('#0', anchor='w', width=60)
        if order:
            text.bind("<Button-1>", orderable)
        if cmd:
            text.bind("<Double-1>", cmd)
        colm = 0
        for rows in columns:
            text.heading(
                rows, 
                text=headers[rows]['text'], 
                anchor='center', 
            )
            anchor = 'w'
            if 'anchor' in headers[rows]:
                anchor = headers[rows]['anchor']
            text.column(rows, anchor=anchor, width=headers[rows]['width'])
            colm += 1
        for rows in ordlist:
            text.insert('', 'end', text=rows, values=combolist[rows])
        text.grid(row=row, column=col, columnspan=colspan, rowspan=rowspan, stick='E')
        grid_order = [True]
        return text
    
    def image(self, field, textwidth, imagefile, row, col, colspam=1, rowspan=1, bg='', imagewidth=None, cmd=None):
        ''' Inserir imagem em formulários. '''
        from PIL import Image, ImageTk, ImageFont
        image = Image.open(imagefile)
        if imagewidth:
            image = image.resize(imagewidth, Image.ANTIALIAS)
        logo = ImageTk.PhotoImage(image)
        text = tkinter.Label(self.instance, image=logo)
        if bg:
            text['bg'] = bg
        if self.color:
            text['bg'] = self.color
        if textwidth:
            text['width'] = textwidth
        if cmd:
            text.bind("<Button-1>", cmd)
        text.grid(row=row, column=col, columnspan=colspam, rowspan=rowspan)
        text.photo = logo
        return text

    def geometry(self, x, y):
        return str(y) + 'x' + str(x) + '+' + str(int(510 - y / 2)) + '+172'


class Menu:
    def __init__(self):
        self.main_menu = {}
        self.ord_menu = []
        self.sub_menu = []

    def add_menu(self, title, active=True, cmd=None):
        if not cmd:
            self.main_menu[title] = []
        else:
            self.main_menu[title] = cmd
        self.ord_menu.append(title)

    def add_option(self, title, option, active=True, cmd=None):
        if title not in self.main_menu:
            self.main_menu[title] = []
        self.main_menu[title].append([False, option, active, cmd])

    def add_submenu(self, id, title, option, active=True):
        self.main_menu[title].append([True, id, title, option, active])
        self.sub_menu.append(id)


class App(tkinter.Tk):
    def __init__(self, title='Meu programa', backcolor='khaki1', geometry='960x600+30+30', font=None, mainmenu=None):
        # Menu retorna objeto da classe menu
        self.root = tkinter.Tk()
        self.mainframe = tkinter.Frame(self.root, bg=backcolor)
        self.mainframe.pack()
        self.title = title
        self.backcolor = backcolor
        self.geometry = geometry
        self.font = font
        self.mainmenu = mainmenu
        self._applyformat()

    def _applyformat(self):
        self.root.title(self.title)
        self.root['bg'] = self.backcolor
        self.root.geometry(self.geometry)
        if str(type(self.mainmenu)) == "<class 'forms.Menu'>":
            self.menu()
        style = ttk.Style()
        style.configure(".", font=(FONT, 10))
        style.configure("Treeview.Heading", font=(FONT, 10, 'bold'))
        self.root.option_add("*Font", "Arial 11")

    def destroy(self):
        self.root.quit()

    def form_child(self, config={}):
        self.config = config
        self.child = tkinter.Toplevel(self.root)
        self.child.title("Formulário")
        # self.child.resizable(0, 0)
        if 'dimension' in self.config.keys():
            self.child.geometry(self.config['dimension'])
        if 'title' in self.config.keys():
            self.child.title(self.config['title'])
        if 'color' in self.config.keys():
            self.child['bg'] = self.config['color']
        return self.child

    def menu(self):
        # Configura o menu da Aplicação a ser construída.
        #   menus
        # title = Nome a ser exibido no cabeçalho do menu
        #   opcoes
        # title = Nome a ser exibido no item do menu
        # submenu = True ou False
        menu = {}
        root_menu = tkinter.Menu(self.root)
        for row in self.mainmenu.ord_menu:
            new_menu = tkinter.Menu(root_menu, tearoff=0, title=row)
            if type(self.mainmenu.main_menu[row]) is list:
                root_menu.add_cascade(label=row, menu=new_menu, font=(fonte, 10))
                for i in self.mainmenu.main_menu[row]:
                    sub = i[0]
                    sub_menu = {}
                    if sub:
                        if i[4]:
                            sub_menu[i[1]] = tkinter.Menu(new_menu, tearoff=0, title=row)
                            new_menu.add_cascade(label=i[3], menu=sub_menu[i[1]], font=(fonte, 10))
                            for subrow in self.mainmenu.sub_menu:
                                for subi in self.mainmenu.main_menu[subrow]:
                                    if subi[2]:
                                        sub_menu[i[1]].add_command(label=subi[1], command=subi[3], font=(fonte, 10))
                    else:
                        if i[2]:
                            new_menu.add_command(label=i[1], command=i[3], font=(fonte, 10))
            else:                
                root_menu.add_command(label=row, command=self.mainmenu.main_menu[row], font=(fonte, 10))
        '''
        main_menu = tkinter.Menu(self.root)
        for row in menus:
            command = tkinter.Menu(main_menu, tearoff=0)
            for row2 in opcoes:
                if row2['menu'] == row['title']:
                    if 'submenu' in row2.keys():
                        subcommand = tkinter.Menu(command, tearoff=0)
                        command.add_cascade(label=row2['title'], menu=subcommand)
                        for row3 in opcoes:
                            if row3['menu'] == row2['title']:
                                subcommand.add_command(label=row3['title'], command=row3['command'])
                    else:
                        command.add_command(label=row2['title'], command=row2['command'])
            main_menu.add_cascade(label=row['title'], menu=command)
        '''
        self.root.config(menu=root_menu)

    def clear_mainframe(self):
        if self.mainframe.winfo_children():
            for widget in self.mainframe.winfo_children():
                widget.destroy()

    def run(self, param={}):
        self.root.mainloop()


class Constructor():
    '''
    Essa classe foi construída para construir formulários para o app de modo automático.
    filename = arquivo sqlite3
    table = nome da tabela usada
    name = nome para o formulario
    '''
    def __init__(self, filename, table, name):
        self.conn = sqlite3.connect(filename)
        self.table = table
        data = self.conn.execute('PRAGMA TABLE_INFO(%s)' % self.table)
        self.dict_fields = {}
        self.fields = []
        for i in data:
            self.fields.append(i[1])
            type_field = i[2].split(' ')
            type_field = type_field[0].split('(')
            type_field = type_field[0]
            self.dict_fields[i[1]] = type_field
        self.name = name
    
    def run(self):
        # Etapa 1 - Construir a classe
        class_list = []
        class_edit = []
        i = ' ' * 4
        class_list.append('class %sForm:' % self.name.capitalize())
        class_list.append('%s# Objetivo: ' % i)
        class_list.append('%sdef __init__(self, instance, conn, saved={}):' % i)
        var = '''        self.conn = conn
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
        self.filter1.focus()'''
        v = var.split('\n')
        class_list += v
        class_list.append('')
        class_list.append('%sdef grid(self):' % i)
        var = '''        Label(self.mainframe, text='', width=10, bg=BGCOLOR).grid(row=0, column=0)
        Label(self.mainframe, text='CADASTRO DE %s', width=60, bg=BGCOLOR, font=('Arial Bold', 16)).grid(row=1, column=0)
        self.frame.grid(row=2, column=0)
        Label(self.frame, text='\ n', width=5, height=10, bg=BGFORM).grid(row=0, column=0, rowspan=5) # remover espaço para Enter.
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
        Label(self.frame, text='', bg=BGFORM, width=5).grid(row=5, column=3)''' % (self.name.upper())
        v = var.split('\n')
        class_list += v
        class_list.append('')
        class_list.append("%sdef data(self, filter='', order=''):" % i)
        class_list.append('%s%sc = self.conn.cursor()' % (i, i))
        class_list.append("%s%scmd = 'SELECT %s FROM %s'" % (i, i, ', '.join(self.fields), self.table))
        var = '''        if filter: cmd += filter
        if order:
            cmd += ' ORDER BY %s' % order
        c.execute(cmd)
        dados = c.fetchall()
        # Se for necessário tratar dados (chaves estrangeiras) criar var _dados e o tratamento aplicado.
        # Preenche a tabela'''
        v = var.split('\n')
        class_list += v
        class_list.append("%s%sself.table1['columns'] = %s" % (i, i, str(self.fields[1:])))
        var = '''        self.table1.heading('#0', text='Id', anchor='center')
        self.table1.column('#0', anchor='w', width=60)
        self.table1.delete(*self.table1.get_children())
        self.table1.tag_configure('total', background='green yellow')
        columns = {'''
        v = var.split('\n')
        class_list += v
        fill = []
        for item in self.fields:
            fill.append("'%s': 120" % item)
        class_list.append('%s%s%s%s' % (i, i, i, ', '.join(fill)))
        class_list.append('%s%s}'% (i, i))
        class_list.append("%s%sfor row in %s:" % (i, i, str(self.fields[1:])))
        var = '''            self.table1.heading(
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
        self.instance.clear_mainframe()'''
        v = var.split('\n')
        class_list += v
        class_list.append('%s%smain = %sEditForm(self.instance, self.conn, saved=saved)' % (i, i, self.name.capitalize()))
        var = '''        main.grid()

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
                    self.instance.clear_mainframe()'''
        v = var.split('\n')
        class_list += v
        class_list.append('%s%s%s%s%smain = %sEditForm(self.instance, self.conn, saved=saved, data=_id)' % (i, i, i, i, i, self.name.capitalize()))
        var = '''                    main.grid()
            else:
                messagebox.showerror(title='Atenção', message='Selecione um registro para a edição.')

    def cmd_quit(self):
        self.instance.clear_mainframe()
        MainPanel(self.instance, self.conn).grid()

        '''
        v = var.split('\n')
        class_list += v

        class_edit.append('class %sEditForm:' % self.name.capitalize())
        class_edit.append('%sdef __init__(self, instance, conn, saved={}, data=None):' % i)
        var = '''        self.instance = instance
        self.mainframe = instance.mainframe
        self.conn = conn
        self.saved = saved
        self.data = data
        self.frame = Frame(self.mainframe, bd=1, relief='sunken', bg=BGFORM)'''
        v = var.split('\n')
        class_edit += v
        for item in self.fields:
            class_edit.append("%s%sself.%s_l = Label(self.frame, anchor='e', text='%s ', bg=BGFORM, width=25)" % (i, i, item, item.capitalize()))
            class_edit.append("%s%sself.%s = Entry(self.frame, width=20)" % (i, i, item))
        var = '''        self.buttons = Frame(self.frame, bg=BGFORM, width=30)
        self.cancel = Button(self.buttons, text='Cancelar', width=10, command=self.cmd_cancel)
        self.confirm = Button(self.buttons, text='Confirmar', width=10, command=self.cmd_confirm)
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
        # Insira aqui o widget focus.'''
        v = var.split('\n')
        class_edit += v
        class_edit.append('')
        var = '''    def grid(self):
        Label(self.mainframe, text='', width=10, bg=BGCOLOR).grid(row=0, column=0)
        Label(self.mainframe, text='EDIÇÃO DE %s', width=60, bg=BGCOLOR, font=('Arial Bold', 16)).grid(row=1, column=0)
        self.frame.grid(row=2, column=0)
        Label(self.frame, text='\ n', width=5, height=18, bg=BGFORM).grid(row=0, column=0, rowspan=11) # juntar o Enter
        Label(self.frame, text='', width=10, bg=BGFORM).grid(row=0, column=1)''' % self.name.upper()
        v = var.split('\n')
        class_edit += v
        row = 1
        for item in self.fields:
            class_edit.append("%s%sself.%s_l.grid(row=%s, column=1)" % (i, i, item, row))
            class_edit.append("%s%sself.%s.grid(row=%s, column=2, sticky='w')" % (i, i, item, row))
            row += 1
        class_edit.append("%s%sself.buttons.grid(row=%s, column=1, columnspan=2)" % (i, i, row))
        row += 1
        var = '''        Label(self.buttons, text='', bg=BGFORM, width=30).grid(row=0, column=1, columnspan=2)
        self.cancel.grid(row=1, column=1)
        self.confirm.grid(row=1, column=2)'''
        v = var.split('\n')
        class_edit += v
        class_edit.append("%s%sLabel(self.frame, text='', bg=BGFORM, width=5).grid(row=%s, column=1)" % (i, i, row))
        class_edit.append("%s%sLabel(self.frame, text='', bg=BGFORM, width=5).grid(row=%s, column=3)" % (i, i, row))
        class_edit.append('')
        class_edit.append('%sdef fill_data(self):' % i)
        class_edit.append('%s%sc = self.conn.cursor()' % (i, i))
        var = "%s%scmd = 'SELECT %s FROM %s WHERE id = " % (i, i, ', '.join(self.fields), self.table)
        var += "%s' % self.data"
        class_edit.append(var)
        class_edit.append('%s%sc.execute(cmd)' % (i, i))
        class_edit.append('%s%sdata = c.fetchone()' % (i, i))
        num = 0
        for item in self.fields:
            class_edit.append('%s%sself.%s.insert(0, data[%s])' % (i, i, item, num))
            num += 1
        class_edit.append('')
        class_edit.append('%sdef cmd_cancel(self):' % i)
        class_edit.append('%s%sself.instance.clear_mainframe()' % (i, i))
        class_edit.append('%s%smain = %sForm(self.instance, self.conn, saved=self.saved)' % (i, i, self.name.capitalize()))
        class_edit.append('%s%smain.grid()' % (i, i))
        class_edit.append('%s%smain.cmd_seek()' % (i, i))
        class_edit.append('')
        notnull = self.conn.execute('PRAGMA TABLE_INFO(%s)' % self.table)
        block = []
        for item in notnull:
            if item[3]:
                block.append('self.%s.get()' % item[1])
        block = ' and '.join(block)
        class_edit.append('%sdef cmd_confirm(self):' % i)
        class_edit.append('%s%sif %s:' % (i, i, block))
        var = '''            resp = messagebox.askyesno(title='Confirmação', message='Tem certeza que deseja confirmar os dados?')            
            if resp:
                c = self.conn.cursor()
                if not self.data:'''
        v = var.split('\n')
        class_edit += v
        s = "'''"
        class_edit.append('%s%s%s%s%sc.execute(%sINSERT INTO %s (%s)' % (i, i, i, i, i, s, self.table, ', '.join(self.fields[1:])))
        values = []
        for item in self.fields[1:]:
            if self.dict_fields[item] in ['VARCHAR']:
                values.append('"%s"')
            else:
                values.append('%s')
        values = ', '.join(values)
        values = 'VALUES(' + values + ')'
        class_edit.append('%s%s%s%s%s%s%s %s (' % (i, i, i, i, i, values, s, '%'))
        values = []
        for item in self.fields[1:]:
            values.append('self.%s.get()' % item)
        values = ', '.join(values)
        class_edit.append('%s%s%s%s%s%s%s' % (i, i, i, i, i, i, values))
        class_edit.append('%s%s%s%s%s))' % (i, i, i, i, i))
        class_edit.append('%s%s%s%selse:' % (i, i, i, i))
        class_edit.append('%s%s%s%s%sc.execute(%sUPDATE %s' % (i, i, i, i, i, s, self.table))
        values = []
        for item in self.fields[1:]:
            if self.dict_fields[item] in ['VARCHAR']:
                values.append('%s = "%s"' % (item, '%s'))
            else:
                values.append('%s = %s' % (item, '%s'))
        values = ', '.join(values)
        values = 'SET ' + values
        class_edit.append('%s%s%s%s%s%s' % (i, i, i, i, i, values))
        class_edit.append('%s%s%s%s%sWHERE id = %s%s %s (' % (i, i, i, i, i, '%s', s, '%'))
        values = []
        for item in self.fields[1:]:
            values.append('self.%s.get()' % item)
        values = ', '.join(values)
        class_edit.append('%s%s%s%s%s%s%s, self.data' % (i, i, i, i, i, i, values))
        class_edit.append('%s%s%s%s%s))' % (i, i, i, i, i))
        var = '''                self.conn.commit()
                messagebox.showinfo('Informação', 'Dados atualizados com sucesso!')
                self.instance.clear_mainframe()
                main = %sForm(self.instance, self.conn, saved=self.saved)
                main.grid()
                main.cmd_seek()
        else:
            messagebox.showerror(title='Aviso', message='Não é possível atualizar. Verifique os dados preenchidos.')''' % self.name.capitalize()
        v = var.split('\n')
        class_edit += v
        class_edit.append('')
        class_edit.append('')
        return class_list + class_edit

class RHEnconder():
    def __init__(self, value=None):
        self.value = value

    def encode(self, key, clear):
        enc = []
        for i in range(len(clear)):
            key_c = key[i % len(key)]
            enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
            enc.append(enc_c)
        return base64.urlsafe_b64encode("".join(enc))

    def decode(self, key, enc):
        dec = []
        enc = base64.urlsafe_b64decode(enc)
        for i in range(len(enc)):
            key_c = key[i % len(key)]
            dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
            dec.append(dec_c)
        return "".join(dec)


def pos_frame(l=[], fd=True, new_column=False):
    ''' Posiciona o widget de modo inteligente.
    l = localização no grid
    new_column = muda a colunação
    fd = field (rótulo) ou data (dado a exibir)
    Se o fd for falso, será exibido na coluna seguinte.
    '''
    if fd:
        if l[1] % 2 == 0:
            l[1] += 1
    else:
        l[0] += 1
        if l[1] % 2 == 1:
            l[1] -= 1
    if new_column:
        l[0] = 0
        l[1] += 1
    return l


def geometry(x, y):
    return str(y) + 'x' + str(x) + '+' + str(int(510 - y / 2)) + '+172'


if platform.system() == 'Windows':
    fonte = 'Tahoma'
else:
    fonte = 'Helvetica'
if len(sys.argv) > 1:
    if sys.argv[1] == '-g':
        if sys.argv[3] == 'hoje':
            day = str(datetime.now().date())
        else:
            day = sys.argv[3]
        print(generator(int(sys.argv[2]), day, int(sys.argv[4])))       
#print(generator(648, '2018-04-27', 60))
#print(validator(688, '2018-03-02', '9Q18JC0330OT1E'))
