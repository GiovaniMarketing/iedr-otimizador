import React, { useEffect, useState } from 'react';
import { StorageService } from '../services/storageService';

const EconomyDashboard = () => {
    const [history, setHistory] = useState([]);
    const [totalSaved, setTotalSaved] = useState(0);

    useEffect(() => {
        const loadHistory = async () => {
            const data = await StorageService.getHistory();
            setHistory(data);
            
            // Calcula o total poupado acumulado no dispositivo
            const total = data.reduce((acc, curr) => acc + (curr.savings || 0), 0);
            setTotalSaved(total);
        };
        loadHistory();
    }, []);

    return (
        <div className="economy-container">
            <h2>Sua Economia Total</h2>
            <div className="total-badge">R$ {totalSaved.toFixed(2)}</div>
            
            <h3>Últimas Compras Otimizadas</h3>
            <ul>
                {history.map((item, index) => (
                    <li key={index}>
                        {new Date(item.date).toLocaleDateString()} - 
                        Economia de: <strong>R$ {item.savings.toFixed(2)}</strong>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default EconomyDashboard;