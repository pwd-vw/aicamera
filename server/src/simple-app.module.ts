import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { AuthModule } from './auth/auth.module';

const GlobalConfigModule = ConfigModule.forRoot({ isGlobal: true }) as unknown as import('@nestjs/common').DynamicModule;

@Module({
  imports: [GlobalConfigModule, AuthModule],
  controllers: [],
  providers: [],
})
export class SimpleAppModule {}
