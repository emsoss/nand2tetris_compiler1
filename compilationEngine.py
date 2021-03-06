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

    def get_dynamic_space(self):
        '''return indentation required for valid xml writing'''
        return self.space*self.indent

    def open_new_root_tag(self,type_of_tag):
        self.output_file.write(self.get_dynamic_space()+self.tag_root(type_of_tag,'open')+'\n')
        self.bracket.append(type_of_tag)
        self.indent+=1

    def write_terminal_elm_advance_compile(self,call_compile_method):
        self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
        self.tokens.advance()
        call_compile_method()

    def close_tag(self):
        self.indent-=1
        self.output_file.write(self.get_dynamic_space()+self.tag_root(self.bracket.pop(),'close')+'\n')


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

        if self.tokens.current_token[0]=='class':
            self.open_new_root_tag('class')
            self.write_terminal_elm_advance_compile(self.compileClass)
            #self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            #self.tokens.advance()
            #self.compileClass()

        elif self.tokens.current_token[0]=='':
            return

        #handle classvarDec opening
        elif self.tokens.current_token[0] in ['static','field']:
            self.compileClassVarDec()


        #tag identifier
        elif self.tokens.current_token[0] not in self.symbol and self.tokens.current_token[0] not in self.keyword:
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileClass()

        #tag symbol
        elif self.tokens.current_token[0] in self.symbol :
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileClass()

        #tag statements_key
        elif self.tokens.current_token[0] in self.statements_key:
            self.check_for_statements()

        #tag keyword other than statements_key
        elif self.tokens.current_token[0] in self.keyword:
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileClass()


    def compileSubroutine(self):
        #
        if self.tokens.previous_token(2)[0]=='}' and (self.bracket[-1] in ['subroutineBody','subroutineDec']):
            self.close_tag()
            self.compileSubroutine()


        elif self.tokens.current_token[0] in ['method','function','subroutine','constructor']:
            self.open_new_root_tag('subroutineDec')
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileSubroutine()

        elif self.tokens.current_token[0]=='':
            return

        elif self.tokens.current_token[0]=='(' :
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.open_new_root_tag('parameterList')
            self.tokens.advance()
            self.compileSubroutine()

        elif self.tokens.current_token[0]==')' :
            self.close_tag()
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileSubroutine()

        elif self.tokens.current_token[0]=='{' and self.tokens.next_token()[0]=='var':
            self.open_new_root_tag('subroutineBody')
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileVarDec()

        elif self.tokens.current_token[0]=='{' :
            self.open_new_root_tag('subroutineBody')
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.open_new_root_tag('statements')
            self.tokens.advance()
            self.compileSubroutine()

        elif self.tokens.current_token[0]=='}' :
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.close_tag()
            self.compileSubroutine()

           #tag identifier
        elif self.tokens.current_token[0] not in self.symbol and self.tokens.current_token[0] not in self.keyword:
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileSubroutine()

        elif self.tokens.current_token[0] in self.symbol :
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileSubroutine()

        #tag statements_key
        elif self.tokens.current_token[0] in self.statements_key :
            self.check_for_statements()

        #tag remaing keyword not in statements_key
        elif self.tokens.current_token[0] in self.keyword :
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileSubroutine()

    def compileVarDec(self):

        if self.tokens.current_token[0]=='var':
            self.open_new_root_tag('varDec')
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileVarDec()

        elif self.tokens.current_token[0]=='':
            return


        elif self.tokens.current_token[0]==',':
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileVarDec()

        elif self.tokens.current_token[0]==';':
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.close_tag()
            self.tokens.advance()
            self.compileVarDec()

           #tag identifier
        elif self.tokens.current_token[0] not in self.symbol and self.tokens.current_token[0] not in self.keyword:
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileVarDec()

        #tag token in statements_key
        elif self.tokens.current_token[0] in self.statements_key:
            self.check_for_statements()

        #tag keyword token not in statements_key
        elif self.tokens.current_token[0] in self.keyword:
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileVarDec()



    def compileLet(self):

        if self.tokens.current_token[0]=='let':
            if 'statements' not in self.bracket:
                self.open_new_root_tag('statements')
                self.open_new_root_tag('letStatement')
                self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
                self.tokens.advance()
                self.compileLet()

            else:
                self.open_new_root_tag('letStatement')
                self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
                self.tokens.advance()
                self.compileLet()

           #tag identifier
        elif self.tokens.current_token[0] not in self.symbol and self.tokens.current_token[0] not in self.keyword:
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileLet()

        elif self.tokens.current_token[0]=='=':
            self.compileExpression()

        elif self.tokens.current_token[0]=='[':
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.compileExpression()

    def compileExpression(self):

        if self.tokens.current_token[0]=='=':
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.open_new_root_tag('expression')
            self.compileTerm()

            #handles multiple func ParameterList ex: drawer.drawrec(x,y,c,z)
        elif self.tokens.current_token[0]==',' and self.bracket[-2]=='expressionList':
            self.close_tag()
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.open_new_root_tag('expression')
            self.open_new_root_tag('term')
            self.tokens.advance()
            self.compileTerm()

        elif self.tokens.current_token[0]=='(' and self.tokens.previous_token(2)[0]=='&':
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.open_new_root_tag('expression')
            self.open_new_root_tag('term')
            self.tokens.advance()
            self.compileTerm()

        elif self.tokens.current_token[0]=='(' and self.bracket[-1] in ['whileStatement','ifStatement']:
            self.open_new_root_tag('expression')
            self.compileTerm()

        elif self.tokens.current_token[0]=='(' or self.tokens.current_token[0]=='[':
            self.open_new_root_tag('expression')
            self.compileTerm()

        elif self.tokens.current_token[0]==']':
            self.close_tag()
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileExpression()

        elif self.tokens.current_token[0]==')' and self.bracket[-1]=='term':
            self.compileTerm()

        elif self.tokens.current_token[0]==')' and self.bracket[-1]=='expression':
            self.close_tag()
            #if in whileStatement go to whileStatement;
            if self.bracket[-1]=='whileStatement':
                self.compileWhile()

            #if in ifstament go to compileIf
            elif self.bracket[-1]=='ifStatement':
                self.compileIf()

            elif self.bracket[-1]=='term' and self.tokens.next_token()[0]=='&':
                self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
                self.close_tag()
                #replace & by &amp;
                self.tokens.advance()
                self.tokens.current_token=('&amp;','symbol')
                self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
                self.tokens.advance()
                self.compileTerm()

            elif self.bracket[-1]=='term':
                self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
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
            self.close_tag()
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.close_tag()
            self.tokens.advance()
            self.compileExpression()

        elif self.tokens.previous_token(2)[0]=='}' and (self.bracket[-1] in ['subroutineBody','subroutineDec']):
            self.compileSubroutine()

        elif self.tokens.current_token[0]=='}':
            self.close_tag()
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))

            condition2= self.bracket[-1]=='whileStatement' #condition for whileStatement closing
            if (self.bracket[-1]=='ifStatement' and self.tokens.next_token()[0]!='else') or condition2:
                self.close_tag()
                self.tokens.advance()
                self.compileExpression()
            else :
                self.tokens.advance()
                self.compileExpression()

        else:
            self.check_for_statements()


    def compileTerm(self):

        less_or_great_sign={'<':('&lt;','symbol'),'>':('&gt;','symbol')}
        equal_sign_in_if_condition=self.tokens.current_token[0]=='=' and self.get_current_statement(-1)=='ifStatement'
        equal_sign_in_while_condition=self.tokens.current_token[0]=='=' and self.get_current_statement(-1)=='whileStatement'

        #handle '+' sign token
        if self.tokens.current_token[0] in ['+','-','/','*','|'] or equal_sign_in_if_condition or equal_sign_in_while_condition:
            self.close_tag()
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.open_new_root_tag('term')
            self.tokens.advance()
            self.compileTerm()


        elif self.tokens.current_token[0]=='=':
            self.open_new_root_tag('term')
            self.tokens.advance()
            self.compileTerm()

            #handles multiple func ParameterList ex: drawer.drawrec(x,y,c,z)
        elif self.tokens.current_token[0]==',' and self.bracket[-3]=='expressionList':
            self.close_tag()
            self.compileExpression()

            #handle let i=(-x) type statement
        elif self.tokens.current_token[0] in ['-','~'] and self.tokens.previous_token(2)[0]=='(':
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.open_new_root_tag('term')
            self.tokens.advance()
            self.compileTerm()




        #handle '<' sign token
        elif self.tokens.current_token[0] in less_or_great_sign:
            #change current token
            self.tokens.current_token=less_or_great_sign[self.tokens.current_token[0]]
            self.close_tag()
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.open_new_root_tag('term')
            self.tokens.advance()
            self.compileTerm()

        elif self.tokens.current_token[0]=='(' and self.tokens.previous_token(2)[0]=='&':
            self.open_new_root_tag('term')
            self.compileExpression()

        elif self.tokens.current_token[0]=='(' and self.bracket[-2] in ['whileStatement','ifStatement']:
            self.open_new_root_tag('term')
            self.tokens.advance()
            self.compileTerm()

        elif self.tokens.current_token[0]=='(' and self.bracket[-2]=='expressionList':
            self.open_new_root_tag('term')
            self.tokens.advance()
            self.compileTerm()

        #if not in a function or function call. and already tagged by compileExpression. tag and advance
        elif self.tokens.current_token[0]=='(' and self.tokens.previous_token(3) not in ['.','void'] and self.bracket[-1]=='expression':
            self.open_new_root_tag('term')
            self.tokens.advance()
            self.compileTerm()

        #can combine the below elif with the above statement_type
        elif self.tokens.current_token[0]=='[' and self.bracket[-1]=='expression':
            self.open_new_root_tag('term')
            self.tokens.advance()
            self.compileTerm()

            #if in a new term send it to expression
        elif self.tokens.current_token[0]=='[' and self.bracket[-1]=='term':
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.compileExpression()

        elif self.tokens.current_token[0]=='(':
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.compileExpressionList()

        elif self.tokens.current_token[0]==')' and self.bracket[-1]=='doStatement':
            self.tokens.advance()
            self.compileDo()

        #if condition is true, close current tag and go to compileExpression without advancing the tokens
        elif self.tokens.current_token[0]==')' or self.tokens.current_token[0]==';'  or self.tokens.current_token[0]==']' :
            self.close_tag()
            self.compileExpression()

           #tag identifier
        elif self.tokens.current_token[0] not in self.symbol and self.tokens.current_token[0] not in self.keyword:
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileTerm()

        #handle symbol
        elif self.tokens.current_token[0] in self.symbol :
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileTerm()

        elif self.tokens.current_token[0] in self.keyword :
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileTerm()

        elif self.tokens.current_token[0]=='':
            return

    def compileExpressionList(self):
        if self.tokens.current_token[0]=='(' and  self.tokens.next_token()[0]==')':
            self.open_new_root_tag('expressionList')
            self.tokens.advance()
            self.compileExpressionList()

        #if not in a function or function call. go to compileExpression for tagging
        elif self.tokens.current_token[0]=='(' and self.tokens.previous_token(3)[0] not in ['.','void']:
            self.compileExpression()


        elif self.tokens.current_token[0]=='(':
            self.open_new_root_tag('expressionList')
            self.compileExpression()

        elif self.tokens.current_token[0]==')' and self.bracket[-1]=='expressionList':
            self.close_tag()
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.compileTerm()

        elif self.tokens.current_token[0]==')' and self.bracket[-1] in self.statement_type:
            self.tokens.advance()
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.close_tag()
            self.tokens.advance()
            self.check_for_statements()


    def compileWhile(self):
        if self.tokens.current_token[0]=='while':
            self.open_new_root_tag('whileStatement')
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileWhile()

        elif self.tokens.current_token[0]=='(':
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.compileExpression()

        elif self.tokens.current_token[0]==')':
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileWhile()

        elif self.tokens.current_token[0]=='{':
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.open_new_root_tag('statements')
            self.tokens.advance()
            self.check_for_statements()

    def compileDo(self):
        #
        if self.tokens.current_token[0]=='do':
            self.open_new_root_tag('doStatement')
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileDo()

        elif self.tokens.current_token[0] not in self.symbol and self.tokens.current_token[0] not in self.keyword:
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileDo()

        elif self.tokens.current_token[0]=='(':
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.compileExpressionList()

            #close doStatement
        elif self.tokens.current_token[0]==';':
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.close_tag()
            self.tokens.advance()
            self.compileDo()


        elif self.tokens.current_token[0]=='}':
            self.close_tag()
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            if self.bracket[-1] in ['ifStatement','whileStatement']:
                self.close_tag()
            self.tokens.advance()
            self.compileDo()

        #handle symbol
        elif self.tokens.current_token[0] in self.symbol :
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileDo()

        else:
            self.check_for_statements()

    def compileReturn(self):
        if self.tokens.current_token[0]=='return' and self.bracket[-1]=='ifStatement':
            self.close_tag()
            self.open_new_root_tag('returnStatement')
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileReturn()

        elif self.tokens.current_token[0]=='return':
            self.open_new_root_tag('returnStatement')
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileReturn()

        elif self.tokens.current_token[0]==';':
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.close_tag()
            self.close_tag()
            self.tokens.advance()
            self.compileReturn()

        elif self.tokens.current_token[0]=='}':# and len(self.bracket)>0:
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.close_tag()
            self.tokens.advance()
            #check to see if it is a terminal bracket if not close it twice
            if len(self.bracket)>0:
                self.close_tag()
                self.compileReturn()

        #tag expression and term and go to term
        elif (self.tokens.current_token[0] not in self.symbol and self.tokens.current_token[0] not in self.keyword) or (self.tokens.current_token[0] not in self.symbol and self.tokens.current_token[0]=='this'):
            self.open_new_root_tag('expression')
            self.open_new_root_tag('term')
            self.compileTerm()

        else:
            self.check_for_statements()

    def compileClassVarDec(self):
        if self.tokens.current_token[0] in ['static','field']:
            self.open_new_root_tag('classVarDec')
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileClassVarDec()

        #tag identifier
        elif self.tokens.current_token[0] not in self.symbol and self.tokens.current_token[0] not in self.keyword:
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileClassVarDec()

        elif self.tokens.current_token[0]==';':
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.close_tag()
            self.tokens.advance()
            self.check_for_statements()

        elif self.tokens.current_token[0] in self.keyword  or self.tokens.current_token[0] in self.symbol :
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileClassVarDec()


    def compileIf(self):
        #
        if self.tokens.current_token[0]=='if' and self.bracket[-1]=='statements':
            self.open_new_root_tag('ifStatement')
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileIf()

        elif self.tokens.current_token[0]=='if':
            self.open_new_root_tag('statements')
            self.open_new_root_tag('ifStatement')
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileIf()

        elif self.tokens.current_token[0]=='(':
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.compileExpression()

        elif self.tokens.current_token[0]==')':
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.tokens.advance()
            self.compileIf()

        elif self.tokens.current_token[0]=='{':
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
            self.open_new_root_tag('statements')
            self.tokens.advance()
            self.check_for_statements()

        elif self.tokens.current_token[0]=='else':
            self.output_file.write(self.get_dynamic_space()+self.tag_body(self.tokens.current_token))
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
