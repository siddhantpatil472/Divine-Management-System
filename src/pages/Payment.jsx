import {useState} from "react";
import {useLocation,useNavigate} from "react-router-dom";
import {api} from "../services/api";

function amountFor(booking){
 if(booking.amount) return Number(booking.amount);
 if(booking.type==="Darshan") return Number(booking.data?.persons||1)*100;
 if(booking.type==="Pooja") return 251;
 if(booking.type==="Room Booking"){
   const a=new Date(booking.data?.checkin),b=new Date(booking.data?.checkout);
   const nights=Math.max(1,Math.round((b-a)/86400000));
   return nights*Number(booking.data?.rooms||1)*1000;
 }
 return 0;
}

export default function Payment(){
 const location=useLocation(),navigate=useNavigate(),booking=location.state;
 const [transactionId,setTransactionId]=useState(""),[method,setMethod]=useState("UPI"),[loading,setLoading]=useState(false),[error,setError]=useState("");
 if(!booking?.user) return <section className="section page narrow"><div className="error">Payment session expired. Please start your booking again.</div></section>;
 const amount=amountFor(booking);
 async function submit(e){
   e.preventDefault();setError("");
   if(!transactionId.trim())return setError("Enter the UPI/payment transaction ID after completing payment.");
   setLoading(true);
   try{
    const payment={amount,method,transaction_id:transactionId.trim(),paid_at:new Date().toISOString().slice(0,19).replace("T"," ")};
    let result;
    if(booking.type==="Donation") result=await api.donation({...booking.data,name:booking.user.name,phone:booking.user.phone,email:booking.user.email,temple_id:booking.data.temple,payment});
    else result=await api.booking({booking_type:booking.type,temple_id:booking.data.temple,date:booking.data.date,slot:booking.data.slot,persons:Number(booking.data.persons||1),pooja:booking.data.pooja,checkin:booking.data.checkin,checkout:booking.data.checkout,rooms:Number(booking.data.rooms||0),name:booking.user.name,phone:booking.user.phone,email:booking.user.email,event_name:booking.data.name,payment});
    navigate("/booking-confirmation",{state:{...booking,result,payment:true,amount,transactionId}});
   }catch(err){setError(err.message)}finally{setLoading(false)}
 }
 return <section className="section page narrow"><div className="section-heading"><p className="eyebrow">SECURE PAYMENT</p><h1>Pay ₹{amount.toLocaleString("en-IN")}</h1><p>{booking.temple} • {booking.type}</p></div>
 <div className="payment-layout">
  <div className="payment-card qr-card"><span className="mini-label">SCAN TO PAY</span><div className="qr-box"><img src="/payment-qr.png" alt="Temple UPI payment QR code"/></div><h3>Temple UPI Payment</h3><p>Scan the temple QR code using your UPI app. After payment, enter the transaction ID below.</p><div className="payment-note"><strong>UPI Payment:</strong> Scan the QR code above with any UPI app, complete the payment, then enter your Transaction / UTR ID on this page.</div></div>
  <form className="form-card payment-form" onSubmit={submit}>
   <label>Payment Method<select value={method} onChange={e=>setMethod(e.target.value)}><option>UPI</option><option>Bank Transfer</option><option>Other</option></select></label>
   <label>Transaction / UTR ID<input required value={transactionId} onChange={e=>setTransactionId(e.target.value)} placeholder="Enter payment reference number"/></label>
   <label>Paid Amount (₹)<input readOnly value={amount}/></label>
   <div className="payment-summary"><strong>Important:</strong> Payment is submitted to the selected temple trustee for verification. Your booking/receipt becomes confirmed only after trustee approval.</div>
   {error&&<div className="error">{error}</div>}
   <button className="btn primary" disabled={loading}>{loading?"Submitting Payment...":"Submit Payment Details"}</button>
  </form>
 </div></section>
}
