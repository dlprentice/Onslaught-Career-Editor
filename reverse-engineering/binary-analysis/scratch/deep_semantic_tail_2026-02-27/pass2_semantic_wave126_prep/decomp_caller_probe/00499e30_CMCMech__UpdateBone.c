/* address: 0x00499e30 */
/* name: CMCMech__UpdateBone */
/* signature: undefined CMCMech__UpdateBone(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CMCMech__UpdateBone(int *param_1,float *param_2,float *param_3,int param_4,int *param_5,int *param_6
                   ,float param_7,float param_8)

{
  float fVar1;
  byte bVar2;
  int iVar3;
  undefined8 uVar4;
  float fVar5;
  bool bVar6;
  char cVar7;
  float *pfVar8;
  int iVar9;
  int iVar10;
  float *extraout_EAX;
  void *pvVar11;
  float *extraout_EAX_00;
  float *extraout_EAX_01;
  float *extraout_EAX_02;
  float *extraout_EAX_03;
  void *extraout_EAX_04;
  void *this;
  float *extraout_EAX_05;
  int *piVar12;
  int iVar13;
  int iVar14;
  int *piVar15;
  undefined4 *puVar16;
  float *this_00;
  void *unaff_EDI;
  float *pfVar17;
  undefined4 *puVar18;
  float10 fVar19;
  float10 fVar20;
  double dVar21;
  undefined1 local_1c8 [16];
  undefined4 local_1b8;
  int local_1b4;
  float local_1b0 [12];
  int local_180;
  undefined4 local_17c;
  undefined1 local_178 [16];
  float local_168;
  float local_164;
  float local_160;
  float local_15c;
  float local_158;
  float local_154;
  float local_150;
  float local_14c;
  int local_148;
  int local_144;
  int local_140;
  float local_13c [6];
  float local_124;
  float local_11c;
  float local_118;
  float local_114;
  float local_110;
  float local_10c;
  float local_108;
  float local_104;
  float local_100;
  float local_fc [4];
  float local_ec;
  float local_e8;
  float local_e4;
  float local_e0;
  float local_dc;
  float local_d8;
  float local_d4;
  float local_d0;
  float local_cc [8];
  float local_ac;
  float local_a8;
  float local_a4;
  uint local_9c;
  void *local_98;
  float local_94;
  float local_90;
  float local_8c;
  undefined4 local_88;
  int *local_84;
  float local_80;
  float local_7c;
  undefined8 local_78;
  uint local_70;
  int *local_6c;
  float local_68;
  float local_64;
  float local_60;
  float local_5c;
  float local_58;
  float local_54;
  float local_50;
  float local_4c;
  float local_48;
  float local_44;
  float local_40;
  float local_3c;
  float local_38;
  float local_34;
  float local_30;
  float local_2c;
  char local_25;
  float local_24;
  float local_20;
  undefined8 local_1c;
  char local_11;
  void *local_10;
  undefined1 *puStack_c;
  undefined4 local_8;

  this_00 = param_3;
  puStack_c = &LAB_005d332b;
  local_10 = ExceptionList;
  local_1b8 = 0x49;
  uVar4 = rdtsc();
  local_17c = (undefined4)((ulonglong)uVar4 >> 0x20);
  local_1b4 = (int)uVar4;
  local_8 = 0;
  ExceptionList = &local_10;
  local_180 = local_1b4;
  local_6c = param_1;
  if (param_1[0x2b] == 0) {
    ExceptionList = &local_10;
    CMCMech__Init(*(undefined4 *)(param_4 + 0x128));
  }
  local_48 = 1.0;
  local_40 = 0.0;
  local_44 = 0.0;
  local_fc[0] = 1.0;
  local_fc[2] = 0.0;
  local_25 = '\0';
  local_11 = '\0';
  local_fc[1] = 0.0;
  local_fc[3] = local_3c;
  pfVar8 = (float *)Vec3__SetXYZ();
  local_ec = *pfVar8;
  local_e8 = pfVar8[1];
  local_e4 = pfVar8[2];
  local_e0 = pfVar8[3];
  pfVar8 = (float *)Vec3__SetXYZ();
  local_dc = *pfVar8;
  local_10c = 0.0;
  local_d8 = pfVar8[1];
  local_108 = 0.0;
  local_104 = 0.0;
  local_d4 = pfVar8[2];
  local_140 = 0;
  local_84 = (int *)param_1[2];
  local_d0 = pfVar8[3];
  iVar9 = *(int *)(param_4 + 0x88);
  bVar2 = **(byte **)(param_4 + 0xc4);
  iVar14 = param_1[0x39];
  local_70 = CONCAT31(local_70._1_3_,bVar2);
  iVar10 = *(int *)(*(int *)(iVar14 + 0xc) + iVar9 * 4);
  if (iVar10 == 1) {
    pfVar8 = (float *)((uint)bVar2 * 0x10 + *(int *)(param_4 + 200));
    param_7 = 0.0;
    param_8 = 0.0;
    local_78 = local_78 & 0xffffffff;
    local_54 = param_3[4] * *pfVar8 + param_3[5] * pfVar8[1] + param_3[6] * pfVar8[2];
    local_50 = param_3[8] * *pfVar8 + param_3[9] * pfVar8[1] + param_3[10] * pfVar8[2];
    local_94 = *param_3 * *pfVar8 + param_3[1] * pfVar8[1] + param_3[2] * pfVar8[2] + *param_2;
    local_90 = local_54 + param_2[1];
    local_8c = local_50 + param_2[2];
    iVar9 = (**(code **)(*param_1 + 0x28))();
    if (iVar9 == 0) {
      if (local_84 == (int *)0x0) {
        piVar12 = (int *)0x0;
      }
      else {
        piVar12 = local_84 + -2;
      }
      local_98 = (void *)piVar12[0x45];
      fVar19 = (float10)(**(code **)(*param_1 + 0x2c))();
      local_1c = (double)CONCAT44((float)fVar19,(float)local_1c);
      fVar19 = (float10)(**(code **)(*param_1 + 0x30))();
      CSquadNormal__Helper_004062d0
                (local_13c,local_98,local_1c._4_4_,(float)fVar19,(float)unaff_EDI);
      local_38 = local_13c[2] * _DAT_005d8be0;
      local_34 = local_124 * _DAT_005d8be0;
      local_30 = local_114 * _DAT_005d8be0;
    }
    else {
      CMonitor__Helper_0047ec60(0x6fadc8,&local_48,&local_94);
      local_38 = local_48;
      local_34 = local_44;
      local_30 = local_40;
    }
    fVar1 = (float)param_1[4];
    local_40 = 0.0;
    fVar5 = _DAT_005d8568 - (float)param_1[4];
    local_58 = local_38 * fVar5;
    local_54 = fVar5 * local_34;
    local_38 = local_58 + fVar1 * (float)param_1[0x22];
    local_48 = 0.0;
    local_34 = local_54 + fVar1 * (float)param_1[0x23];
    local_44 = -1.0;
    param_1[0x22] = (int)local_38;
    local_30 = fVar5 * local_30 + fVar1 * (float)param_1[0x24];
    param_1[0x23] = (int)local_34;
    param_1[0x24] = (int)local_30;
    param_1[0x25] = (int)local_3c;
    local_2c = local_3c;
    Vec3__SetXYZ();
    local_20 = local_44;
    local_24 = local_48;
    local_1c = (double)CONCAT44(local_3c,local_40);
    Vec3__Cross(&local_68,&local_38,&local_24,unaff_EDI);
    Vec3__Cross(&local_68,&local_58,&local_38,unaff_EDI);
    SQRT__Wrapper_00406d50(&local_38);
    SQRT__Wrapper_00406d50(&local_58);
    SQRT__Wrapper_00406d50(&local_68);
    local_fc[2] = local_68;
    local_fc[0] = local_38;
    local_e4 = local_64;
    local_fc[1] = local_58;
    local_d4 = local_60;
    local_ec = local_34;
    local_e8 = local_54;
    iVar9 = 0;
    local_dc = local_30;
    local_d8 = local_50;
    if (0 < param_1[0x2a]) {
      iVar14 = param_1[8];
      do {
        if (0 < *(int *)(iVar14 + iVar9 * 4)) {
          CMCMech__Helper_004aa820
                    (*(void **)(param_4 + 0x128),0x62df54,(void *)(iVar9 + 1),(int)unaff_EDI);
          CMCMech__Helper_004b0fb0();
          local_64 = local_54 - local_90;
          iVar14 = param_1[8];
          fVar19 = (float10)fsin((float10)*(int *)(iVar14 + iVar9 * 4) * (float10)_DAT_005db4f4 *
                                 (float10)_DAT_005db54c);
          local_1c = (double)CONCAT44((float)fVar19,(float)local_1c);
          local_68 = (float)(fVar19 * ((float10)local_58 - (float10)local_94));
          if (_DAT_005d85d8 < local_68) {
            local_68 = 5.0;
          }
          fVar1 = (float)fVar19 * local_64;
          if (_DAT_005d85d8 < (float)fVar19 * local_64) {
            fVar1 = _DAT_005d85d8;
          }
          if (local_68 < _DAT_005db2b0) {
            local_68 = -5.0;
          }
          if (fVar1 < _DAT_005db2b0) {
            fVar1 = _DAT_005db2b0;
          }
          param_7 = fVar1 + fVar1 + param_7;
          param_8 = local_68 + local_68 + param_8;
          local_78 = CONCAT44(local_78._4_4_ - (float)fVar19 * _DAT_005d85c0,(float)local_78);
        }
        iVar9 = iVar9 + 1;
      } while (iVar9 < param_1[0x2a]);
    }
    fVar1 = (float)param_1[0x26];
    fVar19 = (float10)param_7 * (float10)(float)param_1[0x26] * (float10)_DAT_005db4f4 *
             (float10)_DAT_005db54c;
    fVar20 = (float10)fcos(fVar19);
    local_64 = (float)fVar20;
    fVar19 = (float10)fsin(fVar19);
    local_60 = (float)-fVar19;
    pfVar8 = (float *)Vec3__SetXYZ();
    local_11c = *pfVar8;
    fVar19 = (float10)(param_8 * fVar1) * (float10)_DAT_005db4f4 * (float10)_DAT_005db54c;
    local_118 = pfVar8[1];
    fVar20 = (float10)fcos(fVar19);
    local_114 = pfVar8[2];
    local_110 = pfVar8[3];
    local_38 = (float)fVar20;
    fVar19 = (float10)fsin(fVar19);
    local_30 = (float)fVar19;
    pfVar8 = (float *)Vec3__SetXYZ();
    local_168 = *pfVar8;
    local_164 = pfVar8[1];
    local_160 = pfVar8[2];
    local_15c = pfVar8[3];
    pfVar8 = (float *)Vec3__SetXYZ();
    local_158 = *pfVar8;
    local_154 = pfVar8[1];
    local_150 = pfVar8[2];
    local_14c = pfVar8[3];
    if (local_84 == (int *)0x0) {
      piVar12 = (int *)0x0;
    }
    else {
      piVar12 = local_84 + -2;
    }
    if ((*(byte *)(piVar12 + 0xb) & 4) != 0) {
      local_11 = '\x01';
      local_10c = *param_2;
      local_108 = param_2[1];
      local_104 = param_2[2];
      local_100 = param_2[3];
      if (local_84 == (int *)0x0) {
        piVar12 = (int *)0x0;
      }
      else {
        piVar12 = local_84 + -2;
      }
      fVar19 = (float10)(**(code **)(*piVar12 + 0x1a8))();
      local_104 = (float)fVar19;
    }
    local_58 = local_d4 * local_11c + local_dc;
    local_54 = local_d8 * local_64 + local_d4 * local_118 + _DAT_005d856c;
    local_50 = local_d8 * local_60 + local_d4 * local_114 + _DAT_005d856c;
    Vec3__SetXYZ();
    Vec3__SetXYZ();
    Mat34__SetRows();
    local_48 = local_168 * local_a8 + local_158 * local_a4 + local_38 * local_ac;
    local_44 = local_164 * local_a8 + local_154 * local_a4;
    local_40 = local_ac * local_30 + local_160 * local_a8 + local_150 * local_a4;
    Vec3__SetXYZ();
    Vec3__SetXYZ();
    Mat34__SetRows();
    piVar12 = local_6c;
    pfVar8 = local_1b0;
    pfVar17 = local_fc;
    for (iVar9 = 0xc; iVar9 != 0; iVar9 = iVar9 + -1) {
      *pfVar17 = *pfVar8;
      pfVar8 = pfVar8 + 1;
      pfVar17 = pfVar17 + 1;
    }
    iVar9 = 0xc;
    pfVar8 = local_1b0;
    pfVar17 = (float *)(piVar12 + 0x16);
LAB_0049b5b6:
    for (; iVar9 != 0; iVar9 = iVar9 + -1) {
      *pfVar17 = *pfVar8;
      pfVar8 = pfVar8 + 1;
      pfVar17 = pfVar17 + 1;
    }
  }
  else {
    if (iVar10 == 2) {
      pvVar11 = *(void **)(*(int *)(iVar14 + 0x10) + iVar9 * 4);
      *param_5 = (int)pvVar11;
      pfVar8 = (float *)((uint)bVar2 * 0x10 + *(int *)(param_4 + 200));
      local_54 = param_3[6] * pfVar8[2] + param_3[4] * *pfVar8 + param_3[5] * pfVar8[1];
      local_50 = param_3[8] * *pfVar8 + pfVar8[1] * param_3[9] + pfVar8[2] * param_3[10];
      local_38 = *param_3 * *pfVar8 + pfVar8[2] * param_3[2] + pfVar8[1] * param_3[1] + *param_2;
      local_34 = local_54 + param_2[1];
      local_30 = local_50 + param_2[2];
      CMCMech__Helper_004aa820(*(void **)(param_4 + 0x128),0x62df54,pvVar11,(int)unaff_EDI);
      CMCMech__Helper_004b0fb0();
      pfVar8 = (float *)(*param_5 * 0x10 + -0x10 + param_1[9]);
      local_80 = local_38 - *pfVar8;
      local_7c = local_34 - pfVar8[1];
      fVar1 = pfVar8[2];
      *pfVar8 = local_38;
      pfVar8[1] = local_34;
      pfVar8[2] = local_30;
      pfVar8[3] = local_2c;
      local_24 = local_48;
      local_20 = local_44;
      local_1c._0_4_ = local_40;
      local_1c._4_4_ = local_3c;
      local_78 = CONCAT44(local_78._4_4_,local_30 - fVar1);
      fVar19 = (float10)CMCMech__GetFootHeight(&local_48,*param_5,param_8);
      local_24 = local_80 + local_24;
      local_20 = local_20 + local_7c;
      fVar1 = (float)((float10)(float)local_78 + fVar19);
      if (_DAT_005d8ba0 < param_7) {
        pfVar8 = (float *)(*param_5 * 0x10 + -0x10 + param_1[5]);
        *pfVar8 = local_24;
        pfVar8[1] = local_20;
        pfVar8[2] = fVar1;
        pfVar8[3] = local_1c._4_4_;
      }
      iVar9 = *param_5 * 0x10;
      local_68 = local_24 - *(float *)(iVar9 + -0x10 + param_1[5]);
      iVar9 = iVar9 + -0x10 + param_1[5];
      fVar5 = local_20 - *(float *)(iVar9 + 4);
      local_60 = fVar1 - *(float *)(iVar9 + 8);
      *(undefined4 *)(param_1[7] + -4 + *param_5 * 4) = 0;
      local_1c = (double)CONCAT44(param_1[8],fVar1);
      piVar12 = (int *)(param_1[8] + -4 + *param_5 * 4);
      iVar9 = *piVar12;
      if (iVar9 < 1) {
        if (SQRT(local_80 * local_80 + (float)local_78 * (float)local_78 + local_7c * local_7c) <=
            _DAT_005d8574) {
          local_98 = (void *)param_1[0x29];
          fVar1 = local_68 * local_68 + fVar5 * fVar5;
        }
        else {
          local_98 = (void *)param_1[0x28];
          fVar1 = local_68 * local_68 + fVar5 * fVar5 + local_60 * local_60;
        }
        local_78 = CONCAT44(SQRT(fVar1),(float)local_78);
        if ((float)local_98 < SQRT(fVar1)) {
          local_148 = 0;
          param_7 = 0.0;
          param_7._3_1_ = '\0';
          param_3._3_1_ = '\0';
          local_11 = '\x01';
          local_9c = 0;
          cVar7 = '\0';
          if (0 < param_1[0x2a]) {
            do {
              param_3._3_1_ = cVar7;
              local_144 = *(int *)((int)local_1c._4_4_ + local_9c * 4);
              if (local_144 != 0) {
                local_1c = (double)CONCAT44(param_1[8],(float)local_1c);
                local_144 = *(int *)(param_1[8] + local_9c * 4);
                iVar9 = (**(code **)(*param_1 + 0x34))();
                if (local_144 <= iVar9) {
                  local_148 = local_148 + 1;
                }
              }
              if (((local_144 == 0) || (0x5a < local_144)) && (local_9c != *param_5 - 1U)) {
                if (((byte)local_9c & 1) == 1) {
                  param_7 = (float)((local_9c & 1) << 0x18);
                }
                else {
                  param_3._3_1_ = '\x01';
                }
              }
              else if (local_9c == *param_5 - 2U) {
                local_11 = '\0';
              }
              local_9c = local_9c + 1;
              cVar7 = param_3._3_1_;
            } while ((int)local_9c < param_1[0x2a]);
          }
          if (((char)*param_5 - 1U & 1) != 1) {
            param_7._3_1_ = param_3._3_1_;
          }
          if ((param_7._3_1_ == '\0') || (local_11 == '\0')) {
            bVar6 = false;
          }
          else {
            bVar6 = true;
          }
          if (param_1[0x31] <= local_148) {
            bVar6 = false;
          }
          if (((float)local_98 + (float)local_98 < local_78._4_4_) || (bVar6)) {
            *(undefined4 *)(param_1[8] + -4 + *param_5 * 4) = 1;
          }
        }
      }
      else {
        local_1c = (double)(longlong)ROUND(param_7 * (float)param_1[0x27]);
        *piVar12 = (int)(float)local_1c + iVar9;
        iVar9 = *param_5;
        iVar14 = *(int *)(param_1[8] + -4 + iVar9 * 4);
        if (iVar14 < 0xb5) {
          fVar1 = (float)iVar14;
          local_58 = local_68 * fVar1;
          pfVar8 = (float *)(iVar9 * 0x10 + -0x10 + param_1[5]);
          local_50 = fVar1 * local_60;
          local_68 = local_58 * _DAT_005db54c;
          fVar1 = fVar5 * fVar1 * _DAT_005db54c;
          local_60 = local_50 * _DAT_005db54c;
          *pfVar8 = local_68 + *pfVar8;
          pfVar8[1] = fVar1 + pfVar8[1];
          pfVar8[2] = local_60 + pfVar8[2];
          *(undefined4 *)(param_1[6] + -4 + *param_5 * 4) = 0;
          fVar19 = (float10)fsin((float10)*(int *)(*param_5 * 4 + -4 + param_1[8]) *
                                 (float10)_DAT_005db4f4 * (float10)_DAT_005db54c);
          *(float *)(param_1[7] + -4 + *param_5 * 4) = (float)-(fVar19 * (float10)(float)param_1[3])
          ;
        }
        else {
          *(undefined4 *)(param_1[8] + -4 + iVar9 * 4) = 0;
        }
      }
      CMCMech__GetFootHeight(&local_48,*param_5,param_8);
      iVar9 = *param_5 * 0x10 + -0x10 + param_1[5];
      local_94 = *(float *)(*param_5 * 0x10 + -0x10 + param_1[5]);
      local_90 = *(float *)(iVar9 + 4);
      local_88 = *(undefined4 *)(iVar9 + 0xc);
      local_8c = local_40;
      fVar19 = (float10)CMCMech__GetFootHeight(&local_94,*param_5,param_8);
      *(float *)(*param_5 * 0x10 + -8 + param_1[5]) = (float)fVar19;
      iVar9 = *param_5;
      pfVar8 = (float *)(iVar9 * 0x10 + -0x10 + param_1[5]);
      local_24 = *pfVar8;
      local_20 = pfVar8[1];
      fVar5 = pfVar8[2] + *(float *)(param_1[7] + -4 + iVar9 * 4);
      fVar1 = pfVar8[3];
      local_1c = (double)CONCAT44(fVar1,fVar5);
      if ((*(int *)(param_1[6] + -4 + iVar9 * 4) == 0) &&
         (_DAT_005d95b4 < *(float *)(param_1[7] + -4 + iVar9 * 4))) {
        param_1[0x34] = 1;
        param_1[0x35] = (int)local_24;
        param_1[0x36] = (int)local_20;
        param_1[0x37] = (int)fVar5;
        param_1[0x38] = (int)fVar1;
        *(undefined4 *)(param_1[6] + -4 + *param_5 * 4) = 1;
      }
      iVar9 = 0;
      param_7 = 0.0;
      param_8 = 0.0;
      if (0 < param_1[0x2b]) {
        piVar12 = *(int **)param_1[0x39];
        do {
          fVar1 = ABS(*(float *)(*param_5 * 4 + -4 + *piVar12) -
                      SQRT((local_30 - fVar5) * (local_30 - fVar5) +
                           (local_34 - local_20) * (local_34 - local_20) +
                           (local_38 - local_24) * (local_38 - local_24)));
          iVar14 = iVar9;
          if ((param_8 != _DAT_005d856c) && (param_8 <= fVar1)) {
            iVar14 = (int)param_7;
            fVar1 = param_8;
          }
          param_8 = fVar1;
          param_7 = (float)iVar14;
          iVar9 = iVar9 + 1;
          piVar12 = piVar12 + 1;
        } while (iVar9 < param_1[0x2b]);
      }
      local_11 = '\x01';
      piVar12 = local_6c + 0x16;
      *param_6 = local_6c[0x2c] + (int)param_7;
      local_68 = (float)local_6c[0x17] * _DAT_005d8be0;
      local_10c = local_38;
      local_64 = (float)local_6c[0x1b] * _DAT_005d8be0;
      local_108 = local_34;
      local_104 = local_30;
      local_100 = local_2c;
      local_60 = (float)local_6c[0x1f] * _DAT_005d8be0;
      Vec3__SetXYZ();
      local_58 = local_68;
      local_54 = local_64;
      local_50 = local_60;
      local_4c = local_5c;
      Vec3__Cross(&local_38,&local_24,&local_58,unaff_EDI);
      Vec3__Cross(&local_38,&local_80,&local_24,unaff_EDI);
      SQRT__Wrapper_00406d50(&local_24);
      SQRT__Wrapper_00406d50(&local_80);
      SQRT__Wrapper_00406d50(&local_38);
      local_fc[0] = local_24;
      local_fc[1] = local_80;
      local_fc[2] = local_38;
      local_ec = local_20;
      local_e8 = local_7c;
      local_e4 = local_34;
      local_dc = (float)local_1c;
      local_d8 = (float)local_78;
      local_d4 = local_30;
      CUnitAI__Unk_0049bc80(piVar12,local_cc,unaff_EDI);
      CUnitAI__Unk_0049bc10((int)local_cc);
      dVar21 = CUnitAI__Unk_0049bc40(piVar12);
      fVar1 = (float)dVar21;
      CMCBuggy__DivideVector(fVar1);
      CMCBuggy__DivideVector(fVar1);
      CMCBuggy__DivideVector(fVar1);
      fVar1 = local_a8 * this_00[4];
      fVar5 = local_ac * *this_00;
      local_58 = local_a4 * this_00[8];
      pfVar8 = local_cc;
      pfVar17 = local_13c;
      for (iVar9 = 0xc; iVar9 != 0; iVar9 = iVar9 + -1) {
        *pfVar17 = *pfVar8;
        pfVar8 = pfVar8 + 1;
        pfVar17 = pfVar17 + 1;
      }
      local_58 = local_58 + fVar5 + fVar1;
      local_54 = local_ac * this_00[1] + local_a8 * this_00[5] + local_a4 * this_00[9];
      local_50 = local_a8 * this_00[6] + local_a4 * this_00[10] + local_ac * this_00[2];
      Vec3__SetXYZ();
      Vec3__SetXYZ();
      Mat34__SetRows();
      pfVar8 = local_1b0;
      pfVar17 = this_00;
      for (iVar9 = 0xc; iVar9 != 0; iVar9 = iVar9 + -1) {
        *pfVar17 = *pfVar8;
        pfVar8 = pfVar8 + 1;
        pfVar17 = pfVar17 + 1;
      }
      pvVar11 = (void *)(*(int *)(*(int *)(local_6c[0x39] + 4) + (int)param_7 * 4) + -0x30 +
                        *param_5 * 0x30);
      CUnitAI__Unk_0049bc80(pvVar11,local_13c,unaff_EDI);
      CUnitAI__Unk_0049bc10((int)local_13c);
      dVar21 = CUnitAI__Unk_0049bc40(pvVar11);
      CUnitAI__Unk_0049bbb0(local_13c,(void *)(float)dVar21,(float)unaff_EDI);
      pfVar8 = local_13c;
      pfVar17 = local_cc;
      for (iVar9 = 0xc; iVar9 != 0; iVar9 = iVar9 + -1) {
        *pfVar17 = *pfVar8;
        pfVar8 = pfVar8 + 1;
        pfVar17 = pfVar17 + 1;
      }
      Vec3__SetXYZ();
      Vec3__SetXYZ();
      Vec3__SetXYZ();
      Mat34__SetRows();
      iVar9 = 0xc;
      pfVar8 = local_1b0;
      pfVar17 = this_00;
      goto LAB_0049b5b6;
    }
    if (iVar10 == 3) {
      CMonitor__Helper_0047ec60(0x6fadc8,&local_58,(void *)(*param_5 * 0x10 + -0x10 + param_1[5]));
      local_34 = local_54;
      local_38 = local_58;
      local_48 = 0.0;
      local_44 = -1.0;
      local_40 = 0.0;
      local_30 = local_50;
      local_2c = local_4c;
      CThing__Helper_004404f0(&local_38,&local_68,unaff_EDI);
      local_20 = local_44;
      local_24 = local_48;
      local_1c = (double)CONCAT44(local_3c,local_40);
      Vec3__Cross(&local_68,&local_94,&local_24,unaff_EDI);
      Vec3__Cross(&local_68,&local_80,&local_94,unaff_EDI);
      SQRT__Wrapper_00406d50(&local_94);
      SQRT__Wrapper_00406d50(&local_80);
      SQRT__Wrapper_00406d50(&local_68);
      local_fc[0] = local_94;
      local_fc[1] = local_80;
      local_fc[2] = local_68;
      local_ec = local_90;
      local_e8 = local_7c;
      local_e4 = local_64;
      local_dc = local_8c;
      local_d8 = (float)local_78;
      local_d4 = local_60;
      local_25 = '\x01';
    }
    else if (iVar10 == 4) {
      iVar9 = *(int *)(*(int *)(iVar14 + 0x10) + iVar9 * 4);
      iVar14 = CMCMech__Helper_004aa820
                         (*(void **)(param_4 + 0x128),0x62df28,(void *)(iVar9 + 1),(int)unaff_EDI);
      local_1c = (double)CONCAT44(iVar14,(float)local_1c);
      if ((iVar14 != 0) &&
         (iVar10 = (*param_5 + -1) * param_1[0x30] + iVar9 % 3,
         iVar10 < param_1[0x2a] * param_1[0x30])) {
        iVar14 = *(int *)(*(int *)(iVar14 + 0x98) + 0x98);
        vector_constructor_iterator_nothrow(local_13c,0x10,3,&LAB_00402d20);
        do {
          pfVar8 = (float *)((*(int *)(local_6c[0x2f] + iVar10 * 4) - local_6c[0x2d]) * 0x10 +
                            *(int *)(*(int *)(local_6c[0x39] + 8) + iVar9 * 4));
          local_24 = *pfVar8;
          local_20 = pfVar8[1];
          local_1c = *(double *)(pfVar8 + 2);
          iVar3 = *(int *)(iVar14 + 0x88);
          pfVar8 = (float *)(iVar3 * 0x10 + local_6c[0xd]);
          local_48 = *pfVar8;
          local_44 = pfVar8[1];
          local_40 = pfVar8[2];
          fVar1 = pfVar8[3];
          pfVar8 = (float *)(iVar3 * 0x30 + local_6c[0xc]);
          pfVar17 = local_13c;
          for (iVar13 = 0xc; iVar13 != 0; iVar13 = iVar13 + -1) {
            *pfVar17 = *pfVar8;
            pfVar8 = pfVar8 + 1;
            pfVar17 = pfVar17 + 1;
          }
          local_3c = fVar1;
          Vec3__SetXYZ();
          local_24 = local_94 + local_48;
          local_20 = local_44 + local_90;
          local_1c = (double)CONCAT44(local_88,local_40 + local_8c);
          dVar21 = CStaticShadows__Helper_0047eb80(0x6fadc8,&local_24);
          if ((double)(float)local_1c <= dVar21 + (double)_DAT_005d85c0) {
            if ((double)(float)local_1c < dVar21 - (double)_DAT_005d85c0) {
              *(int *)(local_6c[0x2f] + iVar10 * 4) = *(int *)(local_6c[0x2f] + iVar10 * 4) + 1;
              piVar12 = (int *)(local_6c[0x2f] + iVar10 * 4);
              if (local_6c[0x2e] < *piVar12) {
                *piVar12 = local_6c[0x2e];
              }
            }
            goto LAB_0049b52a;
          }
          *(int *)(local_6c[0x2f] + iVar10 * 4) = *(int *)(local_6c[0x2f] + iVar10 * 4) + -1;
        } while (local_6c[0x2d] <= *(int *)(local_6c[0x2f] + iVar10 * 4));
        *(int *)(local_6c[0x2f] + iVar10 * 4) = local_6c[0x2d];
LAB_0049b52a:
        *param_6 = *(int *)(local_6c[0x2f] + iVar10 * 4);
      }
    }
    else if (iVar10 == 5) {
      local_25 = '\x01';
      if (local_84 == (int *)0x0) {
        piVar12 = (int *)0x0;
        piVar15 = (int *)0x0;
      }
      else {
        piVar12 = local_84 + -2;
        piVar15 = local_84 + -2;
      }
      pvVar11 = (void *)piVar12[0x38];
      vector_constructor_iterator_nothrow(local_1b0,0x10,3,&LAB_00402d20);
      CSquadNormal__Helper_004062d0(local_1b0,pvVar11,0.0,0.0,(float)unaff_EDI);
      CMCBuggy__Helper_0040d320(piVar15 + 0xf,local_13c,local_1b0,unaff_EDI);
      iVar9 = 0xc;
      pfVar17 = local_fc;
      pfVar8 = extraout_EAX;
      goto LAB_0049b5b6;
    }
  }
  piVar12 = local_84;
  if (*param_5 != -1) {
    local_140 = *param_6;
    local_70 = CONCAT31(local_70._1_3_,*(undefined1 *)(*(int *)(param_4 + 0xc4) + *param_6));
  }
  if (local_84 == (int *)0x0) {
LAB_0049b708:
    if (local_11 == '\0') {
      Vec3__SetXYZ();
      *param_2 = local_58 + *param_2;
      param_2[1] = local_54 + param_2[1];
      param_2[2] = local_50 + param_2[2];
    }
    else {
      *param_2 = local_10c;
      param_2[1] = local_108;
      param_2[2] = local_104;
      param_2[3] = local_100;
    }
    if (local_25 == '\0') {
      CMCBuggy__Helper_0040d320
                (this_00,local_1b0,(void *)((local_70 & 0xff) * 0x30 + *(int *)(param_4 + 0x10c)),
                 unaff_EDI);
      pfVar8 = extraout_EAX_02;
      pfVar17 = this_00;
      for (iVar9 = 0xc; iVar9 != 0; iVar9 = iVar9 + -1) {
        *pfVar17 = *pfVar8;
        pfVar8 = pfVar8 + 1;
        pfVar17 = pfVar17 + 1;
      }
      CMCBuggy__Helper_0040d320(local_fc,local_1b0,this_00,unaff_EDI);
      pfVar8 = extraout_EAX_03;
    }
    else {
LAB_0049b813:
      pfVar8 = local_fc;
    }
  }
  else {
    if (*(int *)(param_4 + 0x88) == 0) {
      pfVar8 = (float *)(**(code **)*local_84)(local_1c8);
      *param_2 = *pfVar8 + *param_2;
      param_2[1] = pfVar8[1] + param_2[1];
      param_2[2] = pfVar8[2] + param_2[2];
      pvVar11 = (void *)(**(code **)(*piVar12 + 4))(local_1b0);
      CMCBuggy__Helper_0040d320(this_00,local_13c,pvVar11,unaff_EDI);
      pfVar8 = extraout_EAX_00;
      pfVar17 = this_00;
      for (iVar9 = 0xc; iVar9 != 0; iVar9 = iVar9 + -1) {
        *pfVar17 = *pfVar8;
        pfVar8 = pfVar8 + 1;
        pfVar17 = pfVar17 + 1;
      }
    }
    iVar9 = (**(code **)(*local_84 + 0x38))(*(undefined4 *)(param_4 + 0x88));
    if (iVar9 != 0) goto LAB_0049b708;
    if (local_11 == '\0') {
      pfVar8 = (float *)((local_70 & 0xff) * 0x10 + *(int *)(param_4 + 200));
      *param_2 = *pfVar8 + *param_2;
      param_2[1] = pfVar8[1] + param_2[1];
      param_2[2] = pfVar8[2] + param_2[2];
    }
    else {
      *param_2 = local_10c;
      param_2[1] = local_108;
      param_2[2] = local_104;
      param_2[3] = local_100;
    }
    if (local_25 != '\0') goto LAB_0049b813;
    pfVar8 = (float *)((local_70 & 0xff) * 0x30 + *(int *)(param_4 + 0x10c));
    pfVar17 = this_00;
    for (iVar9 = 0xc; iVar9 != 0; iVar9 = iVar9 + -1) {
      *pfVar17 = *pfVar8;
      pfVar8 = pfVar8 + 1;
      pfVar17 = pfVar17 + 1;
    }
    CMCBuggy__Helper_0040d320(local_fc,local_1b0,this_00,unaff_EDI);
    pfVar8 = extraout_EAX_01;
  }
  pfVar17 = this_00;
  for (iVar9 = 0xc; iVar9 != 0; iVar9 = iVar9 + -1) {
    *pfVar17 = *pfVar8;
    pfVar8 = pfVar8 + 1;
    pfVar17 = pfVar17 + 1;
  }
  if ((float)local_6c[0xb] == _DAT_005d856c) goto LAB_0049ba52;
  iVar9 = -1;
  param_5 = (int *)0x0;
  if ((int *)local_6c[2] != (int *)0x0) {
    iVar9 = (**(code **)(*(int *)local_6c[2] + 0x1c))();
  }
  if (((*(int *)(param_4 + 0xb8) < 2) || (*(int *)(*(int *)(param_4 + 0x128) + 0x14) == 0)) ||
     (iVar9 < 0)) {
LAB_0049b91f:
    CDXEngine__Helper_0055dfe7(0.0);
  }
  else {
    if ((int *)local_6c[2] != (int *)0x0) {
      fVar19 = (float10)(**(code **)(*(int *)local_6c[2] + 0x18))();
      param_5 = (int *)(float)fVar19;
    }
    iVar14 = *(int *)(*(int *)(param_4 + 0x128) + 0x18);
    local_1c = (double)((float)*(int *)(iVar14 + 0x1c + iVar9 * 0x24) * (float)param_5 +
                       (float)*(int *)(iVar14 + iVar9 * 0x24 + 0x14));
    dVar21 = CDXEngine__Helper_0055dfe7(local_1c);
    local_78 = (ulonglong)ROUND(dVar21);
    CDXEngine__Helper_0055dfe7(local_1c);
    dVar21 = CDXEngine__Helper_0055dfe7(0.0);
    local_1c = (double)(longlong)ROUND(dVar21);
    iVar9 = (int)(float)local_1c + 1;
    dVar21 = CDXEngine__Helper_0055dfe7(0.0);
    local_1c = (double)(longlong)ROUND(dVar21);
    if ((int)(float)local_1c < iVar9) goto LAB_0049b91f;
  }
  vector_constructor_iterator_nothrow(local_1b0,0x10,3,&LAB_00402d20);
  piVar12 = local_6c;
  CMCMech__Helper_004b0fb0();
  Vec3__SetXYZ();
  Vec3__SetXYZ();
  Vec3__SetXYZ();
  *param_2 = local_58;
  fVar1 = _DAT_005d8568;
  param_2[1] = local_54;
  param_2[2] = local_50;
  param_2[3] = local_4c;
  CMCMech__Helper_00495ed0(this_00,local_13c,(void *)(fVar1 - (float)piVar12[0xb]),(float)unaff_EDI)
  ;
  pfVar8 = local_cc;
  pvVar11 = extraout_EAX_04;
  CMCMech__Helper_00495ed0(local_1b0,local_178,(void *)piVar12[0xb],(float)pfVar8);
  Mat34__Add(this,pfVar8,pvVar11,unaff_EDI);
  pfVar8 = extraout_EAX_05;
  pfVar17 = this_00;
  for (iVar9 = 0xc; iVar9 != 0; iVar9 = iVar9 + -1) {
    *pfVar17 = *pfVar8;
    pfVar8 = pfVar8 + 1;
    pfVar17 = pfVar17 + 1;
  }
LAB_0049ba52:
  if (local_6c[0x33] < 3) {
    pfVar8 = (float *)(*(int *)(param_4 + 0x88) * 0x10 + local_6c[0x10]);
    *pfVar8 = *param_2;
    pfVar8[1] = param_2[1];
    pfVar8[2] = param_2[2];
    pfVar8[3] = param_2[3];
    pfVar8 = this_00;
    pfVar17 = (float *)(*(int *)(param_4 + 0x88) * 0x30 + local_6c[0xf]);
    for (iVar9 = 0xc; iVar9 != 0; iVar9 = iVar9 + -1) {
      *pfVar17 = *pfVar8;
      pfVar8 = pfVar8 + 1;
      pfVar17 = pfVar17 + 1;
    }
    *(float *)(local_6c[0x11] + *(int *)(param_4 + 0x88) * 4) = (float)local_140;
  }
  else {
    iVar9 = *(int *)(param_4 + 0x88) * 0x10;
    puVar16 = (undefined4 *)(local_6c[0xd] + iVar9);
    puVar18 = (undefined4 *)(local_6c[0x10] + iVar9);
    *puVar18 = *puVar16;
    puVar18[1] = puVar16[1];
    puVar18[2] = puVar16[2];
    puVar18[3] = puVar16[3];
    iVar9 = *(int *)(param_4 + 0x88) * 0x30;
    puVar16 = (undefined4 *)(local_6c[0xc] + iVar9);
    puVar18 = (undefined4 *)(local_6c[0xf] + iVar9);
    for (iVar14 = 0xc; iVar14 != 0; iVar14 = iVar14 + -1) {
      *puVar18 = *puVar16;
      puVar16 = puVar16 + 1;
      puVar18 = puVar18 + 1;
    }
    iVar9 = *(int *)(param_4 + 0x88) * 4;
    *(undefined4 *)(local_6c[0x11] + iVar9) = *(undefined4 *)(local_6c[0xe] + iVar9);
  }
  pfVar8 = (float *)(local_6c[0xd] + *(int *)(param_4 + 0x88) * 0x10);
  *pfVar8 = *param_2;
  pfVar8[1] = param_2[1];
  pfVar8[2] = param_2[2];
  pfVar8[3] = param_2[3];
  pfVar8 = (float *)(*(int *)(param_4 + 0x88) * 0x30 + local_6c[0xc]);
  for (iVar9 = 0xc; iVar9 != 0; iVar9 = iVar9 + -1) {
    *pfVar8 = *this_00;
    this_00 = this_00 + 1;
    pfVar8 = pfVar8 + 1;
  }
  *(float *)(local_6c[0xe] + *(int *)(param_4 + 0x88) * 4) = (float)local_140;
  uVar4 = rdtsc();
  DAT_00835764 = DAT_00835764 + ((int)uVar4 - local_180);
  DAT_00835934 = DAT_00835934 + 1;
  ExceptionList = local_10;
  return;
}
