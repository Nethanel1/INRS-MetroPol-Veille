document.addEventListener('DOMContentLoaded', () => {
    const accordionContainer = document.getElementById('metropolAccordion');
    const loader = document.getElementById('loader');
    const searchInput = document.getElementById('searchInput');
    const ficheCountSpan = document.getElementById('ficheCount');
    const lastUpdatedSpan = document.getElementById('lastUpdated');
    const noResultsP = document.getElementById('noResults');

    let allFiches = [];

    fetch('data.json')
        .then(response => {
            if (!response.ok) {
                throw new Error(`Le fichier data.json n'a pas pu être chargé : ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            loader.style.display = 'none';
            allFiches = data.data;
            
            // Affichage des métadonnées
            ficheCountSpan.textContent = `${data.fiches_count} fiches répertoriées`;
            const updateDate = new Date(data.last_updated_utc);
            lastUpdatedSpan.textContent = `Dernière mise à jour : ${updateDate.toLocaleString('fr-FR')}`;

            displayFiches(allFiches);
        })
        .catch(error => {
            loader.innerHTML = `<p class="text-danger"><strong>Erreur :</strong> ${error.message}</p><p>Le fichier de données n'a pas pu être trouvé. Veuillez lancer le script de scraping pour le générer.</p>`;
            console.error('Erreur lors du chargement des données:', error);
        });

    searchInput.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();
        const filteredFiches = allFiches.filter(fiche => 
            fiche.title.toLowerCase().includes(searchTerm) || 
            fiche.id.toLowerCase().includes(searchTerm)
        );
        displayFiches(filteredFiches);
        noResultsP.classList.toggle('d-none', filteredFiches.length > 0);
    });

    function displayFiches(fiches) {
        accordionContainer.innerHTML = '';
        fiches.forEach((fiche, index) => {
            let historyHtml = '<ul>';
            if (fiche.history && fiche.history.length > 0) {
                fiche.history.forEach(item => {
                    historyHtml += `<li><strong>Version ${item.version}</strong> (${item.date}): ${item.modification}</li>`;
                });
            } else {
                historyHtml += '<li>Aucun historique disponible.</li>';
            }
            historyHtml += '</ul>';

            const accordionItem = `
                <div class="accordion-item">
                    <h2 class="accordion-header" id="heading-${index}">
                        <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse-${index}" aria-expanded="false" aria-controls="collapse-${index}">
                            <strong>${fiche.title}</strong>&nbsp; <small class="text-muted">(${fiche.id})</small>
                        </button>
                    </h2>
                    <div id="collapse-${index}" class="accordion-collapse collapse" aria-labelledby="heading-${index}" data-bs-parent="#metropolAccordion">
                        <div class="accordion-body">
                            <p><strong>Historique des versions :</strong></p>
                            ${historyHtml}
                            <a href="${fiche.url}" target="_blank" class="btn btn-sm btn-outline-primary mt-2">
                                Voir la fiche sur inrs.fr <i class="bi bi-box-arrow-up-right"></i>
                            </a>
                        </div>
                    </div>
                </div>
            `;
            accordionContainer.innerHTML += accordionItem;
        });
    }
});
