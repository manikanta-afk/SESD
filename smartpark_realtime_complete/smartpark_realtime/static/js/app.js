(() => {
 const $=id=>document.getElementById(id); const state={lot:null,slots:[],selected:null,timer:null};
 const toast=(msg)=>{const el=$('toast');el.textContent=msg;el.classList.add('show');setTimeout(()=>el.classList.remove('show'),3200)};
 const params=()=>({date:$('bookingDate').value,start:$('startTime').value,hours:$('duration').value});
 const selectedLot=()=>$('lotSelect').value;
 function render(slots){state.slots=slots;const grid=$('slots');grid.innerHTML='';let available=0;
  slots.forEach(s=>{if(s.available)available++;const b=document.createElement('button');b.className='slot'+(s.available?'':' occupied');b.disabled=!s.available;b.innerHTML=`${s.number}<small>${s.available?'Available':'Reserved'}</small>`;b.addEventListener('click',()=>openBooking(s));grid.appendChild(b)});
  $('availableCount').textContent=available;$('syncStatus').textContent=`Live status synced at ${new Date().toLocaleTimeString()} · refreshes every 4 seconds`;
 }
 async function refresh(){if(!selectedLot())return;try{const p=new URLSearchParams(params());const res=await fetch(`/api/availability/${selectedLot()}?${p}`,{cache:'no-store'});if(!res.ok)throw new Error('Could not load availability');const data=await res.json();render(data.slots)}catch(e){$('syncStatus').textContent='Connection interrupted. Retrying…'}}
 function openBooking(slot){state.selected=slot;$('chosenText').textContent=`Slot ${slot.number} · ${$('lotSelect').selectedOptions[0].textContent} · ₹${$('lotSelect').selectedOptions[0].dataset.rate}/hour`;$('vehicle').value='';updateTotal();$('modal').classList.add('show')}
 function updateTotal(){const rate=Number($('lotSelect').selectedOptions[0]?.dataset.rate||0);$('estimated').textContent=`₹${rate*Number($('duration').value)}`}
 async function book(){if(!state.selected)return;const btn=$('confirmBtn');btn.disabled=true;btn.textContent='Saving reservation…';try{const res=await fetch('/api/bookings',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({...params(),slot_id:state.selected.id,vehicle_number:$('vehicle').value})});const data=await res.json();if(!res.ok||!data.ok)throw new Error(data.message||'Booking failed');$('modal').classList.remove('show');toast(`Booking confirmed · ${data.booking.code}`);await refresh();setTimeout(()=>location.href=`/booking/${data.booking.code}`,850)}catch(e){toast(e.message);await refresh()}finally{btn.disabled=false;btn.textContent='Confirm reservation'}}
 $('lotSelect').addEventListener('change',()=>{state.selected=null;refresh()});['bookingDate','startTime','duration'].forEach(id=>$(id).addEventListener('change',()=>{updateTotal();refresh()}));$('duration').addEventListener('change',updateTotal);$('closeModal').addEventListener('click',()=>$('modal').classList.remove('show'));$('modal').addEventListener('click',e=>{if(e.target===$('modal'))$('modal').classList.remove('show')});$('confirmBtn').addEventListener('click',book);document.querySelectorAll('.lot-button').forEach(b=>b.addEventListener('click',()=>{$('lotSelect').value=b.dataset.lot;refresh();$('parking')?.scrollIntoView({behavior:'smooth'})}));
 refresh();state.timer=setInterval(refresh,4000);
})();
