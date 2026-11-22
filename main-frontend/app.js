/* ═══════════════════════════════════════════════════════════
   U-Scout AI — Application Logic (Vanilla JS)
   ═══════════════════════════════════════════════════════════ */

// ── Mock Data ──
const PLAYERS = [
    { 
        id:1, name:"Octavian Popescu", initials:"OP", pos:"CAM / LW", age:22, height:"1.80m", weight:"70kg", foot:"Drept", club:"FCSB", contract:"2027", freeAgent:false, value:3000000, aiScore:93, formTrend:'up', 
        riskScore:25, riskSummary:"Risc scăzut. Loialitate mare față de clubul formator.",
        psychTags: ["Introvertit", "Imprevizibil", "Tehnic"],
        characterSummary: "Jucător cu un talent tehnic incontestabil, dar care necesită un mediu de suport emoțional puternic pentru a avea constanță. Tinde să aibă fluctuații de moral când este presat mediatic. Introvertit, se exprimă cel mai bine când are libertate de creație totală în treimea adversă, însă arată semne de frustrare când jocul echipei nu funcționează. Risc de adaptare dacă antrenorul are un stil autoritar rigid.",
        injuries: [
            { date: 'Oct 2023', type: 'Leziune musculară minoră', days: 14 },
            { date: 'Feb 2024', type: 'Răceală severă', days: 7 }
        ],
        injuryHistory: [90, 88, 80, 85, 92, 94],
        transferHistory: [
            { club: 'FCSB', period: '2020 - Prezent', years: 4, type: 'Transfer', logo: 'https://img.icons8.com/color/48/football-team.png' },
            { club: 'U Craiova U19', period: '2019 - 2020', years: 1, type: 'Academie', logo: 'https://img.icons8.com/color/48/trophy.png' }
        ],
        pros: ["Controlul balonului în regim de viteză", "Creativitate peste medie în ultimii 30m", "Eficiență xG: +12%"],
        cons: ["Dueluri aeriene pierdute frecvent", "Recuperare defensivă lentă"],
        aiAlert: "Stabilitate ridicată. Potențial bun pentru integrare pe termen lung.",
        disciplineStats: [10, 15, 88, 85],
        stats:{pace:85,shoot:78,pass:82,drib:88,def:35,phys:65} 
    },
    { 
        id:2, name:"Marius Ștefănescu", initials:"MȘ", pos:"LW", age:24, foot:"Drept", club:"FCSB", contract:"2028", freeAgent:false, value:1200000, aiScore:89, formTrend:'up', 
        riskScore:65, riskSummary:"Risc mediu-ridicat. Tendință de accidentări musculare recurente.",
        psychTags: ["Exploziv", "Introvertit", "Instabil"],
        characterSummary: "Profil psihologic: Jucătorul ia cartonașe frecvent în meciurile cu miză, indicând dificultăți în gestionarea presiunii. Preferă comunicarea minimală în presă.",
        injuries: [
            { date: 'Nov 2023', type: 'Ruptură fibrilară coapsă', days: 45 },
            { date: 'Mai 2022', type: 'Entorsă gleznă', days: 30 }
        ],
        injuryHistory: [85, 80, 30, 45, 55, 60],
        transferHistory: [
            { club: 'FCSB', period: '2024 - Prezent', years: 0.5, type: 'Transfer', logo: 'https://img.icons8.com/color/48/football-team.png' },
            { club: 'Sepsi OSK', period: '2018 - 2024', years: 6, type: 'Transfer', logo: 'https://img.icons8.com/color/48/shield.png' },
            { club: 'KSE Târgu Secuiesc', period: '2017 - 2018', years: 1, type: 'Împrumut', logo: 'https://img.icons8.com/color/48/stadium.png' }
        ],
        pros: ["Șut de la distanță periculos", "Dribling imprevizibil pe spații mici"],
        cons: ["Pase greșite sub presiune mare", "Rata succesului în dueluri 1 la 1: 42%"],
        aiAlert: "Dificultăți de adaptare la presiunea unui club cu așteptări imediate.",
        disciplineStats: [20, 40, 70, 65],
        stats:{pace:82,shoot:70,pass:68,drib:80,def:28,phys:65} 
    },
    { 
        id:3, name:"Alex Pop", initials:"AP", pos:"ST", age:22, foot:"Drept", club:"FC Botoșani", contract:"2027", freeAgent:false, value:350000, aiScore:86, formTrend:'up', 
        riskScore:12, riskSummary:"Profil disciplinat, fără istoric medical major.",
        psychTags: ["Muncitor", "Disciplinat", "Team Player"],
        characterSummary: "Profil psihologic: Jucător extrem de disciplinat, focalizat pe sarcini tactice. Se integrează rapid în grupuri noi.",
        injuries: [],
        injuryHistory: [92, 94, 91, 93, 95, 94],
        transferHistory: [
            { club: "FC Botoșani", period: "2023 - Prezent", years: 1.5, type: 'Transfer', logo: 'https://img.icons8.com/color/48/football-team.png' },
            { club: "Unirea Dej", period: "2021 - 2023", years: 2, type: 'Transfer', logo: 'https://img.icons8.com/color/48/shield.png' }
        ],
        pros: ["Plasament excelent în careu", "Joc de cap peste medie"],
        cons: ["Viteză de reacție pe distanțe lungi"],
        aiAlert: "Jucător loial, cu un parcurs stabil.",
        disciplineStats: [5, 10, 85, 80],
        stats:{pace:78,shoot:75,pass:62,drib:70,def:30,phys:72} 
    },
    { id:5, name:"Denis Drăguș", initials:"DD", pos:"ST / LW", age:25, height:"1.85m", weight:"79kg", foot:"Drept", club:"Trabzonspor", contract:"2027", freeAgent:false, value:2500000, aiScore:91, formTrend:'up', 
        psychTags: ["Exploziv", "Încrezător", "Individualist"],
        characterSummary: "Jucător cu o doză mare de încredere în propriile forțe, capabil de momente de magie individuală. Profil psihologic axat pe acțiuni pe cont propriu; uneori tinde să forțeze rezolvarea fazelor singur în detrimentul jocului de pase. Răspunde excelent la antrenorii care îi oferă validare constantă. A demonstrat o creștere masivă a rezilienței mentale după experiențele internaționale, adaptându-se bine în campionate dure.",
        stats:{pace:80,shoot:78,pass:55,drib:72,def:25,phys:75} },
    { id:6, name:"Ionuț Pantîru", initials:"IP", pos:"LB", age:27, foot:"Stâng", club:"FC Botoșani", contract:"2026", freeAgent:false, value:300000, aiScore:65, formTrend:'steady', stats:{pace:74,shoot:30,pass:64,drib:58,def:70,phys:72} },
    { id:7, name:"Claudiu Petrila", initials:"CP", pos:"LW", age:24, foot:"Drept", club:"CFR Cluj", contract:"2027", freeAgent:false, value:800000, aiScore:84, formTrend:'up', stats:{pace:84,shoot:68,pass:65,drib:78,def:25,phys:60} },
    { id:9, name:"Virgil Ghiță", initials:"VG", pos:"CB", age:28, foot:"Drept", club:"Rapid", contract:"2026", freeAgent:false, value:400000, aiScore:72, formTrend:'down', stats:{pace:55,shoot:28,pass:52,drib:40,def:78,phys:80} },
    { id:10, name:"David Miculescu", initials:"DM", pos:"RW", age:23, foot:"Drept", club:"FCSB", contract:"2027", freeAgent:false, value:1500000, aiScore:81, formTrend:'up', stats:{pace:80,shoot:72,pass:60,drib:76,def:20,phys:68} },
    { id:11, name:"Daniel Bîrligea", initials:"DB", pos:"ST", age:25, height:"1.84m", weight:"80kg", foot:"Drept", club:"CFR Cluj", contract:"2028", freeAgent:false, value:2000000, aiScore:90, formTrend:'up', 
        psychTags: ["Muncitor", "Agresivitate Pozitivă", "Ambițios"],
        characterSummary: "Profil de luptător, caracterizat printr-o determinare feroce și o etică a muncii (work-rate) excelentă. Lider prin efort pe teren, dispus la sacrificiu fizic pentru echipă. Are un nivel ridicat de agresivitate pozitivă pe faza de pressing (recuperare sus). Se adaptează rapid la cerințe tactice riguroase și are o mentalitate de 'killer' orientată spre performanță pură. Risc minim de indisciplină în vestiar.",
        stats:{pace:78,shoot:80,pass:50,drib:68,def:22,phys:78} },
    { id:12, name:"Matei Ilie", initials:"MI", pos:"CDM", age:20, foot:"Drept", club:"U Cluj", contract:"2028", freeAgent:false, value:200000, aiScore:82, formTrend:'up', stats:{pace:65,shoot:40,pass:68,drib:60,def:72,phys:74} },
    { id:13, name:"Adrian Păun", initials:"AP2", pos:"CAM", age:31, foot:"Stâng", club:"U Cluj", contract:"2026", freeAgent:false, value:150000, aiScore:58, formTrend:'down', stats:{pace:58,shoot:65,pass:72,drib:70,def:30,phys:55} },
    { id:14, name:"Cristian Dumitru", initials:"CD", pos:"CB", age:19, foot:"Drept", club:"Petrolul", contract:"2027", freeAgent:false, value:180000, aiScore:85, formTrend:'up', stats:{pace:62,shoot:25,pass:50,drib:42,def:70,phys:75} },
    { id:15, name:"Florin Tănase", initials:"FT", pos:"RW", age:30, foot:"Drept", club:"FCSB", contract:"2026", freeAgent:false, value:1000000, aiScore:70, formTrend:'steady', stats:{pace:72,shoot:75,pass:70,drib:74,def:28,phys:62} },
    { id:16, name:"Luca Mihai", initials:"LM", pos:"GK", age:21, foot:"Drept", club:"Voluntari", contract:"2027", freeAgent:false, value:120000, aiScore:62, formTrend:'steady', stats:{pace:35,shoot:10,pass:50,drib:22,def:18,phys:65} },
    { id:17, name:"George Ganea", initials:"GG", pos:"ST", age:19, foot:"Stâng", club:"Farul", contract:"2028", freeAgent:false, value:250000, aiScore:88, formTrend:'up', stats:{pace:82,shoot:68,pass:45,drib:66,def:18,phys:70} },
    { 
        id:18, name:"Bogdan Racovițan", initials:"BR", pos:"CB", age:24, foot:"Stâng", club:"Rapid", contract:"2026", freeAgent:false, value:500000, aiScore:74, formTrend:'steady', stats:{pace:60,shoot:30,pass:55,drib:45,def:76,phys:78} 
    },
    { 
        id:99, name:"João Pedro", initials:"JP", pos:"ST", age:20, foot:"Drept", club:"Santos FC", contract:"2026", freeAgent:false, value:4500000, aiScore:92, formTrend:'up',
        riskScore:75, riskSummary:"Risc ridicat de acomodare. Șoc cultural și barieră lingvistică.",
        psychTags: ["Talent pur", "Extrovertit", "Homesick-prone"],
        characterSummary: "Profil psihologic: Jucător extrem de talentat, dar dependent de mediul social. Prima ieșire din Brazilia poate cauza o scădere drastică a formei în primele luni.",
        injuries: [],
        injuryHistory: [95, 92, 94, 96, 95, 94],
        transferHistory: [
            { club: 'Santos FC', period: '2021 - Prezent', years: 3 }
        ],
        pros: ["Viteză explozivă", "Tehnică individuală de elită"],
        cons: ["Nu vorbește limba română sau engleză", "Lipsă experiență în Europa"],
        aiAlert: "Necesită suport specializat pentru integrare culturală.",
        disciplineStats: [15, 25, 60, 40],
        stats:{pace:92,shoot:82,pass:65,drib:90,def:20,phys:68} 
    },
];

// ── Integration & Adaptability Mock Data ──
const integrationDataMock = {
    1: { // Octavian Popescu - Low Risk
        riskScore: 15,
        curve: [85, 88, 90, 92, 94, 95],
        factors: [
            { label: "Bariera Lingvistică", value: 95, status: "green", desc: "Nativ (Română)" },
            { label: "Experiență Internațională", value: 80, status: "green", desc: "Adaptat la fotbalul european" },
            { label: "Cultură / Climă", value: 100, status: "green", desc: "Mediu identic" },
            { label: "Stabilitate Familială", value: 90, status: "green", desc: "Relocare facilă" },
            { label: "Diferență de Nivel", value: 85, status: "green", desc: "Cunoaște campionatul" }
        ]
    },
    99: { // João Pedro - High Risk
        riskScore: 75,
        curve: [88, 60, 45, 55, 70, 85],
        factors: [
            { label: "Bariera Lingvistică", value: 20, status: "red", desc: "Vorbește doar Portugheză" },
            { label: "Experiență Internațională", value: 10, status: "red", desc: "Prima ieșire din țară" },
            { label: "Cultură / Climă", value: 30, status: "red", desc: "Șoc termic/cultural (Europa de Est)" },
            { label: "Stabilitate Familială", value: 40, status: "red", desc: "Singur, predispus la homesickness" },
            { label: "Diferență de Nivel", value: 50, status: "yellow", desc: "Trecere de la ritm lent la fizic" }
        ]
    }
};

// ── AI Match Mock ──
const AI_MATCHES = [
    { name:"Matei Ilie", initials:"MI", pos:"CDM", age:20, club:"U Cluj", value:200000, matchPct:92, stats:{pace:65,shoot:40,pass:68,drib:60,def:72,phys:74} },
    { name:"Cristian Dumitru", initials:"CD", pos:"CB", age:19, club:"Petrolul", value:180000, matchPct:87, stats:{pace:62,shoot:25,pass:50,drib:42,def:70,phys:75} },
    { name:"George Ganea", initials:"GG", pos:"ST", age:19, club:"Farul", value:250000, matchPct:81, stats:{pace:82,shoot:68,pass:45,drib:66,def:18,phys:70} },
];

// ── API Configuration & Fetch Utilities ──
const API_BASE = window.location.origin + "/api/v1";
const API_KEY = "super-secret-admin-key";

let _serverHealthy = null;
let _healthCheckTime = 0;

async function checkServerHealth() {
    // Cache result for 30 seconds
    if (_serverHealthy !== null && (Date.now() - _healthCheckTime) < 30000) return _serverHealthy;
    try {
        const res = await fetch(window.location.origin + "/health", { signal: AbortSignal.timeout(3000) });
        _serverHealthy = res.ok;
    } catch {
        _serverHealthy = false;
    }
    _healthCheckTime = Date.now();
    return _serverHealthy;
}

async function fetchFromAPI(endpoint, options = {}) {
    try {
        const mergedHeaders = { 'x-api-key': API_KEY, 'Content-Type': 'application/json', ...(options.headers || {}) };
        const res = await fetch(`${API_BASE}${endpoint}`, {
            ...options,
            headers: mergedHeaders
        });
        if (!res.ok) throw new Error(`API Error: ${res.status}`);
        return await res.json();
    } catch (e) {
        console.error("API Fetch Error:", e);
        return null;
    }
}

async function fetchFilteredPlayers(params = {}) {
    const query = new URLSearchParams();
    for (const [key, val] of Object.entries(params)) {
        if (val !== null && val !== undefined && val !== '') {
            query.append(key, val);
        }
    }
    
    console.log('[Scout] API Query:', `/scout/search?${query.toString()}`);
    const result = await fetchFromAPI(`/scout/search?${query.toString()}`);
    return result || { data: [], meta: { totalPlayers: 0, currentPage: 1, totalPages: 0 } };
}

async function getPlayerDetails(id) {
    return await fetchFromAPI(`/players/${id}`);
}

async function getTransfermarktData(id) {
    return await fetchFromAPI(`/players/${id}/transfermarkt`);
}

async function getIntegrationReport(id) {
    return await fetchFromAPI(`/players/${id}/integration-report`);
}

function getFlagUrl(nat) {
    const map = {
        'Romania': 'ro', 'Bulgaria': 'bg', 'Hungary': 'hu', 'Serbia': 'rs', 
        'Moldova': 'md', 'France': 'fr', 'Italy': 'it', 'Spain': 'es',
        'Brazil': 'br', 'Argentina': 'ar', 'Portugal': 'pt', 'Germany': 'de',
        'Nigeria': 'ng', 'Ghana': 'gh', 'Ivory Coast': 'ci', 'Cameroon': 'cm'
    };
    const code = map[nat] || 'ro';
    return `https://flagcdn.com/w20/${code}.png`;
}

// ── Utilities ──
function fmt(v) { return v >= 1000000 ? (v/1000000).toFixed(1)+'M' : v >= 1000 ? Math.round(v/1000)+'K' : v; }
function parseCurrency(val) {
    if (typeof val === 'number') return val;
    if (!val) return 0;
    let s = val.toString().replace(/[€$,]/g, '').toUpperCase();
    let multiplier = 1;
    if (s.endsWith('M')) { multiplier = 1000000; s = s.slice(0, -1); }
    else if (s.endsWith('K')) { multiplier = 1000; s = s.slice(0, -1); }
    return parseFloat(s) * multiplier;
}
const STAT_LABELS = ['Pace','Shoot','Pass','Drib','Def','Phys'];
function statsArr(s) { return [s.pace, s.shoot, s.pass, s.drib, s.def, s.phys]; }

let _activeTypewriter = null;
function typewriter(element, text, speed = 18) {
    if (_activeTypewriter) clearInterval(_activeTypewriter);
    element.textContent = "";
    let i = 0;
    _activeTypewriter = setInterval(() => {
        if (i < text.length) {
            element.textContent += text.charAt(i);
            i++;
        } else {
            clearInterval(_activeTypewriter);
            _activeTypewriter = null;
        }
    }, speed);
    return _activeTypewriter;
}

// ── State Management ──
const TACTICAL_PROFILES = {
    ST: ["Target Man", "Poacher", "Deep Lying Forward", "Advanced Forward", "Pressing Forward"],
    LW: ["Inverted Winger", "Inside Forward", "Classic Winger", "Raumdeuter"],
    RW: ["Inverted Winger", "Inside Forward", "Classic Winger", "Raumdeuter"],
    CAM: ["Advanced Playmaker", "Shadow Striker", "Trequartista", "Enganche"],
    CM: ["Box-to-Box", "Deep Lying Playmaker", "Mezzala", "Ball Winning Midfielder", "Roaming Playmaker"],
    CDM: ["Anchor Man", "Regista", "Half Back", "Volante"],
    CB: ["Ball Playing Defender", "No-Nonsense Center Back", "Libero"],
    LB: ["Full Back", "Wing Back", "Inverted Full Back"],
    RB: ["Full Back", "Wing Back", "Inverted Full Back"],
    GK: ["Sweeper Keeper", "Traditional Goalkeeper"]
};

// ═══════════════════════ SPA Navigation ═══════════════════════
document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();
    initNavigation();
    initAuth(); // <--- Added this
    initScoutingView();
    initComparator();
    initInsightCards();
    initHeroAISearch();
    initAIFilters();
});

// ════════════════════════ Authentication ════════════════════════
function getAuthToken() {
    return localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
}

function isAuthenticated() {
    return !!getAuthToken();
}

function clearAuth() {
    localStorage.removeItem('authToken');
    sessionStorage.removeItem('authToken');
    localStorage.removeItem('isAuthenticated');
}

function initAuth() {
    const tabSignIn = document.getElementById('tab-signin');
    const tabSignUp = document.getElementById('tab-signup');
    const formSignIn = document.getElementById('form-signin');
    const formSignUp = document.getElementById('form-signup');
    const btnSignIn = document.getElementById('btn-signin-submit');
    const btnSignUp = document.getElementById('btn-signup-submit');
    const signInLoader = document.getElementById('signin-loader');
    const signUpLoader = document.getElementById('signup-loader');
    
    // Check for existing session (either storage)
    if (isAuthenticated()) {
        showDashboard();
    }

    // Tab Switching
    tabSignIn?.addEventListener('click', () => {
        tabSignIn.classList.add('bg-white', 'text-black', 'shadow-lg');
        tabSignIn.classList.remove('text-neutral-400');
        tabSignUp.classList.remove('bg-white', 'text-black', 'shadow-lg');
        tabSignUp.classList.add('text-neutral-400');
        formSignIn.classList.remove('hidden');
        formSignUp.classList.add('hidden');
    });

    tabSignUp?.addEventListener('click', () => {
        tabSignUp.classList.add('bg-white', 'text-black', 'shadow-lg');
        tabSignUp.classList.remove('text-neutral-400');
        tabSignIn.classList.remove('bg-white', 'text-black', 'shadow-lg');
        tabSignIn.classList.add('text-neutral-400');
        formSignUp.classList.remove('hidden');
        formSignIn.classList.add('hidden');
    });

    // ── Sign In: Real API call ──
    btnSignIn?.addEventListener('click', async (e) => {
        e.preventDefault();

        const email = document.getElementById('signin-email').value.trim();
        const password = document.getElementById('signin-password').value;
        const rememberMe = document.getElementById('remember-me').checked;

        // Clear any previous error
        document.getElementById('signin-error')?.remove();

        if (!email || !password) {
            showSignInError('Completează email-ul și parola.');
            return;
        }

        // Show loading state
        btnSignIn.disabled = true;
        signInLoader.classList.remove('hidden');
        const btnSpan = btnSignIn.querySelector('span');
        const btnIcon = btnSignIn.querySelector('i, svg');
        if (btnSpan) btnSpan.textContent = 'Se autentifică...';
        if (btnIcon) btnIcon.classList.add('hidden');

        try {
            const res = await fetch('/api/v1/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });

            if (!res.ok) {
                const errData = await res.json().catch(() => ({}));
                throw new Error(errData.detail || 'Autentificare eșuată.');
            }

            const data = await res.json();

            // Store token based on "Remember this device"
            if (rememberMe) {
                localStorage.setItem('authToken', data.token);
                localStorage.setItem('isAuthenticated', 'true');
            } else {
                sessionStorage.setItem('authToken', data.token);
                // Also set a flag so syncAuthState works
                sessionStorage.setItem('isAuthenticated', 'true');
            }

            showDashboard();
        } catch (err) {
            showSignInError(err.message || 'Email sau parolă incorectă.');
        } finally {
            // Reset button
            btnSignIn.disabled = false;
            signInLoader.classList.add('hidden');
            if (btnSpan) btnSpan.textContent = 'Sign In';
            if (btnIcon) btnIcon.classList.remove('hidden');
        }
    });

    // Allow Enter key to submit
    document.getElementById('signin-password')?.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            btnSignIn?.click();
        }
    });
    document.getElementById('signin-email')?.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            btnSignIn?.click();
        }
    });

    // Sign Up — same flow (mock)
    btnSignUp?.addEventListener('click', (e) => {
        e.preventDefault();
        if (btnSignUp && signUpLoader) {
            btnSignUp.disabled = true;
            signUpLoader.classList.remove('hidden');
            setTimeout(() => {
                localStorage.setItem('authToken', 'ucluj-admin-token-777');
                localStorage.setItem('isAuthenticated', 'true');
                showDashboard();
                btnSignUp.disabled = false;
                signUpLoader.classList.add('hidden');
            }, 1000);
        }
    });

    // Navbar Logout
    const navAuthBtn = document.getElementById('nav-auth-btn');
    navAuthBtn?.addEventListener('click', (e) => {
        e.preventDefault();
        if (isAuthenticated()) {
            clearAuth();
            syncAuthState();
            navigateTo('home');
        } else {
            syncAuthState();
        }
    });
}

function showSignInError(msg) {
    // Remove previous error if any
    document.getElementById('signin-error')?.remove();

    const errorDiv = document.createElement('div');
    errorDiv.id = 'signin-error';
    errorDiv.className = 'flex items-center gap-2 text-red-400 text-xs mt-2 animate-fade-in';
    errorDiv.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>
        </svg>
        <span>${msg}</span>
    `;

    // Insert after the password field's parent div
    const passwordField = document.getElementById('signin-password');
    passwordField?.closest('.space-y-2')?.after(errorDiv);
}

function syncAuthState() {
    const isAuth = isAuthenticated();
    const authView = document.getElementById('view-auth');
    const dashboard = document.getElementById('dashboard-container');
    const navAuthBtn = document.getElementById('nav-auth-btn');

    if (isAuth) {
        if (authView) {
            authView.classList.add('hidden');
            authView.classList.remove('active');
        }
        if (dashboard) dashboard.classList.remove('hidden');
        if (navAuthBtn) navAuthBtn.textContent = 'Logout';
        lucide.createIcons();
    } else {
        if (dashboard) dashboard.classList.add('hidden');
        if (authView) {
            authView.classList.remove('hidden');
            authView.classList.add('active');
            authView.style.opacity = '1';
            authView.style.transform = 'scale(1)';
        }
        if (navAuthBtn) navAuthBtn.textContent = 'Login / Sign Up';
    }
}

// ════════════════════════ Initial Load ════════════════════════
window.addEventListener('load', () => {
    syncAuthState();
    if (isAuthenticated()) {
        navigateTo('home');
    }
});

function showDashboard() {
    const authView = document.getElementById('view-auth');
    
    // Fade out auth
    authView.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    authView.style.opacity = '0';
    authView.style.transform = 'scale(0.98)';
    
    setTimeout(() => {
        syncAuthState();
        navigateTo('home');
    }, 500);
}

// Logout helper for console
window.logout = () => {
    clearAuth();
    location.reload();
};

function initNavigation() {
    document.querySelectorAll('[data-view]').forEach(link => {
        link.addEventListener('click', e => {
            e.preventDefault();
            navigateTo(link.dataset.view);
        });
    });
}

function navigateTo(viewId) {
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
    document.querySelectorAll('.nav-left').forEach(l => l.classList.toggle('active', l.dataset.view === viewId));
    
    const target = document.getElementById('view-' + viewId);
    if (target) {
        target.classList.add('active');
        target.style.animation = 'none';
        target.offsetHeight; // reflow
        target.style.animation = '';
    }
    
    const navLink = document.querySelector(`.nav-link[data-view="${viewId}"]`);
    if (navLink) navLink.classList.add('active');
    window.scrollTo({ top: 0, behavior: 'smooth' });

    if (viewId === 'comparator') {
        // Check for cross-page navigation intent stored in localStorage
        const targetId = localStorage.getItem('tac_target_player_id');
        const targetName = localStorage.getItem('tac_target_player_name');
        if (targetId) {
            localStorage.removeItem('tac_target_player_id');
            localStorage.removeItem('tac_target_player_name');
            _autoLoadComparatorPlayer(targetId, targetName);
        } else {
            setTimeout(updateTacticalComparator, 100);
        }
    }
}

/**
 * Auto-loads a player into the Comparator page.
 * Fetches full metadata from the API, fills the search bar,
 * sets the position dropdown, and triggers evaluation.
 * This is the single source of truth for cross-page navigation.
 */
async function _autoLoadComparatorPlayer(playerId, displayName) {
    const posSel = document.getElementById('tac-position');
    const playerSearch = document.getElementById('tac-player-search');

    // Immediately show the name so the UI feels responsive
    if (displayName) playerSearch.value = displayName;

    try {
        const res = await fetch(`/api/v1/players/${playerId}`, {
            headers: { 'x-api-key': 'super-secret-admin-key' }
        });
        if (!res.ok) throw new Error('Player not found');
        const p = await res.json();

        // Populate all global state exactly like a manual autocomplete selection
        window.currentTacPlayerId = p.wyId;
        window.currentTacPlayerName = `${p.firstName} ${p.lastName}`;
        window.currentTacPlayerPos = p.positionCode;
        window.currentTacPlayerAge = p.birthDate
            ? new Date().getFullYear() - parseInt(p.birthDate.substring(0, 4))
            : '?';
        window.currentTacPlayerClub = p.club || 'Fara club';
        window.currentTacPlayerValue = p.market_value || 0;
        window.currentTacPlayerPhoto = p.photoUrl || '';

        // Update UI
        playerSearch.value = window.currentTacPlayerName;
        const mappedPos = mapPosToComparator(p.positionCode);
        if (mappedPos) posSel.value = mappedPos;

        // Trigger the tactical evaluation (component is fully mounted)
        updateTacticalComparator();
    } catch (err) {
        console.error('[Comparator] Auto-load failed:', err);
        setTimeout(updateTacticalComparator, 100);
    }
}

// ═══════════════════════ Hero AI Search Demo ═══════════════════════
function initHeroAISearch() {
    const searchInp = document.getElementById('hero-search');
    const searchBtn = document.getElementById('hero-search-btn');

    const triggerSearch = () => {
        const val = searchInp.value.trim();
        if (!val) return;
        
        // Hide filter menu if open
        document.getElementById('ai-filter-menu')?.classList.add('hidden');
        
        runHeroAIScout(val);
    };

    searchBtn?.addEventListener('click', triggerSearch);
    searchInp?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') triggerSearch();
    });
}

function initAIFilters() {
    const btnOpen = document.getElementById('btn-open-ai-filters');
    const menu = document.getElementById('ai-filter-menu');
    const btnApply = document.getElementById('btn-apply-ai-filters');
    const btnReset = document.getElementById('btn-reset-ai-filters');

    btnOpen?.addEventListener('click', (e) => {
        e.stopPropagation();
        menu.classList.toggle('hidden');
    });

    // Close on click outside
    document.addEventListener('click', (e) => {
        if (menu && !menu.contains(e.target) && e.target !== btnOpen && !btnOpen.contains(e.target)) {
            menu.classList.add('hidden');
        }
    });

    btnApply?.addEventListener('click', () => {
        menu.classList.add('hidden');
        updateAIFilterIndicator();
        // Feedback effect
        const btn = document.getElementById('hero-search-btn');
        btn.style.transform = 'scale(1.1)';
        setTimeout(() => btn.style.transform = '', 200);
    });

    btnReset?.addEventListener('click', () => {
        document.querySelectorAll('#ai-filter-menu input').forEach(input => {
            if (input.type === 'checkbox' || input.type === 'radio') {
                input.checked = false;
            } else {
                input.value = '';
            }
        });
        updateAIFilterIndicator();
    });
}

function updateAIFilterIndicator() {
    const indicator = document.getElementById('filter-indicator');
    const inputs = document.querySelectorAll('#ai-filter-menu input');
    let hasActive = false;

    inputs.forEach(input => {
        if (input.type === 'checkbox' || input.type === 'radio') {
            if (input.checked) hasActive = true;
        } else {
            if (input.value !== '') hasActive = true;
        }
    });

    if (hasActive) indicator.classList.remove('hidden');
    else indicator.classList.add('hidden');
}

async function runHeroAIScout(query) {
    const isTwinQuery = ["like ", "asemanator", "twin", "similar"].some(kw => query.toLowerCase().includes(kw));

    const widgets = document.getElementById('hero-widgets');
    const thinking = document.getElementById('hero-ai-thinking');
    const results = document.getElementById('hero-ai-results');
    const thinkingText = document.getElementById('ai-thinking-text');

    // Show thinking state
    widgets.classList.add('hidden');
    results.classList.add('hidden');
    thinking.classList.remove('hidden');
    
    if (isTwinQuery) {
        thinkingText.textContent = '✨ AI is scanning the database for digital twins...';
        try {
            const data = await fetchFromAPI(`/scout/ai-twin?query=${encodeURIComponent(query)}`, { method: 'GET' });
            if (!data || !data.twins) throw new Error("API Error");
            showTwinResults(data);
        } catch (e) {
            console.error("AI Twin Error:", e);
            thinkingText.textContent = "Eroare la procesarea AI Twin.";
            setTimeout(resetHeroAI, 2000);
        }
        return;
    }

    thinkingText.textContent = 'Analizez promptul natural...';

    try {
        const data = await fetchFromAPI('/scout/ai-search', {
            method: 'POST',
            body: JSON.stringify({ query })
        });

        if (!data || !data.aiResponse) throw new Error("API Error");

        const ai = data.aiResponse;
        
        // Dynamic thinking steps effect
        const steps = [
            'Interpretare semantică...',
            ai.referencePlayer ? `Extrag profilul lui ${ai.referencePlayer.name}...` : 'Identificare criterii scouting...',
            'Calculare similaritate 40-90...',
            'Finalizare recomandări...'
        ];

        for (let i = 0; i < steps.length; i++) {
            thinkingText.textContent = steps[i];
            await new Promise(r => setTimeout(r, 600));
        }

        showHeroAIResults(ai);
    } catch (e) {
        console.error("AI Scout Error:", e);
        thinkingText.textContent = "Eroare la procesarea AI.";
        setTimeout(resetHeroAI, 2000);
    }
}

function showTwinResults(data) {
    const thinking = document.getElementById('hero-ai-thinking');
    const results = document.getElementById('hero-ai-results');
    const cardsContainer = document.getElementById('hero-ai-cards');
    const titleEl = results.querySelector('h2');
    const subtitleEl = results.querySelector('p');

    thinking.classList.add('hidden');
    results.classList.remove('hidden');

    titleEl.innerHTML = `✨ AI Digital Twins pentru <span class="text-emerald-400">${data.targetPlayerName}</span>`;
    subtitleEl.innerHTML = "Jucători cu cel mai ridicat grad de similaritate statistică, prioritizând potențialul.";

    if (!data.twins || data.twins.length === 0) {
        cardsContainer.innerHTML = `<div class="col-span-full py-12 text-center text-neutral-500">Nu am găsit gemeni digitali pentru acest jucător.</div>`;
        return;
    }

    cardsContainer.innerHTML = data.twins.map((t, i) => {
        const initials = t.name.split(' ').map(n => n[0]).join('').toUpperCase();
        const avatarHtml = t.photoUrl ? `<img src="${t.photoUrl}" class="w-full h-full object-cover rounded-2xl">` : initials;
        
        return `
            <div class="ai-card animate-slide-up cursor-pointer" style="animation-delay: ${i * 0.1}s" onclick="openPlayerModal(${t.id})">
                <div class="ai-card-top flex gap-4">
                    <div class="ai-card-avatar ${t.photoUrl ? '' : 'bg-neutral-800'} w-12 h-12 rounded-xl overflow-hidden flex items-center justify-center text-white font-bold shrink-0">
                        ${avatarHtml}
                    </div>
                    <div class="flex-1">
                        <div class="flex justify-between items-start">
                            <div>
                                <h4 class="text-sm font-bold text-white truncate w-32">${t.name}</h4>
                                <p class="text-[10px] text-neutral-500 uppercase tracking-widest mt-1">${t.position} • ${t.age} ani</p>
                            </div>
                            <div class="flex flex-col items-end">
                                <div class="text-sm font-black text-emerald-400">${t.similarityScore}%</div>
                                <div class="text-[8px] text-neutral-500 uppercase tracking-tighter">Match</div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="mt-4 pt-4 border-t border-white/5">
                    <p class="text-xs text-neutral-400 italic">"${t.explanation}"</p>
                </div>
            </div>
        `;
    }).join('');
}

function showHeroAIResults(ai) {
    const thinking = document.getElementById('hero-ai-thinking');
    const results = document.getElementById('hero-ai-results');
    const cardsContainer = document.getElementById('hero-ai-cards');
    const titleEl = results.querySelector('h2');
    const subtitleEl = results.querySelector('p');

    thinking.classList.add('hidden');
    results.classList.remove('hidden');

    // Update Headers
    titleEl.textContent = ai.referencePlayer ? `Match-uri AI pentru ${ai.referencePlayer.name}` : "Rezultate Scouting AI";
    subtitleEl.innerHTML = ai.scoutingSummary;

    const players = ai.recommendations || [];
    
    if (players.length === 0) {
        cardsContainer.innerHTML = `<div class="col-span-full py-12 text-center text-neutral-500">Nu am găsit rezultate pentru această căutare.</div>`;
        return;
    }

    cardsContainer.innerHTML = players.map((p, i) => {
        const meta = p.csvMetaData || {};
        const initials = p.name.split(' ').map(n => n[0]).join('').toUpperCase();
        const avatarHtml = meta.imageUrl ? `<img src="${meta.imageUrl}" class="w-full h-full object-cover rounded-2xl">` : initials;

        return `
            <div class="ai-card animate-slide-up cursor-pointer" style="animation-delay: ${i * 0.1}s" onclick="openPlayerModal(${p.playerId})">
                <div class="ai-card-top">
                    <div class="ai-card-avatar ${meta.imageUrl ? '' : 'bg-neutral-800'}">${avatarHtml}</div>
                    <div class="ai-card-info">
                        <span class="ai-card-name">${p.name}</span>
                        <span class="ai-card-meta">${p.primaryPosition} · ${meta.age || '?'} ani · ${meta.club || 'N/A'}</span>
                    </div>
                    <div class="ai-card-match-badge">
                        <span class="ai-card-match">${p.matchPercentage}%</span>
                        <span class="text-[8px] uppercase tracking-tighter opacity-50">Match</span>
                    </div>
                </div>
                <hr class="ai-card-divider">
                <div class="ai-card-chart"><canvas id="hero-ai-radar-${i}"></canvas></div>
                <div class="ai-card-footer flex justify-between items-center w-full">
                    <span class="ai-card-value">Val: <strong>${meta.marketValue ? '€' + fmt(meta.marketValue) : '€ -'}</strong></span>
                </div>
            </div>
        `;
    }).join('');

    lucide.createIcons();
    
    // Render Charts
    setTimeout(() => {
        players.forEach((p, i) => {
            const ctx = document.getElementById(`hero-ai-radar-${i}`);
            if (!ctx) return;
            
            const radarData = p.radarScores || { "Mentality": 50, "Shooting": 50, "Passing": 50, "Dribbling": 50, "Defending": 50, "Physicality": 50 };
            const rKeys = Object.keys(radarData);
            const dataValues = Object.values(radarData);

            new Chart(ctx, {
                type: 'radar',
                data: {
                    labels: rKeys,
                    datasets: [
                        { 
                            label: p.name, 
                            data: dataValues, 
                            borderColor: '#4ade80', 
                            backgroundColor: 'rgba(74,222,128,.1)', 
                            borderWidth: 2, 
                            pointRadius: 3 
                        }
                    ]
                },
                options: radarOptions()
            });
        });
    }, 100);
}

window.resetHeroAI = () => {
    const widgets = document.getElementById('hero-widgets');
    const thinking = document.getElementById('hero-ai-thinking');
    const results = document.getElementById('hero-ai-results');
    const searchInp = document.getElementById('hero-search');

    widgets.classList.remove('hidden');
    thinking.classList.add('hidden');
    results.classList.add('hidden');
    searchInp.value = '';
};

function initInsightCards() {
    document.querySelectorAll('.insight-card[data-goto]').forEach(card => {
        card.addEventListener('click', () => navigateTo(card.dataset.goto));
    });
}

// ═══════════════════════ Unified Scouting View ═══════════════════════
let currentScoutView = 'grid';
let multiSortState = []; // Array of { field, dir }
let currentScoutPage = 1;
let scoutTotalPages = 1;
let scoutResultsData = [];

function initScoutingView() {
    const btnApply = document.getElementById('btn-apply-scouting');
    const toggleGrid = document.getElementById('toggle-grid');
    const toggleList = document.getElementById('toggle-list');
    const posFilter = document.getElementById('filter-position');
    const skillInput = document.getElementById('skill-search');
    const globalSearch = document.getElementById('global-search');

    posFilter?.addEventListener('change', updateTacticalProfileDropdown);
    btnApply?.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        currentScoutPage = 1; // Reset to page 1 on new filter apply
        scoutResultsData = [];
        applyScoutingFilters();
    });
    toggleGrid?.addEventListener('click', () => setScoutView('grid'));
    toggleList?.addEventListener('click', () => setScoutView('list'));
    globalSearch?.addEventListener('input', () => {
        currentScoutPage = 1;
        scoutResultsData = [];
        applyScoutingFilters();
    });

    // Load More Button
    const btnLoadMore = document.getElementById('btn-load-more');
    btnLoadMore?.addEventListener('click', () => {
        if (currentScoutPage < scoutTotalPages) {
            currentScoutPage++;
            applyScoutingFilters(true);
        }
    });

    // Sorting event listeners
    document.querySelectorAll('.data-table th.sortable').forEach(th => {
        th.addEventListener('click', () => handleSortClick(th.dataset.sort));
    });

    // Skill Tagging
    skillInput?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && e.target.value.trim()) {
            addSkillTag(e.target.value.trim());
            e.target.value = '';
        }
    });

    currentScoutPage = 1;
    scoutResultsData = [];
    applyScoutingFilters();
}

function addSkillTag(skill) {
    const container = document.getElementById('selected-skills');
    if (!container) return;
    
    // Check if already exists
    if (Array.from(container.querySelectorAll('.skill-tag span')).some(s => s.textContent === skill)) return;

    const tag = document.createElement('div');
    tag.className = 'skill-tag';
    tag.innerHTML = `<span>${skill}</span><button onclick="this.parentElement.remove(); applyScoutingFilters();"><i data-lucide="x" class="w-2.5 h-2.5"></i></button>`;
    container.appendChild(tag);
    lucide.createIcons();
    applyScoutingFilters();
}

function handleSortClick(field) {
    const existingIndex = multiSortState.findIndex(s => s.field === field);
    
    if (existingIndex !== -1) {
        const item = multiSortState[existingIndex];
        if (item.dir === 'asc') {
            item.dir = 'desc';
        } else {
            multiSortState.splice(existingIndex, 1);
        }
    } else {
        multiSortState.push({ field, dir: 'asc' });
    }
    
    applyScoutingFilters();
}

function updateSortUI() {
    document.querySelectorAll('.data-table th.sortable').forEach(th => {
        const field = th.dataset.sort;
        const sortItem = multiSortState.find(s => s.field === field);
        const index = multiSortState.findIndex(s => s.field === field);
        
        th.classList.remove('active-sort', 'sort-asc', 'sort-desc');
        const indicator = th.querySelector('.sort-indicator');
        if (indicator) indicator.innerHTML = '';
        
        if (sortItem) {
            th.classList.add('active-sort', `sort-${sortItem.dir}`);
            if (multiSortState.length > 1) {
                const badge = document.createElement('span');
                badge.className = 'priority-badge';
                badge.textContent = index + 1;
                indicator.appendChild(badge);
            }
        }
    });
}
function updateTacticalProfileDropdown() {
    const pos = document.getElementById('filter-position').value;
    const profileSelect = document.getElementById('filter-tactical-profile');
    
    if (!profileSelect) return;
    
    if (!pos) {
        profileSelect.innerHTML = '<option value="">Selectează poziția...</option>';
        return;
    }
    
    const profiles = TACTICAL_PROFILES[pos] || [];
    profileSelect.innerHTML = '<option value="">Toate profilurile</option>' + 
        profiles.map(p => `<option value="${p}">${p}</option>`).join('');
}

function setScoutView(view) {
    currentScoutView = view;
    document.getElementById('toggle-grid').classList.toggle('bg-white/10', view === 'grid');
    document.getElementById('toggle-list').classList.toggle('bg-white/10', view === 'list');
    document.getElementById('scouting-grid').classList.toggle('hidden', view === 'list');
    document.getElementById('scouting-list').classList.toggle('hidden', view === 'grid');
}

async function applyScoutingFilters(isLoadMore = false) {
    const grid = document.getElementById('scouting-grid');
    const btnLoadMore = document.getElementById('btn-load-more');
    const spinner = document.getElementById('load-more-spinner');
    const paginationContainer = document.getElementById('pagination-container');

    if (!isLoadMore) {
        if (grid) grid.innerHTML = '<div class="p-8 text-center text-neutral-500 w-full col-span-full"><div class="w-8 h-8 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>Fetching live scout data...</div>';
    } else {
        spinner?.classList.remove('hidden');
    }

    // Gather all filters
    const pos = document.getElementById('filter-position')?.value || null;
    const valMin = document.getElementById('filter-val-min')?.value || null;
    const valMax = document.getElementById('filter-val-max')?.value || null;
    const ageMin = document.getElementById('filter-age-min')?.value || null;
    const ageMax = document.getElementById('filter-age-max')?.value || null;
    const searchVal = document.getElementById('global-search')?.value || null;
    const footRadio = document.querySelector('input[name="foot"]:checked');
    const foot = (footRadio && footRadio.value !== 'Ambele') ? footRadio.value : null;

    const params = {
        position: pos,
        min_price: valMin,
        max_price: valMax,
        age_min: ageMin,
        age_max: ageMax,
        name: searchVal,
        foot: foot,
        page: currentScoutPage,
        limit: 20
    };

    // Fetch from API
    const response = await fetchFilteredPlayers(params);
    const rawData = response.data || [];
    scoutTotalPages = response.meta.totalPages || 1;
    const totalPlayers = response.meta.totalPlayers || 0;

    // Map to Frontend Model
    const newPlayers = rawData.map(p => ({
        id: p.wyId,
        name: `${p.firstName} ${p.lastName}`.trim() || p.shortName || "Unknown",
        initials: p.shortName ? p.shortName.substring(0, 2).toUpperCase() : "??",
        pos: p.positionCode ? p.positionCode.toUpperCase() : "Unknown",
        age: p.birthDate ? (new Date().getFullYear() - new Date(p.birthDate).getFullYear()) : 25,
        club: p.club || "—",
        value: p.market_value || 0,
        aiScore: Math.round(p.performance_score || 0),
        foot: p.foot || "N/A",
        photoUrl: p.photoUrl || null,
        nationality: p.nationality || "Romania",
        contract: p.contractExpiration || "N/A"
    }));

    if (isLoadMore) {
        scoutResultsData = [...scoutResultsData, ...newPlayers];
        spinner?.classList.add('hidden');
    } else {
        scoutResultsData = newPlayers;
    }

    // Update Pagination UI
    if (paginationContainer) {
        if (totalPlayers > scoutResultsData.length) {
            paginationContainer.classList.remove('hidden');
        } else {
            paginationContainer.classList.add('hidden');
        }
    }
    
    const paginationInfo = document.getElementById('pagination-info');
    if (paginationInfo) {
        paginationInfo.textContent = `Afișez ${scoutResultsData.length} din ${totalPlayers} jucători`;
    }

    updateSortUI();
    renderScoutingResults(scoutResultsData);
}

function renderScoutingResults(players) {
    const grid = document.getElementById('scouting-grid');
    const tbody = document.getElementById('scouting-tbody');
    const count = document.getElementById('scouting-count');
    count.textContent = `${players.length} jucători găsiți`;

    grid.innerHTML = players.map(p => {
        const dashOffset = 126 - (126 * p.aiScore) / 100;
        const color = p.aiScore >= 85 ? '#4ade80' : p.aiScore >= 70 ? '#facc15' : '#f87171';
        
        // Avatar: show photo if available, otherwise initials
        const avatarContent = p.photoUrl 
            ? `<img src="${p.photoUrl}" alt="${p.name}" style="width:100%;height:100%;object-fit:cover;border-radius:inherit;">` 
            : p.initials;
        
        return `
        <div class="player-card animate-fade-in" data-player-id="${p.id}" onclick="openPlayerModal(${p.id})">
            <div class="pc-ai-potential">
                <svg class="circular-progress">
                    <circle class="bg" cx="22" cy="22" r="20"></circle>
                    <circle class="fg" cx="22" cy="22" r="20" style="stroke-dashoffset: ${dashOffset}; stroke: ${color}"></circle>
                </svg>
                <div class="pc-ai-val">${p.aiScore}</div>
            </div>

            <div class="pc-top">
                <div class="pc-avatar">${avatarContent}</div>
                <div class="pc-badges">
                    <img src="assets/u_cluj_logo.png" class="pc-club-logo" alt="Club">
                    <img src="${getFlagUrl(p.nationality)}" class="pc-flag" alt="${p.nationality}">
                </div>
            </div>

            <div class="pc-body">
                <h3 class="pc-name">${p.name}</h3>
                <div class="pc-meta">
                    <span class="pc-pos-badge">${p.pos}</span>
                    <span class="pc-age">${p.age} ani</span>
                </div>
            </div>

            <div class="pc-stats-grid">
                <div class="pc-stat-item">
                    <i data-lucide="footprints"></i>
                    <span class="pc-stat-val" data-field="foot">${p.foot || 'N/A'}</span>
                </div>
                <div class="pc-stat-item">
                    <i data-lucide="calendar"></i>
                    <span class="pc-stat-val" data-field="contract">${p.contract || 'N/A'}</span>
                </div>
                <div class="pc-stat-item">
                    <i data-lucide="wallet"></i>
                    <span class="pc-stat-val" data-field="value">€${fmt(p.value)}</span>
                </div>
            </div>

            <div class="flex gap-2 mt-auto">
                <button class="pc-cta flex-1" onclick="openPlayerModal(${p.id})">Analiză AI</button>
                <button class="pc-cta-secondary px-3" title="Compară" onclick="event.stopPropagation(); sendToComparator(${p.id}, '${(p.name || '').replace(/'/g, "\\'")}')">
                    <i data-lucide="git-compare"></i>
                </button>
            </div>
        </div>
    `}).join('');

    tbody.innerHTML = players.map((p, i) => `
        <tr onclick="openPlayerModal(${p.id})" data-player-id="${p.id}">
            <td>${i + 1}</td>
            <td><div class="td-player"><div class="td-avatar">${p.initials}</div><span class="td-name">${p.name}</span></div></td>
            <td><span class="pc-pos-badge">${p.pos}</span></td>
            <td>${p.age}</td>
            <td data-field="club">${p.club}</td>
            <td class="td-value" data-field="value">€${fmt(p.value)}</td>
            <td>
                <div class="flex items-center gap-2">
                    <span class="text-green-400 font-bold">${p.aiScore}</span>
                    <div class="w-12 h-1.5 bg-white/5 rounded-full overflow-hidden">
                        <div class="h-full bg-green-500" style="width: ${p.aiScore}%"></div>
                    </div>
                </div>
            </td>
            <td><div class="td-actions">
                <button class="td-action-btn" onclick="event.stopPropagation(); sendToComparator(${p.id}, '${(p.name || '').replace(/'/g, "\\'")}')"><i data-lucide="git-compare"></i></button>
            </div></td>
        </tr>
    `).join('');
    lucide.createIcons();
}

/**
 * Live-update a rendered player card with enriched Transfermarkt data.
 * Called asynchronously after TM data loads — updates the DOM in-place
 * without re-rendering the entire grid (preserves scroll position, animations).
 */
function refreshCardData(player) {
    // Update Grid Card
    const card = document.querySelector(`.player-card[data-player-id="${player.id}"]`);
    if (card) {
        // Update avatar with photo
        if (player.photoUrl) {
            const avatar = card.querySelector('.pc-avatar');
            if (avatar && !avatar.querySelector('img')) {
                avatar.innerHTML = `<img src="${player.photoUrl}" alt="${player.name}" style="width:100%;height:100%;object-fit:cover;border-radius:inherit;">`;
            }
        }
        // Update foot
        const footEl = card.querySelector('[data-field="foot"]');
        if (footEl && player.foot && player.foot !== 'N/A') footEl.textContent = player.foot;
        // Update value
        const valEl = card.querySelector('[data-field="value"]');
        if (valEl && player.value) valEl.textContent = `€${fmt(player.value)}`;
        // Update contract
        const contractEl = card.querySelector('[data-field="contract"]');
        if (contractEl && player.contract && player.contract !== 'N/A') contractEl.textContent = player.contract;
    }

    // Update Table Row
    const row = document.querySelector(`tr[data-player-id="${player.id}"]`);
    if (row) {
        const clubTd = row.querySelector('[data-field="club"]');
        if (clubTd && player.club && player.club !== '—') clubTd.textContent = player.club;
        const valTd = row.querySelector('[data-field="value"]');
        if (valTd && player.value) valTd.textContent = `€${fmt(player.value)}`;
    }
}

// ═══════════════════════ AI MATCH VIEW ═══════════════════════
let aiChartInstances = [];

// Extended pool of AI match candidates
const AI_MATCH_POOL = [
    { name:"Vladislav Blănuță", initials:"VB", pos:"ST", age:22, club:"FC U Craiova", value:400000, freeAgent:false, matchPct:94, stats:{pace:78,shoot:76,pass:55,drib:72,def:25,phys:75} },
    { name:"Louis Munteanu", initials:"LM", pos:"ST", age:21, club:"CFR Cluj", value:1200000, freeAgent:false, matchPct:91, stats:{pace:82,shoot:80,pass:65,drib:78,def:22,phys:68} },
    { name:"Jovan Markovic", initials:"JM", pos:"ST", age:23, club:"Univ. Craiova", value:800000, freeAgent:false, matchPct:88, stats:{pace:75,shoot:78,pass:62,drib:80,def:20,phys:72} },
    { name:"Darius Olaru", initials:"DO", pos:"CM", age:26, club:"FCSB", value:7000000, freeAgent:false, matchPct:89, stats:{pace:78,shoot:74,pass:80,drib:76,def:65,phys:72} },
    { name:"Constantin Grameni", initials:"CG", pos:"CM", age:21, club:"Farul", value:2000000, freeAgent:false, matchPct:85, stats:{pace:70,shoot:68,pass:78,drib:72,def:60,phys:65} },
    { name:"Matei Ilie", initials:"MI", pos:"CDM", age:20, club:"U Cluj", value:200000, freeAgent:false, matchPct:92, stats:{pace:65,shoot:40,pass:68,drib:60,def:72,phys:74} },
    { name:"Cristian Dumitru", initials:"CD", pos:"CB", age:19, club:"Petrolul", value:180000, freeAgent:false, matchPct:87, stats:{pace:62,shoot:25,pass:50,drib:42,def:70,phys:75} },
    { name:"Luca Mihai", initials:"LM", pos:"GK", age:21, club:"Voluntari", value:120000, freeAgent:false, matchPct:74, stats:{pace:35,shoot:10,pass:50,drib:22,def:18,phys:65} },
];

function getFilteredAIMatches(referencePos = 'CM') {
    const ageMax = parseInt(document.getElementById('ai-filter-age')?.value) || Infinity;
    const maxBudget = parseInt(document.getElementById('ai-filter-budget')?.value) || Infinity;
    const u21Only = document.getElementById('ai-filter-u21-toggle')?.checked || false;

    let pool = [...AI_MATCH_POOL];

    // CRITICAL: Filter by position to match reference
    pool = pool.filter(p => p.pos === referencePos);

    // Apply age filter
    const effectiveAgeMax = u21Only ? Math.min(ageMax, 21) : ageMax;
    if (effectiveAgeMax < Infinity) {
        pool = pool.filter(p => p.age <= effectiveAgeMax);
    }

    // Apply budget filter
    if (maxBudget < Infinity) {
        pool = pool.filter(p => p.value <= maxBudget);
    }

    // Sort by match percentage and take top 3
    pool.sort((a, b) => b.matchPct - a.matchPct);
    return pool.slice(0, 3);
}

function renderAIMatchCards(matches) {
    const data = matches;
    const container = document.getElementById('ai-cards-container');

    if (data.length === 0) {
        container.innerHTML = `<div style="grid-column: 1/-1; text-align:center; padding: 3rem 1rem;">
            <p style="color:var(--text-muted); font-size:.95rem;">Niciun jucător găsit cu filtrele selectate pentru această poziție.</p>
            <p style="color:var(--text-muted); font-size:.8rem; margin-top:.4rem;">Încercați să relaxați criteriile de vârstă sau buget.</p>
        </div>`;
        return;
    }

    container.innerHTML = data.map((m, i) => `
        <div class="ai-card">
            <div class="ai-card-top">
                <div class="ai-card-avatar">${m.initials}</div>
                <div class="ai-card-info">
                    <span class="ai-card-name">${m.name}</span>
                    <span class="ai-card-meta">${m.pos} · ${m.age} ani · ${m.club}</span>
                </div>
                <span class="ai-card-match">${m.matchPct}%</span>
            </div>
            <hr class="ai-card-divider">
            <div class="ai-card-chart"><canvas id="ai-radar-${i}"></canvas></div>
            <div class="ai-card-footer flex justify-between items-center w-full">
                <span class="ai-card-value">Val: <strong>€${fmt(m.value)}</strong></span>
            </div>
        </div>
    `).join('');
    lucide.createIcons();
    window._currentAIMatches = data;
}

// AI Search with loading state
document.getElementById('btn-ai-search')?.addEventListener('click', triggerAISearch);

async function triggerAISearch() {
    const btn = document.getElementById('btn-ai-search');
    const cardsContainer = document.getElementById('ai-cards-container');
    const searchVal = document.getElementById('ai-match-input').value;

    // Enter loading state
    btn.classList.add('loading');
    cardsContainer.classList.add('loading-state');

    // Determine Reference Player
    let refPos = 'CM';
    let refStats = [68, 60, 74, 66, 65, 70]; // Default CM (Nistor)
    let refScore = 85;

    if (searchVal.toLowerCase().includes('birligea')) {
        refPos = 'ST';
        refStats = [82, 85, 55, 76, 25, 80];
        refScore = 90;
        updateReferenceCard("Daniel Bîrligea", "DB", "ST", 23, 1500000);
    } else {
        updateReferenceCard("Dan Nistor", "DN", "CM", 36, 150000);
    }

    // Fetch players from API matching the position
    const maxBudget = parseInt(document.getElementById('ai-filter-budget')?.value) || null;
    let players = await fetchFilteredPlayers(refPos, null, maxBudget);

    // Local filters
    const ageMax = parseInt(document.getElementById('ai-filter-age')?.value) || 99;
    const u21Only = document.getElementById('ai-filter-u21-toggle')?.checked || false;
    const effectiveAgeMax = u21Only ? Math.min(ageMax, 21) : ageMax;
    
    players = players.filter(p => {
        const age = p.birthDate ? (new Date().getFullYear() - new Date(p.birthDate).getFullYear()) : 25;
        return age <= effectiveAgeMax;
    });

    // Sort by performance score descending
    players.sort((a,b) => (b.performance_score || 0) - (a.performance_score || 0));
    const topPlayers = players.slice(0, 3);

    // Map to matches and lazily fetch details for radar
    const matches = [];
    for (const p of topPlayers) {
        const age = p.birthDate ? (new Date().getFullYear() - new Date(p.birthDate).getFullYear()) : 25;
        
        // Mock Similarity Match % based on proximity to refScore
        const diff = Math.abs((p.performance_score || 0) - refScore);
        const matchPct = Math.max(0, Math.min(99, Math.round(99 - (diff * 1.5))));

        // Fetch detailed stats for radar
        const details = await getPlayerDetails(p.wyId);
        let playerStats = [50, 50, 50, 50, 50, 50]; // fallback
        
        if (details && details.normalized_stats && details.normalized_stats.radarScores) {
            const rs = details.normalized_stats.radarScores;
            if (refPos === 'GK') {
                playerStats = [rs.Saving||50, rs.Distribution||50, rs.Reflexes||50, rs.Positioning||50, rs.Handling||50, rs.Mentality||50];
            } else {
                playerStats = [rs.Shooting||50, rs.Passing||50, rs.Dribbling||50, rs.Defending||50, rs.Physicality||50, rs.Mentality||50];
            }
        }

        matches.push({
            name: `${p.firstName} ${p.lastName}`.trim() || p.shortName || "Unknown",
            initials: p.shortName ? p.shortName.substring(0, 2).toUpperCase() : "??",
            pos: p.positionCode ? p.positionCode.toUpperCase() : "Unknown",
            age: age,
            club: "Unknown", // Fallback
            value: p.market_value || 0,
            matchPct: matchPct,
            stats: {
                pace: playerStats[0], shoot: playerStats[1], pass: playerStats[2], 
                drib: playerStats[3], def: playerStats[4], phys: playerStats[5]
            }
        });
    }

    // Exit loading state
    btn.classList.remove('loading');
    cardsContainer.classList.remove('loading-state');

    renderAIMatchCards(matches);
    setTimeout(() => renderAICharts(matches, refStats), 80);
}

function updateReferenceCard(name, initials, pos, age, value) {
    const refCard = document.getElementById('reference-player');
    if (!refCard) return;
    refCard.querySelector('.ref-avatar').textContent = initials;
    refCard.querySelector('.ref-name').textContent = name;
    refCard.querySelector('.ref-meta').textContent = `${pos} · ${age} ani · Valoare: €${fmt(value)}`;
}

// Sync U21 toggle with age input
document.getElementById('ai-filter-u21-toggle')?.addEventListener('change', e => {
    const ageInp = document.getElementById('ai-filter-age');
    if (e.target.checked) {
        ageInp.value = '21';
    }
});

function renderAICharts(matches, referenceStats) {
    aiChartInstances.forEach(c => c.destroy());
    aiChartInstances = [];
    const refStats = referenceStats || [68, 60, 74, 66, 65, 70];
    const data = matches || window._currentAIMatches || [];
    data.forEach((m, i) => {
        const ctx = document.getElementById('ai-radar-' + i);
        if (!ctx) return;
        const chart = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: STAT_LABELS,
                datasets: [
                    { label: 'Referință', data: refStats, borderColor: 'rgba(255,255,255,.4)', backgroundColor: 'rgba(255,255,255,.05)', borderWidth: 1.5, pointRadius: 2 },
                    { label: m.name, data: statsArr(m.stats), borderColor: '#4ade80', backgroundColor: 'rgba(74,222,128,.1)', borderWidth: 2, pointRadius: 3 }
                ]
            },
            options: radarOptions()
        });
        aiChartInstances.push(chart);
    });
}

function radarOptions(maxTick) {
    return {
        responsive: true, maintainAspectRatio: false,
        scales: {
            r: {
                beginAtZero: true, max: maxTick || 100,
                grid: { color: 'rgba(255,255,255,.06)' },
                angleLines: { color: 'rgba(255,255,255,.06)' },
                pointLabels: { color: '#a3a3a3', font: { family: 'Inter', size: 10 } },
                ticks: { display: false }
            }
        },
        plugins: { legend: { display: false } }
    };
}


// ═══════════════════════ TACTICAL COMPARATOR ═══════════════════════
let tacRadarChart = null;
let tacGaugeChart = null;

// ── Position-specific axis labels ──
const positionMetricsMapping = {
    GK:  ['Joc bun de picior\n(Inițiere)', 'Reflexe &\nPoziționare', 'Viziune &\nScanare teren', 'Comunicare\ncu fundașii', 'Siguranță\n& Control'],
    LB:  ['Viteză &\nRezistență', 'Centrare\nprecisă', 'Tehnică &\nDribling', 'Citirea jocului\n(Anticipare)', 'Recuperare &\nInițiere atac', 'Cooperare tactică\n(cu mijlocașii)'],
    RB:  ['Viteză &\nRezistență', 'Centrare\nprecisă', 'Tehnică &\nDribling', 'Citirea jocului\n(Anticipare)', 'Recuperare &\nInițiere atac', 'Cooperare tactică\n(cu mijlocașii)'],
    CB:  ['Inițiere atac\n(pase scurte/medii)', 'Decizii sub\npresiune', 'Talie &\nForță fizică', 'Dueluri\n1 vs 1', 'Reacție imediată\n& Anticipare'],
    CM:  ['Viziunea\njocului', 'Tehnica\nde pasare', 'Agresivitate &\nRecuperare', 'Identificare\noportunități', 'Asigurarea\nechilibrului'],
    CDM: ['Viziunea\njocului', 'Tehnica\nde pasare', 'Agresivitate &\nRecuperare', 'Identificare\noportunități', 'Asigurarea\nechilibrului'],
    CAM: ['Viziunea\njocului', 'Tehnica\nde pasare', 'Agresivitate &\nRecuperare', 'Identificare\noportunități', 'Asigurarea\nechilibrului'],
    LW:  ['Viteză &\nAccelerare', 'Progresie &\nDribling', 'Forță &\nPotență aerobă', 'Participare la\nconstrucție', 'Decizii ofensive\nrapide'],
    RW:  ['Viteză &\nAccelerare', 'Progresie &\nDribling', 'Forță &\nPotență aerobă', 'Participare la\nconstrucție', 'Decizii ofensive\nrapide'],
    ST:  ['Finalizare\nprecisă', 'Joc de cap\n& Dueluri', 'Pressing imediat\nla pierdere', 'Poziționare &\nSpații libere', 'Inițiere\nContraatac', 'Disciplină\ntactică']
};
function getTacLabels(pos) { return positionMetricsMapping[pos] || positionMetricsMapping.ST; }
function getTacShortLabels(pos) { return getTacLabels(pos).map(l => l.replace(/\n/g, ' ')); }

// ── Tactical Requirements Database ──
// Values represent the ideal score (0-100) for each axis per system+position
const tacticsDB = {
    '4-2-3-1': {
        GK:  { vals: [80, 85, 70, 80, 90], reqs: ['Construcție de la poartă (picioare)', 'Reflexe rapide pe șuturi', 'Scanare teren înainte de pasă', 'Ieșiri la centrări'] },
        LB:  { vals: [82, 75, 68, 78, 80, 72], reqs: ['Suprapuneri pe flanc', 'Centrări precise', 'Repliere rapidă', 'Disciplină defensivă'] },
        RB:  { vals: [82, 75, 68, 78, 80, 72], reqs: ['Suprapuneri pe flanc', 'Joc combinativ cu extrema', 'Repliere rapidă', 'Dueluri 1v1 defensive'] },
        CB:  { vals: [72, 78, 85, 82, 88], reqs: ['Construcție de la portar', 'Bloc compact & poziționare', 'Dueluri aeriene dominante', 'Anticipare și interceptare'] },
        CM:  { vals: [85, 82, 80, 75, 88], reqs: ['Contra-pressing dominant', 'Construcție din linia a 2-a', 'Disciplină în bloc compact', 'Identificare spații'] },
        CDM: { vals: [78, 80, 92, 70, 95], reqs: ['Interceptări și contra-pressing', 'Distribuție precisă', 'Acoperire spații (bloc compact)', 'Dueluri fizice dominante'] },
        CAM: { vals: [90, 88, 65, 85, 72], reqs: ['Conectare între linii (Pivot)', 'Viziune și ultimul pas', 'Pressing imediat la pierdere', 'Inserții în careu'] },
        LW:  { vals: [90, 82, 60, 70, 78], reqs: ['Sprint pe contraatac', 'Dribling 1v1 pe flanc', 'Repliere pe faza defensivă', 'Centrări din alergare'] },
        RW:  { vals: [88, 82, 60, 72, 80], reqs: ['Sprint pe contraatac', 'Joc combinativ pe dreapta', 'Repliere defensivă', 'Finalizare din interior'] },
        ST:  { vals: [90, 80, 85, 88, 82, 75], reqs: ['Finalizare & Pivot central', 'Contra-pressing intens la pierdere', 'Tranziție D→O: Sprint în profunzime', 'Disciplină în blocul compact'] }
    },
    '4-3-3': {
        GK:  { vals: [85, 82, 72, 78, 88], reqs: ['Construcție precisă cu picioarele', 'Comandă careu pe cornere', 'Scanare înainte de distribuție', 'Ieșiri rapide pe contraatac'] },
        LB:  { vals: [85, 78, 70, 75, 85, 78], reqs: ['Suprapuneri ofensive constante', 'Centrări din alergare', 'Tranziție defensivă rapidă', 'Joc combinativ cu LW'] },
        RB:  { vals: [85, 78, 70, 75, 85, 78], reqs: ['Suprapuneri ofensive constante', 'Centrări din alergare', 'Tranziție defensivă rapidă', 'Joc combinativ cu RW'] },
        CB:  { vals: [75, 80, 82, 78, 90], reqs: ['Construcție sub presiune', 'Bloc compact strict', 'Dominanță aeriană', 'Acoperire pe linia de fund'] },
        CM:  { vals: [88, 85, 78, 80, 85], reqs: ['Contra-pressing ca pivot central', 'Construcție progresivă', 'Acoperire echilibrată', 'Dueluri fizice la mijloc'] },
        CDM: { vals: [82, 85, 90, 72, 92], reqs: ['Filtru defensiv central', 'Distribuție laterală', 'Disciplină absolută', 'Dominanță fizică'] },
        CAM: { vals: [92, 85, 62, 88, 78], reqs: ['Inserții ofensive ca mezzala', 'Pressing coordonat', 'Creativitate în ultimii 30m', 'Recuperare în mijlocul terenului'] },
        LW:  { vals: [92, 88, 58, 65, 82], reqs: ['Explozie maximă pe tranziție', 'Dribling 1v1 dominant', 'Pressing pe fundașul advers', 'Finalizare din semi-spații'] },
        RW:  { vals: [92, 88, 58, 65, 82], reqs: ['Explozie maximă pe tranziție', 'Centrări & finalizare', 'Pressing pe fundașul advers', 'Repliere ocazională'] },
        ST:  { vals: [92, 78, 80, 88, 90, 70], reqs: ['Profunzime & finalizare de calitate', 'Pressing înalt coordonat', 'Explozie pe tranziție rapidă', 'Joc spate-la-poartă limitat'] }
    },
    '4-4-2': {
        GK:  { vals: [70, 88, 65, 82, 92], reqs: ['Joc cu piciorul simplu', 'Comandă autoritar la careu', 'Scanare pe blocul compact', 'Ieșiri rare, decizii sigure'] },
        LB:  { vals: [78, 68, 62, 80, 82, 85], reqs: ['Suprapuneri limitate, focus defensiv', 'Centrări ocazionale', 'Compactitate cu blocul', 'Dueluri 1v1 pe flanc'] },
        RB:  { vals: [78, 68, 62, 80, 82, 85], reqs: ['Suprapuneri limitate, focus defensiv', 'Centrări ocazionale', 'Compactitate cu blocul', 'Dueluri 1v1 pe flanc'] },
        CB:  { vals: [65, 72, 90, 85, 92], reqs: ['Bloc compact ca prioritate', 'Dueluri aeriene dominante', 'Construcție simplă, fără riscuri', 'Comunicare cu partenerul CB'] },
        CM:  { vals: [82, 80, 88, 72, 90], reqs: ['Motor al echipei – efort total', 'Construcție & distribuție', 'Compactitate alături de partener', 'Dueluri fizice constante'] },
        CDM: { vals: [78, 82, 92, 68, 95], reqs: ['Scut defensiv central', 'Intercepție & anticipare', 'Compactitate strictă', 'Dueluri aeriene la centrări'] },
        CAM: { vals: [85, 88, 68, 80, 78], reqs: ['Conectare între linii', 'Pasă decisivă', 'Pressing pe linia mediană', 'Efort de acoperire laterală'] },
        LW:  { vals: [82, 75, 65, 72, 78], reqs: ['Acoperire pe tot flancul', 'Centrări & inserții', 'Disciplină defensivă strictă', 'Tranziție rapidă D→O'] },
        RW:  { vals: [82, 75, 65, 72, 78], reqs: ['Acoperire pe tot flancul', 'Centrări & inserții', 'Disciplină defensivă strictă', 'Tranziție rapidă D→O'] },
        ST:  { vals: [88, 88, 82, 78, 75, 80], reqs: ['Joc de pivot cu partenerul de atac', 'Finalizare directă & instinct', 'Dueluri aeriene în careu', 'Pressing coordonat în tandem'] }
    }
};

// ── Player Tactical Profiles (mapped to their NATURAL position axes) ──
const playerTacticalDB = {
    1:  { naturalPos:'CAM', stats:{ CAM:[88,85,60,82,68], ST:[80,45,72,78,75,65] }, verdict:'Depășește cerințele de creativitate și viziune. Deficiență la dueluri aeriene. Recomandare: Utilizare ca CAM sau „fals 9".' },
    2:  { naturalPos:'LW',  stats:{ LW:[92,88,50,55,75], ST:[75,50,70,72,92,60] }, verdict:'Explozie excelentă pe tranziție, dribling dominant. Disciplina defensivă și forța sub standard. Recomandare: Extremă pe contraatac.' },
    3:  { naturalPos:'ST',  stats:{ ST:[85,80,78,72,70,68] }, verdict:'Finalizator de instinct cu dueluri aeriene solide. Ideal în 4-4-2 ca al doilea atacant.' },
    5:  { naturalPos:'ST',  stats:{ ST:[88,78,72,82,80,62] }, verdict:'Atacant complet cu finalizare premium. Contra-pressing necesită adaptare. Excelent în 4-2-3-1.' },
    6:  { naturalPos:'LB',  stats:{ LB:[70,60,55,78,82,65] }, verdict:'Fundaș lateral disciplinat, focus defensiv. Contribuția ofensivă limitată. Se potrivește în 4-4-2.' },
    7:  { naturalPos:'LW',  stats:{ LW:[88,85,48,62,70], RW:[88,85,48,62,70] }, verdict:'Extremă rapidă cu explozie pe tranziție. Disciplina defensivă sub cerințe. Impact player în 4-3-3.' },
    9:  { naturalPos:'CB',  stats:{ CB:[55,68,92,85,80] }, verdict:'Fundaș central dominant fizic și aerian. Construcția cu mingea sub standard. Ideal în 4-4-2 cu bloc compact.' },
    10: { naturalPos:'RW',  stats:{ RW:[80,76,52,60,72], LW:[80,76,52,60,72] }, verdict:'Extremă ofensivă cu finalizare. Contra-pressing și disciplina necesită îmbunătățire.' },
    11: { naturalPos:'ST',  stats:{ ST:[92,75,80,88,90,70] }, verdict:'Depășește cerințele la Finalizare și Contraatac. Deficiență la Joc de cap (75 vs 80). Atacant de profunzime.' },
    12: { naturalPos:'CDM', stats:{ CDM:[72,78,88,65,85], CM:[75,72,85,68,82] }, verdict:'Mijlocaș defensiv disciplinat cu recuperare excelentă. Se potrivește ideal ca CDM.' },
    13: { naturalPos:'CAM', stats:{ CAM:[82,85,42,78,55] }, verdict:'Viziune tactică bună, dar mobilitatea și efortul fizic sub standard. Opțiune de rotație.' },
    14: { naturalPos:'CB',  stats:{ CB:[52,65,85,78,72] }, verdict:'Tânăr fundaș central cu potențial fizic. Construcția cu mingea necesită dezvoltare.' },
    15: { naturalPos:'RW',  stats:{ RW:[65,70,50,72,78] }, verdict:'Jucător experimentat cu finalizare bună. Ritmul a scăzut. Opțiune de rotație.' },
    16: { naturalPos:'GK',  stats:{ GK:[68,75,60,72,82] }, verdict:'Portar tânăr cu comandă bună de careu. Jocul cu picioarele necesită antrenament intensiv.' },
    17: { naturalPos:'ST',  stats:{ ST:[80,68,75,78,85,58] }, verdict:'Atacant tânăr exploziv. Jocul de cap și disciplina tactică în dezvoltare. Super-sub ideal.' },
    18: { naturalPos:'CB',  stats:{ CB:[58,70,82,75,80] }, verdict:'Fundaș central solid cu forță fizică bună. Se integrează bine în 4-4-2 cu bloc compact.' }
};

// Get player's tactical stats for any evaluated position (generates mock if not mapped)
function getPlayerTacStats(playerId, evalPos) {
    const p = playerTacticalDB[playerId];
    if (!p) return null;
    // Direct mapping exists
    if (p.stats[evalPos]) return p.stats[evalPos];
    // Fallback: use natural position stats and pad/trim to match target axis count
    const natural = p.stats[p.naturalPos];
    const targetLen = getTacLabels(evalPos).length;
    if (natural.length === targetLen) return natural;
    // Generate plausible mock by scaling down (out-of-position penalty)
    const scaled = [];
    for (let i = 0; i < targetLen; i++) {
        scaled.push(Math.max(25, Math.round((natural[i % natural.length] || 50) * 0.7 + Math.random() * 10)));
    }
    return scaled;
}

function initComparator() {
    const systemSel = document.getElementById('tac-system');
    const posSel = document.getElementById('tac-position');
    const playerSearch = document.getElementById('tac-player-search');
    const autocompleteRes = document.getElementById('tac-autocomplete-results');

    // Autocomplete Logic
    let searchTimeout;
    playerSearch.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        const q = e.target.value.trim();
        if (q.length < 2) {
            autocompleteRes.classList.add('hidden');
            return;
        }
        searchTimeout = setTimeout(async () => {
            try {
                const res = await fetch(`/api/v1/scout/search?name=${encodeURIComponent(q)}&limit=5`, {
                    headers: { 'x-api-key': 'super-secret-admin-key' }
                });
                const data = await res.json();
                if (data.data && data.data.length > 0) {
                    autocompleteRes.innerHTML = data.data.map(p => `
                        <div class="px-4 py-2 hover:bg-white/5 cursor-pointer text-sm text-white flex justify-between items-center" data-id="${p.wyId}" data-name="${p.firstName} ${p.lastName}" data-pos="${p.positionCode || 'N/A'}" data-age="${p.birthDate ? new Date().getFullYear() - parseInt(p.birthDate.substring(0,4)) : '?'}" data-club="${p.club || 'Fara club'}" data-value="${p.market_value || 0}" data-photo="${p.photoUrl || ''}">
                            <span>${p.firstName} ${p.lastName}</span>
                            <span class="text-[10px] text-neutral-500">${p.positionCode || 'N/A'}</span>
                        </div>
                    `).join('');
                    autocompleteRes.classList.remove('hidden');
                    
                    // Attach click handlers
                    autocompleteRes.querySelectorAll('div').forEach(item => {
                        item.addEventListener('click', () => {
                            window.currentTacPlayerId = item.dataset.id;
                            window.currentTacPlayerName = item.dataset.name;
                            window.currentTacPlayerPos = item.dataset.pos;
                            window.currentTacPlayerAge = item.dataset.age;
                            window.currentTacPlayerClub = item.dataset.club;
                            window.currentTacPlayerValue = item.dataset.value;
                            window.currentTacPlayerPhoto = item.dataset.photo;
                            
                            playerSearch.value = item.dataset.name;
                            autocompleteRes.classList.add('hidden');
                            
                            // Auto-update position dropdown
                            const mappedPos = mapPosToComparator(item.dataset.pos);
                            if (mappedPos) {
                                posSel.value = mappedPos;
                            }
                            
                            updateTacticalComparator();
                        });
                    });
                } else {
                    autocompleteRes.innerHTML = '<div class="px-4 py-2 text-xs text-neutral-500">Niciun jucător găsit.</div>';
                    autocompleteRes.classList.remove('hidden');
                }
            } catch (err) {
                console.error('Search error', err);
            }
        }, 300);
    });
    
    // Hide autocomplete on click outside
    document.addEventListener('click', (e) => {
        if (!playerSearch.contains(e.target) && !autocompleteRes.contains(e.target)) {
            autocompleteRes.classList.add('hidden');
        }
    });

    systemSel.addEventListener('change', updateTacticalComparator);
    posSel.addEventListener('change', updateTacticalComparator);
}

function mapPosToComparator(pos) {
    if (!pos) return null;
    const p = pos.toUpperCase();
    if (p.includes('ST') || p.includes('CF')) return 'ST';
    if (p.includes('CAM')) return 'CAM';
    if (p.includes('LW') || p.includes('LM')) return 'LW';
    if (p.includes('RW') || p.includes('RM')) return 'RW';
    if (p.includes('CM')) return 'CM';
    if (p.includes('CDM')) return 'CDM';
    if (p.includes('CB')) return 'CB';
    if (p.includes('LB') || p.includes('LWB')) return 'LB';
    if (p.includes('RB') || p.includes('RWB')) return 'RB';
    if (p.includes('GK')) return 'GK';
    return null;
}

function sendToComparator(playerId, playerName) {
    // Auto-resolve name if not passed but found in PLAYERS memory
    if (!playerName) {
        const p = PLAYERS.find(pl => pl.id == playerId);
        if (p) playerName = p.name;
    }
    
    // Store navigation intent in localStorage
    localStorage.setItem('tac_target_player_id', String(playerId));
    if (playerName) localStorage.setItem('tac_target_player_name', playerName);
    
    navigateTo('comparator');
}

async function updateTacticalComparator() {
    const system = document.getElementById('tac-system').value;
    const pos = document.getElementById('tac-position').value;
    const playerId = window.currentTacPlayerId;

    // Render tactical requirements (keep existing mock req logic for left panel)
    const clubReqs = tacticsDB[system]?.[pos];
    if (clubReqs) {
        const reqsContainer = document.getElementById('tac-requirements');
        reqsContainer.innerHTML = clubReqs.reqs.map((req, i) => `
            <div class="tac-req-item">
                <span class="tac-req-num">${i + 1}</span>
                <span class="tac-req-text">${req}</span>
            </div>
        `).join('');
    }

    if (!playerId) {
        document.getElementById('tac-player-avatar').innerHTML = '?';
        document.getElementById('tac-player-name').textContent = '—';
        document.getElementById('tac-player-meta').textContent = 'Selectează un jucător';
        document.getElementById('tac-player-bars').innerHTML = '';
        document.getElementById('tac-match-pct').textContent = '—';
        document.getElementById('tac-verdict-text').textContent = 'Selectează un sistem de joc și un jucător pentru a genera analiza tactică.';
        return;
    }

    try {
        const res = await fetch(`/api/v1/players/${playerId}/tactical-dna`, {
            headers: { 'x-api-key': 'super-secret-admin-key' }
        });
        
        if (!res.ok) throw new Error("No tactical data");
        
        const data = await res.json();
        const p = data.player;
        const evalData = data.tacticalEvaluation;
        
        // Avatar rendering
        const avatarEl = document.getElementById('tac-player-avatar');
        if (window.currentTacPlayerPhoto) {
            avatarEl.innerHTML = `<img src="${window.currentTacPlayerPhoto}" style="width:100%;height:100%;object-fit:cover;border-radius:50%;" />`;
            avatarEl.style.padding = '0';
        } else {
            const initials = p.name.split(' ').map(n => n[0]).join('').substring(0,2);
            avatarEl.innerHTML = initials;
            avatarEl.style.padding = '';
        }

        document.getElementById('tac-player-name').textContent = p.name;
        document.getElementById('tac-player-meta').textContent = p.positionDetails + ` • ${p.marketValue}`;

        const bars = document.getElementById('tac-player-bars');
        bars.innerHTML = evalData.metrics.map(m => {
            const diffColor = m.difference >= 0 ? 'text-emerald-400' : 'text-red-400';
            const diffSign = m.difference >= 0 ? '+' : '';
            const barPct = Math.min(m.playerScore, 100);
            const reqPct = Math.min(m.targetScore, 100);
            
            return `
                <div>
                    <div class="flex justify-between items-center mb-1">
                        <span class="text-[10px] text-neutral-400">${m.label}</span>
                        <span class="text-[10px] font-bold ${diffColor}">${m.playerScore} <span class="text-neutral-600">/</span> ${m.targetScore} <span class="font-medium">(${diffSign}${m.difference})</span></span>
                    </div>
                    <div class="tac-bar-track">
                        <div class="tac-bar-req" style="width:${reqPct}%"></div>
                        <div class="tac-bar-fill ${m.difference >= 0 ? 'tac-bar-good' : 'tac-bar-bad'}" style="width:${barPct}%"></div>
                    </div>
                </div>`;
        }).join('');

        document.getElementById('tac-match-pct').textContent = `${evalData.overallFitPercentage}%`;
        document.getElementById('tac-verdict-text').textContent = `ADN Tactic: Jucătorul are o compatibilitate de ${evalData.overallFitPercentage}% cu profilul U Cluj cerut pentru poziția selectată (${evalData.positionMatched}).`;

        const targetScores = evalData.metrics.map(m => m.targetScore);
        const playerScores = evalData.metrics.map(m => m.playerScore);
        const labels = evalData.metrics.map(m => m.label);
        
        renderTacRadar(targetScores, playerScores, p.name, labels);
        renderTacGauge(evalData.overallFitPercentage);

    } catch (err) {
        console.error(err);
        document.getElementById('tac-verdict-text').textContent = 'Date insuficiente pentru acest jucător.';
    }

    lucide.createIcons();
}

function renderTacRadar(clubVals, playerVals, playerName, labels) {
    const ctx = document.getElementById('tac-radar-chart');
    if (!ctx) return;
    if (tacRadarChart) tacRadarChart.destroy();

    tacRadarChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Standard U Cluj',
                    data: clubVals,
                    borderColor: 'rgba(255,255,255,0.45)',
                    backgroundColor: 'rgba(255,255,255,0.04)',
                    borderWidth: 2,
                    borderDash: [6, 3],
                    pointRadius: 4,
                    pointBackgroundColor: 'rgba(255,255,255,0.6)',
                    pointBorderColor: 'rgba(255,255,255,0.3)',
                    pointBorderWidth: 1
                },
                {
                    label: playerName || 'Jucător',
                    data: playerVals,
                    borderColor: '#34d399',
                    backgroundColor: 'rgba(52,211,153,0.08)',
                    borderWidth: 2.5,
                    pointRadius: 5,
                    pointBackgroundColor: '#34d399',
                    pointBorderColor: '#064e3b',
                    pointBorderWidth: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    grid: { color: 'rgba(255,255,255,0.04)', circular: true },
                    angleLines: { color: 'rgba(255,255,255,0.06)' },
                    pointLabels: {
                        color: '#a3a3a3',
                        font: { family: 'Inter', size: 10, weight: 500 },
                        padding: 18
                    },
                    ticks: { display: false, stepSize: 20 }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#171717',
                    titleColor: '#fff',
                    bodyColor: '#a3a3a3',
                    borderColor: 'rgba(255,255,255,0.1)',
                    borderWidth: 1,
                    padding: 12,
                    cornerRadius: 8,
                    titleFont: { family: 'Inter', size: 12, weight: 600 },
                    bodyFont: { family: 'Inter', size: 11 }
                }
            },
            animation: { duration: 600, easing: 'easeOutCubic' }
        }
    });
}

function renderTacGauge(pct) {
    const ctx = document.getElementById('tac-match-gauge');
    if (!ctx) return;
    if (tacGaugeChart) tacGaugeChart.destroy();

    const color = pct >= 85 ? '#34d399' : pct >= 70 ? '#facc15' : '#f87171';

    tacGaugeChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [pct, 100 - pct],
                backgroundColor: [color, 'rgba(255,255,255,0.04)'],
                borderWidth: 0,
                circumference: 270,
                rotation: 225,
                cutout: '82%'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false }, tooltip: { enabled: false } }
        }
    });
}

function addToComparator(name) {
    const p = PLAYERS.find(pl => pl.name === name);
    if (!p) return;
    sendToComparator(p.id, p.name);
}


// ═══════════════════════ RISK MATRIX MODAL ═══════════════════════
let riskGaugeChart = null;
let injuryChart = null;
let disciplineRadar = null;

async function openPlayerModal(playerId) {
    const modal = document.getElementById('player-modal');
    const overlay = document.getElementById('modal-overlay');
    
    // Show modal in loading state
    document.getElementById('modal-player-avatar').textContent = '...';
    document.getElementById('modal-player-avatar').innerHTML = '...';
    document.getElementById('modal-player-name').textContent = 'Loading...';
    document.getElementById('modal-player-meta').textContent = 'Fetching data...';
    
    // Set loading state for AI sections
    const psychTags = document.getElementById('modal-psych-tags');
    psychTags.innerHTML = `<span class="px-2 py-0.5 bg-white/5 border border-white/10 rounded-full text-[10px] text-neutral-400 font-medium animate-pulse">⏳ Generare profil AI...</span>`;
    document.getElementById('modal-character-summary').textContent = "Analiza AI se încarcă...";
    
    modal.classList.remove('hidden');
    overlay.classList.remove('hidden');
    document.body.style.overflow = 'hidden';

    // Step 1: Health Check
    const serverOnline = await checkServerHealth();
    
    if (!serverOnline) {
        document.getElementById('modal-player-name').textContent = 'Server Offline';
        document.getElementById('modal-player-meta').textContent = 'Serverul backend nu este disponibil.';
        psychTags.innerHTML = `<span class="px-2 py-0.5 bg-red-500/10 border border-red-500/20 rounded-full text-[10px] text-red-400 font-medium">⚠ Server Offline</span>`;
        document.getElementById('modal-character-summary').textContent = "Server Offline — Cannot generate AI Summary. Verifică dacă backend-ul rulează pe localhost.";
        return;
    }

    // Step 2: Fetch core data (fast — no AI)
    const [details, tmData, statsData] = await Promise.all([
        getPlayerDetails(playerId),
        getTransfermarktData(playerId),
        fetch(`/api/v1/players/${playerId}/stats`, { headers: { 'x-api-key': 'super-secret-admin-key' } }).then(res => res.ok ? res.json() : null).catch(() => null)
    ]);

    if (!details) {
        document.getElementById('modal-player-name').textContent = 'Eroare la încărcare date.';
        return;
    }

    const name = `${details.firstName} ${details.lastName}`.trim() || details.shortName || "Unknown";
    const initials = details.shortName ? details.shortName.substring(0, 2).toUpperCase() : "??";
    const age = details.birthDate ? (new Date().getFullYear() - new Date(details.birthDate).getFullYear()) : 25;
    const pos = details.positionCode ? details.positionCode.toUpperCase() : "Unknown";
    const value = tmData && tmData.market_value_formatted ? tmData.market_value_formatted : (tmData && tmData.market_value_raw ? `€${fmt(tmData.market_value_raw)}` : "€ -");
    const club = tmData && tmData.tm_club ? tmData.tm_club : "Unknown";
    const height = tmData && tmData.height_cm ? `${tmData.height_cm} cm` : "N/A";
    const foot = tmData && tmData.foot ? tmData.foot : "N/A";
    const nat = tmData && tmData.nationality ? tmData.nationality : "Unknown";

    // Set Avatar
    const avatarEl = document.getElementById('modal-player-avatar');
    if (tmData && tmData.image_url) {
        avatarEl.innerHTML = `<img src="${tmData.image_url}" alt="${name}" class="w-full h-full object-cover rounded-2xl">`;
    } else {
        avatarEl.textContent = initials;
    }

    // Set Basic Info
    document.getElementById('modal-player-name').textContent = name;
    document.getElementById('modal-player-meta').textContent = `${pos} · ${age} ani · ${nat} · ${club} · ${height} · Picior: ${foot} · Val: ${value}`;

    // Step 3: Parse Radar Scores (from details, always available)
    let radarVals = [50, 50, 50, 50, 50, 50];
    let radarKeys = ['Shooting', 'Passing', 'Dribbling', 'Defending', 'Physicality', 'Mentality'];
    let pros = [];
    let cons = [];

    if (statsData && statsData.radarScores) {
        const rs = statsData.radarScores;
        radarKeys = Object.keys(rs);
        radarVals = Object.values(rs);
        
        radarKeys.forEach((key, i) => {
            if (radarVals[i] >= 65) pros.push(`Aptitudine remarcabilă: ${key} (${radarVals[i]})`);
            else if (radarVals[i] < 55) cons.push(`Deficiență identificată: ${key} (${radarVals[i]})`);
        });
    }

    // Populate Stats Grid
    if (statsData) {
        document.getElementById('modal-stat-goals').textContent = statsData.goals;
        document.getElementById('modal-stat-assists').textContent = statsData.assists;
        document.getElementById('modal-stat-cleansheets').textContent = statsData.cleanSheets;
        document.getElementById('modal-stat-yellows').textContent = statsData.yellowCards;
        document.getElementById('modal-stat-reds').textContent = statsData.redCards;
    } else {
        document.getElementById('modal-stat-goals').textContent = "-";
        document.getElementById('modal-stat-assists').textContent = "-";
        document.getElementById('modal-stat-cleansheets').textContent = "-";
        document.getElementById('modal-stat-yellows').textContent = "-";
        document.getElementById('modal-stat-reds').textContent = "-";
    }

    if (pros.length === 0) pros.push("Performanțe echilibrate pe toate planurile.");
    if (cons.length === 0) cons.push("Fără puncte slabe majore identificate.");

    // Step 4: Fetch AI Integration Report (heavier call, separate)
    const report = await getIntegrationReport(playerId);
    console.log('[Modal] Integration Report:', report);

    // BIND: Psychological Tags (TASK 2 — UI Update 1)
    if (report && report.personality && report.personality.traits && report.personality.traits.length > 0) {
        psychTags.innerHTML = report.personality.traits.map(t => 
            `<span class="px-2 py-0.5 bg-green-500/10 border border-green-500/20 rounded-full text-[10px] text-green-400 font-medium">${t}</span>`
        ).join('');
    } else {
        psychTags.innerHTML = `<span class="px-2 py-0.5 bg-yellow-500/10 border border-yellow-500/20 rounded-full text-[10px] text-yellow-400 font-medium">Analiza AI indisponibilă</span>`;
    }

    // BIND: AI Character Summary (TASK 2 — UI Update 2 + Typewriter)
    const summaryEl = document.getElementById('modal-character-summary');
    if (report && report.personality && report.personality.summary) {
        typewriter(summaryEl, report.personality.summary);
    } else {
        summaryEl.textContent = "Raportul AI nu a putut fi generat momentan. Statisticile de bază sunt disponibile mai jos.";
    }

    // BIND: Risk Score + Integration Factors (4 factors)
    const riskScore = report ? report.riskPercentage : Math.floor(100 - (details.performance_score || 50));
    
    // Animate Risk Score text over 1.5s
    const riskEl = document.getElementById('modal-risk-value');
    const duration = 1500;
    const startTime = performance.now();
    function animateRisk(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const ease = 1 - Math.pow(1 - progress, 3);
        const currentVal = Math.floor(ease * riskScore);
        riskEl.textContent = `${currentVal}%`;
        if (progress < 1) requestAnimationFrame(animateRisk);
        else riskEl.textContent = `${riskScore}%`;
    }
    requestAnimationFrame(animateRisk);

    const factorsList = document.getElementById('modal-integration-factors');
    if (report && report.factors && report.factors.length > 0) {
        factorsList.innerHTML = report.factors.map(f => {
            const statusClass = f.status === 'OPTIM' ? 'status-green' : f.status === 'CRITIC' ? 'status-red' : 'status-yellow';
            const barClass = f.status === 'OPTIM' ? 'bg-emerald-500' : f.status === 'CRITIC' ? 'bg-red-500' : 'bg-yellow-500';
            const statusLabel = f.status === 'OPTIM' ? 'Optim' : f.status === 'CRITIC' ? 'Critic' : 'Mediu';
            return `
                <div class="factor-item">
                    <div class="factor-header">
                        <span class="factor-label">${f.title}</span>
                        <span class="factor-status ${statusClass}">${statusLabel}</span>
                    </div>
                    <div class="factor-bar-bg">
                        <div class="factor-bar-fill ${barClass}" style="width: ${f.score}%"></div>
                    </div>
                    <p class="factor-desc">${f.description}</p>
                </div>
            `;
        }).join('');
    } else {
        factorsList.innerHTML = [
            { label: "Bariera Lingvistică", value: 80, status: "green", desc: nat },
            { label: "Nivel Performanță", value: Math.round(details.performance_score || 50), status: "green", desc: "Z-Score adaptat" },
            { label: "Adaptabilitate Tactică", value: 75, status: "yellow", desc: pos }
        ].map(f => `
            <div class="factor-item">
                <div class="factor-header">
                    <span class="factor-label">${f.label}</span>
                    <span class="factor-status status-${f.status}">${f.status === 'green' ? 'Optim' : f.status === 'red' ? 'Risc' : 'Atenție'}</span>
                </div>
                <div class="factor-bar-bg">
                    <div class="factor-bar-fill ${f.status === 'green' ? 'bg-emerald-500' : f.status === 'red' ? 'bg-red-500' : 'bg-yellow-500'}" style="width: ${f.value}%"></div>
                </div>
                <p class="factor-desc">${f.desc}</p>
            </div>
        `).join('');
    }

    // Inject AI Decision Matrix (Pros & Cons from report)
    if (report && report.aiDecisionMatrix) {
        const dm = report.aiDecisionMatrix;
        document.getElementById('modal-pros-list').innerHTML = (dm.pros || []).map(pro => `<li class="text-[11px] text-neutral-300 flex items-start gap-2"><i data-lucide="check-circle" class="w-3 h-3 text-green-500 mt-0.5"></i> ${pro}</li>`).join('');
        document.getElementById('modal-cons-list').innerHTML = (dm.cons || []).map(con => `<li class="text-[11px] text-neutral-300 flex items-start gap-2"><i data-lucide="x-circle" class="w-3 h-3 text-red-500 mt-0.5"></i> ${con}</li>`).join('');
    } else {
        // Fallback to radar-based pros/cons
        document.getElementById('modal-pros-list').innerHTML = pros.map(pro => `<li class="text-[11px] text-neutral-300 flex items-start gap-2"><i data-lucide="check-circle" class="w-3 h-3 text-green-500 mt-0.5"></i> ${pro}</li>`).join('');
        document.getElementById('modal-cons-list').innerHTML = cons.map(con => `<li class="text-[11px] text-neutral-300 flex items-start gap-2"><i data-lucide="x-circle" class="w-3 h-3 text-red-500 mt-0.5"></i> ${con}</li>`).join('');
    }

    // Timeline (Dynamic scrollable table from TM transfers)
    const timeline = document.getElementById('modal-transfer-timeline');
    const loyaltyBadge = document.getElementById('modal-loyalty-badge');
    if (loyaltyBadge) loyaltyBadge.innerHTML = '';

    if (tmData && tmData.transfers && tmData.transfers.length > 0) {
        const rows = tmData.transfers.map(t => `
            <tr class="border-b border-white/5 hover:bg-white/5 transition-colors">
                <td class="py-2.5 pr-3 text-[11px] text-neutral-400 font-mono whitespace-nowrap">${t.season || '-'}</td>
                <td class="py-2.5 pr-3">
                    <p class="text-[11px] font-semibold text-white truncate max-w-[140px]">${t.from_club_name || 'N/A'}</p>
                </td>
                <td class="py-2.5 px-2 text-neutral-600 text-[10px]">→</td>
                <td class="py-2.5 pr-3">
                    <p class="text-[11px] font-semibold text-emerald-400 truncate max-w-[140px]">${t.to_club_name || 'N/A'}</p>
                </td>
                <td class="py-2.5 text-right text-[10px] text-neutral-400 whitespace-nowrap">${t.transfer_type || '-'}</td>
            </tr>
        `).join('');

        timeline.innerHTML = `
            <div class="overflow-y-auto max-h-[240px] -mx-2 px-2" style="scrollbar-width: thin; scrollbar-color: rgba(255,255,255,0.1) transparent;">
                <table class="w-full">
                    <thead>
                        <tr class="border-b border-white/10">
                            <th class="text-left text-[9px] text-neutral-500 uppercase tracking-wider pb-2 font-medium">Sezon</th>
                            <th class="text-left text-[9px] text-neutral-500 uppercase tracking-wider pb-2 font-medium">De la</th>
                            <th class="pb-2"></th>
                            <th class="text-left text-[9px] text-neutral-500 uppercase tracking-wider pb-2 font-medium">La</th>
                            <th class="text-right text-[9px] text-neutral-500 uppercase tracking-wider pb-2 font-medium">Cost</th>
                        </tr>
                    </thead>
                    <tbody>${rows}</tbody>
                </table>
            </div>
        `;

        if (tmData.transfers.length > 5) {
            loyaltyBadge.innerHTML = `<span class="px-2 py-0.5 bg-red-500/10 border border-red-500/20 rounded-full text-[9px] text-red-400 font-bold uppercase tracking-wider">High Frequency</span>`;
        } else {
            loyaltyBadge.innerHTML = `<span class="px-2 py-0.5 bg-emerald-500/10 border border-emerald-500/20 rounded-full text-[9px] text-emerald-400 font-bold uppercase tracking-wider">Loyal Profile</span>`;
        }
    } else {
        timeline.innerHTML = `<div class="text-neutral-500 text-xs py-4 px-2">Nu există transferuri înregistrate în Transfermarkt pentru acest jucător.</div>`;
    }

    // Init Charts
    setTimeout(() => {
        lucide.createIcons();
        initModalCharts({ 
            id: playerId, 
            riskScore: riskScore, 
            injuryHistory: radarVals, // Mapping radar values to the curve chart!
            curveLabels: radarKeys
        });
    }, 100);
}

function closeModal() {
    document.getElementById('player-modal').classList.add('hidden');
    document.getElementById('modal-overlay').classList.add('hidden');
    document.body.style.overflow = 'auto';
    
    if (riskGaugeChart) riskGaugeChart.destroy();
    if (integrationChart) integrationChart.destroy();
}

let integrationChart = null;

function initModalCharts(p) {
    const iData = integrationDataMock[p.id] || {
        riskScore: p.riskScore || 0
    };
    const risk = iData.riskScore;
    const riskColor = risk > 60 ? '#f87171' : risk > 30 ? '#facc15' : '#4ade80';

    // 1. Risk Gauge (Animated)
    const ctxGauge = document.getElementById('risk-gauge-chart');
    riskGaugeChart = new Chart(ctxGauge, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [risk, 100 - risk],
                backgroundColor: [riskColor, 'rgba(255,255,255,0.05)'],
                borderWidth: 0,
                circumference: 240,
                rotation: 240,
                cutout: '85%'
            }]
        },
        options: { 
            animation: {
                duration: 1500,
                easing: 'easeOutCubic'
            },
            plugins: { legend: { display: false }, tooltip: { enabled: false } }, 
            responsive: true, 
            maintainAspectRatio: false 
        }
    });

    // 2. Player Stats Radar
    const ctxRadar = document.getElementById('player-stats-radar-chart');
    if (ctxRadar) {
        let rVals = p.injuryHistory || [50, 50, 50, 50, 50, 50];
        let rKeys = p.curveLabels || ['Shooting', 'Passing', 'Dribbling', 'Defending', 'Physicality', 'Mentality'];
        
        integrationChart = new Chart(ctxRadar, {
            type: 'radar',
            data: {
                labels: rKeys,
                datasets: [{
                    label: 'Rating',
                    data: rVals,
                    backgroundColor: 'rgba(52, 211, 153, 0.2)',
                    borderColor: 'rgba(52, 211, 153, 1)',
                    pointBackgroundColor: 'rgba(52, 211, 153, 1)',
                    pointBorderColor: '#fff',
                    borderWidth: 2,
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgba(52, 211, 153, 1)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        angleLines: { color: 'rgba(255, 255, 255, 0.1)' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        pointLabels: { color: '#9ca3af', font: { size: 10, family: "'Inter', sans-serif" } },
                        ticks: { display: false, min: 0, max: 100 }
                    }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#111',
                        titleColor: '#fff',
                        bodyColor: '#34d399',
                        padding: 10,
                        cornerRadius: 8
                    }
                }
            }
        });
    }
}

