from datetime import datetime, timedelta
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.response import TemplateResponse
from django.shortcuts import redirect
from django.contrib.contenttypes.models import ContentType
from wagtail.contrib.search_promotions.models import Query
from wagtail.models import Page
from django.db import models
from django.db.models import Q

# Models do sistema de gestão de estoque
from produtos.models import Product, Category
from movimentacoes.models import InventoryMovement

def get_result_type(result):
    return result.content_type.model.replace('_', ' ').title()

def formatar_tipos(tipos):
    """Formata os tipos de conteúdo para exibição."""
    tipos_conhecidos = {
        "product": "Produtos",
        "inventorymovement": "Movimentações",
        "category": "Categorias",
        "page": "Páginas",
        # Tipos Wagtail
        "document": "Documentos",
        "image": "Imagens",
    }
    return [
        {
            "titulo": tipos_conhecidos.get(nome, nome.replace('_', ' ').title()),
            "filtro": nome
        }
        for nome in tipos
    ]

def search(request):
    # Redirecionamento para padronizar parâmetros (q -> query)
    if 'q' in request.GET and 'query' not in request.GET:
        params = request.GET.copy()
        params['query'] = params.pop('q')[0]  # Move o parâmetro 'q' para 'query'
        return redirect(f"{request.path}?{params.urlencode()}")

    # Obter parâmetros da requisição
    search_query = request.GET.get("query", "")
    page = request.GET.get("page", 1)
    selected_types = request.GET.getlist("type")
    date_filter = request.GET.get("date", "sempre")

    # Converter para lista de tipos (remover 'all' se outros tipos estiverem selecionados)
    if "all" in selected_types:
         selected_types = [] 
    elif not selected_types:
        selected_types = []  # Mostrar todos os tipos

    # Definir filtros de data
    now = timezone.now()
    date_filters = {
        'ontem': now - timedelta(days=1),
        'semana': now - timedelta(weeks=1),
        'mes': now - timedelta(days=30),
        'sempre': None,
        'intervalo': None  # Implementar lógica específica para intervalo se necessário
    }
    date_cutoff = date_filters.get(date_filter)

    # Executar busca
    if search_query:
        # Dividir a query em palavras para busca mais flexível
        search_terms = search_query.strip().split()
        
        all_results = []
        
        # Busca em Produtos
        if not selected_types or "product" in selected_types:
            produtos_query = Product.objects.filter(is_active=True)
            for term in search_terms:
                produtos_query = produtos_query.filter(
                    Q(name__icontains=term) |
                    Q(sku__icontains=term) |
                    Q(description__icontains=term) |
                    Q(category__name__icontains=term)
                )
            all_results.extend(list(produtos_query))
        
        # Busca em Movimentações
        if not selected_types or "inventorymovement" in selected_types:
            movimentacoes_query = InventoryMovement.objects.all()
            for term in search_terms:
                movimentacoes_query = movimentacoes_query.filter(
                    Q(product__name__icontains=term) |
                    Q(product__sku__icontains=term) |
                    Q(document__icontains=term) |
                    Q(notes__icontains=term)
                )
            
            # Aplicar filtro de data em movimentações
            if date_cutoff:
                movimentacoes_query = movimentacoes_query.filter(created_at__gte=date_cutoff)
            
            all_results.extend(list(movimentacoes_query))
        
        # Busca em Categorias
        if not selected_types or "category" in selected_types:
            categorias_query = Category.objects.filter(is_active=True)
            for term in search_terms:
                categorias_query = categorias_query.filter(
                    Q(name__icontains=term) |
                    Q(description__icontains=term)
                )
            all_results.extend(list(categorias_query))
        
        # Busca nas páginas Wagtail (se houver)
        if not selected_types or "page" in selected_types:
            try:
                pages_query = Page.objects.live().public()
                for term in search_terms:
                    pages_query = pages_query.filter(
                        Q(title__icontains=term) |
                        Q(search_description__icontains=term)
                    )
                
                # Aplicar filtro de data em páginas
                if date_cutoff:
                    pages_query = pages_query.filter(
                        last_published_at__gte=date_cutoff
                    )
                
                all_results.extend(list(pages_query))
            except Exception:
                # Se não houver páginas Wagtail configuradas, continua
                pass

        # Paginação dos resultados combinados
        paginator = Paginator(all_results, 10)
        try:
            paginated_results = paginator.page(page)
        except PageNotAnInteger:
            paginated_results = paginator.page(1)
        except EmptyPage:
            paginated_results = paginator.page(paginator.num_pages)

        # Registrar a query para search promotions
        Query.get(search_query).add_hit()
    else:
        paginated_results = []
    
    # Obter tipos disponíveis no sistema
    available_types = [
        "product",
        "inventorymovement",
        "category",
        "page",
    ]

    tipos_formatados = formatar_tipos(available_types)

    # Montar query_params sem parâmetros de paginação
    query_params_dict = request.GET.copy()
    query_params_dict.pop('page', None)
    query_params = query_params_dict.urlencode()

    return TemplateResponse(
        request,
        "search/search.html",
        {
            "search_query": search_query,
            "search_results": paginated_results,
            "selected_types": selected_types,
            "selected_date": date_filter,
            "breadcrumbs": True,
            "query_params": query_params,
            "get_result_type": get_result_type,
            "tipos_disponiveis": tipos_formatados,
        },
    )