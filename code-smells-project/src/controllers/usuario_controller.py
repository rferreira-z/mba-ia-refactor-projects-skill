"""Casos de uso de usuário e autenticação."""
import logging

from src.config.constants import TIPO_USUARIO_PADRAO
from src.controllers.validators import validar_credenciais, validar_novo_usuario
from src.errors import NotFoundError, UnauthorizedError

logger = logging.getLogger(__name__)


class UsuarioController:
    def __init__(self, usuarios, senhas, tokens):
        self.usuarios = usuarios
        self.senhas = senhas
        self.tokens = tokens

    def listar(self):
        return self.usuarios.listar()

    def obter(self, usuario_id):
        usuario = self.usuarios.buscar_por_id(usuario_id)
        if usuario is None:
            raise NotFoundError("Usuário não encontrado")
        return usuario

    def criar(self, dados):
        novo = validar_novo_usuario(dados)
        usuario_id = self.usuarios.criar(
            novo["nome"],
            novo["email"],
            self.senhas.gerar_hash(novo["senha"]),
            TIPO_USUARIO_PADRAO,
        )
        logger.info("usuario.criado id=%s", usuario_id)
        return usuario_id

    def autenticar(self, dados):
        credenciais = validar_credenciais(dados)
        registro = self.usuarios.buscar_credenciais_por_email(credenciais["email"])

        if registro is None or not self.senhas.verificar(credenciais["senha"], registro["senha_hash"]):
            logger.info("login.falhou")
            raise UnauthorizedError("Email ou senha inválidos")

        usuario = registro["usuario"]
        logger.info("login.sucesso usuario_id=%s", usuario["id"])
        return {**usuario, "token": self.tokens.emitir(usuario["id"], usuario["tipo"])}
