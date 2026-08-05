class Tarea:

    def __init__(self, tarea_asunto, tarea_id = None):
        self.tarea_id = tarea_id,
        self.tarea_asunto = tarea_asunto

    def __str__(self):
        return f"Tarea(tarea_id = {self.tarea_id}), Ausnto = '{self.tarea_asunto}'"