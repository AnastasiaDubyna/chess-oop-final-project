(function main () {

    function checkReadiness() {
        return fetch('/check-readiness')
        .then(response => response.json());
    }

    function redirectIfReady() {
        checkReadiness().then(({ isReady }) => {
            if (isReady) {
                window.location.replace(`${window.location.origin}/`);

            }
        });
    }

    function checkReadinessPolling() {
        redirectIfReady();
        setInterval(() => {
            redirectIfReady();
        }, 3000);
    }

    checkReadinessPolling();
})();