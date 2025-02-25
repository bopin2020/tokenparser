from enum import IntEnum
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename= 'debug.log', level= logging.INFO)

class Token:
    dic = {}
    def __init__(self,type,value,line=None):
        self.type,self.value,self.lineno = type,value,(line or (0,0))
    def __repr__(self):
        return f'Token(type={self.type!r}, value={self.value!r}, lineno={self.lineno!r})'

class LexerStatus(IntEnum):
    COMMENTS        = 0,
    LMULTICOMMENTS  = 1,
    SET             = 2,
    INIT            = 0xfa,
    FINISHED        = 0xfb,

class Lexer:
    comments = {
        '//' : 'COMMENTS',
        '#'  : 'COMMENTS',
        '/*' : 'LMULTICOMMENTS',
    }
    keywords = {
        'set' : 'SET',
        'block': 'BLOCK',
    }
    def log(self,status,line,off):
        tmp = f'statemachine: {status} current line: {line} off: {off}'
        print(tmp)
        logger.info(tmp)

    def tokenize(self,text):
        filesize,off,lineno,idx,state,accum = 0,1,1,0,LexerStatus.INIT, ''
        while idx < len(text):
            filesize += 1
            sym1 = text[idx+0] if idx<len(text)-0 else ' '
            sym2 = text[idx+1] if idx<len(text)-1 else ' '
            sym3 = text[idx+2] if idx<len(text)-2 else ' '
            match state:
                case LexerStatus.COMMENTS:
                    if sym1 != '\n':
                        accum += sym1
                        off += 1
                    else:
                        yield Token('STRING',accum,(lineno,off))
                        state = LexerStatus.INIT
                        off = 0
                        accum = ''
                case LexerStatus.LMULTICOMMENTS:
                    if sym1 != '*' and sym2 != '/':
                        accum += sym1
                        off += 1
                    else:
                        yield Token('STRING',accum,(lineno,off))
                        state = LexerStatus.INIT
                        off = 0
                        accum = ''
                case LexerStatus.SET:
                    if sym1 != ';':
                        if sym1 == '\n' or sym2 == '\n':
                            self.log(state,lineno,off)
                            raise Exception(f"SET missing semicolon {lineno} {off}")
                        accum += sym1
                        off += 1
                    else:
                        tmp = str(accum).split('=')
                        logger.info(f'{str(tmp[0]).strip(' ') + str(tmp[1]).strip(' ')}')
                        Token.dic.update({str(tmp[0]).strip(' '): str(tmp[1]).strip(' ')})
                        yield Token('STRING',accum,(lineno,off))
                        state = LexerStatus.INIT
                        off = 0
                        accum = ''
                case LexerStatus.INIT:
                    if sym1 == '/' and sym2 == '/':
                        idx += 1
                        state = LexerStatus.COMMENTS
                    if sym1 == '#':
                        state = LexerStatus.COMMENTS
                    if sym1 == '/' and sym2 == '*':
                        idx += 1
                        state = LexerStatus.LMULTICOMMENTS
                    if sym1 == 's' and sym2 == 'e' and sym3 == 't':
                        idx += 2
                        state = LexerStatus.SET
                    self.log(state,lineno,off)
            if sym1 == '\n':
                lineno += 1
                off = 0
            idx += 1
        state = LexerStatus.FINISHED
        print(f'filesize: {filesize}')