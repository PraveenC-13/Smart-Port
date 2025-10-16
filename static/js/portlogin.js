<script>
    const form = document.getElementById('loginForm');
    const errorMsg = document.getElementById('error-msg');

    // Allowed users (hardcoded for now)
    const validUsers = [
        { username: "portadmin", password: "secure123" },
        { username: "manager1", password: "dock@456" }
    ];

    form.addEventListener('submit', function(e) {
        e.preventDefault(); // Prevent form from reloading the page

        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value.trim();

        // Check if user exists and password matches
        const authenticated = validUsers.some(user => 
            user.username === username && user.password === password
        );

        if (authenticated) {
            // Redirect to dashboard if credentials are valid
            window.location.href = "portoverview.html";
        } else {
            // Show error message if credentials are invalid
            errorMsg.textContent = "❌ Invalid username or password.";
            errorMsg.style.color = "red";
        }
    });
</script>
