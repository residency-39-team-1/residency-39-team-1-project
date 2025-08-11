import { initializeApp, getApps, getApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';
import { getStorage } from 'firebase/storage';

const firebaseConfig = {
    apiKey: "AIzaSyALSzP_Izw0AQ1YitOericmXsLAqXBt0CQ",
    authDomain: "loopy-productivity-app.firebaseapp.com",
    projectId: "loopy-productivity-app",
    storageBucket: "loopy-productivity-app.appspot.com",
    messagingSenderId: "39855210543",
    appId: "1:39855210543:web:ad9d25cba2ca3231e6c6da"
};

// Ensure a single default app
export const app = getApps().length ? getApp() : initializeApp(firebaseConfig);

export const auth = getAuth(app);
export const db = getFirestore(app);
export const storage = getStorage(app);