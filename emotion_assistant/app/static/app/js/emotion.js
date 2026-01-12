(async function(){
  const video = document.getElementById('video');
  const captureBtn = document.getElementById('captureBtn');
  const emotionResult = document.getElementById('emotionResult');
  if (!patientId) { captureBtn.disabled=true; return; }
  async function startCamera(){
    try {
      const stream = await navigator.mediaDevices.getUserMedia({video:true,audio:false});
      video.srcObject = stream;
    } catch(e){
      emotionResult.textContent='Camera access denied';
    }
  }
  function getCookie(name){ const v=document.cookie.match('(^|;) ?'+name+'=([^;]*)(;|$)'); return v? v[2]: null; }
  captureBtn.onclick = async () => {
    emotionResult.textContent='Capturing...';
    const canvas=document.createElement('canvas'); canvas.width=video.videoWidth||480; canvas.height=video.videoHeight||360;
    canvas.getContext('2d').drawImage(video,0,0,canvas.width,canvas.height);
    const dataUrl = canvas.toDataURL('image/jpeg',0.9);
    emotionResult.textContent='Analyzing...';
    try {
      const form = new URLSearchParams(); form.append('image', dataUrl);
      const resp = await fetch(`/patient/${patientId}/analyze/`, {method:'POST', headers:{'X-CSRFToken': getCookie('csrftoken'), 'Content-Type':'application/x-www-form-urlencoded'}, body: form.toString()});
      const js = await resp.json();
      if (js.emotion) emotionResult.textContent = `Detected: ${js.emotion}`;
      else emotionResult.textContent = js.error || 'No result';
      setTimeout(()=> location.reload(), 800);
    } catch(e){ emotionResult.textContent='Server error'; console.error(e); }
  };
  await startCamera();
})();
