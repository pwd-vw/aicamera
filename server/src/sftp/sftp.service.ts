import { Injectable } from '@nestjs/common';
import * as SftpClient from 'ssh2-sftp-client';

@Injectable()
export class SftpService {
  private sftp = new SftpClient();

  async uploadFile(localPath: string, remotePath: string) {
    await this.sftp.connect({
      host: 'your-sftp-host',
      port: 22,
      username: 'your-username',
      password: 'your-password',
    });
    await this.sftp.put(localPath, remotePath);
    await this.sftp.end();
  }
}