# ============================================
# CORES PARA TERMINAL - VERSÃO COMPLETA
# ============================================

class Cores:
    """Códigos ANSI para colorir o terminal"""
    
    # Estilos
    RESET = '\033[0m'
    NEGRITO = '\033[1m'
    ITALICO = '\033[3m'
    SUBLINHADO = '\033[4m'
    
    # Cores de texto
    PRETO = '\033[30m'
    VERMELHO = '\033[31m'
    VERDE = '\033[32m'
    AMARELO = '\033[33m'
    AZUL = '\033[34m'
    MAGENTA = '\033[35m'
    CIANO = '\033[36m'
    BRANCO = '\033[37m'
    
    # Cores de fundo
    FUNDO_PRETO = '\033[40m'
    FUNDO_VERMELHO = '\033[41m'
    FUNDO_VERDE = '\033[42m'
    FUNDO_AMARELO = '\033[43m'
    FUNDO_AZUL = '\033[44m'
    FUNDO_MAGENTA = '\033[45m'
    FUNDO_CIANO = '\033[46m'
    FUNDO_BRANCO = '\033[47m'
    
    @classmethod
    def colorir(cls, texto: str, cor: str, estilo: str = '') -> str:
        """Aplica cor ao texto"""
        return f"{estilo}{cor}{texto}{cls.RESET}"
    
    @classmethod
    def vermelho(cls, texto: str) -> str:
        return cls.colorir(texto, cls.VERMELHO, cls.NEGRITO)
    
    @classmethod
    def verde(cls, texto: str) -> str:
        return cls.colorir(texto, cls.VERDE, cls.NEGRITO)
    
    @classmethod
    def amarelo(cls, texto: str) -> str:
        return cls.colorir(texto, cls.AMARELO, cls.NEGRITO)
    
    @classmethod
    def azul(cls, texto: str) -> str:
        return cls.colorir(texto, cls.AZUL, cls.NEGRITO)
    
    @classmethod
    def magenta(cls, texto: str) -> str:
        return cls.colorir(texto, cls.MAGENTA, cls.NEGRITO)
    
    @classmethod
    def ciano(cls, texto: str) -> str:
        return cls.colorir(texto, cls.CIANO, cls.NEGRITO)
    
    @classmethod
    def branco(cls, texto: str) -> str:
        return cls.colorir(texto, cls.BRANCO, cls.NEGRITO)
    
    @classmethod
    def sucesso(cls, texto: str) -> str:
        return f"{cls.VERDE}✅ {texto}{cls.RESET}"
    
    @classmethod
    def erro(cls, texto: str) -> str:
        return f"{cls.VERMELHO}❌ {texto}{cls.RESET}"
    
    @classmethod
    def alerta(cls, texto: str) -> str:
        return f"{cls.AMARELO}⚠️ {texto}{cls.RESET}"
    
    @classmethod
    def info(cls, texto: str) -> str:
        return f"{cls.AZUL}ℹ️ {texto}{cls.RESET}"