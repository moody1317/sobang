import './toggle.css';

function Toggle({ checked, onChange, disabled = false, id }) {
  return (
    <label className="toggle">
      <input
        type="checkbox"
        id={id}
        checked={checked}
        onChange={(e) => onChange?.(e.target.checked)}
        disabled={disabled}
      />
      <span className="toggle-track" />
    </label>
  );
}

export default Toggle;
