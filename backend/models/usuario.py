class Usuario:
    def __init__(self, usuario_usuario, usuario_correoElec, usuario_password, 
                 usuario_cargo, usuario_telefono, usuario_apellidoPat=None, usuario_apellidoMat=None, 
                 usuario_imagen=None, usuario_id=None):
        self.usuario_id = usuario_id
        self.usuario_usuario = usuario_usuario
        self.usuario_correoElec = usuario_correoElec
        self.usuario_password = usuario_password
        self.usuario_cargo = usuario_cargo
        self.usuario_apellidoPat = usuario_apellidoPat
        self.usuario_apellidoMat = usuario_apellidoMat
        self.usuario_telefono = usuario_telefono,
        self.usuario_imagen = usuario_imagen

    def __str__(self):
        return f"Usuario(id={self.usuario_id}, usuario='{self.usuario_usuario}', correo='{self.usuario_correoElec}', rol='{self.usuario_cargo}')"