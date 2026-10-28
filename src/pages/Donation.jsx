import {useState} from "react";
import {useNavigate} from "react-router-dom";
import {temples} from "../data/temples";

export default function Donation(){
 const navigate=useNavigate();
 const [form,setForm]=useState({temple:"",amount:"",purpose:"Temple Development",name:"",email:"",phone:""}),[error,setError]=useState("");
 function submit(e){
   e.preventDefault();setError("");
   if(Number(form.amount)<=0)return setError("Enter a donation amount greater than zero.");
   if(!/^\d{10}$/.test(form.phone))return setError("Enter a valid 10 digit mobile number.");
   const t=temples.find(x=>x.id===form.temple);
   navigate("/payment",{state:{type:"Donation",temple:t?.name||"",data:{...form,temple:form.temple},user:{name:form.name,phone:form.phone,email:form.email},amount:Number(form.amount)}});
 }
 return <section className="section page narrow"><div className="section-heading"><p className="eyebrow">DONATION</p><h1>Make a Donation</h1><p>Pay using the temple QR scanner and submit your transaction ID. The trustee will verify and issue the digital receipt.</p></div>
 <form className="form-card" onSubmit={submit}>
  <label>Temple<select required value={form.temple} onChange={e=>setForm({...form,temple:e.target.value})}><option value="">Select Temple</option>{temples.map(t=><option key={t.id} value={t.id}>{t.name}</option>)}</select></label>
  <label>Donor Name<input required value={form.name} onChange={e=>setForm({...form,name:e.target.value})}/></label>
  <label>Mobile<input required pattern="[0-9]{10}" value={form.phone} onChange={e=>setForm({...form,phone:e.target.value})}/></label>
  <label>Email<input required type="email" value={form.email} onChange={e=>setForm({...form,email:e.target.value})}/></label>
  <label>Amount (₹)<input required min="1" type="number" value={form.amount} onChange={e=>setForm({...form,amount:e.target.value})}/></label>
  <label>Purpose<select value={form.purpose} onChange={e=>setForm({...form,purpose:e.target.value})}><option>Temple Development</option><option>Annadanam</option><option>General Donation</option><option>Festival</option></select></label>
  {error&&<div className="error">{error}</div>}
  <button className="btn primary">Continue to Payment</button>
 </form></section>
}
