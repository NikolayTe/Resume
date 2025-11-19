document.querySelector('.mail-form').addEventListener('submit', async function(e) {
    e.preventDefault(); //  ВАЖНО! Отменяет перезагрузку браузера

    const form = this; 
    const email_input = form.querySelector('.mail-input'); 
    const button = form.querySelector('.mail-button'); 
    const success_message = form.querySelector('.mail-success-message'); 
    const email = email_input.value; 

    // Валидация email
    if (!email || !isValidEmail(email)) {
        alert('Пожалуйста, введите корректный email');
        return;
    }

    // Блокируем кнопку на время запроса
    button.disabled = true;
    button.textContent = 'Отправка...';

    try {
        // Замените URL на ваш реальный endpoint
        const response = await fetch('http://localhost:5002/api/send-resume', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                },
            body: JSON.stringify({ to: email })
        });
        
        if (response.ok) {
            // Показываю сообщение об успехе
            const result = await response.json();
            success_message.textContent = result.message;
            success_message.style.display = 'block';
            email_input.value = '';
            
            // Скрываю сообщение через несколько секунд
            setTimeout(() => {
                success_message.style.display = 'none';
            }, 5000);
        } else {
            throw new Error('Ошибка сервера');
        }
        
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при отправке. Попробуйте еще раз.');
    } finally {
        // Восстанавливаем кнопку
        button.disabled = false;
        button.textContent = 'Получить резюме';
    }

});

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

