
const Footer = () => {
  return (
    <footer className="bg-mega-dark text-white py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Logo and Description */}
          <div className="space-y-4">
            <div className="text-2xl font-bold">
              Mega<span className="text-mega-primary">X</span>
            </div>
            <p className="text-gray-300 text-sm">
              Empowering social enterprises with AI-powered impact reporting, 
              interactive dashboards, and intelligent investor matching.
            </p>
          </div>

          {/* Product */}
          <div>
            <h3 className="font-semibold mb-4">Product</h3>
            <ul className="space-y-2 text-sm text-gray-300">
              <li><a href="#" className="hover:text-mega-primary transition-colors">Dashboard</a></li>
              <li><a href="#" className="hover:text-mega-primary transition-colors">Reports</a></li>
              <li><a href="#" className="hover:text-mega-primary transition-colors">Investor Matching</a></li>
              <li><a href="#" className="hover:text-mega-primary transition-colors">Integrations</a></li>
            </ul>
          </div>

          {/* Company */}
          <div>
            <h3 className="font-semibold mb-4">Company</h3>
            <ul className="space-y-2 text-sm text-gray-300">
              <li><a href="#" className="hover:text-mega-primary transition-colors">About</a></li>
              <li><a href="#" className="hover:text-mega-primary transition-colors">Blog</a></li>
              <li><a href="#" className="hover:text-mega-primary transition-colors">Careers</a></li>
              <li><a href="#" className="hover:text-mega-primary transition-colors">Contact</a></li>
            </ul>
          </div>

          {/* Support */}
          <div>
            <h3 className="font-semibold mb-4">Support</h3>
            <ul className="space-y-2 text-sm text-gray-300">
              <li><a href="#" className="hover:text-mega-primary transition-colors">Help Center</a></li>
              <li><a href="#" className="hover:text-mega-primary transition-colors">API Docs</a></li>
              <li><a href="#" className="hover:text-mega-primary transition-colors">Privacy Policy</a></li>
              <li><a href="#" className="hover:text-mega-primary transition-colors">Terms of Service</a></li>
            </ul>
          </div>
        </div>

        <div className="border-t border-gray-800 mt-8 pt-8 flex flex-col md:flex-row justify-between items-center">
          <p className="text-gray-400 text-sm">
            © 2024 Mega X. All rights reserved.
          </p>
          <div className="flex space-x-6 mt-4 md:mt-0">
            <a href="#" className="text-gray-400 hover:text-mega-primary transition-colors text-sm">
              Privacy
            </a>
            <a href="#" className="text-gray-400 hover:text-mega-primary transition-colors text-sm">
              Terms
            </a>
            <a href="#" className="text-gray-400 hover:text-mega-primary transition-colors text-sm">
              Cookies
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
