# 🔑 SSH Keys และ GitHub Secrets Setup Guide

## 📋 **สิ่งที่ต้องทำ:**

### **1. ติดตั้ง SSH Public Key บนเครื่อง Server และ Edge**

#### **บนเครื่อง Server (lprserver.tail605477.ts.net):**
```bash
# SSH เข้าไปที่ server
ssh lpruser@lprserver.tail605477.ts.net

# เพิ่ม public key ลงใน authorized_keys
echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCeL4SoHelb+9aDlO1/wrqw/C+VGA5DMlRJ+U8mbNpn+8ueczEgApme8PJC6te4lt4LSOkLyKSgLLOts3fQpKPabtFER4ssgyHXrn8G2v1ObTtzwtYIpE5qTWJJiGXs63zMXrJW08D5cTLtTqxoVBmV8NhT2IEuejOWhf6BHH4xZahx2AGprWNvc7gSJCxRkScPNjTtlj2kj85rNlwCgzJJV3052NSyLg8Th4CdYqcn43J2EwBDjIIfMuySE1dFav2nnhScgu/JF9HouYggnfxbOblasmCVWNK1ADsZmEgnAP9G/Y559MQLcwF0wbef9Np23KIOet0clOHqmzH8ZziUKeItyx8SR82KhuCbvVTfiiAxPsfQoR5cQ+0WaTXCs5ulLQseRY9utno+Tq2NpDaG6SezkB5UOk8H9eYxOc/Ob4wDVrA4A87PXFo7s4CqD3fCRznA7gr6GmR9qE9WXbfuz2uWjcr+VNFpaZxV4UF1WenuHxMKRwfRqLyn2wRnJiXijJ4sQ4MTYPGewqeqa3XCQySGbiPmxzdsUpfROWSk52H459hmXh1SoPYnuSo1Pk3fkxAk9pwWaIo5+gPAt6Vmv6ANeTOX+BP3hTfJ73gAILc/3qx08lLQT6bcDRh/JMp3oyjgTjUZVV4jAvUPrXoDb/2w/zKRjeH518lswvRLnw== aicamera-deployment@github.com" >> ~/.ssh/authorized_keys

# ตั้งค่าสิทธิ์
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh
```

#### **บนเครื่อง Edge (aicamera1, aicamera2, aicamera3):**
```bash
# SSH เข้าไปที่ edge device
ssh camuser@aicamera1.tail605477.ts.net
ssh camuser@aicamera2.tail605477.ts.net
ssh camuser@aicamera3.tail605477.ts.net

# เพิ่ม public key ลงใน authorized_keys (ทำบนทุกเครื่อง)
echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCeL4SoHelb+9aDlO1/wrqw/C+VGA5DMlRJ+U8mbNpn+8ueczEgApme8PJC6te4lt4LSOkLyKSgLLOts3fQpKPabtFER4ssgyHXrn8G2v1ObTtzwtYIpE5qTWJJiGXs63zMXrJW08D5cTLtTqxoVBmV8NhT2IEuejOWhf6BHH4xZahx2AGprWNvc7gSJCxRkScPNjTtlj2kj85rNlwCgzJJV3052NSyLg8Th4CdYqcn43J2EwBDjIIfMuySE1dFav2nnhScgu/JF9HouYggnfxbOblasmCVWNK1ADsZmEgnAP9G/Y559MQLcwF0wbef9Np23KIOet0clOHqmzH8ZziUKeItyx8SR82KhuCbvVTfiiAxPsfQoR5cQ+0WaTXCs5ulLQseRY9utno+Tq2NpDaG6SezkB5UOk8H9eYxOc/Ob4wDVrA4A87PXFo7s4CqD3fCRznA7gr6GmR9qE9WXbfuz2uWjcr+VNFpaZxV4UF1WenuHxMKRwfRqLyn2wRnJiXijJ4sQ4MTYPGewqeqa3XCQySGbiPmxzdsUpfROWSk52H459hmXh1SoPYnuSo1Pk3fkxAk9pwWaIo5+gPAt6Vmv6ANeTOX+BP3hTfJ73gAILc/3qx08lLQT6bcDRh/JMp3oyjgTjUZVV4jAvUPrXoDb/2w/zKRjeH518lswvRLnw== aicamera-deployment@github.com" >> ~/.ssh/authorized_keys

# ตั้งค่าสิทธิ์
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh
```

### **2. ตั้งค่า GitHub Repository Secrets**

#### **ไปที่ GitHub Repository:**
1. เปิด repository: `https://github.com/popwandee/aicamera`
2. ไปที่ **Settings** → **Secrets and variables** → **Actions**
3. คลิก **New repository secret**

#### **เพิ่ม Secrets ต่อไปนี้:**

**SSH_PRIVATE_KEY:**
```
-----BEGIN OPENSSH PRIVATE KEY-----
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
-----END OPENSSH PRIVATE KEY-----
```

**SERVER_USER:**
```
lpruser
```

**EDGE_USER:**
```
camuser
```

### **3. ตั้งค่า Repository Variables**

#### **ไปที่ Variables tab และเพิ่ม:**

**ENABLE_SERVER_DEPLOYMENT:**
```
true
```

**ENABLE_EDGE_DEPLOYMENT:**
```
true
```

### **4. ทดสอบ SSH Connection**

#### **ทดสอบจาก GitHub Actions:**
หลังจากตั้งค่าเสร็จแล้ว ให้ push โค้ดใหม่เพื่อทดสอบ:

```bash
git add .
git commit -m "test: Test SSH connection and deployment"
git push origin main
```

#### **ตรวจสอบผลลัพธ์:**
1. ไปที่ **Actions** tab ใน GitHub
2. ดูว่า workflow ทำงานสำเร็จหรือไม่
3. ตรวจสอบ logs ว่ามี SSH connection error หรือไม่

### **5. ตรวจสอบ Deployment**

#### **Server Health Check:**
```bash
curl http://lprserver.tail605477.ts.net:3000/health
```

#### **Edge Health Check:**
```bash
curl http://aicamera1.tail605477.ts.net/health
curl http://aicamera2.tail605477.ts.net/health
curl http://aicamera3.tail605477.ts.net/health
```

## ⚠️ **หมายเหตุสำคัญ:**

1. **Private Key**: เก็บไฟล์ `aicamera_deploy_key` ไว้อย่างปลอดภัย
2. **Public Key**: ต้องติดตั้งบนทุกเครื่อง target
3. **Permissions**: ต้องตั้งค่าไฟล์ permissions ให้ถูกต้อง
4. **Secrets**: อย่าเปิดเผย secrets ในโค้ดหรือ logs

## 🔧 **แก้ไขปัญหา:**

หากเจอปัญหา SSH connection:
1. ตรวจสอบว่า public key ถูกเพิ่มใน `~/.ssh/authorized_keys` แล้ว
2. ตรวจสอบ file permissions (600 สำหรับ authorized_keys, 700 สำหรับ .ssh)
3. ตรวจสอบว่า GitHub secrets ถูกตั้งค่าถูกต้อง
4. ดู logs ใน GitHub Actions เพื่อหาข้อผิดพลาด
