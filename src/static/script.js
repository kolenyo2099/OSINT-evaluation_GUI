document.getElementById('searchForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const searchTerm = document.getElementById('searchTerm').value;

    document.getElementById('loading').style.display = 'block';
    document.getElementById('results').innerHTML = '';

    fetch('/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            'searchTerm': searchTerm
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Response data:', data); // Log raw data for debugging
        document.getElementById('loading').style.display = 'none';
        if (data.status === 'success') {
            renderResults(data.result);
        } else {
            document.getElementById('results').innerText = 'Error: ' + data.message;
        }
    })
    .catch(error => {
        console.error('Fetch error:', error);
        document.getElementById('loading').style.display = 'none';
        document.getElementById('results').innerText = 'An error occurred. Please try again.';
    });
});

document.getElementById('resetButton').addEventListener('click', function() {
    document.getElementById('results').innerHTML = '';
    document.getElementById('searchTerm').value = '';
    document.getElementById('loading').style.display = 'none';
});

function renderResults(results) {
    let resultsContainer = '';

    // Display trustworthiness
    if (results.trustworthiness !== undefined) {
        resultsContainer += `<h2>Trustworthiness: ${results.trustworthiness}</h2>`;
    }

    // Display summary
    if (results.summary) {
        resultsContainer += `<h3>Summary</h3><p>${results.summary}</p>`;
    }

    // Display improvements
    if (results.improvements) {
        resultsContainer += `<h3>Improvements</h3><p>${results.improvements}</p>`;
    }

    // Display scores in a table
    if (results.scores) {
        let totalScore = 0;
        let table = '<table><thead><tr><th>Criteria</th><th>Aspect</th><th>Score</th><th>Reasoning</th></tr></thead><tbody>';

        for (const category in results.scores) {
            for (const aspect in results.scores[category]) {
                const score = results.scores[category][aspect].score;
                const reasoning = results.scores[category][aspect].reasoning;
                totalScore += score;
                table += `<tr><td>${category}</td><td>${aspect}</td><td>${score}</td><td>${reasoning}</td></tr>`;
            }
        }

        table += `<tr><td colspan="2"><strong>Total Score</strong></td><td colspan="2">${totalScore}</td></tr>`;
        table += '</tbody></table>';

        resultsContainer += table;
    } else {
        resultsContainer += '<p>No scores available</p>';
    }

    document.getElementById('results').innerHTML = resultsContainer;
}
