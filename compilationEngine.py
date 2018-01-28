import tokenizer2 as Tokenizer


class compilationEngine:

    def __init__(self,file_path):
        '''create a tokenizer object'''
        tokens = Tokenizer.JackTokenizer(file_path)
        tokens.tokenize()
        tokens.advance()
        self.output_file=open('compile_output.xml','w')
        self.tokens=tokens
        self.symbol=tokens.jack_symbol
        self.keyword=tokens.jack_keyword
        self.indent=0
        self.space='  '
        self.statements_key=['let','var','do','while','if','return','function']
        self.bracket=[]
        self.statement_type=['letStatement']

    def tag_root(self, kind,state):
        if state=='open':
            return '<'+kind+ '>'
        elif state=='close':
            return '</'+kind+'>'

    def tag_body(self, token):
        return self.tag_root(token[1],'open')+' '+ token[0]+' ' + self.tag_root(token[1],'close')+'\n'

    def get_current_statement(self,idx):
        '''takes -1 for argument and return the current statement type we are currently in'''
        statements=['whileStatement','ifStatement','letStatement','statements','returnStatement','doStatement','']
        if self.bracket[idx]  in statements:
            return self.bracket[idx]
        elif idx==-len(self.bracket) and self.bracket[idx] not in statements:
            return 'no statement found'
        else: return self.get_current_statement(idx-1)



    def check_for_statements(self):
        '''
        check which compile statement should run next and calls it.
        '''
        if self.tokens.current_token[0] in ['method','function','subroutine','constructor']:
            self.compileSubroutine()

        elif self.tokens.current_token[0]=='var' :
            self.compileVarDec()

        elif self.tokens.current_token[0]=='let':
            self.compileLet()

        elif self.tokens.current_token[0]=='while':
            self.compileWhile()

        elif self.tokens.current_token[0]=='do':
            self.compileDo()

        elif self.tokens.current_token[0]=='return':
            self.compileReturn()

        elif self.tokens.current_token[0]=='if':
            self.compileIf()

        elif self.tokens.current_token[0]=='else':
            self.compileIf()

        elif self.tokens.current_token[0] in ['static','field']:
            self.compileClassVarDec()


    def compileClass(self):
        space=self.space*self.indent
        if self.tokens.current_token[0]=='class':
            self.output_file.write(space+self.tag_root('class','open')+'\n')
            self.bracket.append('class')
            self.indent+=1
            space=self.space*self.indent #update space
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileClass()

        elif self.tokens.current_token[0]=='':
            return

        #handle classvarDec opening
        elif self.tokens.current_token[0] in ['static','field']:
            self.compileClassVarDec()

        #close classvarDec
        #elif self.tokens.current_token[0]=='static':

        #tag identifier
        elif self.tokens.current_token[0] not in self.symbol and self.tokens.current_token[0] not in self.keyword:
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileClass()

        #tag symbol
        elif self.tokens.current_token[0] in self.symbol :
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileClass()

        #tag statements_key
        elif self.tokens.current_token[0] in self.statements_key:
            self.check_for_statements()


        #tag keyword other than statements_key
        elif self.tokens.current_token[0] in self.keyword:
            print 'entered'
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileClass()




    def compileSubroutine(self):
        space=self.space*self.indent
        if self.tokens.previous_token(2)[0]=='}' and (self.bracket[-1] in ['subroutineBody','subroutineDec']):
            #close subroutineBody tag
            self.indent-=1
            space=self.space*self.indent
            self.output_file.write(space+self.tag_root(self.bracket.pop(),'close')+'\n')
            self.compileSubroutine()


        elif self.tokens.current_token[0] in ['method','function','subroutine','constructor']:
            self.output_file.write(space+self.tag_root('subroutineDec','open')+'\n')
            self.bracket.append('subroutineDec')
            self.indent+=1
            space=self.space*self.indent #update space
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileSubroutine()

        elif self.tokens.current_token[0]=='':
            return

        elif self.tokens.current_token[0]=='(' :
            #insert subroutineBody tag
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.output_file.write(space+self.tag_root('parameterList','open')+'\n')
            self.bracket.append('parameterList')
            self.indent+=1
            space=self.space*self.indent
            self.tokens.advance()
            self.compileSubroutine()

        elif self.tokens.current_token[0]==')' :
            self.indent-=1
            space=self.space*self.indent
            self.output_file.write(space+self.tag_root(self.bracket.pop(),'close')+'\n')
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileSubroutine()

        elif self.tokens.current_token[0]=='{' and self.tokens.next_token()[0]=='var':
            #insert subroutineBody tag
            self.output_file.write(space+self.tag_root('subroutineBody','open')+'\n')
            self.bracket.append('subroutineBody')
            self.indent+=1
            space=self.space*self.indent
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileVarDec()


        elif self.tokens.current_token[0]=='{' :
            #insert subroutineBody tag
            self.output_file.write(space+self.tag_root('subroutineBody','open')+'\n')
            self.bracket.append('subroutineBody')
            self.indent+=1
            space=self.space*self.indent
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.output_file.write(space+self.tag_root('statements','open')+'\n')
            self.bracket.append('statements')
            self.indent+=1
            self.tokens.advance()
            self.compileSubroutine()




        elif self.tokens.current_token[0]=='}' :
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            #close subroutineBody tag
            self.indent-=1
            self.output_file.write(space+self.tag_root(self.bracket.pop(),'close')+'\n')
            self.compileSubroutine()

           #tag identifier
        elif self.tokens.current_token[0] not in self.symbol and self.tokens.current_token[0] not in self.keyword:
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileSubroutine()

        elif self.tokens.current_token[0] in self.symbol :
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileSubroutine()

        #tag statements_key
        elif self.tokens.current_token[0] in self.statements_key :
            self.check_for_statements()

        #tag remaing keyword not in statements_key
        elif self.tokens.current_token[0] in self.keyword :
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileSubroutine()



    def compileVarDec(self):
        space=self.space*self.indent

        if self.tokens.current_token[0]=='var':
            self.output_file.write(space+self.tag_root('varDec','open')+'\n')
            self.bracket.append('varDec')
            self.indent+=1
            space=self.space*self.indent #update space
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileVarDec()

        elif self.tokens.current_token[0]=='':
            return



        elif self.tokens.current_token[0]==',':
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileVarDec()

        elif self.tokens.current_token[0]==';':
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.indent-=1
            space=self.space*self.indent
            self.output_file.write(space+self.tag_root(self.bracket.pop(),'close')+'\n')
            self.tokens.advance()
            self.compileVarDec()

           #tag identifier
        elif self.tokens.current_token[0] not in self.symbol and self.tokens.current_token[0] not in self.keyword:
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileVarDec()

        #tag token in statements_key
        elif self.tokens.current_token[0] in self.statements_key:
            self.check_for_statements()


        #tag keyword token not in statements_key
        elif self.tokens.current_token[0] in self.keyword:
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileVarDec()



    def compileLet(self):
        space=self.space*self.indent

        if self.tokens.current_token[0]=='let':
            if 'statements' not in self.bracket:
                self.output_file.write(space+self.tag_root('statements','open')+'\n')
                self.bracket.append('statements')
                self.indent+=1
                space=self.space*self.indent #update space
                self.output_file.write(space+self.tag_root('letStatement','open')+'\n')
                self.bracket.append('letStatement')
                self.indent+=1
                space=self.space*self.indent #update space
                self.output_file.write(space+self.tag_body(self.tokens.current_token))
                self.tokens.advance()
                self.compileLet()

            else:
                self.output_file.write(space+self.tag_root('letStatement','open')+'\n')
                self.bracket.append('letStatement')
                self.indent+=1
                space=self.space*self.indent #update space
                self.output_file.write(space+self.tag_body(self.tokens.current_token))
                self.tokens.advance()
                self.compileLet()

           #tag identifier
        elif self.tokens.current_token[0] not in self.symbol and self.tokens.current_token[0] not in self.keyword:
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileLet()

        elif self.tokens.current_token[0]=='=':
            self.compileExpression()

        elif self.tokens.current_token[0]=='[':
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.compileExpression()

    def compileExpression(self):
        space=self.space*self.indent

        if self.tokens.current_token[0]=='=':
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.output_file.write(space+self.tag_root('expression','open')+'\n')
            self.bracket.append('expression')
            self.indent+=1
            self.compileTerm()

            #handles multiple func ParameterList ex: drawer.drawrec(x,y,c,z)
        elif self.tokens.current_token[0]==',' and self.bracket[-2]=='expressionList':
            self.indent-=1
            space=self.space*self.indent
            self.output_file.write(space+self.tag_root(self.bracket.pop(),'close')+'\n')
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            #open expression and term tags
            self.output_file.write(space+self.tag_root('expression','open')+'\n')
            self.bracket.append('expression')
            self.indent+=1
            space=self.space*self.indent
            self.output_file.write(space+self.tag_root('term','open')+'\n')
            self.bracket.append('term')
            self.indent+=1
            self.tokens.advance()
            self.compileTerm()

        elif self.tokens.current_token[0]=='(' and self.tokens.previous_token(2)[0]=='&':
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.output_file.write(space+self.tag_root('expression','open')+'\n')
            self.bracket.append('expression')
            self.indent+=1

            space=self.space*self.indent
            self.output_file.write(space+self.tag_root('term','open')+'\n')
            self.bracket.append('term')
            self.indent+=1
            self.tokens.advance()
            self.compileTerm()

        elif self.tokens.current_token[0]=='(' and self.bracket[-1] in ['whileStatement','ifStatement']:
            self.output_file.write(space+self.tag_root('expression','open')+'\n')
            self.bracket.append('expression')
            self.indent+=1
            self.compileTerm()

        elif self.tokens.current_token[0]=='(' or self.tokens.current_token[0]=='[':
            self.output_file.write(space+self.tag_root('expression','open')+'\n')
            self.bracket.append('expression')
            self.indent+=1
            self.compileTerm()

        elif self.tokens.current_token[0]==']':
            self.indent-=1
            space=self.space*self.indent
            self.output_file.write(space+self.tag_root(self.bracket.pop(),'close')+'\n')
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileExpression()

        elif self.tokens.current_token[0]==')' and self.bracket[-1]=='term':
            self.compileTerm()

        elif self.tokens.current_token[0]==')' and self.bracket[-1]=='expression':
            self.indent-=1
            space=self.space*self.indent
            self.output_file.write(space+self.tag_root(self.bracket.pop(),'close')+'\n')

            #if in whileStatement go to whileStatement;
            if self.bracket[-1]=='whileStatement':
                self.compileWhile()

            #if in ifstament go to compileIf
            elif self.bracket[-1]=='ifStatement':
                self.compileIf()

            elif self.bracket[-1]=='term' and self.tokens.next_token()[0]=='&':
                self.output_file.write(space+self.tag_body(self.tokens.current_token))
                self.indent-=1
                space=self.space*self.indent
                self.output_file.write(space+self.tag_root(self.bracket.pop(),'close')+'\n')
                #replace & by &amp;
                self.tokens.advance()
                self.tokens.current_token=('&amp;','symbol')
                self.output_file.write(space+self.tag_body(self.tokens.current_token))
                self.tokens.advance()
                self.compileTerm()

            elif self.bracket[-1]=='term':
                self.output_file.write(space+self.tag_body(self.tokens.current_token))
                self.tokens.advance()
                self.compileTerm()

            # if in expressionList go to compileExpressionexpressionList
            else:
                self.compileExpressionList()

        #if in a term level with ';' as the token go to compileterm to close
        elif self.tokens.current_token[0]==';'  and self.bracket[-1]=='term':
            self.compileTerm()

        #close current statment tag and call the next statement
        elif self.tokens.current_token[0]==';' :
            self.indent-=1
            space=self.space*self.indent
            self.output_file.write(space+self.tag_root(self.bracket.pop(),'close')+'\n')
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            #close the current statement tag
            self.indent-=1
            space=self.space*self.indent
            self.output_file.write(space+self.tag_root(self.bracket.pop(),'close')+'\n')
            self.tokens.advance()
            self.compileExpression()

        elif self.tokens.previous_token(2)[0]=='}' and (self.bracket[-1] in ['subroutineBody','subroutineDec']):
            self.compileSubroutine()

            #check for closing bracket
        elif self.tokens.current_token[0]=='}':

            self.indent-=1
            space=self.space*self.indent
            self.output_file.write(space+self.tag_root(self.bracket.pop(),'close')+'\n')
            self.output_file.write(space+self.tag_body(self.tokens.current_token))

            condition2= self.bracket[-1]=='whileStatement' #condition for whileStatement closing
            if (self.bracket[-1]=='ifStatement' and self.tokens.next_token()[0]!='else') or condition2:
                self.indent-=1
                space=self.space*self.indent
                self.output_file.write(space+self.tag_root(self.bracket.pop(),'close')+'\n')
                #go to compileSubroutine to close
                self.tokens.advance()

                self.compileExpression()
            else :
                self.tokens.advance()
                self.compileExpression()
            #check to see if it is a terminal bracket if not close it twice
                #if len(self.bracket)>0:
                #    self.indent-=1
                #    space=self.space*self.indent
                #    self.output_file.write(space+self.tag_root(self.bracket.pop(),'close')+'\n')
        else:
            self.check_for_statements()


    def compileTerm(self):
        space=self.space*self.indent
        less_or_great_sign={'<':('&lt;','symbol'),'>':('&gt;','symbol')}

        equal_sign_in_if_condition=self.tokens.current_token[0]=='=' and self.get_current_statement(-1)=='ifStatement'
        equal_sign_in_while_condition=self.tokens.current_token[0]=='=' and self.get_current_statement(-1)=='whileStatement'

        #handle '+' sign token
        if self.tokens.current_token[0] in ['+','-','/','*','|'] or equal_sign_in_if_condition or equal_sign_in_while_condition:
            #change current token
            self.indent-=1

            space=self.space*self.indent
            self.output_file.write(space+self.tag_root(self.bracket.pop(),'close')+'\n')
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.output_file.write(space+self.tag_root('term','open')+'\n')
            self.bracket.append('term')
            self.tokens.advance()
            self.indent+=1
            self.compileTerm()


        elif self.tokens.current_token[0]=='=':
            self.output_file.write(space+self.tag_root('term','open')+'\n')
            self.bracket.append('term')
            self.indent+=1
            self.tokens.advance()
            self.compileTerm()

            #handles multiple func ParameterList ex: drawer.drawrec(x,y,c,z)
        elif self.tokens.current_token[0]==',' and self.bracket[-3]=='expressionList':
            self.indent-=1
            space=self.space*self.indent
            self.output_file.write(space+self.tag_root(self.bracket.pop(),'close')+'\n')
            self.compileExpression()

            #handle let i=(-x) type statement
        elif self.tokens.current_token[0] in ['-','~'] and self.tokens.previous_token(2)[0]=='(':
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.output_file.write(space+self.tag_root('term','open')+'\n')
            self.bracket.append('term')
            self.indent+=1
            self.tokens.advance()
            self.compileTerm()




        #handle '<' sign token
        elif self.tokens.current_token[0] in less_or_great_sign:
            #change current token
            self.tokens.current_token=less_or_great_sign[self.tokens.current_token[0]]
            self.indent-=1
            space=self.space*self.indent
            self.output_file.write(space+self.tag_root(self.bracket.pop(),'close')+'\n')
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.output_file.write(space+self.tag_root('term','open')+'\n')
            self.bracket.append('term')
            self.tokens.advance()
            self.indent+=1
            self.compileTerm()

        elif self.tokens.current_token[0]=='(' and self.tokens.previous_token(2)[0]=='&':
            self.output_file.write(space+self.tag_root('term','open')+'\n')
            self.bracket.append('term')
            self.indent+=1
            self.compileExpression()

        elif self.tokens.current_token[0]=='(' and self.bracket[-2] in ['whileStatement','ifStatement']:
            self.output_file.write(space+self.tag_root('term','open')+'\n')
            self.bracket.append('term')
            self.indent+=1
            self.tokens.advance()
            self.compileTerm()

        elif self.tokens.current_token[0]=='(' and self.bracket[-2]=='expressionList':
            self.output_file.write(space+self.tag_root('term','open')+'\n')
            self.bracket.append('term')
            self.indent+=1
            self.tokens.advance()
            self.compileTerm()

        #if not in a function or function call. and already tagged by compileExpression. tag and advance

        elif self.tokens.current_token[0]=='(' and self.tokens.previous_token(3) not in ['.','void'] and self.bracket[-1]=='expression':
            self.output_file.write(space+self.tag_root('term','open')+'\n')
            self.bracket.append('term')
            self.indent+=1
            self.tokens.advance()
            self.compileTerm()

        #can combine the below elif with the above statement_type
        elif self.tokens.current_token[0]=='[' and self.bracket[-1]=='expression':
            self.output_file.write(space+self.tag_root('term','open')+'\n')
            self.bracket.append('term')
            self.indent+=1
            self.tokens.advance()
            self.compileTerm()

            #if in a new term send it to expression
        elif self.tokens.current_token[0]=='[' and self.bracket[-1]=='term':
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.compileExpression()

        elif self.tokens.current_token[0]=='(':
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.compileExpressionList()

        elif self.tokens.current_token[0]==')' and self.bracket[-1]=='doStatement':
            self.tokens.advance()
            self.compileDo()

        #if condition is true, close current tag and go to compileExpression without advancing the tokens
        elif self.tokens.current_token[0]==')' or self.tokens.current_token[0]==';'  or self.tokens.current_token[0]==']' :
            self.indent-=1
            space=self.space*self.indent
            self.output_file.write(space+self.tag_root(self.bracket.pop(),'close')+'\n')
            self.compileExpression()

           #tag identifier
        elif self.tokens.current_token[0] not in self.symbol and self.tokens.current_token[0] not in self.keyword:
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileTerm()

        #handle symbol
        elif self.tokens.current_token[0] in self.symbol :
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileTerm()

        elif self.tokens.current_token[0] in self.keyword :
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileTerm()

        elif self.tokens.current_token[0]=='':
            return

    def compileExpressionList(self):
        space=self.space*self.indent
        if self.tokens.current_token[0]=='(' and  self.tokens.next_token()[0]==')':
            self.output_file.write(space+self.tag_root('expressionList','open')+'\n')
            self.bracket.append('expressionList')
            self.indent+=1
            self.tokens.advance()
            self.compileExpressionList()

        #if not in a function or function call. go to compileExpression for tagging
        elif self.tokens.current_token[0]=='(' and self.tokens.previous_token(3)[0] not in ['.','void']:
            print 'int', self.tokens.previous_token(3)[0]
            self.compileExpression()


        elif self.tokens.current_token[0]=='(':
            self.output_file.write(space+self.tag_root('expressionList','open')+'\n')
            self.bracket.append('expressionList')
            self.indent+=1
            self.compileExpression()

        elif self.tokens.current_token[0]==')' and self.bracket[-1]=='expressionList':
            self.indent-=1
            space=self.space*self.indent
            self.output_file.write(space+self.tag_root(self.bracket.pop(),'close')+'\n')
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.compileTerm()

        elif self.tokens.current_token[0]==')' and self.bracket[-1] in self.statement_type:
            self.tokens.advance()
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.indent-=1
            space=self.space*self.indent
            self.output_file.write(space+self.tag_root(self.bracket.pop(),'close')+'\n')
            self.tokens.advance()
            self.check_for_statements()


    def compileWhile(self):
        space=self.space*self.indent
        if self.tokens.current_token[0]=='while':
            self.output_file.write(space+self.tag_root('whileStatement','open')+'\n')
            self.bracket.append('whileStatement')
            self.indent+=1
            space=self.space*self.indent
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileWhile()

        elif self.tokens.current_token[0]=='(':
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.compileExpression()

        elif self.tokens.current_token[0]==')':
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileWhile()

        elif self.tokens.current_token[0]=='{':
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.output_file.write(space+self.tag_root('statements','open')+'\n')
            self.bracket.append('statements')
            self.tokens.advance()
            self.indent+=1
            self.check_for_statements()

    def compileDo(self):
        space=self.space*self.indent
        if self.tokens.current_token[0]=='do':
            self.output_file.write(space+self.tag_root('doStatement','open')+'\n')
            self.bracket.append('doStatement')
            self.indent+=1
            space=self.space*self.indent #update space
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileDo()

        elif self.tokens.current_token[0] not in self.symbol and self.tokens.current_token[0] not in self.keyword:
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileDo()

        elif self.tokens.current_token[0]=='(':
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.compileExpressionList()

            #close doStatement
        elif self.tokens.current_token[0]==';':
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.indent-=1
            space=self.space*self.indent
            self.output_file.write(space+self.tag_root(self.bracket.pop(),'close')+'\n')
            self.tokens.advance()
            self.compileDo()


        elif self.tokens.current_token[0]=='}':
            self.indent-=1
            space=self.space*self.indent
            self.output_file.write(space+self.tag_root(self.bracket.pop(),'close')+'\n')
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            if self.bracket[-1] in ['ifStatement','whileStatement']:
                self.indent-=1
                space=self.space*self.indent
                self.output_file.write(space+self.tag_root(self.bracket.pop(),'close')+'\n')
            self.tokens.advance()
            self.compileDo()

        #handle symbol
        elif self.tokens.current_token[0] in self.symbol :
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileDo()

        else:
            self.check_for_statements()

    def compileReturn(self):
        space=self.space*self.indent
        if self.tokens.current_token[0]=='return' and self.bracket[-1]=='ifStatement':
            self.indent-=1
            space=self.space*self.indent
            self.output_file.write(space+self.tag_root(self.bracket.pop(),'close')+'\n')
            self.output_file.write(space+self.tag_root('returnStatement','open')+'\n')
            self.bracket.append('returnStatement')
            self.indent+=1
            space=self.space*self.indent #update space
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileReturn()

        elif self.tokens.current_token[0]=='return':
            self.output_file.write(space+self.tag_root('returnStatement','open')+'\n')
            self.bracket.append('returnStatement')
            self.indent+=1
            space=self.space*self.indent #update space
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileReturn()

        elif self.tokens.current_token[0]==';':
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.indent-=1
            space=self.space*self.indent
            #close returnstatements
            self.output_file.write(space+self.tag_root(self.bracket.pop(),'close')+'\n')
            self.indent-=1
            space=self.space*self.indent
            #close statement
            self.output_file.write(space+self.tag_root(self.bracket.pop(),'close')+'\n')
            self.tokens.advance()
            self.compileReturn()

        elif self.tokens.current_token[0]=='}':# and len(self.bracket)>0:
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.indent-=1
            space=self.space*self.indent
            self.output_file.write(space+self.tag_root(self.bracket.pop(),'close')+'\n')
            self.tokens.advance()
            #check to see if it is a terminal bracket if not close it twice
            if len(self.bracket)>0:
                self.indent-=1
                space=self.space*self.indent
                self.output_file.write(space+self.tag_root(self.bracket.pop(),'close')+'\n')
                self.compileReturn()

        #tag expression and term and go to term
        elif (self.tokens.current_token[0] not in self.symbol and self.tokens.current_token[0] not in self.keyword) or (self.tokens.current_token[0] not in self.symbol and self.tokens.current_token[0]=='this'):
            self.output_file.write(space+self.tag_root('expression','open')+'\n')
            self.bracket.append('expression')
            self.indent+=1
            space=self.space*self.indent
            self.output_file.write(space+self.tag_root('term','open')+'\n')
            self.bracket.append('term')
            self.indent+=1
            self.compileTerm()

        else:
            self.check_for_statements()

    def compileClassVarDec(self):
        space=self.space*self.indent
        if self.tokens.current_token[0] in ['static','field']:
            self.output_file.write(space+self.tag_root('classVarDec','open')+'\n')
            self.bracket.append('classVarDec')
            self.indent+=1
            space=self.space*self.indent #update space
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileClassVarDec()

        #tag identifier
        elif self.tokens.current_token[0] not in self.symbol and self.tokens.current_token[0] not in self.keyword:
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileClassVarDec()

        elif self.tokens.current_token[0]==';':
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.indent-=1
            space=self.space*self.indent #update space
            self.output_file.write(space+self.tag_root(self.bracket.pop(),'close')+'\n')
            self.tokens.advance()
            self.check_for_statements()

        elif self.tokens.current_token[0] in self.keyword  or self.tokens.current_token[0] in self.symbol :
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileClassVarDec()


    def compileIf(self):
        space=self.space*self.indent
        if self.tokens.current_token[0]=='if' and self.bracket[-1]=='statements':
            self.output_file.write(space+self.tag_root('ifStatement','open')+'\n')
            self.bracket.append('ifStatement')
            self.indent+=1
            space=self.space*self.indent #update space
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileIf()

        elif self.tokens.current_token[0]=='if':
            #open statements
            self.output_file.write(space+self.tag_root('statements','open')+'\n')
            self.bracket.append('statements')
            self.indent+=1
            space=self.space*self.indent #update space
            #open ifstatement
            self.output_file.write(space+self.tag_root('ifStatement','open')+'\n')
            self.bracket.append('ifStatement')
            self.indent+=1
            space=self.space*self.indent #update space
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileIf()

        elif self.tokens.current_token[0]=='(':
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.compileExpression()

        elif self.tokens.current_token[0]==')':
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileIf()

        elif self.tokens.current_token[0]=='{':
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.output_file.write(space+self.tag_root('statements','open')+'\n')
            self.bracket.append('statements')
            self.indent+=1
            self.tokens.advance()
            self.check_for_statements()

        elif self.tokens.current_token[0]=='else':
            self.output_file.write(space+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileIf()

    def compileStatements(self):
        pass


    def compileParameterList(self):
        pass


if __name__=='__main__':
    path='/home/emmanuel/Desktop/programming_project/from-nand2tetris/compiler/Main.jack'
    obj=compilationEngine(path)
    obj.compileClass()
