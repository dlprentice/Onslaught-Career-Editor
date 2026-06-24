/* address: 0x0058b1a0 */
/* name: CTexture__Helper_0058b1a0 */
/* signature: int __thiscall CTexture__Helper_0058b1a0(void * this, void * param_1, void * param_2) */


int __thiscall CTexture__Helper_0058b1a0(void *this,void *param_1,void *param_2)

{
  char cVar1;
  undefined4 *extraout_EAX;
  undefined4 *extraout_EAX_00;
  undefined4 *extraout_EAX_01;
  void *this_00;
  int extraout_EAX_02;
  undefined4 *extraout_EAX_03;
  void *this_01;
  int extraout_EAX_04;
  char *pcVar2;
  int iVar3;
  void *unaff_EDI;
  undefined4 *puVar4;
  undefined1 local_68 [56];
  undefined4 local_30 [8];
  undefined4 local_10;
  void *local_c;
  undefined4 *local_8;

  local_10 = *(undefined4 *)((int)this + 0x54);
  puVar4 = local_30;
  local_c = this;
  for (iVar3 = 8; iVar3 != 0; iVar3 = iVar3 + -1) {
    *puVar4 = 0;
    puVar4 = puVar4 + 1;
  }
  CFastVB__Helper_00426fd0(0x10);
  if (extraout_EAX == (undefined4 *)0x0) {
    local_8 = (undefined4 *)0x0;
  }
  else {
    *extraout_EAX = "DIRECT3D";
    extraout_EAX[1] = 0;
    extraout_EAX[2] = 0;
    extraout_EAX[3] = 0;
    local_8 = extraout_EAX;
  }
  if (local_8 != (undefined4 *)0x0) {
    iVar3 = CTexture__Helper_0058a58d(local_8);
    if (iVar3 < 0) goto LAB_0058b34c;
    CFastVB__Helper_00426fd0(0x10);
    if (extraout_EAX_00 == (undefined4 *)0x0) {
      local_8 = (undefined4 *)0x0;
    }
    else {
      *extraout_EAX_00 = &DAT_005ea630;
      extraout_EAX_00[1] = 0;
      extraout_EAX_00[2] = 0;
      extraout_EAX_00[3] = 0;
      local_8 = extraout_EAX_00;
    }
    if (local_8 != (undefined4 *)0x0) {
      iVar3 = CTexture__Helper_0058a58d(local_8);
      if (iVar3 < 0) goto LAB_0058b34c;
      local_30[0] = 2;
      local_30[2] = 0x900;
      CFastVB__Helper_00426fd0(0x10);
      if (extraout_EAX_01 == (undefined4 *)0x0) {
        local_8 = (undefined4 *)0x0;
      }
      else {
        *extraout_EAX_01 = "DIRECT3D_VERSION";
        extraout_EAX_01[1] = 0;
        extraout_EAX_01[2] = 0;
        extraout_EAX_01[3] = 0;
        local_8 = extraout_EAX_01;
      }
      if (local_8 != (undefined4 *)0x0) {
        CFastVB__Helper_00426fd0(0x30);
        if (this_00 == (void *)0x0) {
          iVar3 = 0;
        }
        else {
          CTexture__Unk_005989db(this_00,local_30,unaff_EDI);
          iVar3 = extraout_EAX_02;
        }
        local_8[2] = iVar3;
        if (iVar3 != 0) {
          iVar3 = CTexture__Helper_0058a58d(local_8);
          if (iVar3 < 0) goto LAB_0058b34c;
          local_30[0] = 2;
          local_30[2] = 0x900;
          CFastVB__Helper_00426fd0(0x10);
          if (extraout_EAX_03 == (undefined4 *)0x0) {
            local_8 = (undefined4 *)0x0;
          }
          else {
            *extraout_EAX_03 = "D3DX_VERSION";
            extraout_EAX_03[1] = 0;
            extraout_EAX_03[2] = 0;
            extraout_EAX_03[3] = 0;
            local_8 = extraout_EAX_03;
          }
          if (local_8 != (undefined4 *)0x0) {
            CFastVB__Helper_00426fd0(0x30);
            if (this_01 == (void *)0x0) {
              iVar3 = 0;
            }
            else {
              CTexture__Unk_005989db(this_01,local_30,unaff_EDI);
              iVar3 = extraout_EAX_04;
            }
            local_8[2] = iVar3;
            if (iVar3 != 0) {
              iVar3 = CTexture__Helper_0058a58d(local_8);
              if (-1 < iVar3) {
                local_8 = (undefined4 *)0x0;
                if (param_1 != (void *)0x0) {
                  CTexture__Helper_0058c37c(local_68);
                  *(undefined1 **)((int)local_c + 0x54) = local_68;
                  iVar3 = *(int *)param_1;
                  while (iVar3 != 0) {
                    pcVar2 = *(char **)((int)param_1 + 4);
                    if (pcVar2 != (char *)0x0) {
                      do {
                        cVar1 = *pcVar2;
                        pcVar2 = pcVar2 + 1;
                      } while (cVar1 != '\0');
                    }
                    iVar3 = CMeshCollisionVolume__Helper_0058c396();
                    if ((iVar3 < 0) ||
                       (iVar3 = CTexture__Helper_0058a713
                                          (local_c,*(int *)param_1,(void *)0x0,unaff_EDI), iVar3 < 0
                       )) {
                      CTexture__Helper_0059877e();
                      goto LAB_0058b34c;
                    }
                    param_1 = (void *)((int)param_1 + 8);
                    iVar3 = *(int *)param_1;
                  }
                  CTexture__Helper_0059877e();
                }
                iVar3 = 0;
              }
              goto LAB_0058b34c;
            }
          }
        }
      }
    }
  }
  iVar3 = -0x7ff8fff2;
LAB_0058b34c:
  *(undefined4 *)((int)local_c + 0x54) = local_10;
  if (local_8 != (undefined4 *)0x0) {
    CTexture__Helper_0058939b(local_8,(void *)0x1,(int)unaff_EDI);
  }
  return iVar3;
}
