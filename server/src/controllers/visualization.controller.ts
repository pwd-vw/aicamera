import { Controller, Get, Post, Put, Delete, Body, Param, Query } from '@nestjs/common';
import { VisualizationService } from '../services/visualization.service';
import { VisualizationType } from '../../generated/prisma';

@Controller('visualizations')
export class VisualizationController {
  constructor(private readonly visualizationService: VisualizationService) {}

  @Post()
  async create(@Body() data: {
    name: string;
    description?: string;
    type: VisualizationType;
    configuration: any;
    dataSource: string;
    refreshInterval?: number;
    isActive?: boolean;
    createdBy?: string;
  }) {
    return this.visualizationService.create(data);
  }

  @Get()
  async findAll(
    @Query('type') type?: VisualizationType,
    @Query('isActive') isActive?: boolean,
  ) {
    const where: any = {};
    if (type) where.type = type;
    if (isActive !== undefined) where.isActive = isActive;
    
    return this.visualizationService.findAll(where);
  }

  @Get('active')
  async getActiveVisualizations() {
    return this.visualizationService.getActiveVisualizations();
  }

  @Get('type/:type')
  async findByType(@Param('type') type: VisualizationType) {
    return this.visualizationService.findByType(type);
  }

  @Get(':id')
  async findById(@Param('id') id: string) {
    return this.visualizationService.findById(id);
  }

  @Put(':id')
  async update(
    @Param('id') id: string,
    @Body() data: Partial<{
      name: string;
      description: string;
      type: VisualizationType;
      configuration: any;
      dataSource: string;
      refreshInterval: number;
      isActive: boolean;
    }>,
  ) {
    return this.visualizationService.update(id, data);
  }

  @Delete(':id')
  async delete(@Param('id') id: string) {
    return this.visualizationService.delete(id);
  }
}
