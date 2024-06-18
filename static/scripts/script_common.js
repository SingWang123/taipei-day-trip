
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
  