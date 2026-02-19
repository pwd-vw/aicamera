import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository, DataSource } from 'typeorm';
import { Camera, Detection, Analytics, CameraHealth } from '../entities';

export interface CameraSummaryRow {
  id: string;
  camera_id: string;
  name: string;
  status: string;
  location_lat: string | null;
  location_lng: string | null;
  location_address: string | null;
  total_detections: string;
  unique_plates: string;
  average_confidence: string | null;
  last_detection: Date | null;
  created_at: Date;
  updated_at: Date;
}

@Injectable()
export class DeviceService {
  constructor(
    @InjectRepository(Camera)
    private readonly cameraRepo: Repository<Camera>,
    @InjectRepository(Detection)
    private readonly detectionRepo: Repository<Detection>,
    @InjectRepository(Analytics)
    private readonly analyticsRepo: Repository<Analytics>,
    @InjectRepository(CameraHealth)
    private readonly cameraHealthRepo: Repository<CameraHealth>,
    private readonly dataSource: DataSource,
  ) {}

  async findAllCameras(): Promise<Camera[]> {
    return this.cameraRepo.find({ order: { createdAt: 'DESC' } });
  }

  async findCameraById(id: string): Promise<Camera | null> {
    return this.cameraRepo.findOne({ where: { id } });
  }

  async findCameraByCameraId(cameraId: string): Promise<Camera | null> {
    return this.cameraRepo.findOne({ where: { cameraId } });
  }

  async createCamera(data: Partial<Camera>): Promise<Camera> {
    const camera = this.cameraRepo.create(data);
    return this.cameraRepo.save(camera);
  }

  async updateCamera(id: string, data: Partial<Camera>): Promise<Camera> {
    await this.cameraRepo.update(id, data as Record<string, unknown>);
    const updated = await this.cameraRepo.findOne({ where: { id } });
    if (!updated) throw new Error('Camera not found');
    return updated;
  }

  async deleteCamera(id: string): Promise<void> {
    await this.cameraRepo.delete(id);
  }

  async findAllDetections(cameraId?: string, limit = 100): Promise<Detection[]> {
    const qb = this.detectionRepo
      .createQueryBuilder('d')
      .leftJoinAndSelect('d.camera', 'c')
      .orderBy('d.timestamp', 'DESC')
      .take(limit);
    if (cameraId) qb.andWhere('d.camera_id = :cameraId', { cameraId });
    return qb.getMany();
  }

  async findDetectionsByCameraId(cameraId: string, limit = 100): Promise<Detection[]> {
    return this.detectionRepo.find({
      where: { cameraId },
      relations: ['camera'],
      order: { timestamp: 'DESC' },
      take: limit,
    });
  }

  async createDetection(data: Partial<Detection>): Promise<Detection> {
    const detection = this.detectionRepo.create(data);
    return this.detectionRepo.save(detection);
  }

  async getCameraSummary(): Promise<CameraSummaryRow[]> {
    const rows = await this.dataSource.query('SELECT * FROM camera_summary');
    return rows as CameraSummaryRow[];
  }

  async runUpdateDailyAnalytics(): Promise<void> {
    await this.dataSource.query('SELECT update_daily_analytics()');
  }

  async findAllCameraHealth(cameraId?: string, limit = 200): Promise<CameraHealth[]> {
    const qb = this.cameraHealthRepo
      .createQueryBuilder('h')
      .leftJoinAndSelect('h.camera', 'c')
      .orderBy('h.timestamp', 'DESC')
      .take(limit);
    if (cameraId) qb.andWhere('h.camera_id = :cameraId', { cameraId });
    return qb.getMany();
  }

  async createCameraHealth(data: Partial<CameraHealth>): Promise<CameraHealth> {
    const health = this.cameraHealthRepo.create(data);
    return this.cameraHealthRepo.save(health);
  }
}
