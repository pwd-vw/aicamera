import { registerDecorator, ValidationOptions, ValidationArguments } from 'class-validator';

// Custom validation decorator for strong passwords
export function IsStrongPassword(validationOptions?: ValidationOptions) {
  return function (object: Object, propertyName: string) {
    registerDecorator({
      name: 'isStrongPassword',
      target: object.constructor,
      propertyName: propertyName,
      options: validationOptions,
      validator: {
        validate(value: any, args: ValidationArguments) {
          if (typeof value !== 'string') return false;
          
          // At least 8 characters, 1 uppercase, 1 lowercase, 1 number, 1 special character
          const strongPasswordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
          return strongPasswordRegex.test(value);
        },
        defaultMessage(args: ValidationArguments) {
          return `${args.property} must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one number, and one special character`;
        },
      },
    });
  };
}

// Custom validation decorator for IP addresses
export function IsIPAddress(validationOptions?: ValidationOptions) {
  return function (object: Object, propertyName: string) {
    registerDecorator({
      name: 'isIPAddress',
      target: object.constructor,
      propertyName: propertyName,
      options: validationOptions,
      validator: {
        validate(value: any, args: ValidationArguments) {
          if (typeof value !== 'string') return false;
          
          const ipRegex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
          return ipRegex.test(value);
        },
        defaultMessage(args: ValidationArguments) {
          return `${args.property} must be a valid IP address`;
        },
      },
    });
  };
}

// Custom validation decorator for camera IDs
export function IsCameraId(validationOptions?: ValidationOptions) {
  return function (object: Object, propertyName: string) {
    registerDecorator({
      name: 'isCameraId',
      target: object.constructor,
      propertyName: propertyName,
      options: validationOptions,
      validator: {
        validate(value: any, args: ValidationArguments) {
          if (typeof value !== 'string') return false;
          
          // Camera ID format: cam-XXX where XXX is alphanumeric
          const cameraIdRegex = /^cam-[a-zA-Z0-9]{3,10}$/;
          return cameraIdRegex.test(value);
        },
        defaultMessage(args: ValidationArguments) {
          return `${args.property} must be a valid camera ID in format 'cam-XXX'`;
        },
      },
    });
  };
}

// Custom validation decorator for license plates
export function IsLicensePlate(validationOptions?: ValidationOptions) {
  return function (object: Object, propertyName: string) {
    registerDecorator({
      name: 'isLicensePlate',
      target: object.constructor,
      propertyName: propertyName,
      options: validationOptions,
      validator: {
        validate(value: any, args: ValidationArguments) {
          if (typeof value !== 'string') return false;
          
          // License plate format: 1-3 letters, 1-4 numbers, optional 1-2 letters
          const licensePlateRegex = /^[A-Z]{1,3}\d{1,4}[A-Z]{0,2}$/;
          return licensePlateRegex.test(value.toUpperCase());
        },
        defaultMessage(args: ValidationArguments) {
          return `${args.property} must be a valid license plate number`;
        },
      },
    });
  };
}

// Custom validation decorator for coordinates
export function IsCoordinate(validationOptions?: ValidationOptions) {
  return function (object: Object, propertyName: string) {
    registerDecorator({
      name: 'isCoordinate',
      target: object.constructor,
      propertyName: propertyName,
      options: validationOptions,
      validator: {
        validate(value: any, args: ValidationArguments) {
          if (typeof value !== 'number') return false;
          
          // Latitude: -90 to 90, Longitude: -180 to 180
          const isLatitude = args.property.toLowerCase().includes('lat');
          if (isLatitude) {
            return value >= -90 && value <= 90;
          } else {
            return value >= -180 && value <= 180;
          }
        },
        defaultMessage(args: ValidationArguments) {
          const isLatitude = args.property.toLowerCase().includes('lat');
          if (isLatitude) {
            return `${args.property} must be a valid latitude between -90 and 90`;
          } else {
            return `${args.property} must be a valid longitude between -180 and 180`;
          }
        },
      },
    });
  };
}

// Custom validation decorator for file size
export function IsFileSize(maxSizeInMB: number, validationOptions?: ValidationOptions) {
  return function (object: Object, propertyName: string) {
    registerDecorator({
      name: 'isFileSize',
      target: object.constructor,
      propertyName: propertyName,
      options: validationOptions,
      validator: {
        validate(value: any, args: ValidationArguments) {
          if (!value || !value.size) return false;
          
          const maxSizeInBytes = maxSizeInMB * 1024 * 1024;
          return value.size <= maxSizeInBytes;
        },
        defaultMessage(args: ValidationArguments) {
          return `${args.property} file size must not exceed ${maxSizeInMB}MB`;
        },
      },
    });
  };
}

// Custom validation decorator for file type
export function IsFileType(allowedTypes: string[], validationOptions?: ValidationOptions) {
  return function (object: Object, propertyName: string) {
    registerDecorator({
      name: 'isFileType',
      target: object.constructor,
      propertyName: propertyName,
      options: validationOptions,
      validator: {
        validate(value: any, args: ValidationArguments) {
          if (!value || !value.mimetype) return false;
          
          return allowedTypes.includes(value.mimetype);
        },
        defaultMessage(args: ValidationArguments) {
          return `${args.property} must be one of the following file types: ${allowedTypes.join(', ')}`;
        },
      },
    });
  };
}
