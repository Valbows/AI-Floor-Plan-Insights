// Charney Design System Components
import React from 'react';

// Typography Components
export const DisplayXL = ({ children, className = '', mixed = false, ...props }) => (
  <h1 
    className={`text-6xl font-black leading-none tracking-tight uppercase ${className}`}
    {...props}
  >
    {mixed ? (
      <span dangerouslySetInnerHTML={{ __html: children }} />
    ) : (
      children
    )}
  </h1>
);

export const DisplayLG = ({ children, className = '', mixed = false, ...props }) => (
  <h1 
    className={`text-5xl font-black leading-tight tracking-tight uppercase ${className}`}
    {...props}
  >
    {mixed ? (
      <span dangerouslySetInnerHTML={{ __html: children }} />
    ) : (
      children
    )}
  </h1>
);

export const DisplayMD = ({ children, className = '', mixed = false, ...props }) => (
  <h2 
    className={`text-4xl font-black leading-tight tracking-tight uppercase ${className}`}
    {...props}
  >
    {mixed ? (
      <span dangerouslySetInnerHTML={{ __html: children }} />
    ) : (
      children
    )}
  </h2>
);

export const HeadingLG = ({ children, className = '', ...props }) => (
  <h3 className={`text-3xl font-bold leading-tight uppercase ${className}`} {...props}>
    {children}
  </h3>
);

export const HeadingMD = ({ children, className = '', ...props }) => (
  <h4 className={`text-2xl font-bold leading-normal ${className}`} {...props}>
    {children}
  </h4>
);

export const BodyLG = ({ children, className = '', ...props }) => (
  <p className={`text-lg font-normal leading-relaxed ${className}`} {...props}>
    {children}
  </p>
);

export const BodyMD = ({ children, className = '', ...props }) => (
  <p className={`text-base font-normal leading-relaxed ${className}`} {...props}>
    {children}
  </p>
);

// Button Components
export const Button = ({ 
  children, 
  variant = 'primary', 
  size = 'md',
  className = '', 
  ...props 
}) => {
  const baseClasses = 'font-bold uppercase tracking-wide border-none cursor-pointer transition-all duration-200 inline-block no-underline';
  
  const variants = {
    primary: 'bg-charney-red text-charney-white hover:bg-red-600 hover:-translate-y-0.5 hover:shadow-lg',
    secondary: 'bg-charney-black text-charney-white hover:bg-gray-800',
    outline: 'bg-transparent text-charney-black border-3 border-charney-black hover:bg-charney-black hover:text-charney-white'
  };
  
  const sizes = {
    sm: 'px-6 py-2 text-sm rounded-sm',
    md: 'px-8 py-4 text-base rounded-sm',
    lg: 'px-10 py-5 text-lg rounded-md'
  };

  return (
    <button 
      className={`${baseClasses} ${variants[variant]} ${sizes[size]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
};

// Card Component
export const Card = ({ children, className = '', ...props }) => (
  <div 
    className={`bg-charney-white rounded-lg overflow-hidden shadow-sm ${className}`}
    {...props}
  >
    {children}
  </div>
);

export const CardContent = ({ children, className = '', ...props }) => (
  <div className={`p-md ${className}`} {...props}>
    {children}
  </div>
);

// Accent Bar Component
export const AccentBar = ({ className = '', color = 'red', ...props }) => {
  const colorClasses = {
    red: 'bg-charney-red',
    black: 'bg-charney-black'
  };

  return (
    <div 
      className={`w-full h-1.5 my-md ${colorClasses[color]} ${className}`}
      {...props}
    />
  );
};

// Layout Components
export const Container = ({ children, className = '', ...props }) => (
  <div 
    className={`max-w-7xl mx-auto px-lg py-xl ${className}`}
    {...props}
  >
    {children}
  </div>
);

// Mixed Color Text Helper
export const MixedColorText = ({ blackText, redText, className = '' }) => (
  <span className={className}>
    {blackText} <span className="text-charney-red">{redText}</span>
  </span>
);

// Red Background Section (with proper text color enforcement)
export const RedSection = ({ children, className = '', ...props }) => (
  <section 
    className={`bg-charney-red text-charney-black ${className}`}
    style={{ color: '#000000' }} // Enforce black text as per design system
    {...props}
  >
    {children}
  </section>
);
