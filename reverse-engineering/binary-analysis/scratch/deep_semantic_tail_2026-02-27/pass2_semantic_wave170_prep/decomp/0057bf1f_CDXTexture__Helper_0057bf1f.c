/* address: 0x0057bf1f */
/* name: CDXTexture__Helper_0057bf1f */
/* signature: int __thiscall CDXTexture__Helper_0057bf1f(void * this, void * param_1, void * param_2, void * param_3) */


int __thiscall CDXTexture__Helper_0057bf1f(void *this,void *param_1,void *param_2,void *param_3)

{
  int iVar1;
  uint uVar2;
  int *piVar3;
  void *extraout_EAX;
  int *extraout_EAX_00;
  int *piVar4;
  void *extraout_EAX_01;
  int *extraout_EAX_02;
  int *piVar5;
  int iVar6;
  uint uVar7;
  int iVar8;
  void *pvVar9;
  uint uVar10;
  uint uVar11;
  int local_2c;
  uint local_24;
  int *local_20;
  uint local_1c;
  uint local_18;
  uint local_14;
  int local_8;

  if (((param_2 < (void *)0x4) || (*(int *)param_1 != 0x20534444)) || ((int)param_2 - 4U < 0x7c)) {
    return -0x7fffbffb;
  }
  local_8 = (int)param_1 + 0x80;
  *(undefined4 *)((int)this + 0xc) = *(undefined4 *)((int)param_1 + 0x10);
  *(undefined4 *)((int)this + 0x10) = *(undefined4 *)((int)param_1 + 0xc);
  if ((*(byte *)((int)param_1 + 10) & 0x80) == 0) {
    iVar1 = 1;
  }
  else {
    iVar1 = *(int *)((int)param_1 + 0x18);
  }
  *(int *)((int)this + 0x14) = iVar1;
  if (iVar1 == 0) {
    *(undefined4 *)((int)this + 0x14) = 1;
  }
  uVar2 = *(uint *)((int)param_1 + 0x70) & 0xfc00;
  if (uVar2 == 0xfc00) {
    local_1c = 6;
  }
  else {
    if (uVar2 != 0) {
      return -0x7fffbffb;
    }
    local_1c = 1;
  }
  local_24 = *(uint *)((int)param_1 + 0x1c);
  if (local_24 == 0) {
    local_24 = 1;
  }
  uVar2 = *(uint *)((int)param_1 + 0x50);
  if ((uVar2 & 4) != 0) {
    uVar2 = 4;
  }
  local_20 = (int *)(uVar2 & 0xc4040);
  piVar3 = &DAT_00657290;
  iVar1 = DAT_00657290;
  while ((iVar1 != 0 &&
         ((((((*(int *)((int)param_1 + 0x4c) != 0x20 || (piVar3[2] != uVar2)) ||
             (((uVar2 & 4) != 0 && (*(int *)((int)param_1 + 0x54) != piVar3[3])))) ||
            (((uVar2 & 0xc4462) != 0 && (*(int *)((int)param_1 + 0x58) != piVar3[4])))) ||
           (((uVar2 & 0xe4040) != 0 && (*(int *)((int)param_1 + 0x5c) != piVar3[5])))) ||
          (((((uVar2 & 0xc4440) != 0 && (*(int *)((int)param_1 + 0x60) != piVar3[6])) ||
            ((local_20 != (int *)0x0 && (*(int *)((int)param_1 + 100) != piVar3[7])))) ||
           (((uVar2 & 0x80003) != 0 && (*(int *)((int)param_1 + 0x68) != piVar3[8]))))))))) {
    piVar3 = piVar3 + 9;
    iVar1 = *piVar3;
  }
  iVar1 = *piVar3;
  if (iVar1 == 0) {
    return -0x7fffbffb;
  }
  piVar3 = CMeshCollisionVolume__Helper_00574270(iVar1);
  if ((*(byte *)((int)param_1 + 10) & 0x80) == 0) {
    *(uint *)((int)this + 0x44) = (uint)(local_1c == 6) * 2 + 3;
  }
  else {
    *(undefined4 *)((int)this + 0x44) = 4;
  }
  if (piVar3[1] == 1) {
    if ((void *)((int)param_2 - 0x80U) < (void *)0x400) {
      return -0x7fffbffb;
    }
    param_2 = (void *)((int)param_2 + -0x480);
    local_2c = local_8;
    local_8 = (int)param_1 + 0x480;
  }
  else {
    local_2c = 0;
    param_2 = (void *)((int)param_2 - 0x80U);
  }
  local_18 = 0;
  piVar5 = param_2;
  if (local_1c != 0) {
    do {
      uVar2 = *(uint *)((int)this + 0x10);
      uVar10 = *(uint *)((int)this + 0xc);
      param_1 = *(void **)((int)this + 0x14);
      piVar4 = this;
      if (local_18 != 0) {
        CFastVB__Helper_00426fd0(0x54);
        if (extraout_EAX == (void *)0x0) {
          piVar4 = (int *)0x0;
        }
        else {
          CDXTexture__Helper_00579ca5(extraout_EAX);
          piVar4 = extraout_EAX_00;
        }
        if (piVar4 == (int *)0x0) {
          return -0x7ff8fff2;
        }
        local_20[0x14] = (int)piVar4;
      }
      local_20 = piVar4;
      local_14 = 0;
      piVar4 = piVar5;
      if (local_24 != 0) {
        do {
          piVar5 = local_20;
          if (local_14 != 0) {
            CFastVB__Helper_00426fd0(0x54);
            if (extraout_EAX_01 == (void *)0x0) {
              piVar5 = (int *)0x0;
            }
            else {
              CDXTexture__Helper_00579ca5(extraout_EAX_01);
              piVar5 = extraout_EAX_02;
            }
            if (piVar5 == (int *)0x0) {
              return -0x7ff8fff2;
            }
            piVar4[0x13] = (int)piVar5;
          }
          if (iVar1 < 0x34545845) {
            if (iVar1 == 0x34545844) {
LAB_0057c190:
              iVar6 = (uVar10 + 3 >> 2) << 4;
            }
            else {
              if (iVar1 != 0x31545844) {
                if (iVar1 != 0x32545844) {
                  if (iVar1 == 0x32595559) goto LAB_0057c225;
                  if (iVar1 != 0x33545844) goto LAB_0057c217;
                }
                goto LAB_0057c190;
              }
              iVar6 = (uVar10 + 3 >> 2) << 3;
            }
            iVar8 = (uVar2 + 3 >> 2) * iVar6;
          }
          else {
            if (iVar1 == 0x35545844) goto LAB_0057c190;
            if (((iVar1 == 0x42475247) || (iVar1 == 0x47424752)) || (iVar1 == 0x59565955)) {
LAB_0057c225:
              iVar6 = (uVar10 + 1 >> 1) << 2;
            }
            else {
LAB_0057c217:
              iVar6 = ((uint)piVar3[2] >> 3) * uVar10;
            }
            iVar8 = iVar6 * uVar2;
          }
          piVar5[0xe] = 0;
          piVar5[0xf] = 0;
          pvVar9 = (void *)(iVar8 * (int)param_1);
          *piVar5 = iVar1;
          piVar5[0xc] = iVar6;
          piVar5[1] = local_8;
          piVar5[5] = (int)param_1;
          piVar5[0xd] = iVar8;
          piVar5[3] = uVar10;
          piVar5[4] = uVar2;
          piVar5[2] = local_2c;
          if (param_2 < pvVar9) {
            return -0x7fffbffb;
          }
          local_8 = local_8 + (int)pvVar9;
          param_2 = (void *)((int)param_2 - (int)pvVar9);
          uVar7 = 1;
          uVar11 = uVar7;
          if (uVar10 != 1) {
            uVar11 = uVar10 >> 1;
          }
          if (uVar2 != 1) {
            uVar7 = uVar2 >> 1;
          }
          if (param_1 == (void *)0x1) {
            param_1 = (void *)0x1;
          }
          else {
            param_1 = (void *)((uint)param_1 >> 1);
          }
          local_14 = local_14 + 1;
          uVar2 = uVar7;
          piVar4 = piVar5;
          uVar10 = uVar11;
        } while (local_14 < local_24);
      }
      local_18 = local_18 + 1;
    } while (local_18 < local_1c);
  }
  return 0;
}
