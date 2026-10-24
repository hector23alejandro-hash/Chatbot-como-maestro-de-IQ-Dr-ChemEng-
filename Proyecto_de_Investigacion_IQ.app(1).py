# --- 3. ESCRITURA DEL ARCHIVO `app.py` PARA STREAMLIT ---
app_code = '''import streamlit as st
import os
import io
import contextlib
import numpy as np
import scipy.optimize as optimize
import scipy.integrate as integrate
import google.generativeai as genai

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Asistente Universal de Ingeniería Química",
    page_icon="⚗️",
    layout="wide",
)

# --- CONFIGURACIÓN DE LA API DE GEMINI EN LA BARRA LATERAL ---
st.sidebar.title("⚙️ Configuración")
api_key_input = st.sidebar.text_input(
    "Ingresa tu Google Gemini API Key:", type="password"
)

API_KEY = ""
if api_key_input:
    API_KEY = api_key_input
elif "GEMINI_API_KEY" in os.environ:
    API_KEY = os.environ.get("GEMINI_API_KEY", "")
else:
    try:
        if "GEMINI_API_KEY" in st.secrets:
            API_KEY = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass

if API_KEY:
    genai.configure(api_key=API_KEY)
    st.sidebar.success("API Key configurada correctamente ✅")
else:
    st.sidebar.warning(
        "⚠️ Por favor, ingresa tu API Key en el campo de arriba para comenzar a chatear."
    )

# --- SYSTEM PROMPT UNIVERSAL ---
SYSTEM_INSTRUCTION = """
Eres un profesor e investigador experto en Ingeniería Química con dominio absoluto de los textos fundamentales:

1. H. Scott Fogler - Cinética y Reactores.
2. R.B. Bird, W.E. Stewart y E.N. Lightfoot - Fenómenos de transporte.
3. J.M. Smith, H.C. Van Ness y M.M. Abbott - Termodinámica.
4. Richard M. Felder y Ronald W. Rousseau - Balances de Materia y Energía.
5. Phillip C. Wankat / J.D. Seader - Procesos de Separación (Destilación, Absorción, etc.).

INSTRUCCIONES CRÍTICAS PARA CADA PROBLEMA QUE EL USUARIO PROPORCIONE:
1. Identifica el libro, capítulo y tema del problema subido por el usuario, siguiendo rigurosamente la metodología clásica.
2. Resuelve el problema mediante un riguroso desarrollo analítico paso a paso usando notación LaTeX clara.
3. MOTOR NUMÉRICO OBLIGATORIO: Incluye un bloque de código Python ejecutable (`numpy`, `scipy`) para resolver de forma numérica exacta el sistema de ecuaciones o balance planteado.
4. COHERENCIA ABSOLUTA: Los valores numéricos y resultados presentados en tu desarrollo analítico deben coincidir exactamente con los impresos por tu bloque de código Python.
"""

# --- DISEÑO DE LA INTERFAZ ---
st.title("⚗️ Asistente Universal de Ingeniería Química (UANL)")
st.write(
    "Sube una foto, un PDF o escribe el enunciado de **cualquier ejercicio** de Fogler, Smith, Bird, Felder, Wankat o Seader. El asistente planteará la solución y generará el código numérico para resolverlo."
)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

uploaded_file = st.file_uploader(
    "Sube la imagen o documento del problema:", type=["png", "jpg", "jpeg", "pdf"]
)
prompt = st.chat_input("Escribe tu enunciado o pregunta sobre cualquier libro...")

if prompt or uploaded_file:
    if not API_KEY:
        st.error(
            "🚨 Por favor, ingresa tu API Key de Gemini en la barra lateral antes de enviar una consulta."
        )
    else:
        user_content = (
            prompt
            if prompt
            else "Resuelve paso a paso este problema de ingeniería química adjunto."
        )
        st.session_state.messages.append({"role": "user", "content": user_content})

        with st.chat_message("user"):
            if uploaded_file:
                if "image" in uploaded_file.type:
                    st.image(uploaded_file, caption="Problema adjunto")
                else:
                    st.write(f"📁 Archivo adjunto: {uploaded_file.name}")
            st.markdown(user_content)

        with st.chat_message("assistant"):
            with st.spinner(
                "Analizando problema, consultando marcos teóricos y calculando..."
            ):
                try:
                    model = genai.GenerativeModel(
                        model_name="gemini-1.5-flash",
                        system_instruction=SYSTEM_INSTRUCTION,
                    )

                    contents = [user_content]
                    if uploaded_file:
                        bytes_data = uploaded_file.getvalue()
                        file_part = {"mime_type": uploaded_file.type, "data": bytes_data}
                        contents.append(file_part)

                    response = model.generate_content(contents)
                    bot_response = response.text

                    st.markdown(bot_response)

                    if "```python" in bot_response:
                        st.markdown("---")
                        st.subheader("💻 Ejecución Numérica Automatizada (SciPy / NumPy)")

                        try:
                            parts = bot_response.split("```python")
                            code_block = parts[1].split("```")[0].strip()

                            with st.expander(
                                "Ver código Python generado para este problema",
                                expanded=False,
                            ):
                                st.code(code_block, language="python")

                            buffer = io.StringIO()
                            locals_dict = {
                                "np": np,
                                "integrate": integrate,
                                "optimize": optimize,
                            }

                            with contextlib.redirect_stdout(buffer):
                                exec(code_block, locals_dict)

                            output_result = buffer.getvalue()
                            if output_result:
                                st.success("Resultados obtenidos por el motor numérico:")
                                st.code(output_result, language="text")
                            else:
                                st.info(
                                    "El código se ejecutó correctamente (sin salidas impresas explícitas)."
                                )

                        except Exception as exec_error:
                            st.warning(
                                f"Nota: El código generado requirió revisión de sintaxis en el entorno local: {exec_error}"
                            )

                    st.session_state.messages.append(
                        {"role": "assistant", "content": bot_response}
                    )

                except Exception as e:
                    st.error(f"Ocurrió un error al procesar la solicitud: {e}")
'''

with open("app.py", "w", encoding="utf-8") as f:
    f.write(app_code)

print("-> Archivo 'app.py' generado exitosamente.")