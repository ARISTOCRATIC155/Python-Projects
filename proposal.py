import webbrowser
import os

partner = input("Enter her name: ")
your_name = input("Enter your name: ")

html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Proposal</title>
<style>
body {{
    margin: 0;
    background: linear-gradient(to top, #000000, #3a0ca3);
    color: white;
    font-family: Arial;
    text-align: center;
    overflow: hidden;
}}

h1 {{
    margin-top: 20%;
    font-size: 2.5em;
    padding: 0 10px;
}}

button {{
    padding: 12px 20px;
    font-size: 18px;
    margin: 10px;
    cursor: pointer;
    border: none;
    border-radius: 10px;
}}

#yes {{
    background: green;
    color: white;
}}

#no {{
    background: red;
    color: white;
}}

#buttons {{
    margin-top: 20px;
}}

#message {{
    margin-top: 10px;
    font-size: 18px;
    color: yellow;
    font-weight: bold;
}}

.heart {{
    position: absolute;
    color: pink;
    animation: float 6s linear infinite;
}}

@keyframes float {{
    from {{ transform: translateY(100vh); }}
    to {{ transform: translateY(-10vh); }}
}}

@media (max-width: 600px) {{
    h1 {{
        font-size: 1.8em;
        margin-top: 25%;
    }}

    button {{
        font-size: 16px;
        padding: 10px 15px;
    }}
}}
</style>
</head>

<body>

<h1 id="text"></h1>

<div id="buttons" style="display:none;">
    <button id="yes" onclick="yesClicked()">YES ❤️</button>
    <button id="no" onclick="noClicked()">NO 💔</button>
</div>

<div id="message"></div>

<script>
const intro = "From the moment I met you {partner}... my life changed forever.";
let i = 0;

function typeIntro() {{
    if (i < intro.length) {{
        document.getElementById("text").innerHTML += intro[i];
        i++;
        setTimeout(typeIntro, 50);
    }} else {{
        setTimeout(showProposal, 1000);
    }}
}}

// Floating hearts
setInterval(() => {{
    let heart = document.createElement("div");
    heart.className = "heart";
    heart.style.left = Math.random()*100 + "vw";
    heart.innerHTML = "❤️";
    document.body.appendChild(heart);
    setTimeout(() => heart.remove(), 6000);
}}, 300);

window.onload = function() {{
    typeIntro();
}};

function showProposal() {{
    document.getElementById("text").innerHTML = "💖 {partner}, Will You Be My Girlfriend? 💖";
    document.getElementById("buttons").style.display = "block";
}}

// YES clicked
function yesClicked() {{
    document.body.innerHTML = "<h1>🎉 You just made me the happiest person alive ❤️</h1><h2>- {your_name}</h2>";
}}

// NO clicked logic
let noCount = 0;
const messages = [
    "Are you sure? 😢",
    "Think again 💔",
    "You’re breaking my heart 😭",
    "This is not fair 🥺",
    "Please reconsider ❤️"
];

function noClicked() {{
    noCount++;
    const msg = document.getElementById("message");

    if(noCount <= 5) {{
        msg.innerHTML = messages[noCount - 1];
    }} else if(noCount === 6) {{
        msg.innerHTML = "💔😭 You’ve shattered my heart… but I’ll still love you forever 💔😭";
    }}
}}
</script>

</body>
</html>
"""

file_path = os.path.abspath("proposal.html")
with open(file_path, "w", encoding="utf-8") as f:
    f.write(html_content)

webbrowser.open("file://" + file_path)

print("💖 Proposal opened successfully!")