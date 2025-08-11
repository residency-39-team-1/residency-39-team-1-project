import React, { useEffect, useState } from 'react';
import { View, Text, Button, FlatList } from 'react-native';
import * as WebBrowser from 'expo-web-browser';
import * as Google from 'expo-auth-session/providers/google';
import {
  getAuth,
  onAuthStateChanged,
  signInAnonymously,
  GoogleAuthProvider,
  signInWithCredential,
} from 'firebase/auth';
import { app, db } from '../src/services/firebase';
import {
  collection,
  addDoc,
  serverTimestamp,
  onSnapshot,
  query,
  where,
  orderBy,
  doc,
  updateDoc,
  deleteDoc,
} from 'firebase/firestore';

WebBrowser.maybeCompleteAuthSession();
const auth = getAuth(app);

type Task = { id: string; title: string; state: string };

export default function Index() {
  const [uid, setUid] = useState<string | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [err, setErr] = useState<string | null>(null);

  // Google AuthSession request
  const [request, response, promptAsync] = Google.useAuthRequest({
    // ⬇️ paste your Google OAuth "Web application" Client ID here
    expoClientId: 'YOUR_GOOGLE_OAUTH_CLIENT_ID.apps.googleusercontent.com',
  });

  // Handle Google sign-in result -> Firebase
  useEffect(() => {
    (async () => {
      if (response?.type === 'success' && response.authentication?.idToken) {
        const cred = GoogleAuthProvider.credential(response.authentication.idToken);
        await signInWithCredential(auth, cred);
      }
    })();
  }, [response]);

  // Firebase auth state
  useEffect(() => {
    const unsub = onAuthStateChanged(auth, (u) => setUid(u?.uid ?? null));
    return () => unsub();
  }, []);

  // Real-time tasks for this user
  useEffect(() => {
    if (!uid) return;
    const q = query(
      collection(db, 'tasks'),
      where('ownerId', '==', uid),
      orderBy('createdAt', 'asc')
    );
    const unsub = onSnapshot(
      q,
      (snap) => {
        const next = snap.docs.map((d) => ({ id: d.id, ...(d.data() as any) })) as Task[];
        setTasks(next);
      },
      (e) => setErr(String(e?.message ?? e))
    );
    return () => unsub();
  }, [uid]);

  const handleGuest = async () => {
    try {
      await signInAnonymously(auth);
    } catch (e: any) {
      setErr(String(e?.message ?? e));
    }
  };

  const handleGoogle = async () => {
    try {
      await promptAsync();
    } catch (e: any) {
      setErr(String(e?.message ?? e));
    }
  };

  const addTestTask = async () => {
    try {
      if (!uid) return;
      await addDoc(collection(db, 'tasks'), {
        ownerId: uid,
        title: 'My first task',
        state: 'Exploring',
        createdAt: serverTimestamp(),
        updatedAt: serverTimestamp(),
      });
    } catch (e: any) {
      setErr(String(e?.message ?? e));
    }
  };

  const completeTask = async (id: string) => {
    try {
      await updateDoc(doc(db, 'tasks', id), {
        state: 'Complete',
        updatedAt: serverTimestamp(),
      });
    } catch (e: any) {
      setErr(String(e?.message ?? e));
    }
  };

  const deleteTask = async (id: string) => {
    try {
      await deleteDoc(doc(db, 'tasks', id));
    } catch (e: any) {
      setErr(String(e?.message ?? e));
    }
  };

  return (
    <View style={{ flex: 1, padding: 16, gap: 12 }}>
      <View style={{ alignItems: 'center', marginTop: 24, gap: 8 }}>
        <Text style={{ fontSize: 16 }}>
          {uid ? `Signed in: ${uid}` : 'Not signed in'}
        </Text>
        {!uid && (
          <>
            <Button title="Continue as Guest" onPress={handleGuest} />
            <Button title="Sign in with Google" onPress={handleGoogle} disabled={!request} />
          </>
        )}
      </View>

      {uid && (
        <View style={{ gap: 8 }}>
          <Button title="Add test task" onPress={addTestTask} />
          <Text style={{ marginTop: 8 }}>Tasks ({tasks.length})</Text>
          <FlatList
            data={tasks}
            keyExtractor={(t) => t.id}
            renderItem={({ item }) => (
              <View style={{ padding: 10, borderWidth: 1, borderRadius: 8, marginVertical: 6, gap: 6 }}>
                <Text>{item.title} — {item.state}</Text>
                {item.state !== 'Complete' ? (
                  <Button title="Mark Complete" onPress={() => completeTask(item.id)} />
                ) : (
                  <Text style={{ color: 'green' }}>Done ✅</Text>
                )}
                <Button title="Delete" color="#b00020" onPress={() => deleteTask(item.id)} />
              </View>
            )}
          />
        </View>
      )}

      {err && <Text style={{ color: 'red' }}>{err}</Text>}
    </View>
  );
}
