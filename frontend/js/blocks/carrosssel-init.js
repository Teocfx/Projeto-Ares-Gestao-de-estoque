/**
 * Módulo de inicialização de carrosséis Swiper
 * Gerencia todos os carrosséis do site de forma centralizada
 */

class CarrosselManager {
    constructor() {
        this.carrosseis = {};
        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this.initCarrosselBanners();
            this.initCarrosselSolucoes();
            this.initCarrosselServicos();
            this.initImageGallery();
        });
    }

    initCarrosselBanners() {
        const element = document.querySelector('.carrossel-banners');
        if (!element) return;

        this.carrosseis.banners = new Swiper('.carrossel-banners', {
            slidesPerView: 1,
            spaceBetween: 20,
            autoplay: {
                delay: 8000,
                disableOnInteraction: false,
            },
            pagination: {
                el: '.swiper-banners-pagination',
                clickable: true,
            },
            loop: true,
        });
    }

    initCarrosselSolucoes() {
        const element = document.querySelector('.carrossel-solucoes');
        if (!element) return;

        this.carrosseis.solucoes = new Swiper('.carrossel-solucoes', {
            slidesPerView: 3,
            spaceBetween: 20,
            pagination: {
                el: '.swiper-solucoes-pagination',
                clickable: true,
            },
            navigation: {
                nextEl: '.swiper-solucoes-next',
                prevEl: '.swiper-solucoes-prev',
            },
            loop: true,
            breakpoints: {
                0: { slidesPerView: 1 },
                640: { slidesPerView: 1 },
                768: { slidesPerView: 2 },
                1024: { slidesPerView: 3 }
            }
        });
    }

    initCarrosselServicos() {
        const element = document.querySelector('.swiperServicosOnline');
        if (!element) return;

        this.carrosseis.servicos = new Swiper('.swiperServicosOnline', {
            slidesPerView: 1,
            spaceBetween: 20,
            breakpoints: {
                768: { slidesPerView: 2 },
                1200: { slidesPerView: 3 },
                1440: { slidesPerView: 4, spaceBetween: 30 },
            },
            navigation: {
                nextEl: '.swiper-servicos-button-next',
                prevEl: '.swiper-servicos-button-prev'
            },
            pagination: {
                el: '.swiper-servico-pagination',
                clickable: true,
            },
            loop: true,
        });

        // Inicializar tooltips do Bootstrap
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    initImageGallery() {
        const mainElement = document.querySelector('.image-gallery-swiper-main');
        const thumbsElement = document.querySelector('.image-gallery-swiper-thumbs');
        
        if (!mainElement || !thumbsElement) return;

        const swiperThumbs = new Swiper('.image-gallery-swiper-thumbs', {
            loop: true,
            spaceBetween: 10,
            slidesPerView: 4,
            freeMode: true,
            watchSlidesProgress: true,
        });

        this.carrosseis.imageGallery = new Swiper('.image-gallery-swiper-main', {
            loop: true,
            spaceBetween: 10,
            autoHeight: true,
            navigation: {
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev',
            },
            thumbs: { swiper: swiperThumbs },
        });
    }

    destroy() {
        Object.values(this.carrosseis).forEach(swiper => {
            if (swiper && typeof swiper.destroy === 'function') {
                swiper.destroy(true, true);
            }
        });
    }
}

// Inicializar automaticamente
new CarrosselManager();

// Exportar para uso externo se necessário
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CarrosselManager;
}
