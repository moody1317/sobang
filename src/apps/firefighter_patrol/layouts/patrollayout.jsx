import './patrollayout.css';

function PatrolLayout({ children }) {
  return (
    <div className="patrol-layout">
      <div className="patrol-frame">
        {children}
      </div>
    </div>
  );
}

export default PatrolLayout;
