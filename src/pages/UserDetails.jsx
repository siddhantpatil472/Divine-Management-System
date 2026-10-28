import {useState} from "react";
import {useLocation,useNavigate} from "react-router-dom";

export default function UserDetails(){
 const location=useLocation(),navigate=useNavigate();
 const booking=location.state||{type:"Booking",temple:"",data:{}};
 const [form,setForm]=useState({name:"",phone:"",email:""});
 const [error,setError]=useState("");
 function submit(e){
   e.preventDefault(); setError("");
   if(!/^\d{10}$/.test(form.phone)) return setError("Enter a valid 10 digit mobile number.");
   navigate("/payment",{state:{...booking,user:form}});
 }
 return <section className="section page narrow"><div className="section-heading"><p className="eyebrow">USER DETAILS</p><h1>Enter Your Details</h1><p><strong>{booking.type}</strong>{booking.temple&&` • ${booking.temple}`}</p></div>
 <form className="form-card" onSubmit={submit}>
  <label>Full Name<input required value={form.name} onChange={e=>setForm({...form,name:e.target.value})}/></label>
  <label>Mobile Number<input required type="tel" pattern="[0-9]{10}" placeholder="10 digit mobile number" value={form.phone} onChange={e=>setForm({...form,phone:e.target.value})}/></label>
  <label>Email<input required type="email" value={form.email} onChange={e=>setForm({...form,email:e.target.value})}/></label>
  {error&&<div className="error">{error}</div>}
  <button className="btn primary">Continue to Payment</button>
 </form></section>
}
