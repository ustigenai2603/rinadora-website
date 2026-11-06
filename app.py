
import os, json
from pathlib import Path
from flask import Flask, request, jsonify, render_template_string, send_from_directory
from google import genai

app = Flask(__name__)
ASSETS = Path("/content/assets")
WA = "6282285264517"
IG = "https://www.instagram.com/rinadora.id/"
PRODUCTS = [
 {"id":"mentai","name":"Dimsum Signature Saus Mentai","price":25000,"image":"produk_mentai.jpg"},
 {"id":"teriyaki","name":"Dimsum Signature Saus Teriyaki","price":25000,"image":"produk_teriyaki.jpg"},
 {"id":"padang","name":"Dimsum Signature Saus Padang","price":25000,"image":"produk_padang.jpg"},
 {"id":"blackpepper","name":"Dimsum Signature Saus Black Pepper","price":25000,"image":"produk_blackpepper.jpg"},
 {"id":"mix","name":"Mix Box (Semua Rasa)","price":90000,"image":"banner_mix_box.jpg"}
]
SYSTEM = (
 "Kamu adalah RINADORA AI, asisten pelanggan dimsum yang hangat, santai, sopan, dan ringkas. "
 "Jawab dalam bahasa Indonesia. Menu resmi: Mentai Rp25.000, Teriyaki Rp25.000, Padang Rp25.000, "
 "Black Pepper Rp25.000, Mix Box semua rasa Rp90.000. WhatsApp https://wa.me/6282285264517. "
 "Instagram https://www.instagram.com/rinadora.id/. Jangan mengarang stok, alamat, jam buka, ongkir, "
 "bahan, alergi, sertifikasi, atau metode pembayaran. Untuk info yang belum diketahui, arahkan ke WhatsApp."
)

PAGE = r'''<!doctype html><html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>RINADORA</title>
<style>
:root{--cream:#f7f0e5;--paper:#eadcc8;--brown:#4b3025;--gold:#b38a55;--ink:#38251e;--muted:#876e5e;--white:#fffaf3}
*{box-sizing:border-box}body{margin:0;background:var(--cream);color:var(--ink);font-family:Arial,sans-serif}.wrap{max-width:1120px;margin:auto;padding:24px}
header{display:flex;align-items:center;justify-content:space-between;padding:10px 0 24px}.brand{display:flex;align-items:center;gap:14px}.brand img{width:60px;height:60px;object-fit:cover;border-radius:50%}.brand h1{font:bold 28px Georgia;color:var(--brown);margin:0}.brand p{font-size:11px;letter-spacing:1px;color:var(--muted);margin:4px 0}nav a{margin-left:18px;text-decoration:none;font-weight:bold;font-size:13px}
.hero{display:grid;grid-template-columns:1fr 1fr;background:var(--paper);border-radius:22px;overflow:hidden}.hero-copy{padding:42px;align-self:center}.eyebrow{color:var(--gold);font-size:12px;font-weight:bold;letter-spacing:2px}h2{font:bold 38px Georgia;color:var(--brown);margin:12px 0}.hero p{line-height:1.7;color:#755c4d}.hero img{width:100%;height:330px;object-fit:cover}
.btn{border:0;border-radius:28px;background:var(--brown);color:white;padding:13px 20px;font-weight:bold;cursor:pointer;text-decoration:none;display:inline-block}.btn:hover{background:#76533b}.section{padding:45px 0 12px}.section-title{text-align:center;margin-bottom:22px}.section-title h2{font-size:31px}.section-title p{color:var(--muted)}
.products{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.product{background:var(--white);border:1px solid #e3d1bb;border-radius:17px;overflow:hidden}.product img{width:100%;height:200px;object-fit:cover}.product-body{padding:16px}.product h3{font:bold 19px Georgia;color:var(--brown);margin:0}.price{font-weight:bold;margin:12px 0}
.cart,.help{background:var(--paper);border-radius:20px;padding:26px;margin-top:40px}.cart h2,.help h2{font-size:28px}.cart-row{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #d6c2aa;padding:12px 0;gap:10px}.qty{display:flex;align-items:center;gap:9px}.qty button{border:0;border-radius:50%;width:29px;height:29px;background:var(--brown);color:white;cursor:pointer}.total{font-size:21px;font-weight:bold;margin:20px 0}.fields{display:grid;grid-template-columns:1fr 1fr;gap:10px}.fields input,.fields textarea{padding:13px;border:1px solid #cdb69b;border-radius:10px;background:white;color:var(--ink);width:100%}.fields textarea{grid-column:1/-1}
.gallery{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.gallery img{width:100%;height:160px;object-fit:cover;border-radius:13px}.help{text-align:center;padding:32px}.help .btn{margin:7px}footer{text-align:center;padding:25px;color:var(--muted);font-size:13px}
#ai-launch{position:fixed;right:22px;bottom:20px;z-index:10;box-shadow:0 7px 20px #0003}#ai-panel{display:none;position:fixed;right:22px;bottom:82px;width:min(410px,calc(100vw - 28px));height:min(570px,calc(100vh - 110px));z-index:20;background:var(--white);border:1px solid #d8c4aa;border-radius:18px;box-shadow:0 15px 45px #0004;overflow:hidden;flex-direction:column}.ai-head{background:var(--brown);color:white;padding:16px;display:flex;justify-content:space-between;align-items:center}.ai-head strong{font:bold 19px Georgia}.ai-head button{background:none;border:0;color:white;font-size:24px;cursor:pointer}.ai-sub{font-size:12px;color:#e9d8c5;margin-top:5px}.messages{padding:15px;overflow:auto;flex:1}.bubble{padding:11px 13px;border-radius:13px;margin-bottom:11px;white-space:pre-wrap;line-height:1.5;font-size:14px}.bot{background:#f0e4d5;margin-right:22px}.user{background:#dedede;margin-left:22px}.ai-form{display:flex;gap:8px;padding:12px;border-top:1px solid #e6d8c7}.ai-form input{min-width:0;flex:1;padding:12px;border:1px solid #c9ad8c;border-radius:10px}.ai-form button{border:0;background:var(--brown);color:white;border-radius:10px;padding:0 16px;font-weight:bold}.small{font-size:11px;color:var(--muted);padding:0 13px 10px}
@media(max-width:720px){.wrap{padding:15px}.hero{grid-template-columns:1fr}.hero-copy{padding:26px}.hero img{height:230px}.products{grid-template-columns:repeat(2,1fr);gap:11px}.product img{height:145px}.product-body{padding:11px}.product h3{font-size:16px}.gallery{grid-template-columns:repeat(2,1fr)}nav{display:none}.fields{grid-template-columns:1fr}.fields textarea{grid-column:auto}h2{font-size:31px}}@media(max-width:420px){.products{grid-template-columns:1fr}.product img{height:190px}}
</style></head><body><div class="wrap">
<header><div class="brand"><img src="/assets/logo_rinadora_area.jpg" onerror="this.style.display='none'"><div><h1>RINADORA</h1><p>DIMSUM & SIGNATURE SAUCES</p></div></div><nav><a href="#menu">MENU</a><a href="#cart">KERANJANG</a><a href="#contact">KONTAK</a></nav></header>
<section class="hero"><div class="hero-copy"><span class="eyebrow">REAL DIMSUM. MORE FLAVORS.</span><h2>More Flavors,<br>Same Love.</h2><p>Nikmati dimsum pilihan dengan signature sauces khas RINADORA. Pilih rasa favoritmu dan pesan dengan mudah.</p><a class="btn" href="#menu">PILIH MENU</a></div><img src="/assets/banner_mentai_closeup.jpg" alt="Dimsum RINADORA"></section>
<section class="section" id="menu"><div class="section-title"><span class="eyebrow">OUR SIGNATURE MENU</span><h2>Temukan Rasa Favoritmu</h2><p>Signature dimsum untuk setiap suasana.</p></div><div class="products">{% for p in products %}<article class="product"><img src="/assets/{{p.image}}" alt="{{p.name}}"><div class="product-body"><h3>{{p.name}}</h3><div class="price">{{money(p.price)}}</div><button class="btn" data-add="{{p.id}}">＋ Tambah ke Keranjang</button></div></article>{% endfor %}</div></section>
<section class="cart" id="cart"><h2>🛒 Keranjang Belanja</h2><div id="cart-items">Keranjang masih kosong. Yuk pilih menu favoritmu!</div><div class="total" id="cart-total">Total item: 0 · Total belanja: Rp 0</div><h3>Data Pemesan</h3><div class="fields"><input id="cust-name" placeholder="Nama lengkap"><input id="cust-phone" placeholder="Nomor WhatsApp"><textarea id="cust-address" rows="2" placeholder="Alamat pengiriman"></textarea><textarea id="cust-note" rows="2" placeholder="Catatan pesanan (opsional)"></textarea></div><br><button class="btn" id="checkout">Checkout via WhatsApp</button></section>
<section class="section"><div class="section-title"><span class="eyebrow">RINADORA MOMENTS</span><h2>Our Brand & Moments</h2></div><div class="gallery">{% for img in gallery %}<img src="/assets/{{img}}" alt="RINADORA">{% endfor %}</div></section>
<section class="help" id="contact"><h2>Need Help, Dear?</h2><p>Ada pertanyaan atau mau pesan? Customer Service RINADORA siap membantu.</p><a class="btn" href="https://wa.me/{{wa}}" target="_blank">WHATSAPP · CUSTOMER SERVICE</a><a class="btn" style="background:white;color:#4b3025;border:1px solid #cdb69b" href="{{ig}}" target="_blank">INSTAGRAM · @rinadora.id</a></section><footer>© RINADORA · Dimsum & Signature Sauces</footer></div>
<button class="btn" id="ai-launch">✦ Chat RINADORA AI</button><div id="ai-panel"><div class="ai-head"><div><strong>✦ RINADORA AI Assistant</strong><div class="ai-sub">Teman ngobrol untuk memilih dimsum favoritmu 🤎</div></div><button id="ai-close">×</button></div><div class="messages" id="messages"><div class="bubble bot">Halo, dear! 👋 Selamat datang di RINADORA. Aku siap bantu memilih dimsum favoritmu. Mau tanya apa hari ini? 🤎</div></div><form class="ai-form" id="ai-form"><input id="ai-input" maxlength="1000" placeholder="Tanya menu, rasa, harga, atau cara pesan..." autocomplete="off" required><button id="ai-send">Kirim</button></form><div class="small">Untuk konfirmasi pesanan, hubungi WhatsApp RINADORA.</div></div>
<script>
const PRODUCTS={{products_json|safe}},WA="{{wa}}",money=n=>"Rp "+Number(n).toLocaleString("id-ID");let cart={};try{cart=JSON.parse(localStorage.getItem("rinadora_cart")||"{}")||{}}catch(e){}
function save(){localStorage.setItem("rinadora_cart",JSON.stringify(cart))}
function render(){let ids=Object.keys(cart).filter(id=>cart[id]>0),box=document.getElementById("cart-items");box.innerHTML=ids.length?ids.map(id=>{let p=PRODUCTS.find(x=>x.id===id);return `<div class="cart-row"><div><b>${p.name}</b><br><small>${money(p.price)} × ${cart[id]}</small></div><div class="qty"><button data-minus="${id}">−</button><b>${cart[id]}</b><button data-plus="${id}">+</button></div></div>`}).join(""):"Keranjang masih kosong. Yuk pilih menu favoritmu!";let count=ids.reduce((s,id)=>s+cart[id],0),total=ids.reduce((s,id)=>s+PRODUCTS.find(p=>p.id===id).price*cart[id],0);document.getElementById("cart-total").textContent=`Total item: ${count} · Total belanja: ${money(total)}`}
document.addEventListener("click",e=>{let a=e.target.closest("[data-add]"),p=e.target.closest("[data-plus]"),m=e.target.closest("[data-minus]");if(a){let id=a.dataset.add;cart[id]=(cart[id]||0)+1;save();render();a.textContent="✓ Ditambahkan";setTimeout(()=>a.textContent="＋ Tambah ke Keranjang",700)}if(p){let id=p.dataset.plus;cart[id]=(cart[id]||0)+1;save();render()}if(m){let id=m.dataset.minus;cart[id]=(cart[id]||0)-1;if(cart[id]<=0)delete cart[id];save();render()}});
document.getElementById("checkout").onclick=()=>{let ids=Object.keys(cart).filter(id=>cart[id]>0);if(!ids.length)return alert("Keranjang masih kosong.");let name=document.getElementById("cust-name").value.trim(),phone=document.getElementById("cust-phone").value.trim(),address=document.getElementById("cust-address").value.trim(),note=document.getElementById("cust-note").value.trim();if(!name||!phone||!address)return alert("Lengkapi nama, nomor WhatsApp, dan alamat.");let total=ids.reduce((s,id)=>s+PRODUCTS.find(p=>p.id===id).price*cart[id],0),lines=ids.map(id=>{let p=PRODUCTS.find(x=>x.id===id);return `- ${p.name} x ${cart[id]} = ${money(p.price*cart[id])}`}),msg=["Halo RINADORA! Saya ingin memesan.",`Nama: ${name}`,`WhatsApp: ${phone}`,`Alamat: ${address}`,"DETAIL PESANAN",...lines,`TOTAL: ${money(total)}`,`Catatan: ${note||"-"}`].join("\\n");window.open(`https://wa.me/${WA}?text=${encodeURIComponent(msg)}`,"_blank")};render();
const panel=document.getElementById("ai-panel");document.getElementById("ai-launch").onclick=()=>{panel.style.display="flex";document.getElementById("ai-input").focus()};document.getElementById("ai-close").onclick=()=>panel.style.display="none";
function bubble(t,role){let d=document.createElement("div");d.className="bubble "+(role==="user"?"user":"bot");d.textContent=t;let m=document.getElementById("messages");m.appendChild(d);m.scrollTop=m.scrollHeight;return d}
document.getElementById("ai-form").addEventListener("submit",async e=>{e.preventDefault();let input=document.getElementById("ai-input"),btn=document.getElementById("ai-send"),msg=input.value.trim();if(!msg)return;bubble(msg,"user");input.value="";btn.disabled=true;btn.textContent="...";let pending=bubble("Sebentar ya, aku sedang menyiapkan jawaban 🤎","bot");try{let r=await fetch("/api/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:msg})}),d=await r.json();pending.textContent=d.reply||"Maaf, aku belum bisa menjawab."}catch(err){pending.textContent="Koneksi bermasalah. Coba lagi atau hubungi https://wa.me/"+WA}finally{btn.disabled=false;btn.textContent="Kirim";input.focus()}});
</script></body></html>'''

@app.route("/")
def home():
    gallery=["outlet_rinadora.jpg","paper_bag_produk.jpg","saus_signature.jpg","brand_staff_rinadora.jpg","kemasan_rinadora.jpg","branding_rinadora.jpg","mix_varian_dimsum.jpg","banner_mix_box.jpg"]
    return render_template_string(PAGE,products=PRODUCTS,gallery=gallery,wa=WA,ig=IG,money=lambda n:"Rp "+f"{n:,}".replace(",","."),products_json=json.dumps(PRODUCTS,ensure_ascii=False))

@app.route("/assets/<path:name>")
def assets(name):
    return send_from_directory(ASSETS,name)

@app.route("/api/chat",methods=["POST"])
def chat():
    message=str((request.get_json(silent=True) or {}).get("message","")).strip()
    if not message:return jsonify(reply="Tulis pertanyaanmu dulu ya 🤎"),400
    key=os.environ.get("GEMINI_API_KEY","").strip()
    if not key:return jsonify(reply="Gemini API Key belum dimasukkan. Hubungi WhatsApp RINADORA: https://wa.me/"+WA),503
    try:
        client=genai.Client(api_key=key)
        result=client.models.generate_content(model="gemini-3.5-flash-lite",contents=SYSTEM+"\\n\\nPertanyaan pelanggan: "+message)
        return jsonify(reply=getattr(result,"text",None) or "Maaf, aku belum mendapat jawaban. Coba lagi ya 🤎")
    except Exception as exc:
        print("RINADORA GEMINI ERROR:",repr(exc),flush=True)
        return jsonify(reply="Maaf, AI sedang mengalami kendala. Coba lagi atau hubungi WhatsApp RINADORA: https://wa.me/"+WA),502

if __name__=="__main__":
    if not ASSETS.exists(): print("PERINGATAN: folder /content/assets belum ditemukan.")
    app.run(host="0.0.0.0",port=5000,debug=False)
