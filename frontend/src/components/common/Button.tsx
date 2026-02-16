import React from 'react';

type Variant = 'primary' | 'secondary' | 'danger';
type Size = 'sm' | 'md' | 'lg';

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: Variant;
  size?: Size;
};

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      children,
      variant = 'primary',
      size = 'md',
      disabled = false,
      className = '',
      ...props
    },
    ref
  ) => {
    const baseClasses =
      'font-semibold rounded-lg transition-all duration-200 focus:outline-none focus:ring-2';

    const variantClasses: Record<Variant, string> = {
      primary: 'bg-primary-600 text-white hover:bg-primary-700 focus:ring-primary-500',
      secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300 focus:ring-gray-400',
      danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
    };

    const sizeClasses: Record<Size, string> = {
      sm: 'px-3 py-1.5 text-sm',
      md: 'px-6 py-3 text-base',
      lg: 'px-8 py-4 text-lg',
    };

    return (
      <button
        ref={ref}
        disabled={disabled}
        className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${
          disabled ? 'opacity-50 cursor-not-allowed' : ''
        } ${className}`}
        {...props}
      >
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';
