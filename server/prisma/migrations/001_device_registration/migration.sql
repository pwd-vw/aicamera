-- CreateEnum
CREATE TYPE "DeviceRegistrationStatus" AS ENUM ('pending_approval', 'approved', 'rejected', 'provisioned', 'active', 'inactive');

-- CreateEnum
CREATE TYPE "DeviceRegistrationType" AS ENUM ('self_registration', 'pre_provision', 'admin_approval');

-- CreateTable
CREATE TABLE "device_registrations" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "serial_number" TEXT NOT NULL,
    "device_model" TEXT NOT NULL,
    "device_type" TEXT NOT NULL DEFAULT 'camera',
    "ip_address" TEXT,
    "mac_address" TEXT,
    "location_lat" DECIMAL(10,8),
    "location_lng" DECIMAL(11,8),
    "location_address" TEXT,
    "registration_status" "DeviceRegistrationStatus" NOT NULL DEFAULT 'pending_approval',
    "registration_type" "DeviceRegistrationType" NOT NULL,
    "api_key" TEXT,
    "jwt_secret" TEXT,
    "certificate" TEXT,
    "shared_secret" TEXT,
    "metadata" JSONB NOT NULL DEFAULT '{}',
    "approved_by" UUID,
    "approved_at" TIMESTAMPTZ(6),
    "rejected_by" UUID,
    "rejected_at" TIMESTAMPTZ(6),
    "rejection_reason" TEXT,
    "last_heartbeat" TIMESTAMPTZ(6),
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,

    CONSTRAINT "device_registrations_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "device_registrations_serial_number_key" ON "device_registrations"("serial_number");

-- CreateIndex
CREATE UNIQUE INDEX "device_registrations_api_key_key" ON "device_registrations"("api_key");

-- AddForeignKey
ALTER TABLE "device_registrations" ADD CONSTRAINT "device_registrations_approved_by_fkey" FOREIGN KEY ("approved_by") REFERENCES "users"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "device_registrations" ADD CONSTRAINT "device_registrations_rejected_by_fkey" FOREIGN KEY ("rejected_by") REFERENCES "users"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AlterTable
ALTER TABLE "cameras" ADD COLUMN "device_registration_id" UUID;

-- CreateIndex
CREATE UNIQUE INDEX "cameras_device_registration_id_key" ON "cameras"("device_registration_id");

-- AddForeignKey
ALTER TABLE "cameras" ADD CONSTRAINT "cameras_device_registration_id_fkey" FOREIGN KEY ("device_registration_id") REFERENCES "device_registrations"("id") ON DELETE SET NULL ON UPDATE CASCADE;