import webbrowser
import os

name = input("Enter the birthday person's name: ")

html_content = f"""
<!DOCTYPE html>
<html>
<head>
<title>Happy Birthday</title>
<style>
    body {{
        margin: 0;
        background: linear-gradient(to top, #000000, #1a1a40);
        overflow: hidden;
        text-align: center;
        font-family: Arial;
        color: white;
    }}

    h1 {{
        margin-top: 15%;
        font-size: 3em;
        animation: glow 1s infinite alternate;
        z-index: 2;
        position: relative;
    }}

    @keyframes glow {{
        from {{ text-shadow: 0 0 10px yellow; }}
        to {{ text-shadow: 0 0 25px magenta; }}
    }}

    canvas {{
        position: absolute;
        top: 0;
        left: 0;
        z-index: 0;
    }}

    .balloon {{
        position: absolute;
        width: 40px;
        height: 50px;
        border-radius: 50%;
        animation: float 8s infinite ease-in;
        z-index: 1;
    }}

    .balloon::after {{
        content: '';
        position: absolute;
        width: 2px;
        height: 20px;
        background: white;
        top: 50px;
        left: 19px;
    }}

    @keyframes float {{
        from {{ transform: translateY(100vh); }}
        to {{ transform: translateY(-10vh); }}
    }}

    .cake {{
        position: absolute;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        font-size: 60px;
        z-index: 2;
    }}
</style>
</head>

<body>

<h1 id="message"></h1>
<div class="cake">🎂</div>
<canvas id="canvas"></canvas>

<script>
// FIX: store text first
const fullText = "🎉 HAPPY BIRTHDAY {name.upper()} 🎉";
const message = document.getElementById("message");

// TYPEWRITER EFFECT (FIXED)
let i = 0;
function typeText() {{
    if (i < fullText.length) {{
        message.innerHTML += fullText.charAt(i);
        i++;
        setTimeout(typeText, 80);
    }}
}}

// Start AFTER page loads
window.onload = function() {{
    typeText();
}};

// 🎈 Balloons
for (let i = 0; i < 20; i++) {{
    let b = document.createElement("div");
    b.className = "balloon";
    b.style.left = Math.random() * window.innerWidth + "px";
    b.style.background = "hsl(" + Math.random()*360 + ",100%,50%)";
    b.style.animationDuration = (5 + Math.random()*5) + "s";
    document.body.appendChild(b);
}}

// 🎆 Fireworks
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

let particles = [];

function fireworks() {{
    for (let i = 0; i < 60; i++) {{
        particles.push({{
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height / 2,
            dx: (Math.random() - 0.5) * 6,
            dy: (Math.random() - 0.5) * 6,
            life: 100
        }});
    }}
}}

setInterval(fireworks, 800);

function animate() {{
    requestAnimationFrame(animate);
    ctx.fillStyle = "rgba(0,0,0,0.2)";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    particles.forEach((p, index) => {{
        p.x += p.dx;
        p.y += p.dy;
        p.life--;

        ctx.fillStyle = "hsl(" + Math.random()*360 + ",100%,50%)";
        ctx.fillRect(p.x, p.y, 3, 3);

        if (p.life <= 0) particles.splice(index, 1);
    }});
}}

animate();
</script>

</body>
</html>
"""

file_path = os.path.abspath("birthday_animation.html")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(html_content)

webbrowser.open("file://" + file_path)

print("🎉 Animation opened successfully!")