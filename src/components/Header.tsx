
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Menu, X } from 'lucide-react';

const Header = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <header className="bg-white border-b border-gray-100 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <div className="text-2xl font-bold text-mega-dark">
              Mega<span className="text-mega-primary">X</span>
            </div>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <a href="#features" className="text-gray-600 hover:text-mega-primary transition-colors">
              Features
            </a>
            <a href="#about" className="text-gray-600 hover:text-mega-primary transition-colors">
              About
            </a>
            <a href="#pricing" className="text-gray-600 hover:text-mega-primary transition-colors">
              Pricing
            </a>
            <Button variant="outline" className="border-mega-primary text-mega-primary hover:bg-mega-primary hover:text-white">
              Sign In
            </Button>
            <Button className="bg-mega-primary hover:bg-mega-primary/90 text-white">
              Get Started
            </Button>
          </nav>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="text-gray-600 hover:text-mega-primary"
            >
              {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="md:hidden border-t border-gray-100">
            <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
              <a href="#features" className="block px-3 py-2 text-gray-600 hover:text-mega-primary">
                Features
              </a>
              <a href="#about" className="block px-3 py-2 text-gray-600 hover:text-mega-primary">
                About
              </a>
              <a href="#pricing" className="block px-3 py-2 text-gray-600 hover:text-mega-primary">
                Pricing
              </a>
              <div className="flex flex-col space-y-2 px-3 pt-2">
                <Button variant="outline" className="border-mega-primary text-mega-primary">
                  Sign In
                </Button>
                <Button className="bg-mega-primary hover:bg-mega-primary/90 text-white">
                  Get Started
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
