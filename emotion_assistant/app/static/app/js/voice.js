(function(){
  const startBtn = document.getElementById('startVoiceBtn');
  const stopBtn = document.getElementById('stopVoiceBtn');
  const transcriptBox = document.getElementById('transcriptBox');
  const assistantReply = document.getElementById('assistantReply');
  if (!patientId) { if (startBtn) startBtn.disabled=true; return; }
  window.SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!window.SpeechRecognition){ if (startBtn) startBtn.disabled=true; return; }
  const rec = new window.SpeechRecognition();
  rec.interimResults = true; rec.continuous=true; rec.lang='en-US';
  let final = '';
  rec.onresult = (e) => {
    let interim=''; for (let i=e.resultIndex;i<e.results.length;i++){ if (e.results[i].isFinal) final += e.results[i][0].transcript; else interim += e.results[i][0].transcript; }
    transcriptBox.textContent = final + ' ' + interim;
  };
  rec.onend = ()=> { stopBtn.disabled=true; startBtn.disabled=false; };
  startBtn.onclick = ()=>{ final=''; assistantReply.textContent=''; rec.start(); startBtn.disabled=true; stopBtn.disabled=false; };
  stopBtn.onclick = ()=>{ rec.stop(); stopBtn.disabled=true; startBtn.disabled=false; if (final.trim()){ send(final.trim()); } };
  function getCookie(name){ const v=document.cookie.match('(^|;) ?'+name+'=([^;]*)(;|$)'); return v? v[2]: null; }
  function send(text){
    const f=new FormData(); f.append('text', text); f.append('patient_id', patientId);
    fetch('/voice_assistant/', {method:'POST', headers:{'X-CSRFToken': getCookie('csrftoken')}, body: f})
    .then(r=>r.json()).then(js=>{ if (js.reply){ assistantReply.textContent=js.reply; const u=new SpeechSynthesisUtterance(js.reply); speechSynthesis.speak(u); } else assistantReply.textContent = js.error || 'No reply'; })
    .catch(e=>{ assistantReply.textContent='Error contacting server'; console.error(e); });
  }
})();
