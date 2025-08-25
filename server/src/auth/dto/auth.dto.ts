import { IsEmail, IsString, MinLength, IsOptional, IsEnum, Matches, Length, IsNotEmpty } from 'class-validator';
import { UserRole } from '../../../generated/prisma';
import { IsStrongPassword } from '../../decorators/validation.decorators';

export class LoginDto {
  @IsString()
  @IsNotEmpty({ message: 'Username is required' })
  @Length(3, 50, { message: 'Username must be between 3 and 50 characters' })
  @Matches(/^[a-zA-Z0-9_-]+$/, { message: 'Username can only contain letters, numbers, underscores, and hyphens' })
  username: string;

  @IsString()
  @IsNotEmpty({ message: 'Password is required' })
  @MinLength(6, { message: 'Password must be at least 6 characters long' })
  password: string;
}

export class RegisterDto {
  @IsEmail({}, { message: 'Please provide a valid email address' })
  @IsNotEmpty({ message: 'Email is required' })
  email: string;

  @IsString()
  @IsNotEmpty({ message: 'Username is required' })
  @Length(3, 50, { message: 'Username must be between 3 and 50 characters' })
  @Matches(/^[a-zA-Z0-9_-]+$/, { message: 'Username can only contain letters, numbers, underscores, and hyphens' })
  username: string;

  @IsString()
  @IsNotEmpty({ message: 'Password is required' })
  @IsStrongPassword({ message: 'Password must be strong (8+ chars, uppercase, lowercase, number, special char)' })
  password: string;

  @IsOptional()
  @IsString()
  @Length(1, 50, { message: 'First name must be between 1 and 50 characters' })
  @Matches(/^[a-zA-Z\s-']+$/, { message: 'First name can only contain letters, spaces, hyphens, and apostrophes' })
  firstName?: string;

  @IsOptional()
  @IsString()
  @Length(1, 50, { message: 'Last name must be between 1 and 50 characters' })
  @Matches(/^[a-zA-Z\s-']+$/, { message: 'Last name can only contain letters, spaces, hyphens, and apostrophes' })
  lastName?: string;

  @IsOptional()
  @IsEnum(UserRole, { message: 'Role must be one of: admin, operator, viewer' })
  role?: UserRole;
}

export class ChangePasswordDto {
  @IsString()
  @IsNotEmpty({ message: 'Current password is required' })
  @MinLength(6, { message: 'Current password must be at least 6 characters long' })
  currentPassword: string;

  @IsString()
  @IsNotEmpty({ message: 'New password is required' })
  @IsStrongPassword({ message: 'New password must be strong (8+ chars, uppercase, lowercase, number, special char)' })
  newPassword: string;
}

export class UpdateProfileDto {
  @IsOptional()
  @IsString()
  @Length(1, 50, { message: 'First name must be between 1 and 50 characters' })
  @Matches(/^[a-zA-Z\s-']+$/, { message: 'First name can only contain letters, spaces, hyphens, and apostrophes' })
  firstName?: string;

  @IsOptional()
  @IsString()
  @Length(1, 50, { message: 'Last name must be between 1 and 50 characters' })
  @Matches(/^[a-zA-Z\s-']+$/, { message: 'Last name can only contain letters, spaces, hyphens, and apostrophes' })
  lastName?: string;

  @IsOptional()
  @IsEmail({}, { message: 'Please provide a valid email address' })
  email?: string;
}

export class AuthResponseDto {
  accessToken: string;
  refreshToken: string;
  user: {
    id: string;
    email: string;
    username: string;
    role: UserRole;
    firstName?: string;
    lastName?: string;
  };
}
