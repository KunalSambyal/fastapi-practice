const box = document.getElementById("box");
const btn = document.getElementById("btn");

async function get_data() {
    const response = await fetch("http://127.0.0.1:8000/students");
    const data = await response.json();
    return data;
}

btn.addEventListener("click", async () => {
    const data = await get_data();
    box.textContent = JSON.stringify(data);
});
