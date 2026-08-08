from frontend.state import ESTADO_UI

# --- Paleta clara ---
PALETA_CLARA = {
    "azul_card": "#A5C3F5",
    "fondo_card": "#C3E2FF",
    "input_bg": "#0B2B63",
    "texto_muted": "#D0E0FF",
    "border": "#84ACFF",
    "bg_card_blue": "#D3E4FF",
    "bg_card_yellow": "#F1DC99",
    "text_red": "#D32F2F",
    "bg_card_white": "#FFFFFF",
    "fondo_app": "#F4F8FE",
    "fondo_menu": "#FFFFFF",
    "fondo_lienzo": "#EBF3FF",
    "borde_campo": "#588CEF",
    "boton_secundario": "#588CEF",
    "pildora_inactiva": "#D0E0FF",
    "avatar_bg": "#0B2B63",
    "divisor": "#EBF3FF",
    "texto_secundario": "#6B7280",
    "texto_nav_inactivo": "#0062BF",
    "niveles_empleados": ["#F2A93B", "#84ACFF", "#C9A227"],
    "sombra": "#A9B8CE",
    "pildora_stock_bajo": "#FFEBEE",
    "pildora_por_caducar": "#FFF3E0",
    "pildora_caducado": "#FCE4EC",
    "titulo_avisos": "#D32F2F",
}

# --- Paleta oscura ---
PALETA_OSCURA = {
    "azul_card": "#2F5FDB",
    "fondo_card": "#0B1B3F",
    "input_bg": "#CEDEF9",
    "texto_muted": "#9FB3E8",
    "border": "#2F5FDB",
    "bg_card_blue": "#13275C",
    "bg_card_yellow": "#3A2E12",
    "text_red": "#FF6B6B",
    "bg_card_white": "#122A58",
    "fondo_app": "#0B1B3F",
    "fondo_menu": "#0B1B3F",
    "fondo_lienzo": "#0F2450",
    "borde_campo": "#2F5FDB",
    "boton_secundario": "#1F3E85",
    "pildora_inactiva": "#2A427E",
    "avatar_bg": "#2F5FDB",
    "divisor": "#1A2F5C",
    "texto_secundario": "#8FA3D4",
    "texto_nav_inactivo": "#FFFFFF",
    "niveles_empleados": ["#F2A93B", "#5F86D9", "#C9A227"],
    "sombra": "#1F3E85",
    "pildora_stock_bajo": "#4A1B24",
    "pildora_por_caducar": "#4A3510",
    "pildora_caducado": "#3A1A30",
    "titulo_avisos": "#FFFFFF",
}

# --- Devuelve la paleta activa según el modo actual ---
def colores():
    return PALETA_OSCURA if ESTADO_UI["modo_oscuro"] else PALETA_CLARA

# --- Constantes de compatibilidad (siempre paleta clara) ---
COLOR_AZUL_CARD = PALETA_CLARA["azul_card"]
COLOR_INPUT_BG = PALETA_CLARA["input_bg"]
COLOR_TEXTO_MUTED = PALETA_CLARA["texto_muted"]
COLOR_BORDER = PALETA_CLARA["border"]

BG_CARD_BLUE = PALETA_CLARA["bg_card_blue"]
BG_CARD_YELLOW = PALETA_CLARA["bg_card_yellow"]
TEXT_RED = PALETA_CLARA["text_red"]
BG_CARD_WHITE = PALETA_CLARA["bg_card_white"]

COLORES_NIVELES_EMPLEADOS = PALETA_CLARA["niveles_empleados"]