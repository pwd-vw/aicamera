import { Injectable, NestInterceptor, ExecutionContext, CallHandler, BadRequestException } from '@nestjs/common';
import { Observable, throwError } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { ValidationError } from 'class-validator';

@Injectable()
export class ValidationInterceptor implements NestInterceptor {
  intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
    return next.handle().pipe(
      map(data => {
        // Transform successful responses
        return {
          success: true,
          data,
          timestamp: new Date().toISOString(),
        };
      }),
      catchError(error => {
        // Handle validation errors
        if (error instanceof BadRequestException) {
          const response = error.getResponse() as any;
          
          if (response.message && Array.isArray(response.message)) {
            // Format validation errors
            const formattedErrors = this.formatValidationErrors(response.message);
            
            return throwError(() => new BadRequestException({
              success: false,
              message: 'Validation failed',
              errors: formattedErrors,
              timestamp: new Date().toISOString(),
            }));
          }
        }
        
        // Handle other errors
        return throwError(() => error);
      }),
    );
  }

  private formatValidationErrors(errors: ValidationError[]): any[] {
    const formattedErrors = [];

    for (const error of errors) {
      if (error.constraints) {
        formattedErrors.push({
          field: error.property,
          value: error.value,
          message: Object.values(error.constraints)[0],
          code: this.getErrorCode(error),
        });
      }

      if (error.children && error.children.length > 0) {
        formattedErrors.push(...this.formatValidationErrors(error.children));
      }
    }

    return formattedErrors;
  }

  private getErrorCode(error: ValidationError): string {
    const constraint = Object.keys(error.constraints)[0];
    
    switch (constraint) {
      case 'isNotEmpty':
        return 'FIELD_REQUIRED';
      case 'isEmail':
        return 'INVALID_EMAIL';
      case 'minLength':
        return 'MIN_LENGTH';
      case 'maxLength':
        return 'MAX_LENGTH';
      case 'length':
        return 'INVALID_LENGTH';
      case 'matches':
        return 'INVALID_FORMAT';
      case 'isEnum':
        return 'INVALID_ENUM_VALUE';
      case 'isNumber':
        return 'INVALID_NUMBER';
      case 'min':
        return 'MIN_VALUE';
      case 'max':
        return 'MAX_VALUE';
      case 'isDateString':
        return 'INVALID_DATE';
      case 'isUrl':
        return 'INVALID_URL';
      case 'isIPAddress':
        return 'INVALID_IP_ADDRESS';
      case 'isStrongPassword':
        return 'WEAK_PASSWORD';
      case 'isCameraId':
        return 'INVALID_CAMERA_ID';
      case 'isLicensePlate':
        return 'INVALID_LICENSE_PLATE';
      case 'isCoordinate':
        return 'INVALID_COORDINATE';
      case 'isFileSize':
        return 'FILE_TOO_LARGE';
      case 'isFileType':
        return 'INVALID_FILE_TYPE';
      default:
        return 'VALIDATION_ERROR';
    }
  }
}
