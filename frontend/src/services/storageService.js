import { openDB } from 'idb';

const dbPromise = openDB('IEDR_Local_Environment', 1, {
  upgrade(db) {
    // Unificando para 'local_history' conforme sua função saveHistory
    if (!db.objectStoreNames.contains('local_history')) {
      db.createObjectStore('local_history', { keyPath: 'id', autoIncrement: true });
    }
  },
});

export const StorageService = {

  async getHistory() {
    const db = await dbPromise;
    // Corrigido para buscar da mesma tabela onde os dados são salvos
    return db.getAll('local_history'); 
  },

  // Salva a pesquisa atual para futuras consultas rápidas (Ambiente do Cliente)
  async saveHistory(data) {
    const db = await dbPromise;
    // Salva no IndexedDB local para manter o app leve e rápido nacionalmente
    return db.put('local_history', { 
      ...data, 
      timestamp: new Date().toISOString() 
    });
  }
};