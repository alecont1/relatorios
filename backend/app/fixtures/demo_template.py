"""
Demo template fixture based on CPQ11 Excel template.

Pre-parsed Python dict for cloning into new tenants during onboarding.
Contains representative sections with fields covering main checklist categories.
"""

DEMO_TEMPLATE = {
    "name": "CPQ11 - Comissionamento de Quadros Eletricos",
    "code": "CPQ11-DEMO",
    "category": "Commissioning",
    "title": "Protocolo de Comissionamento de Quadros Eletricos de Baixa Tensao",
    "reference_standards": "NBR IEC 61439-1, NBR IEC 61439-2, NBR 5410",
    "sections": [
        {
            "name": "1. Verificacao Visual e Mecanica",
            "order": 1,
            "fields": [
                {
                    "label": "Integridade fisica do invólucro (sem amassados, trincas ou corrosao)",
                    "field_type": "dropdown",
                    "options": "Conforme,Nao Conforme,N/A",
                    "order": 1,
                    "photo_config": {"required": False, "min_count": 0, "max_count": 5},
                    "comment_config": {"enabled": True, "required": False},
                },
                {
                    "label": "Grau de protecao (IP) conforme projeto",
                    "field_type": "dropdown",
                    "options": "Conforme,Nao Conforme,N/A",
                    "order": 2,
                    "photo_config": {"required": False, "min_count": 0, "max_count": 3},
                    "comment_config": {"enabled": True, "required": False},
                },
                {
                    "label": "Plaqueta de identificacao legivel e correta",
                    "field_type": "dropdown",
                    "options": "Conforme,Nao Conforme,N/A",
                    "order": 3,
                    "photo_config": {"required": True, "min_count": 1, "max_count": 3},
                    "comment_config": {"enabled": True, "required": False},
                },
                {
                    "label": "Fixacao do quadro na parede/estrutura adequada",
                    "field_type": "dropdown",
                    "options": "Conforme,Nao Conforme,N/A",
                    "order": 4,
                    "photo_config": {"required": False, "min_count": 0, "max_count": 3},
                    "comment_config": {"enabled": True, "required": False},
                },
                {
                    "label": "Observacoes da verificacao visual",
                    "field_type": "text",
                    "options": None,
                    "order": 5,
                    "photo_config": {"required": False, "min_count": 0, "max_count": 5},
                    "comment_config": {"enabled": True, "required": False},
                },
            ],
        },
        {
            "name": "2. Verificacao de Conexoes e Cabeamento",
            "order": 2,
            "fields": [
                {
                    "label": "Torque dos terminais conforme especificacao do fabricante",
                    "field_type": "dropdown",
                    "options": "Conforme,Nao Conforme,N/A",
                    "order": 1,
                    "photo_config": {"required": False, "min_count": 0, "max_count": 3},
                    "comment_config": {"enabled": True, "required": False},
                },
                {
                    "label": "Identificacao dos condutores (fases, neutro, terra)",
                    "field_type": "dropdown",
                    "options": "Conforme,Nao Conforme,N/A",
                    "order": 2,
                    "photo_config": {"required": True, "min_count": 1, "max_count": 5},
                    "comment_config": {"enabled": True, "required": False},
                },
                {
                    "label": "Secao dos condutores compativel com projeto",
                    "field_type": "dropdown",
                    "options": "Conforme,Nao Conforme,N/A",
                    "order": 3,
                    "photo_config": {"required": False, "min_count": 0, "max_count": 3},
                    "comment_config": {"enabled": True, "required": False},
                },
                {
                    "label": "Raio de curvatura dos cabos adequado",
                    "field_type": "dropdown",
                    "options": "Conforme,Nao Conforme,N/A",
                    "order": 4,
                    "photo_config": {"required": False, "min_count": 0, "max_count": 3},
                    "comment_config": {"enabled": True, "required": False},
                },
                {
                    "label": "Continuidade do condutor de protecao (PE) verificada",
                    "field_type": "dropdown",
                    "options": "Conforme,Nao Conforme,N/A",
                    "order": 5,
                    "photo_config": {"required": False, "min_count": 0, "max_count": 3},
                    "comment_config": {"enabled": True, "required": False},
                },
            ],
        },
        {
            "name": "3. Testes Funcionais e Medicoes",
            "order": 3,
            "fields": [
                {
                    "label": "Tensao de alimentacao dentro da faixa nominal",
                    "field_type": "dropdown",
                    "options": "Conforme,Nao Conforme,N/A",
                    "order": 1,
                    "photo_config": {"required": False, "min_count": 0, "max_count": 3},
                    "comment_config": {"enabled": True, "required": False},
                },
                {
                    "label": "Resistencia de isolamento dos barramentos (>= 1 MOhm)",
                    "field_type": "dropdown",
                    "options": "Conforme,Nao Conforme,N/A",
                    "order": 2,
                    "photo_config": {"required": False, "min_count": 0, "max_count": 3},
                    "comment_config": {"enabled": True, "required": True},
                },
                {
                    "label": "Funcionamento dos disjuntores (liga/desliga manual)",
                    "field_type": "dropdown",
                    "options": "Conforme,Nao Conforme,N/A",
                    "order": 3,
                    "photo_config": {"required": False, "min_count": 0, "max_count": 5},
                    "comment_config": {"enabled": True, "required": False},
                },
                {
                    "label": "Teste de disparo dos dispositivos DR",
                    "field_type": "dropdown",
                    "options": "Conforme,Nao Conforme,N/A",
                    "order": 4,
                    "photo_config": {"required": False, "min_count": 0, "max_count": 3},
                    "comment_config": {"enabled": True, "required": False},
                },
                {
                    "label": "Valor da resistencia de aterramento (Ohms)",
                    "field_type": "text",
                    "options": None,
                    "order": 5,
                    "photo_config": {"required": False, "min_count": 0, "max_count": 3},
                    "comment_config": {"enabled": True, "required": True},
                },
            ],
        },
    ],
}
