
//Signin / signup

// 做一個切換 登入/註冊 和 登出系統按鈕的功能 
function switchSignInOut(type){
  let signin = document.querySelector(".navbar__buttons_signin");
  let signout = document.querySelector(".navbar__buttons_signout");

  if (type === "signin"){
    signin.style.display = "block";
    signout.style.display = "none";
  } else if (type === "signout"){
    signin.style.display = "none";
    signout.style.display = "block";   
  }
}

// 做一個切換登入/註冊彈窗的功能  
function switchWindow(type){
  let signin = ["275px","flex","none"]
  let signup = ["332px","none","flex"]
  let signinWindow = document.querySelector(".signin__window_content");
  let signupWindow = document.querySelector(".signup__window_content");
  let signinResult = document.querySelector(".signin__result");
  let signupResult = document.querySelector(".signup__result");
  let windowBackground = document.querySelector(".signin__window");
  if (type === "signin"){
    windowBackground.style.height = signin[0];
    signinWindow.style.display = signin[1];
    signupWindow.style.display = signin[2];
    signinResult.style.display = "none"
  } else if (type === "signup"){
    windowBackground.style.height = signup[0];
    signinWindow.style.display = signup[1];
    signupWindow.style.display = signup[2];
    signupResult.style.display = "none"
  } 
}
    
// 顯示註冊結果，跳出提示訊息
function showResult(type,message,message_type){
  classname_result =  "." + type + "__result";

  let result = document.querySelector(classname_result);
  let windowBackground = document.querySelector(".signin__window");
  result.style.color = "rgba(102, 102, 102, 1)";

  if (message_type === "error"){
    result.style.color = "rgba(212,17,17,1)";
  } 

  if (type === "signup"){
    windowBackground.style.height = "368px";
  } else {
    windowBackground.style.height = "312px";
  }
  result.style.display = "block";
  result.textContent = message;
  
}

// 檢查信箱格式是否正確
function checkEmail(type){
  classname_email = "." + type + "__input_email";

  let email = document.querySelector(classname_email);

  // 正則表達式檢查電子郵件格式
  let emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  if (emailPattern.test(email.value)){ 
    return {"error" : false}; //檢查格式正確，回傳沒有錯誤
  } else {
    return {"error" : true};
  }
}



//操作
// 點擊 登入/註冊，跳出登入註冊彈窗，每次點擊必定開啟登入彈窗
document.querySelector(".navbar__buttons_signin").addEventListener("click",function(){
  let popupSignin = document.querySelector(".signin");
  popupSignin.style.display = "block";
  switchWindow("signin");
})

// 點擊 X ，關閉登入註冊彈窗
document.querySelector(".signin__window_close").addEventListener("click",function(){
  let popupSignin = document.querySelector(".signin");
  popupSignin.style.display = "none";
})

// 點擊切換註冊彈窗
document.querySelector(".signin__button_switch_signup").addEventListener("click",function(){
  switchWindow("signup");
})

// 點擊切換登入彈窗
document.querySelector(".signup__button_switch_signin").addEventListener("click",function(){
  switchWindow("signin");
})

// 點擊登出系統
document.querySelector(".navbar__buttons_signout").addEventListener("click",function(){
  localStorage.removeItem("jwt_token");
  location.reload(); //重整頁面
})


//取得LocalStorage的token
let token = localStorage.getItem("jwt_token");

//檢查登入狀態 api（get）
fetch("http://127.0.0.1:8000/api/user/auth",{
  method: "GET",
  headers:{
    "Authorization" : `Bearer ${token}`,
    "Content-Type" : "application/json"    
  }
})
.then(response => response.json())
.then(function(data){
  if (data.data == null){  //data為null，除了沒有Token之外，也有可能是token失效或過期
    switchSignInOut("signin")
    if (localStorage.getItem("jwt_token") != null){  //因應token可能過期或失效，若有殘留的token就清除
      localStorage.removeItem("jwt_token"); 
    }
  } else {
    switchSignInOut("signout")
  }
})


//註冊功能 api (post)
document.querySelector(".signup__button_signup").addEventListener("click",function(){
  let nameSignup = document.querySelector(".signup__input_name")
  let emailSignup = document.querySelector(".signup__input_email")
  let passwordSignup = document.querySelector(".signup__input_password")
 
  if (nameSignup.value.length === 0 || emailSignup.value.length === 0 || passwordSignup.value.length === 0){  
    showResult("signup","請填寫所有註冊欄位","error"); 
  }else if(checkEmail("signup")["error"]){
    showResult("signup","電子信箱格式錯誤","error");
  }else{
  //先建立要傳送的資料
    newMember = {
      "name" : nameSignup.value,
      "email": emailSignup.value,
      "password" : passwordSignup.value
    };
    console.log(newMember);
    //fetch資料
    fetch("http://127.0.0.1:8000/api/user", {
      method: "POST",
      headers:{
        "Content-Type" : "application/json"
      },
      body: JSON.stringify(newMember)
    })
    // .then(response => response.json())
    // .then(function(data){
    //   console.log(data);
    //   // if(data.ok === true){
    //   //   showResult("signup","註冊成功","ok");
    //   // } else if (data.error == true){
    //   //   showResult("signup",data.message,"error");
    //   // }
    // })
  }
})


//登入功能  api (put)
document.querySelector(".signin__button_signin").addEventListener("click",function(){
  let emailSignin = document.querySelector(".signin__input_email")
  let passwordSignin = document.querySelector(".signin__input_password")
 
  if (emailSignin.value.length === 0 || passwordSignin.value.length === 0){  
    showResult("signin","請填寫完整登入資料","error");
  }else if(checkEmail("signin")["error"]){
    showResult("signin","電子信箱格式錯誤","error");
    
  }else{
  //先建立要傳送的資料
    signIn = {
      "email": emailSignin.value,
      "password" : passwordSignin.value
    };
    
    //fetch資料
    fetch("http://127.0.0.1:8000/api/auth", {
      method: "PUT",
      headers:{
        "Content-Type" : "application/json"
      },
      body: JSON.stringify(signIn)
    })
    .then(response => response.json())
    .then(function(data){
      if(data.token){  //有token，登入成功，儲存token，修改畫面
        showResult("signin","登入成功","ok");
        localStorage.setItem("jwt_token",data.token);  //儲存token 到 localStorage
        location.reload(); //重整頁面
        
      } else if (data.error == true){
        showResult("signin",data.message,"error");
      }
    })
  }
})





