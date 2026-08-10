class Tarea:

    def __init__(self, tarea_asunto, tarea_id=None, tarea_fecha=None):
        self.tarea_id = tarea_id
        self.tarea_asunto = tarea_asunto
        self.tarea_fecha = tarea_fecha

    def __str__(self):
        return f"Tarea(tarea_id={self.tarea_id}, tarea_asunto='{self.tarea_asunto}', tarea_fecha={self.tarea_fecha})"