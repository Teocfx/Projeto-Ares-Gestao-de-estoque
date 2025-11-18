import 'odometer/themes/odometer-theme-default.css';
import 'vanilla-calendar-pro/styles/index.css';
import 'vanilla-calendar-pro/styles/layout.css'; // Only the skeleton
import 'vanilla-calendar-pro/styles/themes/light.css'; // Light theme
import "vanilla-cookieconsent/dist/cookieconsent.css"; // Cookieconsent

import "../scss/main.scss";
import "../../tw/styles.css";

import * as bootstrap from 'bootstrap';
window.bootstrap = bootstrap;

import UIkit from 'uikit';
import Icons from 'uikit/dist/js/uikit-icons';

import './header/header.js';
import './header/navbar.js';
import './autenticacao/login.js';
import './dashboard/dashboard.js';
import './produtos/produtos.js';
import './movimentacoes/movimentacoes.js';
import './relatorios/relatorios.js';
import './core/document-viewer.js';
import './core/filtros.js';

import Swiper from 'swiper/bundle';
import 'swiper/css/bundle';

import Odometer from "odometer";

import './cookieconsent-config.js'
import './compartilhamento.js'

window.Swiper = Swiper;
window.Odometer = Odometer;
window.VanillaCalendarPro = require('vanilla-calendar-pro');

UIkit.use(Icons);

//Deve ser importado depois de inicializar o VanillaCalendarPro na window.
import './agenda/agenda.js';