import { NavLink } from 'react-router-dom';
import { Waves } from 'lucide-react';

const links = [
  { to: '/', label: 'Home' },
  { to: '/upload', label: 'Analyze Audio' },
  { to: '/about', label: 'About' },
];

export default function Navbar() {
  return (
    <header className="navbar">
      <div className="container navbar__inner">
        <NavLink to="/" className="navbar__brand">
          <Waves size={28} aria-hidden="true" />
          <span>AcousticSpace</span>
        </NavLink>

        <nav className="navbar__nav" aria-label="Main navigation">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                `navbar__link ${isActive ? 'navbar__link--active' : ''}`
              }
              end={link.to === '/'}
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
      </div>
    </header>
  );
}

