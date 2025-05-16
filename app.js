const ws = new WebSocket(`ws://${location.host}/ws/chat`);
const chat = document.getElementById("chat");
const inp  = document.getElementById("input");
const send = document.getElementById("sendBtn");
const clr  = document.getElementById("clearBtn");
const imgB = document.getElementById("imgBtn");
const codeB= document.getElementById("codeBtn");
const pdfB = document.getElementById("pdfBtn");
const themeB = document.getElementById("themeBtn");
const iconL = document.getElementById("iconLight");
const iconD = document.getElementById("iconDark");
let pendingDiv = null;

// Tema
function setTheme(d){
  document.documentElement.classList.toggle("dark",d);
  iconL.classList.toggle("hidden",!d);
  iconD.classList.toggle("hidden",d);
  localStorage.theme = d?"dark":"light";
}
themeB.onclick = ()=>{
  setTheme(!(localStorage.theme=="dark" || (window.matchMedia("(prefers-color-scheme:dark)").matches && !localStorage.theme)));
};
setTheme(localStorage.theme=="dark" || (!localStorage.theme && window.matchMedia("(prefers-color-scheme:dark)").matches));

// Limpiar
clr.onclick = ()=> chat.innerHTML="";

// Botones rápido
imgB.onclick  = ()=> inp.value="/imagen ";
codeB.onclick = ()=> inp.value="/codigo ";
pdfB.onclick  = ()=> inp.value="/pdf ";

// Enviar
send.onclick = sendMsg;
inp.addEventListener("keydown",e=>{
  if(e.key=="Enter"&&!e.shiftKey){ e.preventDefault(); sendMsg(); }
});

// enviar mensaje
function sendMsg(){
  const t = inp.value.trim();
  if(!t) return;
  append("user",t);
  if(t.startsWith("/imagen")){
    pendingDiv = createPending("🖼 Generando imagen…");
  } else pendingDiv = null;
  ws.send(JSON.stringify({prompt:t}));
  inp.value="";
}

// WebSocket
ws.onmessage = e=>{
  const d = JSON.parse(e.data);
  if(d.type=="image" && pendingDiv){
    pendingDiv.innerHTML="";
    const box=document.createElement("div");
    box.className="image-box";
    const img=new Image();
    img.src=d.url;
    img.onload=()=>chat.scrollTop=chat.scrollHeight;
    box.appendChild(img);
    pendingDiv.appendChild(box);
    pendingDiv=null;
    return;
  }
  if(d.type=="error"){
    if(pendingDiv){ pendingDiv.textContent=d.message; pendingDiv.style.color="tomato"; pendingDiv=null; }
    else append("assistant",d.message,"tomato");
    return;
  }
  // streaming y full
  if(d.stream){
    pendingDiv = pendingDiv || createPending();
    pendingDiv.textContent += d.content;
    chat.scrollTop=chat.scrollHeight;
    return;
  }
  append(d.role,d.content);
};

// helpers
function append(role, txt, color){
  const m = document.createElement("div");
  m.className = "msg "+role;
  if(color) m.style.color=color;
  m.innerHTML = txt.replace(/\n/g,"<br/>");
  chat.appendChild(m);
  chat.scrollTop = chat.scrollHeight;
}
function createPending(label=""){ 
  const m = document.createElement("div");
  m.className="msg assistant flex items-center";
  m.innerHTML = `<div class="spinner"></div><span class="ml-2">${label}</span>`;
  chat.appendChild(m);
  chat.scrollTop=chat.scrollHeight;
  return m;
}
