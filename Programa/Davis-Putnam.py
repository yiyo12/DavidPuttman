import re
import sys

class Clausula:
    def __init__(self):
        self.atomos = []
    
    def agregarAtomo(self, atomo):
        self.atomos.append(atomo)
        
    def getClon(self):
        c = Clausula()
        for a in self.atomos:
            c.agregarAtomo(a.getClon())
        return c

    def notClausula(self):
        f = Formula()
        for a in self.atomos:
            b = a.getClon()
            b.notAtomo()
            c = Clausula()
            c.agregarAtomo(b)
            f.agregarClausula(c)
        return f

    def atomoRepetido(self):
        for atomo1 in self.atomos:
            for atomo2 in self.atomos:
                if (atomo1.nombre == atomo2.nombre):
                    if (atomo1.negado != atomo2.negado):
                        return True
        return False

    def toString(self):
        cad = '( '
        for a in self.atomos:
            cad += a.toString()+ ' , '
        if (len(self.atomos) == 0):
            cad = '( )'
        else:
            cad = cad[:-2]+')'
        return cad


class Atomo:
    def __init__(self,nombre):
        self.nombre = nombre
        self.negado = False
        
    def notAtomo(self):
        self.negado = not(self.negado)
        
    def getClon(self):
        clon = Atomo(self.nombre)
        clon.negado = self.negado
        return clon
    
    def toString(self):
        if(self.negado):
            return '~' + self.nombre
        return self.nombre


class Formula:
    def __init__(self):
        self.clausulas = []
        self.certificado = {}
    
    def agregarClausula(self,clausula):
        self.clausulas.append(clausula)
        
    def andFormula(self,formula):
        f = Formula()
        for c in self.clausulas:
            f.agregarClausula(c)
        for c in formula.clausulas:
            f.agregarClausula(c)
        return f
    
    def notFormula(self):
        f = Formula()
        for c in self.clausulas:
            g = c.notClausula()
            f = f.orFormula(g)
        return f
    
    def orFormula(self,formula):
        f = Formula()
        g = []
        for c in formula.clausulas:
            g.append(self.orClausula(c))
        for h in g:
            for c in h.clausulas:
                f.agregarClausula(c)
        return f
    
    def orClausula(self,clausula):
        f = Formula()
        if(len(self.clausulas) == 0):
            f.agregarClausula(clausula.getClon())
            return f
        for c in self.clausulas:
            x = c.getClon()
            for a in clausula.atomos:
                x.agregarAtomo(a.getClon())
            f.agregarClausula(x)
        return f
    
    def toString(self):
        cad='[ '
        for c in self.clausulas:
            cad += c.toString() + ' & '
        if (len(self.clausulas) == 0):
            cad = '[ ],{ '
        else:
            cad = cad[:-2]+'],{ '
        for a in self.certificado.keys():
            b = Atomo.Atomo(a)
            if(self.certificado[a]==True):
                b.notAtomo()
            cad += b.toString()+' '
        cad += '}'
        return cad
    
def obtenerPrioridad(a):
    if(a == '|'):
        return 1
    if(a == '&'):
        return 2
    if(a == '>'):
        return 3
    if(a == '='):
        return 4
    if(a == '~'):
        return 5
    return 0

def infijo2postfijo(infijo):
    postfijo = []
    pila = []
    for ch in infijo:
        if(ch == '('):
            pila.append(ch)
        elif(ch == ')'):
            while(len(pila)>0):
                tope = pila.pop()
                if(tope != '('):
                    postfijo.append(tope)
                else:
                    break
        elif(ch.isalnum()):
            postfijo.append(ch)
        else:
            if(len(pila) == 0 or obtenerPrioridad(ch) > obtenerPrioridad(pila[-1])):
                pila.append(ch)
            else:
                while(len(pila) > 0 and obtenerPrioridad(ch) < obtenerPrioridad(pila[-1])):
                    tope = pila.pop()
                    postfijo.append(tope)
                pila.append(ch)
    while(len(pila) > 0):
        postfijo.append(pila.pop())
    return postfijo
 
    
def Repetidos(atomos):
    auxAtomos = []
    while (len(atomos) != 0):
        atomo1 = atomos.pop()
        agregar = True
        for atomo2 in auxAtomos:
            if (atomo1.nombre == atomo2.nombre):
                agregar = False
        if (agregar):
            auxAtomos.append(atomo1)
    
        
    return auxAtomos

def Evaluar(postfijo):
    pila = []
    for ch in postfijo:
        if(ch.isalnum()):
            f = Formula()
            c = Clausula()
            a = Atomo(ch)
            c.agregarAtomo(a)
            f.agregarClausula(c)
            pila.append(f)
        else:
            if(ch == '|'):
                b = pila.pop()
                a = pila.pop()
                c = a.orFormula(b)
            elif(ch == '&'):
                b = pila.pop()
                a = pila.pop()
                c = a.andFormula(b)
            elif(ch == '>'):
                b = pila.pop()
                a = pila.pop()
                a = a.notFormula()
                c = a.orFormula(b)
            elif(ch == '='):
                b = pila.pop()
                a = pila.pop()
                d = a.notFormula()
                e = b.notFormula()
                f = d.orFormula(b)
                g = e.orFormula(a)
                c = f.andFormula(g)
            elif(ch == '~'):
                a = pila.pop()
                c = a.notFormula()
            pila.append(c)
    return pila.pop()

def Tautologia(fnc):
    for clausula in fnc.clausulas:
        if (clausula.atomoRepetido()):
            fnc.clausulas.remove(clausula)
            Tautologia(fnc)
            return True
    return False
            
def Unitaria(fnc):    
    for clausula1 in fnc.clausulas:
        if (len(clausula1.atomos) == 1):
            borrar = []
            for clausula2 in fnc.clausulas:
                for atomo in clausula2.atomos:
                    if(clausula1 != clausula2):
                        if (clausula1.atomos[0].nombre == atomo.nombre):
                            if (clausula1.atomos[0].negado != atomo.negado):
                                clausula2.atomos.remove(atomo)
                            else:
                                borrar.append(clausula2)
            
            if (clausula1.atomos[0].negado):
                print('CláusulaUnitaria:', '~', clausula1.atomos[0].nombre, '\t', end='')
            else:
                print('CláusulaUnitaria:', clausula1.atomos[0].nombre, '\t', end='')
            if (len(borrar) != 0):
                for borrarClau in borrar:
                    fnc.clausulas.remove(borrarClau)
            fnc.clausulas.remove(clausula1)
            print(fnc.toString())
            if (len(fnc.clausulas) != 0):
                Unitaria(fnc)
            return True
            
    return False
            
def literalPura(fnc):
    for clausula1 in fnc.clausulas:
        for atomo1 in clausula1.atomos:
            isBorrar = False
            borrar = []
            if (len(fnc.clausulas) != 0):
                isBorrar = True
                for clausula2 in fnc.clausulas:
                    for atomo2 in clausula2.atomos:
                        if (atomo1 != atomo2):
                            if(atomo1.nombre == atomo2.nombre):
                                if(atomo1.negado != atomo2.negado):
                                    isBorrar = False

            if (len(fnc.clausulas) != 0):
                if (isBorrar == True):
                    if (atomo1.negado):
                        print('LiteralPura:', '~', atomo1.nombre, '\t', end='')
                    else:
                        print('LiteralPura:', atomo1.nombre, '\t', end='')
                    fnc.clausulas.remove(clausula1)
                    for clausula2 in fnc.clausulas:
                        for atomo2 in clausula2.atomos:
                            if(atomo1.nombre == atomo2.nombre):
                                fnc.clausulas.remove(clausula2)
                    print(fnc.toString())
                    literalPura(fnc)
                    return True
    return False

def bifurcacion1(fnc, atomo):
    borrar = []    
    for clausula in fnc.clausulas:
        for atomo1 in clausula.atomos:
            if (atomo.nombre == atomo1.nombre):
                if (atomo.negado != atomo1.negado):
                    clausula.atomos.remove(atomo1)
                else:
                    borrar.append(clausula)
    
    if (len(borrar) != 0):
        for borrarClau in borrar:
            fnc.clausulas.remove(borrarClau)
    
def bifurcacion2(fnc, atomo):
    borrar = []
    atomo.negado = not atomo.negado
    for clausula in fnc.clausulas:
        for atomo1 in clausula.atomos:
            if (atomo.nombre == atomo1.nombre):
                if (atomo.negado != atomo1.negado):
                    clausula.atomos.remove(atomo1)
                else:
                    borrar.append(clausula)
    
    if (len(borrar) != 0):
        for borrarClau in borrar:
            fnc.clausulas.remove(borrarClau)    

    
    

def SAT(fnc):
        
    if(Tautologia(fnc)):
        print(fnc.toString())
        
    fncAux = Formula()
    bif1 = False
    bif2 = False
    primeraBifurcacion = True
    atomoBifurcado = Atomo('a')
    bifurcaciones = []
    
    while (True):
        clausulaVacia = False
        if (bif1 == False):
            for clausula in fnc.clausulas:
                if (len(clausula.atomos) == 0):
                    clausulaVacia = True
        else:
            for clausula in fncAux.clausulas:
                if (len(clausula.atomos) == 0):
                    clausulaVacia = True            
        
        if (clausulaVacia):
            print('La cláusula está vacía')
            if (bif1 == False & bif2 == False):
                print('No se ha aplicado ninguna bifurcación')
                return False
            elif (bif1 & bif2):
                print('Se ha aplicado dos veces la bifurcación')
                
                bif1 = True
                bif2 = False
                if (len(bifurcaciones) > 2):
                    
                    atomoBifurcado = bifurcaciones.pop()
                    fncAux = Formula()
                    for clausula in fnc.clausulas:
                        fncAux.agregarClausula(clausula.getClon())
                    
                    if (atomoBifurcado.negado):
                        print('Bifurcación:', '~', atomoBifurcado.nombre, '\t', end='')
                    else:
                        print('Bifurcación:', atomoBifurcado.nombre, '\t', end='')
                    bifurcacion1(fncAux, atomoBifurcado)
                    print(fncAux.toString())
                else:
                    return False
                
            else:
                print('Se ha aplicado una vez la bifurcación')
                if (bif1):
                    bif2 = True
                    fncAux = Formula()
                    for clausula in fnc.clausulas:
                        fncAux.agregarClausula(clausula.getClon())
                else:
                    bif1 = True
                    if (primeraBifurcacion):
                        primeraBifurcacion = False
                        for clausula in fnc.clausulas:
                            fncAux.agregarClausula(clausula.getClon())
                            for atomo in clausula:
                                bifurcaciones.append(atomo)
                        bifurcaciones = Repetidos(bifurcaciones)
                        atomoBifurcado = bifurcaciones.pop()
                    
                if (bif2):
                    if (atomoBifurcado.negado):
                        print('Bifurcación:', atomoBifurcado.nombre, '\t', end='')
                    else:
                        print('Bifurcación:', '~', atomoBifurcado.nombre, '\t', end='')
                    bifurcacion2(fncAux, atomoBifurcado)
                    print(fncAux.toString())
                else:
                    if (atomoBifurcado.negado):
                        print('Bifurcación:', '~', atomoBifurcado.nombre, '\t', end='')
                    else:
                        print('Bifurcación:', atomoBifurcado.nombre, '\t', end='')
                    bifurcacion1(fncAux, atomoBifurcado)
                    print(fncAux.toString())
                
        
        else:  
            print('La cláusula no está vacía')
            formulaVacia = False
            if (bif1 == False):
                if (len(fnc.clausulas) == 0):
                    formulaVacia = True
            else:
                if (len(fncAux.clausulas) == 0):
                    formulaVacia = True
                
            if (formulaVacia):
                print('La formula está vacía')
                return True
            
            else:
                print('La formula no está vacía')
                if (bif1 | bif2):
                    CU = Unitaria(fncAux)
                    LP = literalPura(fncAux)
                else:
                    CU = Unitaria(fnc)
                    LP = literalPura(fnc)

                if (CU | LP):
                    if(CU):
                        print('Si hubo cláusula unitaria')
                    else:
                        print('Si hubo literal pura')
                else:
                    print('No hubo cláusula unitaria o literal pura')
                    if (bif1):
                        bif2 = True
                        fncAux = Formula()
                        for clausula in fnc.clausulas:
                            fncAux.agregarClausula(clausula.getClon())
                        print(fncAux.toString())
                    else:
                        bif1 = True
                        if (primeraBifurcacion):
                            primeraBifurcacion = False
                            for clausula in fnc.clausulas:
                                fncAux.agregarClausula(clausula.getClon())
                                for atomo in clausula.atomos:
                                    bifurcaciones.append(atomo)
                            
                            bifurcaciones = Repetidos(bifurcaciones)
                            atomoBifurcado = bifurcaciones.pop()

                           
                    if (bif2):
                        if (atomoBifurcado.negado):
                            print('Bifurcación:', atomoBifurcado.nombre, '\t', end='')
                        else:
                            print('Bifurcación:', '~', atomoBifurcado.nombre, '\t', end='')
                        bifurcacion2(fncAux, atomoBifurcado)
                        print(fncAux.toString())
                    else:
                        if (atomoBifurcado.negado):
                            print('Bifurcación:', '~', atomoBifurcado.nombre, '\t', end='')
                        else: 
                            print('Bifurcación:', atomoBifurcado.nombre, '\t', end='')
                        bifurcacion1(fncAux, atomoBifurcado)
                        print(fncAux.toString())



#MAAAAAAAAAAAAAAAAAAAAAIN

archivo = open("formulas.txt")
formulas = archivo.readlines()
formula = 5
infijo = re.findall('(\w+|\||\&|\>|\=|\~|\(|\))', formulas[formula])
postfijo = infijo2postfijo(infijo)
#print('\ninfijo String:\n', formulas[formula])
#print('infijo Lista:\n', infijo)
#print('postfijo Lista:\n', postfijo)

fnc = Evaluar(postfijo)
   

print('FNC: \n', fnc.toString())
print('SAT =', SAT(fnc))
