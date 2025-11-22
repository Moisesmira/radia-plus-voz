import os
import streamlit as st
import openai
import streamlit.components.v1 as components

# ---------------------------
# Configuración OpenAI
# ---------------------------
# IMPORTANTE:
# Define en los secretos / variables de entorno:
# OPENAI_API_KEY = "tu_clave"
openai.api_key = os.getenv("OPENAI_API_KEY")


def get_detailed_response(question: str) -> str:
    """
    Devuelve una explicación ampliada usando IA a partir de la pregunta seleccionada.
    Usa el cliente clásico de openai (requiere openai==0.28 en requirements.txt).
    """
    if not openai.api_key:
        return "No se ha encontrado la clave de OpenAI. Revisa la configuración de OPENAI_API_KEY."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.4,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres un asistente para pacientes oncológicos que van a recibir radioterapia. "
                        "Respondes de forma clara, breve, tranquilizadora y sin tecnicismos innecesarios. "
                        "No das recomendaciones específicas de dosis ni cambias tratamientos. "
                        "Siempre recuerdas que las decisiones finales las toma el equipo médico que lleva al paciente."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Explica con un poco más de detalle, para un paciente, esta duda sobre radioterapia: {question}. "
                        "Usa un tono cercano y fácil de entender, sin tecnicismos. Respuesta en español."
                    ),
                },
            ],
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Error al conectar con OpenAI: {e}"


# ---------------------------
# Función para botón de voz (usa el navegador)
# ---------------------------
def tts_button(label: str, text: str):
    """
    Crea un botón que, al pulsarlo, lee en voz alta el texto usando speechSynthesis del navegador.
    No consume API y funciona en la mayoría de navegadores modernos.
    """
    if not text:
        return

    safe = (
        text.replace("\\", "\\\\")
        .replace("'", "\\'")
        .replace("\n", " ")
        .replace("\r", " ")
    )

    html = f"""
    <button onclick="
        var u = new SpeechSynthesisUtterance('{safe}');
        u.lang = 'es-ES';
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(u);
    " style="
        padding:6px 10px;
        margin:4px 4px 8px 0;
        border-radius:999px;
        border:1px solid #d1d5db;
        background:#f3f4f6;
        cursor:pointer;
        font-size:0.85rem;
    ">
      🔊 {label}
    </button>
    """
    components.html(html, height=40)


# ---------------------------
# Configuración de la página
# ---------------------------
st.set_page_config(
    page_title="RADIA + VOZ – Asistente en Radioterapia",
    page_icon=":loud_sound:",
    layout="centered",
)

st.title("RADIA + VOZ – Asistente virtual en radioterapia")
st.subheader("Servicio de Oncología Radioterápica · Hospital Universitari Arnau de Vilanova")
st.markdown("---")

st.markdown(
    """
    **RADIA + VOZ** es una versión de RADIA pensada para facilitar la lectura a pacientes que tienen dificultades
    con el móvil o la tablet.  
    Puedes **leer** y también **escuchar** la pregunta y la respuesta pulsando el icono de altavoz.

    - La información básica ha sido preparada por el Servicio de Oncología Radioterápica.  
    - La opción **“Ampliar información sobre este tema con IA”** utiliza un modelo de **inteligencia artificial**.  

    > ⚠️ La información es general y **no sustituye** la valoración individual de tu equipo médico.
    """
)


# ---------------------------
# Contenido de RADIA
# ---------------------------
class RADIAChatbot:
    def __init__(self):
        self.categories = {
            "Inicio del tratamiento": {
                "¿Cuándo empezaré el tratamiento de radioterapia?":
                    "Tras la primera visita, se realiza un estudio de planificación (TAC y cálculos dosimétricos). "
                    "Cuando todo está preparado, te llamaremos para darte la fecha de inicio.",
                "¿Por qué tarda en empezar el tratamiento después de la primera consulta?":
                    "Porque se necesita tiempo para preparar tu tratamiento de forma precisa y segura: "
                    "planificación, cálculos y comprobaciones de calidad.",
            },
            "Durante el tratamiento": {
                "¿Duele recibir radioterapia?":
                    "No. La radioterapia es un tratamiento indoloro. No notarás nada mientras la máquina está funcionando.",
                "¿Cuánto dura cada sesión de radioterapia?":
                    "En total estarás en la sala entre 10 y 30 minutos. La parte de irradiación dura solo unos pocos minutos.",
                "¿Puedo moverme durante la sesión?":
                    "Es importante que estés lo más quieto/a posible durante la sesión para que el tratamiento sea preciso. "
                    "El equipo te ayudará a colocarte de forma cómoda antes de empezar.",
                "¿Qué ropa debo usar para venir a la radioterapia?":
                    "Es mejor llevar ropa cómoda, holgada y fácil de quitar si hace falta. "
                    "La ropa que esté en contacto con la zona irradiada se recomienda que sea de algodón y sin costuras "
                    "o elásticos que aprieten.",
            },
            "Efectos secundarios y cuidados": {
                "¿Voy a perder el pelo con la radioterapia?":
                    "Solo se pierde el pelo en la zona donde se aplica la radioterapia. "
                    "Si no se irradia la cabeza, el pelo del cuero cabelludo no se pierde.",
                "¿Se me caerá el pelo del cuerpo o de la barba?":
                    "Puede caerse el pelo de la zona del cuerpo que reciba radioterapia (por ejemplo, barba, axila o pubis) "
                    "si está incluida en el campo de tratamiento.",
                "¿Qué cuidados de piel debo tener durante la radioterapia?":
                    "Mantén la piel limpia y seca, utiliza los productos recomendados por tu equipo y evita el sol directo "
                    "en la zona tratada. No apliques cremas ni desodorantes en la zona sin comentarlo antes con el personal sanitario.",
                "¿Puedo ducharme con normalidad durante el tratamiento?":
                    "Sí, puedes ducharte con agua templada y jabón suave. Evita frotar fuerte la zona tratada y sécala con toques suaves.",
            },
            "Vida diaria y transporte": {
                "¿Podré seguir trabajando durante el tratamiento?":
                    "Muchas personas pueden seguir trabajando, sobre todo al inicio del tratamiento. "
                    "Depende de tu tipo de trabajo, de cómo te encuentres y del tipo de radioterapia. "
                    "Coméntalo con tu oncólogo/a para valorar tu caso.",
                "¿Voy a ser radiactivo/a después del tratamiento?":
                    "No. La radioterapia externa no te hace radiactivo/a. Puedes estar con tu familia, niños y embarazadas con total tranquilidad.",
                "¿Puedo conducir durante el tratamiento?":
                    "En general, sí, siempre que te encuentres bien y no tengas mareos ni mucha fatiga. "
                    "Si notas mucho cansancio, es mejor que otra persona te acompañe.",
                "¿Qué pasa si un día llego tarde o no puedo venir a la sesión?":
                    "Si un día no puedes venir, avisa al servicio lo antes posible. "
                    "Se intentará recolocar la sesión en otro momento para que el tratamiento se complete correctamente.",
            },
            "Sexualidad y fertilidad": {
                "¿Puedo mantener relaciones sexuales durante el tratamiento?":
                    "En la mayoría de los casos sí. Si la radioterapia es en la zona pélvica, puede haber molestias o cambios en la lubricación "
                    "o en la sensibilidad. Coméntalo con tu equipo si tienes dudas o molestias.",
                "¿La radioterapia afecta a la fertilidad?":
                    "La radioterapia en la zona pélvica puede afectar a la fertilidad. "
                    "Si te preocupa este tema, es importante hablarlo con el oncólogo/a antes de empezar el tratamiento "
                    "para valorar opciones de preservación.",
                "¿Puedo tener relaciones si estoy muy cansado/a o con menos deseo sexual?":
                    "Es frecuente que durante el tratamiento baje el deseo sexual por cansancio, estrés o cambios físicos. "
                    "Es importante hablarlo con la pareja con naturalidad y, si lo necesitas, comentarlo con el equipo médico.",
            },
            "Otros aspectos prácticos": {
                "¿Puedo comer con normalidad durante la radioterapia?":
                    "Depende de la zona que se trate. En muchos casos puedes seguir una dieta normal. "
                    "Si la radioterapia afecta al aparato digestivo, es posible que te recomienden una dieta especial.",
                "¿Puedo hacer ejercicio físico durante el tratamiento?":
                    "Sí, siempre que sea ejercicio suave o moderado y te encuentres con fuerzas. "
                    "Caminar cada día suele ser muy recomendable.",
                "¿Con quién puedo hablar si tengo más dudas?":
                    "Puedes preguntar siempre a tu oncólogo/a radioterápico/a, a la enfermera del servicio o al personal técnico. "
                    "Están para ayudarte.",
            },
        }

    def get_categories(self):
        return list(self.categories.keys())

    def get_questions(self, category):
        return list(self.categories.get(category, {}).keys())

    def get_response(self, category, question):
        return self.categories.get(category, {}).get(
            question,
            "Lo siento, no encuentro respuesta para esa pregunta dentro de RADIA."
        )


# ---------------------------
# UI principal
# ---------------------------
radia = RADIAChatbot()

st.markdown("### Elige un tema y una pregunta")

categories = radia.get_categories()
if not categories:
    st.error("No se han podido cargar las categorías. Por favor, contacta con el servicio.")
else:
    category = st.selectbox("Tema", categories)
    questions = radia.get_questions(category)

    if questions:
        question = st.selectbox("Pregunta", questions)

        if question:
            st.markdown("#### Pregunta seleccionada")
            st.write(question)
            tts_button("Oír esta pregunta", question)

            base_response = radia.get_response(category, question)

            st.markdown("#### Respuesta básica de RADIA")
            st.success(base_response)
            tts_button("Oír esta respuesta", base_response)

            if st.button("Ampliar información sobre este tema con IA"):
                with st.spinner("Consultando…"):
                    detailed = get_detailed_response(question)
                    st.markdown("#### Explicación ampliada (IA)")
                    st.info(detailed)
                    tts_button("Oír explicación IA", detailed)
                    st.warning(
                        "Esta respuesta ha sido generada por un modelo de inteligencia artificial y "
                        "no representa necesariamente la opinión del Servicio de Oncología Radioterápica. "
                        "Ante cualquier duda, consulta siempre con tu equipo médico."
                    )
    else:
        st.warning("No hay preguntas disponibles en esta categoría.")

st.markdown("---")
st.caption("RADIA + VOZ · Asistente virtual para pacientes en radioterapia · Información general, no sustituye la valoración médica individual.")
