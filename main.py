import streamlit as st
import groq

# --- Configuración de la página ---
st.set_page_config(page_title="Mi Chat de IA", page_icon="😉")

# --- Variables globales ---
ALTURA_CHAT = 400
MODELOS = [
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
    "meta-llama/llama-guard-4-12b"
]

# --- Funciones auxiliares ---
def configurar_pagina():
    """Configura la estructura inicial de la página."""
    st.title("El Chat de Nate")

    nombre = st.text_input("¿Cuál es tu nombre?")
    if st.button("Saludar"):
        st.write(f"¡Hola, {nombre}! 😄​")

    st.sidebar.title("Selección de Modelos")
    modelo = st.sidebar.selectbox("Elegí un Modelo", options=MODELOS, index=0)
    return modelo


def crear_usuario_groq():
    """Crea una instancia del cliente Groq usando la clave del archivo secrets.toml."""
    try:
        clave_secreta = st.secrets["CLAVE_API"]
        return groq.Groq(api_key=clave_secreta)
    except KeyError:
        st.error("❌ No se encontró la clave 'CLAVE_API' en secrets.toml.")
        st.stop()


def configurar_modelo(cliente, modelo_elegido, prompt_usuario):
    """Crea el stream de respuesta del modelo."""
    if not prompt_usuario:
        return None

    return cliente.chat.completions.create(
        model=modelo_elegido,
        messages=[{"role": "user", "content": prompt_usuario}],
        stream=True
    )


def inicializar_estado():
    """Inicializa la sesión de mensajes si aún no existe."""
    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []


def actualizar_historial(rol, contenido, avatar):
    """Guarda los mensajes en el historial."""
    st.session_state.mensajes.append({
        "role": rol,
        "content": contenido,
        "avatar": avatar
    })


def mostrar_historial():
    """Muestra los mensajes guardados en la sesión."""
    for mensaje in st.session_state.mensajes:
        with st.chat_message(mensaje["role"], avatar=mensaje["avatar"]):
            st.write(mensaje["content"])


def area_chat():
    """Área principal del chat."""
    contenedor = st.container(height=ALTURA_CHAT, border=True)
    with contenedor:
        mostrar_historial()


# --- Función principal ---
def main():
    modelo_elegido = configurar_pagina()
    cliente = crear_usuario_groq()
    inicializar_estado()
    
    st.title("SkrIA")

    area_chat()

    prompt = st.chat_input("Escribe un mensaje:")

    if prompt:
        actualizar_historial("user", prompt, "🤔")

        respuesta_bot = ""
        stream = configurar_modelo(cliente, modelo_elegido, prompt)

        if stream:
            for parte in stream:
                contenido = getattr(parte.choices[0].delta, "content", "")
                if contenido:
                    respuesta_bot += contenido
                    print(contenido, end="", flush=True)

            actualizar_historial("assistant", respuesta_bot, "🐲")
            st.rerun()


# --- Ejecución del script ---
if __name__ == "__main__":
    main()

