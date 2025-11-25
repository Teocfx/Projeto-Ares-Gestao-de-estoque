"""
Views para gerenciamento de uploads de arquivos.
Suporta múltiplos arquivos, validação e otimização.
"""
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.files.storage import default_storage
from django.conf import settings
from PIL import Image
import os
import mimetypes
from datetime import datetime


class FileUploadView(View):
    """
    View genérica para upload de arquivos com validação.
    """
    # Configurações padrão (podem ser sobrescritas)
    allowed_extensions = None  # None = todos, ou lista como ['.jpg', '.png', '.pdf']
    max_file_size = 10 * 1024 * 1024  # 10MB
    upload_to = 'uploads/%Y/%m/%d/'  # Path com strftime
    optimize_images = True
    max_image_dimension = 1920
    
    def get_upload_path(self, filename):
        """Gera o path de upload com data."""
        upload_path = datetime.now().strftime(self.upload_to)
        return os.path.join(upload_path, filename)
    
    def validate_file(self, uploaded_file):
        """Valida arquivo enviado."""
        errors = []
        
        # Validar tamanho
        if uploaded_file.size > self.max_file_size:
            max_mb = self.max_file_size / (1024 * 1024)
            errors.append(f'Arquivo {uploaded_file.name} excede o tamanho máximo de {max_mb}MB')
        
        # Validar extensão
        if self.allowed_extensions:
            ext = os.path.splitext(uploaded_file.name)[1].lower()
            if ext not in self.allowed_extensions:
                errors.append(f'Extensão {ext} não permitida para {uploaded_file.name}')
        
        return errors
    
    def optimize_image(self, uploaded_file, save_path):
        """Otimiza imagem se necessário."""
        if not self.optimize_images:
            return
        
        try:
            image = Image.open(uploaded_file)
            
            # Converter RGBA para RGB se necessário
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            
            # Redimensionar se necessário
            if image.width > self.max_image_dimension or image.height > self.max_image_dimension:
                image.thumbnail((self.max_image_dimension, self.max_image_dimension), Image.Resampling.LANCZOS)
            
            # Salvar otimizado
            full_path = default_storage.path(save_path)
            image.save(full_path, optimize=True, quality=85)
            
        except Exception as e:
            # Se falhar, apenas log (arquivo já foi salvo normalmente)
            print(f"Erro ao otimizar imagem {uploaded_file.name}: {e}")
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        """Processa upload de um ou múltiplos arquivos."""
        if not request.FILES:
            return JsonResponse({'error': 'Nenhum arquivo enviado'}, status=400)
        
        uploaded_files = request.FILES.getlist('files[]')
        if not uploaded_files:
            uploaded_files = [request.FILES.get('file')]
        
        results = []
        errors = []
        
        for uploaded_file in uploaded_files:
            if not uploaded_file:
                continue
            
            # Validar arquivo
            validation_errors = self.validate_file(uploaded_file)
            if validation_errors:
                errors.extend(validation_errors)
                continue
            
            # Gerar nome único se arquivo já existir
            file_path = self.get_upload_path(uploaded_file.name)
            base, ext = os.path.splitext(file_path)
            counter = 1
            while default_storage.exists(file_path):
                file_path = f"{base}_{counter}{ext}"
                counter += 1
            
            # Salvar arquivo
            saved_path = default_storage.save(file_path, uploaded_file)
            
            # Otimizar se for imagem
            if uploaded_file.content_type and uploaded_file.content_type.startswith('image/'):
                self.optimize_image(uploaded_file, saved_path)
            
            # Adicionar aos resultados
            results.append({
                'name': uploaded_file.name,
                'path': saved_path,
                'url': default_storage.url(saved_path),
                'size': uploaded_file.size,
                'type': uploaded_file.content_type,
            })
        
        if errors and not results:
            return JsonResponse({'errors': errors}, status=400)
        
        response_data = {
            'success': True,
            'files': results,
            'count': len(results)
        }
        
        if errors:
            response_data['warnings'] = errors
        
        return JsonResponse(response_data)


class ImageUploadView(FileUploadView):
    """View específica para upload de imagens."""
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    max_file_size = 5 * 1024 * 1024  # 5MB para imagens
    upload_to = 'images/%Y/%m/'
    optimize_images = True


class DocumentUploadView(FileUploadView):
    """View específica para upload de documentos."""
    allowed_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt']
    max_file_size = 20 * 1024 * 1024  # 20MB para documentos
    upload_to = 'documents/%Y/%m/'
    optimize_images = False


class ProductImageUploadView(ImageUploadView):
    """View para upload de imagens de produtos."""
    upload_to = 'produtos/imagens/%Y/%m/'
    max_image_dimension = 1200
    
    def post(self, request):
        """Processa upload e pode vincular a produto."""
        produto_id = request.POST.get('produto_id')
        
        response = super().post(request)
        
        if response.status_code == 200 and produto_id:
            # Aqui você pode vincular as imagens ao produto
            # Exemplo:
            # from produtos.models import Produto
            # produto = Produto.objects.get(id=produto_id)
            # for file_info in response_data['files']:
            #     produto.imagens.create(arquivo=file_info['path'])
            pass
        
        return response


# Exemplo de uso com Form Field
class AvatarUploadView(ImageUploadView):
    """View para upload de avatar de usuário."""
    upload_to = 'avatars/'
    max_file_size = 2 * 1024 * 1024  # 2MB
    max_image_dimension = 512
    allowed_extensions = ['.jpg', '.jpeg', '.png']
    
    def post(self, request):
        """Salva avatar do usuário."""
        response = super().post(request)
        
        if response.status_code == 200:
            data = response.json()
            if data['files']:
                # Atualizar avatar do usuário
                user = request.user
                user.profile.avatar = data['files'][0]['path']
                user.profile.save()
        
        return response
