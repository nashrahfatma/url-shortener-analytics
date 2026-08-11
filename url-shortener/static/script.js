function showToast(message, type = "success") {
    const toast = document.getElementById("toast");
    toast.textContent = message;
    toast.className = `toast show ${type}`;

    setTimeout(() => {
        toast.classList.remove("show");
    }, 2600);
}

const form = document.getElementById("shorten-form");
if (form) {
    form.addEventListener("submit", async function (e) {
        e.preventDefault();

        const input = document.getElementById("original-url");
        const url = input.value.trim();
        const button = form.querySelector("button");
        const originalButtonHTML = button.innerHTML;

        button.disabled = true;
        button.innerHTML = "<span>Shortening…</span>";

        try {
            const response = await fetch("/api/shorten", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ original_url: url }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Something went wrong");
            }

            const data = await response.json();
            showToast(`Short link created: ${data.short_code}`, "success");
            input.value = "";

            setTimeout(() => window.location.reload(), 900);
        } catch (err) {
            showToast(err.message, "error");
            button.disabled = false;
            button.innerHTML = originalButtonHTML;
        }
    });
}

document.querySelectorAll(".copy-btn").forEach((btn) => {
    btn.addEventListener("click", async () => {
        const url = btn.getAttribute("data-url");
        try {
            await navigator.clipboard.writeText(url);
            showToast("Link copied to clipboard", "success");
        } catch (err) {
            showToast("Couldn't copy — copy it manually", "error");
        }
    });
});