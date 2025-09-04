// Firebase 설정 파일
// 이 파일은 .gitignore에 추가하여 버전 관리에서 제외하세요

const firebaseConfig = {
    apiKey: "AIzaSyA4Z1B42fmBIJznBED11XIIiVVKN5OSQ1E",
    authDomain: "seller1-b8a4c.firebaseapp.com",
    projectId: "seller1-b8a4c",
    storageBucket: "seller1-b8a4c.firebasestorage.app",
    messagingSenderId: "740000823974",
    appId: "1:740000823974:web:ac62ca392ffb34e96e9267",
    measurementId: "G-Q8ZNT6PDB9",
    databaseURL: "https://seller1-b8a4c-default-rtdb.asia-southeast1.firebasedatabase.app"
};

// 전역으로 설정 노출
window.firebaseConfig = firebaseConfig;
