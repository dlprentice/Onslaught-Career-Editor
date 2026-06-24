/* address: 0x0057c7a4 */
/* name: CMeshCollisionVolume__LoadMappedTextureResourcesByMode */
/* signature: int __thiscall CMeshCollisionVolume__LoadMappedTextureResourcesByMode(void * this, void * param_1, int param_2, int param_3, int param_4) */


int __thiscall
CMeshCollisionVolume__LoadMappedTextureResourcesByMode
          (void *this,void *param_1,int param_2,int param_3,int param_4)

{
  int *piVar1;
  int iVar2;
  uint uVar3;
  void *extraout_EAX;
  int iVar4;
  void *extraout_EDX;
  void *extraout_EDX_00;
  void *extraout_EDX_01;
  void *extraout_EDX_02;
  void *extraout_EDX_03;
  void *extraout_EDX_04;
  void *extraout_EDX_05;
  void *extraout_EDX_06;
  void *pvVar5;
  undefined *puVar6;
  int *piVar7;
  uint unaff_EDI;
  int *piVar8;
  int local_d4;
  int local_d0;
  int local_cc;
  int local_c8;
  int local_c4 [6];
  int local_ac [6];
  undefined4 local_94;
  undefined4 local_8c;
  int local_88;
  void *local_84;
  int local_80;
  int local_7c;
  int local_78;
  int local_74 [4];
  undefined4 local_64;
  int local_60;
  int local_5c [6];
  undefined4 local_44;
  undefined4 local_3c;
  int local_38;
  undefined1 local_34 [12];
  void *local_28 [4];
  void *local_18;
  int local_14;
  void *local_10;
  int *local_c;
  uint local_8;

  local_18 = this;
  CDXTexture__InitMappedFileContext(local_28);
  if (param_2 == 0) {
LAB_0057c7f9:
    puVar6 = &DAT_00657178;
LAB_0057c7fe:
    piVar1 = CMeshCollisionVolume__Helper_00574270(*(int *)this);
    iVar2 = CMeshCollisionVolume__Helper_0057430b(puVar6,*(int *)((int)this + 8),piVar1);
    pvVar5 = extraout_EDX_00;
    local_14 = iVar2;
    if (iVar2 != 0) {
      if (iVar2 != *(int *)this) {
        CDXTexture__InitMappedFileContext(local_34);
        piVar1 = CMeshCollisionVolume__Helper_00574270(iVar2);
        uVar3 = (uint)piVar1[2] >> 3;
        piVar1 = this;
        local_c = this;
        local_8 = uVar3;
        do {
          for (; piVar1 != (int *)0x0; piVar1 = (int *)piVar1[0x13]) {
            OID__AllocObject_DefaultTag_00662b2c(piVar1[3] * piVar1[4] * uVar3 * piVar1[5]);
            local_10 = extraout_EAX;
            if (extraout_EAX == (void *)0x0) {
              CMeshCollisionVolume__Helper_0057cc5d(local_34);
              iVar2 = -0x7ff8fff2;
              pvVar5 = extraout_EDX_02;
              goto LAB_0057ca26;
            }
            local_d4 = piVar1[1];
            local_d0 = *piVar1;
            local_cc = piVar1[0xc];
            local_c8 = piVar1[0xd];
            piVar7 = piVar1 + 6;
            piVar8 = local_c4;
            for (iVar2 = 6; iVar2 != 0; iVar2 = iVar2 + -1) {
              *piVar8 = *piVar7;
              piVar7 = piVar7 + 1;
              piVar8 = piVar8 + 1;
            }
            piVar7 = piVar1 + 6;
            piVar8 = local_ac;
            for (iVar2 = 6; iVar2 != 0; iVar2 = iVar2 + -1) {
              *piVar8 = *piVar7;
              piVar7 = piVar7 + 1;
              piVar8 = piVar8 + 1;
            }
            local_8c = 0;
            local_94 = 1;
            local_88 = piVar1[2];
            local_84 = local_10;
            local_80 = local_14;
            local_7c = piVar1[3] * local_8;
            local_78 = piVar1[3] * piVar1[4] * local_8;
            local_74[0] = 0;
            local_74[1] = 0;
            local_74[2] = piVar1[3];
            local_74[3] = piVar1[4];
            local_64 = 0;
            local_60 = piVar1[5];
            piVar7 = local_74;
            piVar8 = local_5c;
            for (iVar2 = 6; iVar2 != 0; iVar2 = iVar2 + -1) {
              *piVar8 = *piVar7;
              piVar7 = piVar7 + 1;
              piVar8 = piVar8 + 1;
            }
            local_3c = 0;
            local_44 = 1;
            local_38 = piVar1[2];
            iVar2 = CFastVB__InitDualTexelConversionPipeline
                              (local_34,&local_84,(int)&local_d4,0x80001,unaff_EDI);
            if (iVar2 < 0) {
              OID__FreeObject_Callback(local_10);
              CMeshCollisionVolume__Helper_0057cc5d(local_34);
              pvVar5 = extraout_EDX_03;
              goto LAB_0057ca26;
            }
            if (((void *)piVar1[1] != (void *)0x0) && (piVar1[0xe] != 0)) {
              OID__FreeObject_Callback((void *)piVar1[1]);
              piVar1[1] = 0;
            }
            *piVar1 = local_14;
            piVar1[1] = (int)local_10;
            piVar7 = local_5c;
            piVar8 = piVar1 + 6;
            for (iVar2 = 6; iVar2 != 0; iVar2 = iVar2 + -1) {
              *piVar8 = *piVar7;
              piVar7 = piVar7 + 1;
              piVar8 = piVar8 + 1;
            }
            piVar1[0xc] = local_7c;
            piVar1[0xd] = local_78;
            piVar1[0xe] = 1;
            uVar3 = local_8;
            this = local_18;
          }
          local_c = (int *)local_c[0x14];
          piVar1 = local_c;
        } while (local_c != (int *)0x0);
        CMeshCollisionVolume__Helper_0057cc5d(local_34);
      }
      iVar4 = CMeshCollisionVolume__Helper_0058877d(local_28,param_1,param_3,unaff_EDI);
      iVar2 = 0;
      pvVar5 = extraout_EDX_01;
      if (-1 < iVar4) {
        if (param_2 == 0) {
          iVar4 = 1;
LAB_0057ca16:
          iVar4 = CMeshCollisionVolume__Helper_0057a934(this,local_28[0],iVar4,unaff_EDI);
          pvVar5 = extraout_EDX_06;
        }
        else if (param_2 == 1) {
          iVar4 = CMeshCollisionVolume__Helper_0057c5dc(this,local_28[0],unaff_EDI);
          pvVar5 = extraout_EDX_05;
        }
        else {
          if (param_2 != 4) {
            if (param_2 != 6) {
              iVar4 = -0x7fffbfff;
              goto LAB_0057ca24;
            }
            iVar4 = 0;
            goto LAB_0057ca16;
          }
          iVar4 = CMeshCollisionVolume__Helper_0057c28b(this,local_28[0],unaff_EDI);
          pvVar5 = extraout_EDX_04;
        }
        if (-1 < iVar4) goto LAB_0057ca26;
      }
LAB_0057ca24:
      iVar2 = iVar4;
      goto LAB_0057ca26;
    }
  }
  else {
    if (param_2 == 1) {
      puVar6 = &DAT_00657170;
      goto LAB_0057c7fe;
    }
    pvVar5 = extraout_EDX;
    if ((1 < param_2) && (3 < param_2)) {
      if (param_2 == 4) {
        puVar6 = &DAT_006571c8;
        goto LAB_0057c7fe;
      }
      if ((param_2 != 5) && (param_2 == 6)) goto LAB_0057c7f9;
    }
  }
  iVar2 = -0x7789f794;
LAB_0057ca26:
  CDXTexture__CloseHandleIfValid(local_28,pvVar5);
  return iVar2;
}
