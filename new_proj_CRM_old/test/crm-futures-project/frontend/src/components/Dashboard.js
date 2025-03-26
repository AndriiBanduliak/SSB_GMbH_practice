import React from 'react';
import { useTranslation } from 'react-i18next';

function Dashboard() {
  const { t } = useTranslation();

  return (
    <div>
      <h2>{t('dashboard.title')}</h2>
      <p>Welcome to your dashboard. Futures trading data will appear here.</p>
      {/* Здесь будут виджеты, графики и т.д. */}
    </div>
  );
}

export default Dashboard;
