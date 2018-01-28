import re


class JackTokenizer:

    def __init__(self,input_file_path):
        self.input_file= input_file_path
        self.jack_symbol=['{','}','(',')','[',']','.',',',';','+','-','*','/','&','|','<','>','=','_','~']
        self.regex_symbol_str='([\{\}\(\)\[\]\.\,\;\+\-\*\/\&\|\<\>\=\_\~])' #this is the regex split pattern will use it below to tokenize the cleaned txt
        self.jack_keyword=['class','constructor','function', 'method','field','static','var','int', 'char',
            'boolean','void','true','false','null','this','let','do',
            'if','else','while','return']

        self.current_token=''
        self.token_lst=''
        self.all_token_lst=''
        self.next_token_idx=0

    def remove_comments(self):
        '''remove line starting by // and in code commenting and removes spaces'''
        fh=open(self.input_file,'r')
        txt=fh.read()
        new_list=[]
        code_lst=txt.split('\n')
        for line in code_lst:
            line=line.strip()
            #if the line does not start with //,/**,* and line is not empty string. then is
            #valid candidate of code.
            if line.startswith('*')==False and line.startswith('//')==False and line.startswith('/**')==False and line !='':
                candidate=line
                if '//' in candidate:
                    idx=candidate.index('//')
                    candidate=candidate[:idx]
                    new_list.append(candidate.strip())
                else:
                    new_list.append(candidate.strip())
        return ''.join(new_list)

    def tokenType(self):
        if len(self.current_token)==2:
            return self.current_token[1].upper()
        return None

    def classifier(self,tokens):
        classified_tokens=[]
        for token in tokens:
            if token in self.jack_symbol:
                classified_tokens.append((token,'symbol'))
            elif token in self.jack_keyword:
                classified_tokens.append((token,'keyword'))
            elif token.isdigit()==True:
                classified_tokens.append((token,'integerConstant'))
            elif '"' in token:
                classified_tokens.append((token.strip('"'),'stringConstant'))
            else:
                classified_tokens.append((token,'identifier'))
        return classified_tokens

    def tokenize(self):
        cleaned_txt=self.remove_comments()
        pre_tokens=[token.strip() for token in re.split(self.regex_symbol_str,  cleaned_txt) if token.strip()!='']
        tokens=[]
        for token in pre_tokens:
            if '"' not in token:
                tokens+=token.split()
            else: tokens+=[token.strip()]
        tokens_classified=self.classifier(tokens)
        self.token_lst= tokens_classified
        self.all_token_lst= list(tokens_classified)
        #return tokens_classified

    def hasMoreToken(self):
        if len(self.token_lst)>0:
            return True
        return False

    def advance(self):
        if len(self.token_lst)==0:
            self.current_token=('','')
        elif len(self.token_lst)>0:
            self.current_token=self.token_lst.pop(0)
            self.next_token_idx+=1

    def next_token(self):
        '''return the next token that the advance method would return'''
        return self.all_token_lst[self.next_token_idx]

    def previous_token(self,num_stepback):
        if self.next_token_idx>num_stepback:
            return self.all_token_lst[self.next_token_idx - num_stepback]
        else:
            return 'num_stepback is great token list'

    def keyword(self):
        if self.tokenType().lower()=='keyword':
            return self.current_token[0]
        else:
            return  'called on wrong type'

    def symbol(self):
        if self.tokenType().lower()=='symbol':
            return self.current_token[1]
        else: return 'called on wrong type'

    def identifier(self):
        if self.tokenType().lower()=='identifier':
            return self.current_token[0]
        else: return 'called on wrong type'

    def intval(self):
        if self.tokenType().lower()=='integerconstant':
            return self.current_token[0]
        else: return 'called on wrong type'

    def stringval(self):
        if self.tokenType().lower()=='stringconstant':
            return self.current_token[0].strip('"').strip()
        else: return 'called on wrong type'

    def __str__(self):
        if len(self.all_token_lst)>0:
            file=open('file.Txml','w')
            for token in self.all_token_lst:
                file.write('<' +token[1]+'> ' +token[0]+' </'+token[1]+'>'+'\n')
        return 'see file.Txml for output'


if __name__ == '__main__':

    path='/home/emmanuel/Desktop/programming_project/from-nand2tetris/compiler/Main.jack'
    token_lst_file='/home/emmanuel/Desktop/programming_project/from-nand2tetris/compiler/token_lst.txt'

    jack_token_lst=open(token_lst_file,'w')
    obj=JackTokenizer(path)
    #clean=obj.remove_comments()
    clean=obj.tokenize()
    for i in  obj.token_lst:
        print i[0]
