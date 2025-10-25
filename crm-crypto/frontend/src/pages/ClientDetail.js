import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const ClientDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { API_URL } = useAuth();
  const [client, setClient] = useState(null);
  const [pnlData, setPnlData] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchClientData();
  }, [id]);

  const fetchClientData = async () => {
    try {
      setLoading(true);
      const [clientRes, pnlRes, txRes] = await Promise.all([
        axios.get(`${API_URL}/clients/${id}`),
        axios.get(`${API_URL}/pnl/?client_id=${id}&limit=10`),
        axios.get(`${API_URL}/transactions/?client_id=${id}&limit=20`)
      ]);
      
      setClient(clientRes.data);
      setPnlData(pnlRes.data);
      setTransactions(txRes.data);
    } catch (error) {
      console.error('Failed to fetch client data:', error);
      alert('Failed to load client data');
      navigate('/clients');
    } finally {
      setLoading(false);
    }
  };

  if (loading || !client) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-xl text-gray-600">Loading...</div>
      </div>
    );
  }

  const latestPnL = pnlData[0] || {};

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('/clients')}
            className="text-gray-600 hover:text-gray-900"
          >
            ← Back
          </button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{client.full_name}</h1>
            <p className="mt-1 text-sm text-gray-600">{client.email}</p>
          </div>
        </div>
        <span className={`px-3 py-1 inline-flex text-sm leading-5 font-semibold rounded-full ${
          client.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
        }`}>
          {client.status}
        </span>
      </div>

      {/* Key metrics */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <p className="text-sm font-medium text-gray-600">Current AUM</p>
          <p className="text-2xl font-bold text-gray-900 mt-2">
            ${client.current_aum.toLocaleString('en-US', { maximumFractionDigits: 0 })}
          </p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <p className="text-sm font-medium text-gray-600">Total P&L</p>
          <p className={`text-2xl font-bold mt-2 ${latestPnL.total_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            ${(latestPnL.total_pnl || 0).toLocaleString('en-US', { maximumFractionDigits: 0 })}
          </p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <p className="text-sm font-medium text-gray-600">ROI</p>
          <p className={`text-2xl font-bold mt-2 ${latestPnL.roi_percentage >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {(latestPnL.roi_percentage || 0).toFixed(2)}%
          </p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <p className="text-sm font-medium text-gray-600">Win Rate</p>
          <p className="text-2xl font-bold text-gray-900 mt-2">
            {(latestPnL.win_rate || 0).toFixed(1)}%
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6" aria-label="Tabs">
            {['overview', 'transactions', 'performance'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Client Information</h3>
                <dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Email</dt>
                    <dd className="mt-1 text-sm text-gray-900">{client.email}</dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Phone</dt>
                    <dd className="mt-1 text-sm text-gray-900">{client.phone || 'N/A'}</dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Company</dt>
                    <dd className="mt-1 text-sm text-gray-900">{client.company || 'N/A'}</dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Risk Level</dt>
                    <dd className="mt-1 text-sm text-gray-900">{client.risk_level}</dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Lead Source</dt>
                    <dd className="mt-1 text-sm text-gray-900">{client.lead_source || 'N/A'}</dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Trading Strategy</dt>
                    <dd className="mt-1 text-sm text-gray-900">{client.trading_strategy || 'N/A'}</dd>
                  </div>
                </dl>
              </div>
              {client.notes && (
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Notes</h3>
                  <p className="text-sm text-gray-700">{client.notes}</p>
                </div>
              )}
            </div>
          )}

          {/* Transactions Tab */}
          {activeTab === 'transactions' && (
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Transactions</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead>
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Exchange</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Symbol</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Side</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Quantity</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Price</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {transactions.map((tx) => (
                      <tr key={tx.id}>
                        <td className="px-4 py-3 text-sm text-gray-900">
                          {new Date(tx.executed_at).toLocaleDateString()}
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-500">{tx.exchange}</td>
                        <td className="px-4 py-3 text-sm text-gray-900">{tx.symbol}</td>
                        <td className="px-4 py-3 text-sm">
                          <span className={`px-2 py-1 text-xs rounded-full ${
                            tx.side === 'buy' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                          }`}>
                            {tx.side}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-900">{tx.quantity.toFixed(6)}</td>
                        <td className="px-4 py-3 text-sm text-gray-900">${tx.price.toFixed(2)}</td>
                        <td className="px-4 py-3 text-sm font-medium text-gray-900">
                          ${tx.total_amount.toFixed(2)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Performance Tab */}
          {activeTab === 'performance' && (
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Performance History</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead>
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Period</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">P&L</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">ROI</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Trades</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Win Rate</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Max DD</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {pnlData.map((pnl) => (
                      <tr key={pnl.id}>
                        <td className="px-4 py-3 text-sm text-gray-900">{pnl.period}</td>
                        <td className="px-4 py-3 text-sm">
                          <span className={pnl.total_pnl >= 0 ? 'text-green-600' : 'text-red-600'}>
                            ${pnl.total_pnl.toFixed(2)}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-sm">
                          <span className={pnl.roi_percentage >= 0 ? 'text-green-600' : 'text-red-600'}>
                            {pnl.roi_percentage.toFixed(2)}%
                          </span>
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-900">{pnl.total_trades}</td>
                        <td className="px-4 py-3 text-sm text-gray-900">{pnl.win_rate.toFixed(1)}%</td>
                        <td className="px-4 py-3 text-sm text-gray-900">
                          {pnl.max_drawdown_percentage.toFixed(2)}%
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ClientDetail;

