import { Injectable } from '@nestjs/common';
import { PrismaService } from '../database/prisma.service';
import { Visualization, VisualizationType } from '../../generated/prisma';

@Injectable()
export class VisualizationService {
  constructor(private prisma: PrismaService) {}

  async create(data: {
    name: string;
    description?: string;
    type: VisualizationType;
    configuration: any;
    dataSource: string;
    refreshInterval?: number;
    isActive?: boolean;
    createdBy?: string;
  }): Promise<Visualization> {
    return this.prisma.visualization.create({
      data: {
        name: data.name,
        description: data.description,
        type: data.type,
        configuration: data.configuration,
        dataSource: data.dataSource,
        refreshInterval: data.refreshInterval || 300,
        isActive: data.isActive ?? true,
        createdBy: data.createdBy,
      },
    });
  }

  async findAll(where?: {
    type?: VisualizationType;
    isActive?: boolean;
  }): Promise<Visualization[]> {
    return this.prisma.visualization.findMany({
      where,
      orderBy: { createdAt: 'desc' },
    });
  }

  async findById(id: string): Promise<Visualization | null> {
    return this.prisma.visualization.findUnique({
      where: { id },
    });
  }

  async update(
    id: string,
    data: Partial<{
      name: string;
      description: string;
      type: VisualizationType;
      configuration: any;
      dataSource: string;
      refreshInterval: number;
      isActive: boolean;
    }>,
  ): Promise<Visualization> {
    return this.prisma.visualization.update({
      where: { id },
      data,
    });
  }

  async delete(id: string): Promise<Visualization> {
    return this.prisma.visualization.delete({
      where: { id },
    });
  }

  async findByType(type: VisualizationType): Promise<Visualization[]> {
    return this.prisma.visualization.findMany({
      where: { type, isActive: true },
      orderBy: { createdAt: 'desc' },
    });
  }

  async getActiveVisualizations(): Promise<Visualization[]> {
    return this.prisma.visualization.findMany({
      where: { isActive: true },
      orderBy: { createdAt: 'desc' },
    });
  }
}
