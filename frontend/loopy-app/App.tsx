import React, { useEffect, useState } from 'react';
import { View, Text, Button } from 'react-native';
import { onAuthStateChanged, signInAnonymously } from 'firebase/auth';
import { auth } from './src/services/firebase';

export default function App() {
  const [uid, setUid] = useState<string | null>(null);

  useEffect(() => {
    const unsub = onAuthStateChanged(auth, (u) => setUid(u?.uid ?? null));
    return () => unsub();
  }, []);

  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', gap: 12 }}>
      <Text style={{ fontSize: 16 }}>
        {uid ? `Signed in: ${uid}` : 'Not signed in'}
      </Text>
      {!uid && <Button title="Continue as Guest" onPress={() => signInAnonymously(auth)} />}
    </View>
  );
}
