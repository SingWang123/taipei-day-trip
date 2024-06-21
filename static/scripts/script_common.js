
//Signin / signup
// 做一個切換登入/註冊彈窗的功能  
function switchWindow(type){
    let signin = ["275px","flex","none"]
    let signup = ["332px","none","flex"]
    let signinWindow = document.querySelector(".signin__window_content");
    let signupWindow = document.querySelector(".signup__window_content");
    let windowBackground = document.querySelector(".signin__window");
    if (type === "signin"){
      windowBackground.style.height = signin[0];
      signinWindow.style.display = signin[1];
      signupWindow.style.display = signin[2];
    } else if (type === "signup"){
      windowBackground.style.height = signup[0];
      signinWindow.style.display = signup[1];
      signupWindow.style.display = signup[2];
    } 
  }
  
  // 點擊 登入/註冊，跳出登入註冊彈窗，每次點擊必定開啟登入彈窗
  document.querySelector(".navbar__buttons_signin").addEventListener("click",function(){
    let popupSignin = document.querySelector(".signin");
    popupSignin.style.display = "block";
    switchWindow("signin");
  })
  
// 註冊成功或失敗，跳出提示訊息
function showResult(type,message){
  let signupResult = document.createElement("div");
  signupResult.className = "signup__button_switch_signin";

  if (type === "error_400"){
    signupResult.style.color = "red"
  } 
  signupResult.textContent = message;
  document.querySelector(".signup__button_signup").appendChild(signupResult);
}



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
  

  //註冊功能
  let nameSignup = document.getElementById("signup_name")
  let usernameSignup = document.getElementById("signup_email")
  let passwordSignup = document.getElementById("signup_password")

  document.querySelector(".signup__button_signup").addEventListener("click",function(){
    if (nameSignup.value.length === 0 || usernameSignup.value.length === 0 || passwordSignup.value.length === 0){  
      alert("請填寫所有註冊欄位"); 
    }else{
    //先建立要傳送的資料
      newName = {
        "name" : nameSignup.value,
        "email": usernameSignup.value,
        "password" : passwordSignup.value
      };

      //fetch資料
      fetch("http://127.0.0.1:8000/api/user", {
        method: "POST",
        headers:{
            "Content-Type" : "application/json"
        },
        body: JSON.stringify(newName)
      })
      .then(response => response.json())
      .then(function(data){
        if(data.ok === true){
          showResult("ok","註冊成功");
        } else if (data.error == true){
          showResult("error",data.message);
        }
      })
    }
  })

 