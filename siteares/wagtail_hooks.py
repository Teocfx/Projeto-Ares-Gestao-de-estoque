"""
Customizações do Wagtail Admin para o projeto ARES
"""
from django.templatetags.static import static
from django.utils.html import format_html
from wagtail import hooks


@hooks.register("insert_global_admin_css")
def global_admin_css():
    """Adiciona CSS customizado ao admin"""
    return format_html(
        '<link rel="stylesheet" href="{}">',
        static("css/admin/custom-admin.css")
    )


@hooks.register("insert_global_admin_js")
def global_admin_js():
    """Adiciona JavaScript customizado ao admin"""
    return format_html(
        '<script src="{}"></script>',
        static("js/admin/custom-admin.js")
    )


@hooks.register('construct_main_menu')
def hide_default_menu_items(request, menu_items):
    """
    Customiza o menu principal do Wagtail
    Remove itens desnecessários para o projeto ARES
    """
    # Itens a manter: Documents, Images, Settings
    # Remover: Pages, Explorer (caso não use CMS)
    items_to_keep = ['documents', 'images', 'settings']
    menu_items[:] = [item for item in menu_items if item.name in items_to_keep]


@hooks.register('construct_homepage_panels')
def add_ares_dashboard_panel(request, panels):
    """
    Adiciona painel customizado ao dashboard do Wagtail
    Pode ser usado para mostrar estatísticas do estoque
    """
    from django.utils.safestring import mark_safe
    from django.forms import Media
    
    class AresDashboardPanel:
        order = 100
        
        def __init__(self):
            self.media = Media()
        
        def render(self):
            from django.templatetags.static import static
            logo_url = static('img/Logo.svg')
            return mark_safe(f"""
                <section class="ares-dashboard-panel">
                    <h2>
                        <img src="{logo_url}" alt="ARES Logo" style="width: 32px; height: 32px; object-fit: contain;">
                        Sistema ARES
                    </h2>
                    <div class="ares-quick-links">
                        <a href="/dashboard/" class="button button-primary">
                            <svg class="icon icon-home" aria-hidden="true">
                                <use href="#icon-home"></use>
                            </svg>
                            Dashboard Principal
                        </a>
                        <a href="/produtos/" class="button">
                            <svg class="icon icon-tag" aria-hidden="true">
                                <use href="#icon-tag"></use>
                            </svg>
                            Produtos
                        </a>
                        <a href="/movimentacoes/" class="button">
                            <svg class="icon icon-arrows-up-down" aria-hidden="true">
                                <use href="#icon-arrows-up-down"></use>
                            </svg>
                            Movimentações
                        </a>
                        <a href="/relatorios/" class="button">
                            <svg class="icon icon-doc-full" aria-hidden="true">
                                <use href="#icon-doc-full"></use>
                            </svg>
                            Relatórios
                        </a>
                    </div>
                    <style>
                        .ares-dashboard-panel {{
                            background: #f9f9f9;
                            border: 1px solid #e0e0e0;
                            border-radius: 8px;
                            padding: 20px;
                            margin: 20px 0;
                        }}
                        .ares-dashboard-panel h2 {{
                            color: #2c3e50;
                            margin: 0 0 15px 0;
                            display: flex;
                            align-items: center;
                            gap: 10px;
                        }}
                        .ares-quick-links {{
                            display: grid;
                            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                            gap: 10px;
                        }}
                        .ares-quick-links .button {{
                            display: flex;
                            align-items: center;
                            gap: 8px;
                            justify-content: center;
                            padding: 12px 20px;
                            text-decoration: none;
                        }}
                        .ares-quick-links .icon {{
                            width: 1.2em;
                            height: 1.2em;
                        }}
                    </style>
                </section>
            """)
    
    panels.append(AresDashboardPanel())
