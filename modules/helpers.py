import datetime

d = datetime.datetime

class GenerateFatura:
    def __init__(self, conn, diario_id=None, banco=None, fatura=None, tipomov=None):
        self.conn = conn
        self.c = conn.cursor()
        self.diario_id = diario_id
        self.banco = banco
        self.fatura = fatura
        self.diarios = {}
        self.tipomov = tipomov
        self.banco_anterior = None
        self.fatura_anterior = None
        self.pago_anterior = False
        self.diarios_anterior = {}
        self.message = None
        self._anterior()
    
    def _anterior(self):
        # Verifica o valor da fatura informada no pagamento anteriormente.
        if self.diario_id:
            self.c.execute('SELECT banco, fatura FROM diario JOIN bancos on bancos.id = banco WHERE diario.id = %s AND bancos.gerafatura = 1' % (self.diario_id))
            resp = self.c.fetchone()
            if resp:
                self.banco_anterior = resp[0]
                self.fatura_anterior = resp[1]
                self.c.execute('SELECT id, valor, datapago FROM diario WHERE banco = %s AND fatura = "%s" AND tipomov = 3' % (self.banco_anterior, self.fatura_anterior))
                for i in self.c.fetchall():
                    self.diarios_anterior[i[0]] = i[1]
                    if i[2]:
                        self.pago_anterior = True
                if len(self.diarios_anterior) > 1: self.message = ['Aviso', 'Existem %s faturas no mesmo mês para o cartão que o pagamento estava vinculado. Revise o valor no Fluxo de Caixa.' % len(self.diarios_anterior)]
        self.c.execute('SELECT diario.id, valor, datapago FROM diario JOIN bancos on bancos.id = banco WHERE banco = %s AND fatura = "%s" AND diario.tipomov = 3 AND bancos.gerafatura = 1' % (self.banco, self.fatura))
        resp = self.c.fetchall()
        if resp:
            for i in resp:
                self.diarios[i[0]] = i[1]
                if i[2]:
                    self.pago_anterior = True
        else:
            self.c.execute('SELECT gerafatura, diavenc FROM bancos WHERE id = %s' % self.banco)
            banco = self.c.fetchone()
            self.c.execute('SELECT id FROM categorias WHERE tipomov = 2')
            categ = self.c.fetchone()
            if categ:
                categ = categ[0]
            if banco[0]:
                cmd = 'INSERT INTO diario (datafirstupdate, datalastupdate, datadoc, datavenc, datapago, parceiro, banco, fatura, descricao, valor, tipomov, categoriamov, usuario) '
                cmd += 'VALUES("%s", "%s", "%s", "%s", "%s", %s, %s, "%s", "%s", %s, %s, %s, %s)' % (
                    str(d.today().date()),
                    str(d.today().date()),
                    self.fatura + '-01',
                    self.fatura + '-' + str(banco[1]).zfill(2),
                    '',
                    '1',
                    '1',
                    self.fatura,
                    '<CRED.CARD>',
                    '0.0',
                    '4',
                    categ,
                    '1'
                )
                self.c.execute(cmd)
                cmd = 'INSERT INTO diario (datafirstupdate, datalastupdate, datadoc, datavenc, datapago, parceiro, banco, fatura, descricao, valor, tipomov, categoriamov, usuario) '
                cmd += 'VALUES("%s", "%s", "%s", "%s", "%s", %s, %s, "%s", "%s", %s, %s, %s, %s)' % (
                    str(d.today().date()),
                    str(d.today().date()),
                    self.fatura + '-01',
                    self.fatura + '-' + str(banco[1]).zfill(2),
                    '',
                    '1',
                    self.banco,
                    self.fatura,
                    '<CRED.CARD>',
                    '0.0',
                    '3',
                    categ,
                    '1'
                )
                self.c.execute(cmd)
            self.conn.commit()
            self.c.execute('SELECT diario.id, valor, datapago FROM diario JOIN bancos on bancos.id = banco WHERE banco = %s AND fatura = "%s" AND diario.tipomov = 3 AND bancos.gerafatura = 1' % (self.banco, self.fatura))
            resp = self.c.fetchall()
            if resp:
                for i in resp:
                    self.diarios[i[0]] = i[1]
                    if i[2]:
                        self.pago_anterior = True

    def _ajusta_anterior(self):
        if self.fatura_anterior:
            ids = list(self.diarios_anterior.keys())
            ids.sort()
            self.c.execute('SELECT SUM(valor) FROM diario WHERE banco = %s AND fatura = "%s" and tipomov = 1' % (self.banco_anterior, self.fatura_anterior))
            value = -self.c.fetchone()[0]
            soma = 0.0
            for i in ids:
                soma += self.diarios_anterior[i]
            accum = soma - value
            for i in ids:
                if self.diarios_anterior[i] - accum > 0.0:
                    self.diarios_anterior[i] -= round(accum, 2)
                    accum = 0.0
                else:
                    accum = accum - self.diarios_anterior[i]
                    del self.diarios_anterior[i]
            ids = list(self.diarios_anterior.keys())
            ids.sort()
            for i in ids:
                self.c.execute('UPDATE diario SET datalastupdate = "%s", valor = %s WHERE id = %s' % (str(datetime.date.today()), self.diarios_anterior[i], i))
                self.c.execute('UPDATE diario SET datalastupdate = "%s", valor = %s WHERE id = %s' % (str(datetime.date.today()), -self.diarios_anterior[i], i - 1))

    def _ajusta(self):
        if self.fatura:
            ids = list(self.diarios.keys())
            ids.sort()
            self.c.execute('SELECT SUM(valor) FROM diario WHERE banco = %s AND fatura = "%s" and tipomov = 1' % (self.banco, self.fatura))
            value = -self.c.fetchone()[0]
            soma = 0.0
            for i in ids:
                soma += self.diarios[i]
            accum = soma - value
            for i in ids:
                if self.diarios[i] - accum > 0.0:
                    self.diarios[i] -= round(accum, 2)
                    accum = 0.0
                else:
                    accum = accum - self.diarios[i]
                    del self.diarios[i]
            ids = list(self.diarios.keys())
            ids.sort()
            for i in ids:
                self.c.execute('UPDATE diario SET datalastupdate = "%s", valor = %s WHERE id = %s' % (str(datetime.date.today()), self.diarios[i], i))
                self.c.execute('UPDATE diario SET datalastupdate = "%s", valor = %s WHERE id = %s' % (str(datetime.date.today()), -self.diarios[i], i - 1))

    def run(self):
        self._ajusta_anterior()
        self._ajusta()
        '''
        if not self.fatura_anterior and not self.banco_anterior:
            self._ajusta()
        elif self.fatura == self.fatura_anterior and self.banco == self.banco_anterior:
            self._ajusta()
        elif self.fatura == self.fatura_anterior and self.banco != self.banco_anterior:
            self._ajusta()
        elif self.fatura != self.fatura_anterior and self.banco == self.banco_anterior:
            self._ajusta()
        '''

    
class Numbers:
    # Classe para conversão entre números floating, integers e exibição formato Brasil.
    def __init__(self, string):
        if type(string) is not str:
            self.string = str(string).replace('.', ',')
        else:
            self.string = string

    def get_str(self, decimal=2):
        try:
            test = self.string.replace('.', '').replace(',', '.')
            test = float(test)
            valor = []
            valor.append('{0:,}'.format(int(test)).replace(',','.'))
            if valor[0] == '0' and test < 0.0:
                valor[0] = '-0'
            if decimal:
                valor.append(str(abs(int(round(test * (10 ** decimal)) - int(test) * (10 ** decimal)))).zfill(decimal))
        except:
            valor = ['0']
            if decimal:
                valor.append(str(10 ** decimal)[1:])
        return ','.join(valor)
    
    def get_val(self, decimal=2):
        try:
            test = self.string.replace('.', '').replace(',', '.')
            test = float(test)
            if not decimal:
                if float(test) >= 0.0:
                    return int(test)
                else:
                    return -int(abs(float(test)))
            else:
                return round(float(test), decimal)
        except:
            if decimal:
                return 0.0
            else:
                return 0


def query_list(conn, field, table, where='', order_by=''):
    c = conn.cursor()
    cmd = 'SELECT %s FROM %s' % (field, table)
    if where:
        cmd += ' WHERE %s' % where
    if order_by:
        cmd += ' ORDER BY %s' % order_by
    values = []
    c.execute(cmd)
    data = c.fetchall()
    for i in data:
        item = list(map(str, i))
        values.append(' / '.join(item))
    return values

def query_id(conn, table, field=[], types=[], where=''):
    c = conn.cursor()
    cond = where.split(' / ')
    count = 0
    joinned = []
    for i in field:
        if types[count]:
            joinned.append('%s = "%s"' % (i, cond[count]))
        else:
            joinned.append('%s = %s' % (i, cond[count]))
        count += 1
    cmd = 'SELECT id FROM %s WHERE %s' % (table, ' AND '.join(joinned))
    c.execute(cmd)
    data = c.fetchone()
    return data[0]

def date_in(string):
    # Valida se a data existe e converte string DD/MM/YYYY em string YYYY-MM-DD
    try:
        return d.strptime(string, '%d/%m/%Y').strftime('%Y-%m-%d')
    except:
        return ''

def date_out(string):
    # Valida se a data existe e converte string YYYY-MM-DD em string DD/MM/YYYY
    try:
        return d.strptime(string, '%Y-%m-%d').strftime('%d/%m/%Y')
    except:
        return ''

def lastdaymonth(diaini):
    months = {
        1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6:30,
        7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31
    }
    mes = int(str(diaini)[5:7])
    ano = int(str(diaini)[0:4])
    bis = ano % 4
    if bis == 0:
        months[2] = 29
    dia = months[mes]
    lastday = datetime.date(ano, mes, dia)
    return lastday

def cmd(widget):
    if widget.get() and widget.get() not in widget['values']:
        for i in widget['values']:
            if widget.get().lower() in i.lower():
                widget.delete(0, 'end')
                widget.insert(0, i)
                break
        if widget.get() not in widget['values']:
            widget.delete(0, 'end')

def cmd_data(widget):
    if widget.get():
        ad = d.now()
        datesplit = widget.get().split('/')
        if len(datesplit) == 3:
            if len(datesplit[2]) == 4:
                datereturn = date_in(widget.get())
            else:
                datesplit[2] = str(ad.year)[:-len(datesplit[2])] + datesplit[2]
                datereturn = date_in('/'.join(datesplit))
        elif len(datesplit) == 2:
            datereturn = date_in('%s/%s' % (widget.get(), ad.year))
        elif len(datesplit) == 1 and datesplit[0]:
            datereturn = date_in('%s/%s/%s' % (widget.get(), str(ad.month).zfill(2), ad.year))
        else:
            datereturn = ''
        widget.delete(0, 'end')
        widget.insert(0, date_out(datereturn))

def cmd_fat(conn, banco, date_ref, by_fat=False):
    c = conn.cursor()
    c.execute('SELECT gerafatura, diavenc FROM bancos WHERE nomebanco = "%s" and gerafatura = 1' % banco)
    resp = c.fetchone()
    if resp:
        if by_fat:
            new_fat = ''
            new_venc = ''
            date_ref = date_ref.split('-')
            if len(date_ref) == 2:
                year = range(d.today().year - 10, d.today().year + 10)
                month = range(1, 13)
                if int(date_ref[0]) in year and int(date_ref[1]) in month:
                    # Corrigir se fatura acima do dia 28! Bug visto em 27/01/2020.
                    new_fat = '-'.join(date_ref)
                    new_venc = d(int(date_ref[0]), int(date_ref[1]), resp[1]).strftime('%d/%m/%Y')
        else:
            # Busca fatura e vencimento
            hoje = d.strptime(date_ref, '%d/%m/%Y') + datetime.timedelta(days=10)
            dia = hoje.day
            mes = hoje.month
            ano = hoje.year
            if resp[1] >= dia:
                pass
            else:
                mes = mes + 1
                if mes == 13:
                    mes = 1
                    ano += 1
            new_fat = str(ano) + '-' + str(mes).zfill(2)
            new_venc = d(ano, mes, resp[1]).strftime('%d/%m/%Y')
        return {
            'new_fat': new_fat,
            'new_venc': new_venc,
        }
    else:
        return None

def cmd_desc(conn, banco, new_fat):
    c = conn.cursor()
    c.execute('SELECT gerafatura, diavenc FROM bancos WHERE nomebanco = "%s" and gerafatura = 1' % banco)
    resp = c.fetchone()
    periodo_fatura = new_fat.split('-')
    description = ''
    if resp:
        if resp[0] and len(periodo_fatura) == 2:
            if resp[1] > 10:
                data_fatfim = d(int(periodo_fatura[0]), int(periodo_fatura[1]), resp[1] - 10)
                if int(periodo_fatura[1]) == 1:
                    month_fat = 12
                    year_fat = int(periodo_fatura[0]) - 1
                else:
                    month_fat = int(periodo_fatura[1]) - 1
                    year_fat = int(periodo_fatura[0])
                data_fatini = d(year_fat, month_fat, resp[1] - 10) + datetime.timedelta(days=1)
            else:
                days_month = (d(int(periodo_fatura[0]), int(periodo_fatura[1]), 1) - datetime.timedelta(days=1)).day
                day_fat = resp[1] + 20
                if day_fat > days_month:
                    day_fat = days_month
                if int(periodo_fatura[1]) == 1:
                    month_fat = 12
                    year_fat = int(periodo_fatura[0]) - 1
                else:
                    month_fat = int(periodo_fatura[1]) - 1
                    year_fat = int(periodo_fatura[0])
                data_fatfim = d(year_fat, month_fat, day_fat)

                days_month = (d(year_fat, month_fat, 1) - datetime.timedelta(days=1)).day
                day_fat = resp[1] + 20
                if day_fat > days_month:
                    day_fat = days_month
                if month_fat == 1:
                    month_fat = 12
                    year_fat -= 1
                else:
                    month_fat = month_fat - 1
                data_fatini = d(year_fat, month_fat, day_fat) + datetime.timedelta(days=1)
            description += 'Movimentação ('
            description += data_fatini.strftime('%d/%m/%Y') + ' e '
            description += data_fatfim.strftime('%d/%m/%Y') + ')'
    return description
