async function getRecs() {
    const userId = document.getElementById("user_id").value;

    const res = await fetch("/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: parseInt(userId) })
    });

    const data = await res.json();
    const ul = document.getElementById("result");
    ul.innerHTML = "";

    data.recommendations.forEach(m => {
        const li = document.createElement("li");
        li.textContent = m;
        ul.appendChild(li);
    });
}
