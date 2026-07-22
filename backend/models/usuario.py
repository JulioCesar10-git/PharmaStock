class Usuario:
    def __init__(self, usuario_usuario, usuario_correoElec, usuario_password, usuario_cargo, usuario_id = None):
        self.usuario_id = usuario_id
        self.usuario_usuario = usuario_usuario
        self.usuario_correoElec = usuario_correoElec
        self.usuario_password = usuario_password
        self.usuario_cargo = usuario_cargo

    def __str__(self):
        return f"Usuario(usuario_id = {self.usuario_id}), usuario = '{self.usuario_usuario}', correo = '{self.usuario_correoElec}', password = '{self.usuario_password}', cargo = '{self.usuario_cargo}'"