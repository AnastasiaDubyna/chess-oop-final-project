(function main () {
    
    function renderForm() {
        const $container = $('.main-container');

        const $nameInput = $('<input/>', {
            type: 'text',
            placeholder: 'Enter your name...',
            name: 'username',
            class: 'username-input'
        });

        const $button = $('<button/>', {
            text: 'Send',
            role: 'submit',
            class: 'submit-button'
        });

        const $innerContainer = $('<div/>', {
            class: 'inner-container'
        });

        const $form = $('<form/>', {
            action: '/login',
            method: 'POST',
            class: 'login-form'
        });

        $innerContainer.append([
            $nameInput,
            $button
        ]);

        $form.append($innerContainer);

        $container.append($form);
    }

    renderForm();
})();