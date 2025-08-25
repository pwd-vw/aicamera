import { ValidationPipe, ValidationPipeOptions } from '@nestjs/common';

export const validationConfig: ValidationPipeOptions = {
  transform: true,
  whitelist: true,
  forbidNonWhitelisted: true,
  forbidUnknownValues: true,
  disableErrorMessages: process.env.NODE_ENV === 'production',
  validationError: {
    target: false,
    value: false,
  },
  transformOptions: {
    enableImplicitConversion: true,
  },
  exceptionFactory: (errors) => {
    const formattedErrors = errors.map(error => ({
      field: error.property,
      value: error.value,
      constraints: error.constraints,
      children: error.children?.map(child => ({
        field: child.property,
        value: child.value,
        constraints: child.constraints,
      })),
    }));

    return {
      statusCode: 400,
      message: 'Validation failed',
      errors: formattedErrors,
      timestamp: new Date().toISOString(),
    };
  },
};

export const createValidationPipe = (options?: Partial<ValidationPipeOptions>): ValidationPipe => {
  return new ValidationPipe({
    ...validationConfig,
    ...options,
  });
};
