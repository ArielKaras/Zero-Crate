window.__ZC_DEBUG__ = true;

// --- STATE ---
let state = {
    activeRow: 0,
    activeCard: 0,
    rails: [],
    showInfo: false,
};

// --- DOM ELEMENTS ---
const railsContainer = document.getElementById('content-rails');
const heroValueDisplay = document.getElementById('hero-value-display');
const infoModal = document.getElementById('info-modal');
const infoBody = document.getElementById('info-modal-body');
const diagJsStatus = document.getElementById('diag-js-status');

// --- INITIALIZATION ---
function init() {
    try {
        console.log("Ignition: ZeroCrate Cinematic Engine");

        // 1. Hydrate State from DOM (SSR Ground Truth)
        const railEls = document.querySelectorAll('.rail');
        state.rails = Array.from(railEls).map(el => ({
            id: el.dataset.railId,
            element: el,
            cards: Array.from(el.querySelectorAll('.z-card'))
        }));

        // 2. Initial Focus
        if (state.rails.length > 0 && state.rails[0].cards.length > 0) {
            updateFocus();
        }

        // 3. Event Listeners
        window.addEventListener('keydown', handleInput);

        // MOUSE/TOUCH INTERACTION
        railsContainer.addEventListener('click', (e) => {
            const card = e.target.closest('.z-card');
            if (card) {
                // Determine rail and card index
                const railEl = card.closest('.rail');
                const railId = railEl.dataset.railId;
                const railIndex = state.rails.findIndex(r => r.id === railId);
                const cardIndex = Array.from(railEl.querySelectorAll('.z-card')).indexOf(card);

                // Update State
                if (railIndex !== -1 && cardIndex !== -1) {
                    state.activeRow = railIndex;
                    state.activeCard = cardIndex;
                    updateFocus();
                    // Trigger Open logic on click
                    handleOpen();
                }
            }
        });

        // Hover Focus (Optional: Mouseover changes focus)
        railsContainer.addEventListener('mouseover', (e) => {
            const card = e.target.closest('.z-card');
            if (card) {
                const railEl = card.closest('.rail');
                const railIndex = state.rails.findIndex(r => r.id === railEl.dataset.railId);
                const cardIndex = Array.from(railEl.querySelectorAll('.z-card')).indexOf(card);
                if (railIndex !== -1 && cardIndex !== -1) {
                    state.activeRow = railIndex;
                    state.activeCard = cardIndex;
                    updateFocus();
                }
            }
        });

        // 4. Update Diagnostics
        diagJsStatus.innerHTML = '<span style="color:#10b981">ON (Key+Mouse)</span>';

    } catch (e) {
        console.error("Critical Engine Failure", e);
        document.body.innerHTML += `<div style="position:fixed;top:0;left:0;width:100%;background:red;color:white;padding:10px;">JS CRASH: ${e.message}</div>`;
    }
}

// --- LOGIC ---
function updateFocus() {
    // Clear old focus
    document.querySelectorAll('.z-card-focused').forEach(el => el.classList.remove('z-card-focused'));

    // Validate bounds
    if (state.activeRow >= state.rails.length) state.activeRow = state.rails.length - 1;
    if (state.activeRow < 0) state.activeRow = 0;

    const activeRail = state.rails[state.activeRow];
    if (!activeRail || activeRail.cards.length === 0) return; // Empty rail handling

    if (state.activeCard >= activeRail.cards.length) state.activeCard = activeRail.cards.length - 1;
    if (state.activeCard < 0) state.activeCard = 0;

    // Set new focus
    const card = activeRail.cards[state.activeCard];
    card.classList.add('z-card-focused');

    // Scroll into view logic
    card.scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'center' });
}

async function handleInput(e) {
    if (state.showInfo) {
        if (e.key === 'Escape' || e.key === 'i') {
            document.getElementById('info-modal').classList.add('hidden');
            state.showInfo = false;
        }
        return;
    }

    switch (e.key) {
        case 'ArrowUp':
            state.activeRow--;
            // Reset column on row change? Or memory? Let's reset for simplicity/predictability
            state.activeCard = 0;
            updateFocus();
            break;
        case 'ArrowDown':
            state.activeRow++;
            state.activeCard = 0;
            updateFocus();
            break;
        case 'ArrowLeft':
            state.activeCard--;
            updateFocus();
            break;
        case 'ArrowRight':
            state.activeCard++;
            updateFocus();
            break;
        case 'Enter':
            await handleOpen();
            break;
        case 'i':
        case 'I':
            await showWhy();
            break;
    }
}

async function handleOpen() {
    const rail = state.rails[state.activeRow];
    const card = rail.cards[state.activeCard];
    if (!card) return;

    // Guard: Mystery or Opened
    if (card.classList.contains('z-card-mystery')) return; // Locked
    if (card.classList.contains('z-card-opened')) return; // Idempotent UI guard

    const offerId = card.dataset.id;
    const url = card.dataset.url;

    // Optimistic UI Update
    card.classList.remove('z-card-focused'); // temporary visual cue?
    card.classList.add('z-card-opened');

    // Open URL
    if (url) window.open(url, '_blank');

    // API Sync
    try {
        const res = await fetch(`/api/open/${offerId}`, { method: 'POST' });
        const data = await res.json();

        // Update Hero
        if (data.state && data.state.hero) {
            heroValueDisplay.innerText = "$" + data.state.hero.collection_value.toFixed(2);
        }

        // Use Option 1: Reload to reflect move to history?
        // User suggested: "Reload state after open ... Replace innerHTML"
        // Let's do a full reload for robustness in this phase
        window.location.reload();

    } catch (e) {
        console.error("Open API Failed", e);
        // Revert optimistic update?
        card.classList.remove('z-card-opened');
    }
}

async function showWhy() {
    const rail = state.rails[state.activeRow];
    const card = rail.cards[state.activeCard];
    if (!card) return;

    const offerId = card.dataset.id;
    state.showInfo = true;
    infoModal.classList.remove('hidden');
    infoBody.innerHTML = "Accessing Signal Intelligence...";

    try {
        const res = await fetch(`/api/why/${offerId}`);
        const data = await res.json();
        infoBody.innerHTML = `
            <div><span style="color:#888;font-size:0.7rem;">SIGNAL ORIGIN</span><br>${data.title}</div>
            <div><span style="color:#888;font-size:0.7rem;">REASON</span><br><span style="color:#10b981">${data.reason}</span></div>
            <div><span style="color:#888;font-size:0.7rem;">CONFIDENCE</span><br>${data.confidence}</div>
        `;
    } catch (e) {
        infoBody.innerHTML = "Signal Lost.";
    }
}

// --- VERIFICATION HOOK ---
window.ZC_VERIFY = function () {
    console.group("ZeroCrate Verification");
    const checks = [
        { name: "Rails Exist", pass: state.rails.length >= 5 },
        { name: "Free Rail Populated", pass: state.rails[0] && state.rails[0].cards.length > 0 },
        { name: "Diagnostics Active", pass: diagJsStatus.innerText.includes('ON') }
    ];

    let allPass = true;
    checks.forEach(c => {
        console.log(`${c.pass ? '✅' : '❌'} ${c.name}`);
        if (!c.pass) allPass = false;
    });

    if (!allPass) {
        const msg = document.createElement('div');
        msg.style = "position:fixed;bottom:50px;right:10px;background:red;color:white;padding:10px;";
        msg.innerText = "VERIFICATION FAILED";
        document.body.appendChild(msg);
    } else {
        console.log("System Optimal.");
    }
    console.groupEnd();
    return allPass;
};

// Boot
document.addEventListener('DOMContentLoaded', init);
