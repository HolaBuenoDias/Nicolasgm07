"""Contenido del perfil (fuente única, sacado del CV). Los generadores leen de aquí."""

NAME = "Nicolás González Muñoz"
FIRST_NAME = "Nicolás"
LAST_NAMES = "González Muñoz"
ROLE = "Desarrollador web y e-commerce"
HEADLINE = "Desarrollador Web · 2.º DAW · PHP · Java · Angular · Spring Boot · WordPress"
LOCATION = "El Viso del Alcor (Sevilla)"
EMAIL = "nicolasgomu1610@gmail.com"
GITHUB_USER = "Nicolasgm07"
GITHUB = f"https://github.com/{GITHUB_USER}"
LINKEDIN = "https://www.linkedin.com/in/nicol%C3%A1s-gonz%C3%A1lez-mu%C3%B1oz-39a379381"

AVAILABILITY = {
    "text": "Disponible para prácticas de empresa de 2.º DAW",
    "short": "Prácticas · feb – may 2027",
    "start": "2027-02-01",   # "de febrero a mayo de 2027" (día exacto sin fijar)
    "end": "2027-05-31",
}

PROFILE = (
    "Estudiante de 2.º de Desarrollo de Aplicaciones Web con experiencia real en desarrollo web y "
    "e-commerce. Entré en Bastilipo con las prácticas del SMR y me contrataron por mi rendimiento; allí "
    "desarrollé y mantuve seis tiendas online y webs corporativas con WordPress, WooCommerce y PrestaShop, "
    "y lo compaginé con 1.º de DAW. En el ciclo trabajo con Angular, Java, Spring Boot, PHP y SQL. Busco "
    "prácticas donde aportar desde el primer día y seguir aprendiendo."
)

EXPERIENCE = {
    "company": "Bastilipo",
    "role": "Desarrollador web y e-commerce",
    "start": "2025-03", "end": "2026-06",
    "period": "mar. 2025 – jun. 2026",
    "duration": "1 año y 4 meses",
    "note": "Contratado tras las prácticas del SMR",
    "areas": [
        {"key": "tiendas", "icon": "store", "title": "Tiendas y webs",
         "summary": "6 webs con WordPress + WooCommerce y PrestaShop 1.7",
         "bullets": [
             "Desarrollé y mantuve seis tiendas online y webs corporativas con WordPress + WooCommerce "
             "(Divi, Elementor, Astra) y PrestaShop 1.7.",
             "Diseñé la identidad visual de Urbify (logo y favicon)."]},
        {"key": "woo", "icon": "code", "title": "WooCommerce a medida",
         "summary": "PHP (hooks), CSS y JavaScript",
         "bullets": [
             "Personalicé WooCommerce con PHP (hooks), CSS y JavaScript: fichas y tarjetas de producto, "
             "carrito, buscador (FiboSearch) y menú móvil, todo responsive.",
             "Distintivos «Reacondicionado» y «Tara estética» en el catálogo."]},
        {"key": "checkout", "icon": "card", "title": "Proceso de compra",
         "summary": "Redsys (Bizum), PayPal, Klarna · Sendcloud y GLS",
         "bullets": [
             "Pagos con Redsys (Bizum), PayPal y Klarna.",
             "Clases de envío para electrodomésticos grandes y servicios adicionales de pago "
             "(retirada del aparato antiguo, subida por escaleras).",
             "Envíos con Sendcloud y GLS."]},
        {"key": "marketplaces", "icon": "box", "title": "Marketplaces",
         "summary": "Google Shopping, TikTok Shop, eBay y Amazon",
         "bullets": [
             "Llevé el catálogo a Google Shopping, TikTok Shop, eBay y Amazon mediante feeds de Channable.",
             "Adapté plantillas y atributos de producto y gestioné las incidencias de publicación."]},
        {"key": "marketing", "icon": "trend", "title": "Marketing y medición",
         "summary": "Merchant Center, Ads Shopping, Analytics, Tag Manager, SEO",
         "bullets": [
             "Gestioné Google Merchant Center (políticas y verificación) y campañas de Google Ads Shopping.",
             "Medición de conversiones con Google Analytics y Tag Manager, y SEO de las tiendas."]},
        {"key": "hosting", "icon": "shield", "title": "Hosting y seguridad",
         "summary": "IONOS, Cloudflare, DNS, BBDD, rendimiento",
         "bullets": [
             "Administré hosting y seguridad: IONOS, Cloudflare, DNS y bases de datos.",
             "Depuración de errores 500 en PrestaShop y diagnóstico de rendimiento (caché, OPcache, límites de PHP).",
             "Wordfence y copias de seguridad con UpdraftPlus."]},
    ],
}

# Webs del CV. "status" según comprobación del 28/10/2026.
SITES = [
    {"slug": "circuitobebe", "domain": "circuitobebe.com", "url": "https://www.circuitobebe.com/",
     "name": "Circuito Bebé", "sector": "Puericultura: sillas de coche, carritos y cunas",
     "stack": ["WordPress", "WooCommerce", "WoodMart", "WPBakery"], "status": "live",
     "accent": "#8fcfc0"},
    {"slug": "electro-outlet", "domain": "electro-outlet.net", "url": "https://www.electro-outlet.net/",
     "name": "Electro-outlet", "sector": "Electrodomésticos reacondicionados con garantía",
     "stack": ["WordPress", "WooCommerce", "Astra", "FiboSearch"], "status": "live",
     "accent": "#e3101a"},
    {"slug": "urbify", "domain": "urbifyrealstate.com", "url": "https://urbifyrealstate.com/",
     "name": "Urbify", "sector": "Consultora inmobiliaria · identidad visual (logo y favicon)",
     "stack": ["WordPress", "Divi", "Tema hijo"], "status": "live", "accent": "#0a1f44"},
    {"slug": "urende", "domain": "urende.com.es", "url": "https://urende.com.es/",
     "name": "Urende", "sector": "", "stack": [], "status": "unreachable"},
    {"slug": "bastilipo", "domain": "bastilipo.es", "url": "https://bastilipo.es/",
     "name": "Bastilipo", "sector": "Web corporativa", "stack": [], "status": "maintenance"},
    {"slug": "bastilipo-home", "domain": "bastilipo-home.com", "url": "https://bastilipo-home.com/",
     "name": "Bastilipo Home", "sector": "", "stack": [], "status": "maintenance"},
]

PROJECTS = {
    "featured": {
        "title": "Aplicación web inspirada en League of Legends",
        "kicker": "Proyecto full stack · ciclo DAW",
        "text": ("Frontend en Angular (componentes standalone, control de flujo @if/@for) que consume "
                 "una API REST propia hecha con Java y Spring Boot sobre MongoDB. Interfaz responsive "
                 "con animaciones, carrusel y panel de estadísticas."),
        "front": {"repo": "app-lol", "url": f"{GITHUB}/app-lol",
                  "stack": ["Angular 21", "TypeScript", "SSR", "CSS"]},
        "back": {"repo": "league_of_legends", "url": f"{GITHUB}/league_of_legends",
                 "stack": ["Java 21", "Spring Boot", "MongoDB", "Swagger", "Lombok"]},
        "endpoints": ["GET /api/characters", "GET /api/characters/{id}", "POST /api/characters",
                      "PUT /api/characters/{id}", "DELETE /api/characters/{id}",
                      "GET /api/characters/filter/multirol", "GET /api/characters/filter/role/tank"],
    },
    "others": [
        {"repo": "Api_products", "url": f"{GITHUB}/Api_products",
         "title": "API de productos", "text": "API REST de productos y categorías con Spring Boot y MySQL.",
         "stack": ["Java", "Spring Boot", "MySQL"]},
        {"repo": "ActBaseDatos", "url": f"{GITHUB}/ActBaseDatos",
         "title": "Empleados y departamentos", "text": "API REST con Spring Boot y JPA sobre una base de datos MySQL.",
         "stack": ["Java", "Spring Boot", "JPA", "MySQL"]},
    ],
    "class": [
        {"repo": "Practica2JS", "text": "Práctica de JavaScript con el BOM"},
        {"repo": "ActividadEvaluable", "text": "Actividad evaluable de JavaScript"},
        {"repo": "UD1-proyecto-js", "text": "Proyecto de la primera unidad de JavaScript"},
        {"repo": "Actividad1", "text": "Calculadora en Java"},
    ],
}

EDUCATION = [
    {"title": "Técnico Superior en Desarrollo de Aplicaciones Web (DAW)", "short": "DAW",
     "school": "IES Los Alcores, Mairena del Alcor (Sevilla)", "period": "sep. 2025 – jun. 2027",
     "start": "2025-09", "end": "2027-06", "status": "Cursando 2.º"},
    {"title": "Técnico en Sistemas Microinformáticos y Redes (SMR)", "short": "SMR",
     "school": "IES Los Alcores, Mairena del Alcor (Sevilla)", "period": "sep. 2023 – jun. 2025",
     "start": "2023-09", "end": "2025-06", "status": "Título obtenido"},
]

CERTS = [
    {"name": "Google Analytics", "issuer": "Google", "note": "Verificable en LinkedIn"},
    {"name": "Google Ads", "issuer": "Google", "note": "Verificable en LinkedIn"},
]

# Hitos para la línea temporal (fechas aproximadas a mes).
MILESTONES = [
    ("2023-09", "Empiezo SMR", "IES Los Alcores"),
    ("2025-03", "Prácticas en Bastilipo", "y me contratan"),
    ("2025-06", "Título de SMR", ""),
    ("2025-09", "Empiezo DAW", "compaginándolo con el trabajo"),
    ("2026-06", "Cierro etapa en Bastilipo", "1 año y 4 meses"),
    ("2027-02", "Prácticas de DAW", "feb – may 2027"),
    ("2027-06", "Título de DAW", "previsto"),
]

STACK = {
    "Lenguajes": ["PHP", "JavaScript", "TypeScript", "Java", "SQL", "HTML5", "CSS3", "XML"],
    "Frameworks y BBDD": ["Angular", "Spring Boot", "Maven", "MySQL/MariaDB", "MongoDB"],
    "CMS y e-commerce": ["WordPress", "WooCommerce", "PrestaShop", "Divi", "Elementor", "Astra", "Moodle"],
    "Marketing digital": ["Google Merchant Center", "Google Ads", "Google Analytics", "Tag Manager",
                          "Channable", "SEO/SEM"],
    "Sistemas": ["Linux (Ubuntu Server, Debian)", "Windows Server (AD, DNS, DHCP)", "Apache2"],
    "Herramientas": ["Git", "GitHub", "IntelliJ IDEA", "Eclipse", "NetBeans", "XAMPP", "VirtualBox",
                     "IA (Claude, ChatGPT)"],
}

LANGUAGES = [("Español", "Nativo"), ("Inglés", "Básico · lectura fluida de documentación técnica")]
DRIVING = "Carné B en proceso de obtención"
