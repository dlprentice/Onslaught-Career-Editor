/* address: 0x0057b9ce */
/* name: CDXTexture__Unk_0057b9ce */
/* signature: int __stdcall CDXTexture__Unk_0057b9ce(int param_1, int param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int CDXTexture__Unk_0057b9ce(int param_1,int param_2)

{
  undefined1 *puVar1;
  undefined1 uVar2;
  int iVar3;
  uint uVar4;
  int extraout_EAX;
  void *extraout_EAX_00;
  int extraout_EAX_01;
  int iVar5;
  undefined4 unaff_EDI;
  int iVar6;
  undefined1 auStack_158 [256];
  undefined1 local_58 [8];
  double local_50;
  int local_48;
  int local_44;
  int local_40;
  int local_3c;
  int *local_38;
  int local_34;
  int local_30;
  int local_2c;
  int local_28;
  int local_24;
  void *local_20;
  uint local_1c;
  int local_18;
  int local_14;
  uint local_10;
  int local_c;
  void *local_8;

  local_8 = (void *)0x0;
  local_c = 0;
  local_20 = (void *)0x0;
  iVar3 = CDXTexture__Helper_005950e0(param_1,0,param_2);
  if (iVar3 != 0) {
    return -0x7fffbffb;
  }
  local_8 = CDXTexture__Helper_00592dc2("1.0.5",0,0x57b9c1,0x57b9cd);
  if ((local_8 == (void *)0x0) ||
     (local_c = CDXTexture__Helper_005951e9((int)local_8), local_c == 0)) goto LAB_0057bdef;
  iVar3 = __setjmp3(local_8,0);
  if (iVar3 == 0) {
    local_48 = param_1;
    local_44 = param_2;
    CDXTexture__Helper_005950a2((int)local_8,(int)&local_48,0x57b980);
    CDXTexture__Helper_00592eb6(local_8,local_c);
    CDXTexture__Helper_0059364c();
    if (local_30 == 0) {
      *local_38 = 0x32;
    }
    else if (local_30 == 2) {
      *local_38 = 0x14;
    }
    else if (local_30 == 3) {
      *local_38 = 0x29;
    }
    else if (local_30 == 4) {
      *local_38 = 0x33;
    }
    else if (local_30 == 6) {
      *local_38 = 0x15;
    }
    if (local_28 == 0x10) {
      CDXTexture__Helper_005937c7((int)local_8);
      iVar3 = *local_38;
      if (iVar3 == 0x14) {
        *local_38 = 0x36315220;
      }
      else if (iVar3 == 0x15) {
        *local_38 = 0x24;
      }
      else if (iVar3 == 0x32) {
        *local_38 = 0x51;
      }
      else {
        if (iVar3 != 0x33) {
          return -0x7fffbffb;
        }
        *local_38 = 0x36314c41;
      }
    }
    if (local_28 < 8) {
      CDXTexture__Helper_005937db((int)local_8);
    }
    if ((local_30 == 0) && (local_28 < 8)) {
      CDXTexture__Helper_00593989((int)local_8);
    }
    iVar3 = CDXTexture__Helper_0059361e((int)local_8,local_c,&local_3c);
    if (iVar3 == 0) {
      iVar3 = CDXTexture__Helper_005935f2((int)local_8,local_c,local_58);
      if (iVar3 != 0) {
        CDXTexture__Helper_00593951
                  ((int)local_8,
                   (double)CONCAT44(local_58._0_4_,(int)((ulonglong)_DAT_005e96b8 >> 0x20)),
                   (double)CONCAT44(unaff_EDI,local_58._4_4_));
      }
    }
    else {
      CDXTexture__Unk_00594fdc((int)local_8,local_c,local_3c);
    }
    if ((*local_38 != 0x29) &&
       (uVar4 = CDXTexture__Unk_005935a3((int)local_8,local_c,0x10), uVar4 != 0)) {
      CDXTexture__Helper_00593989((int)local_8);
      iVar3 = *local_38;
      if (iVar3 == 0x14) {
        *local_38 = 0x15;
      }
      else if (iVar3 == 0x32) {
        *local_38 = 0x33;
      }
      else if (iVar3 == 0x51) {
        *local_38 = 0x36314c41;
      }
      else if (iVar3 == 0x36315220) {
        *local_38 = 0x24;
      }
    }
    iVar3 = *local_38;
    if (((iVar3 == 0x14) || (iVar3 == 0x36315220)) || (iVar3 == 0x15)) {
      CDXTexture__Helper_005937bc((int)local_8);
    }
    if (*local_38 == 0x14) {
      CDXTexture__Helper_00593812((int)local_8,0xff,1);
      *local_38 = 0x16;
    }
    CDXTexture__Helper_00593024((int)local_8,local_c);
    iVar3 = *local_38;
    if (iVar3 < 0x33) {
      if (iVar3 == 0x32) {
LAB_0057bc2c:
        local_10 = 1;
      }
      else if (iVar3 == 0x14) {
LAB_0057bc4f:
        local_10 = 3;
      }
      else if (((iVar3 == 0x15) || (iVar3 == 0x16)) || (iVar3 == 0x24)) {
        local_10 = 4;
      }
      else if (iVar3 == 0x29) goto LAB_0057bc2c;
    }
    else {
      if (iVar3 != 0x33) {
        if (iVar3 == 0x51) goto LAB_0057bc2c;
        if (iVar3 != 0x36314c41) {
          if (iVar3 != 0x36315220) goto LAB_0057bc5b;
          goto LAB_0057bc4f;
        }
      }
      local_10 = 2;
    }
LAB_0057bc5b:
    uVar4 = CDXTexture__Helper_005935d9((int)local_8,local_c);
    if (local_10 == (uVar4 & 0xff)) {
      local_38[3] = local_34;
      local_38[4] = local_1c;
      local_38[5] = 1;
      iVar3 = CDXTexture__Unk_005935c0((int)local_8,local_c);
      local_38[0xc] = iVar3;
      local_38[0xd] = 0;
      if (local_38[0x10] == 0) goto LAB_0057bef1;
      CFastVB__Helper_00426fd0(iVar3 * local_1c);
      local_38[1] = extraout_EAX;
      if (extraout_EAX != 0) {
        local_38[0xe] = 1;
        CFastVB__Helper_00426fd0(local_1c << 2);
        local_20 = extraout_EAX_00;
        if (extraout_EAX_00 != (void *)0x0) {
          uVar4 = 0;
          if (local_1c != 0) {
            do {
              *(uint *)((int)extraout_EAX_00 + uVar4 * 4) = local_38[0xc] * uVar4 + local_38[1];
              uVar4 = uVar4 + 1;
            } while (uVar4 < local_1c);
          }
          CDXTexture__Unk_005933c6((int)local_8,extraout_EAX_00);
          if (*local_38 == 0x29) {
            local_2c = 0;
            local_24 = 0;
            uVar4 = CDXTexture__Unk_005935a3((int)local_8,local_c,8);
            if (uVar4 != 0) {
              CDXTexture__Helper_0059371d((int)local_8,local_c,&local_14,&local_24);
            }
            uVar4 = CDXTexture__Unk_005935a3((int)local_8,local_c,0x10);
            if (uVar4 != 0) {
              CDXTexture__Helper_00593753((int)local_8,local_c,&local_40,&local_2c,(void *)0x0);
            }
            if ((*(float *)((int)local_8 + 0x130) <= (float)_DAT_005e96b0) ||
               (*(float *)((int)local_8 + 0x134) <= (float)_DAT_005e96b0)) {
              iVar3 = 0;
              do {
                auStack_158[iVar3] = (char)iVar3;
                iVar3 = iVar3 + 1;
              } while (iVar3 < 0x100);
            }
            else {
              local_18 = 0;
              local_50 = (double)((float)_DAT_005e96a8 /
                                 (*(float *)((int)local_8 + 0x134) *
                                 *(float *)((int)local_8 + 0x130)));
              do {
                CMeshCollisionVolume__Helper_0055fa40();
                uVar2 = __ftol();
                iVar3 = local_18 + 1;
                puVar1 = auStack_158 + local_18;
                local_18 = iVar3;
                *puVar1 = uVar2;
              } while (iVar3 < 0x100);
            }
            CFastVB__Helper_00426fd0(0x400);
            local_38[2] = extraout_EAX_01;
            if (extraout_EAX_01 == 0) goto LAB_0057bdef;
            iVar3 = 0;
            local_38[0xf] = 1;
            if (0 < local_2c) {
              iVar6 = 0;
              do {
                iVar5 = iVar3 * 4;
                *(undefined1 *)(iVar5 + local_38[2]) = auStack_158[*(byte *)(iVar6 + local_14)];
                *(undefined1 *)(iVar5 + 1 + local_38[2]) =
                     auStack_158[*(byte *)(iVar6 + 1 + local_14)];
                *(undefined1 *)(iVar5 + 2 + local_38[2]) =
                     auStack_158[*(byte *)(iVar6 + 2 + local_14)];
                puVar1 = (undefined1 *)(iVar3 + local_40);
                iVar3 = iVar3 + 1;
                *(undefined1 *)(iVar5 + 3 + local_38[2]) = *puVar1;
                iVar6 = iVar6 + 3;
              } while (iVar3 < local_2c);
            }
            if (iVar3 < local_24) {
              iVar6 = iVar3 * 3;
              do {
                iVar5 = iVar3 * 4;
                *(undefined1 *)(iVar5 + local_38[2]) = auStack_158[*(byte *)(iVar6 + local_14)];
                *(undefined1 *)(iVar5 + 1 + local_38[2]) =
                     auStack_158[*(byte *)(iVar6 + 1 + local_14)];
                *(undefined1 *)(iVar5 + 2 + local_38[2]) =
                     auStack_158[*(byte *)(iVar6 + 2 + local_14)];
                *(undefined1 *)(iVar5 + 3 + local_38[2]) = 0xff;
                iVar3 = iVar3 + 1;
                iVar6 = iVar6 + 3;
              } while (iVar3 < local_24);
            }
            if (iVar3 < 0x100) {
              iVar3 = iVar3 << 2;
              do {
                *(undefined1 *)(iVar3 + local_38[2]) = 0xff;
                *(undefined1 *)(iVar3 + 1 + local_38[2]) = 0xff;
                *(undefined1 *)(iVar3 + 2 + local_38[2]) = 0xff;
                *(undefined1 *)(iVar3 + 3 + local_38[2]) = 0xff;
                iVar3 = iVar3 + 4;
              } while (iVar3 < 0x400);
            }
          }
LAB_0057bef1:
          iVar3 = 0;
          goto LAB_0057bef3;
        }
      }
LAB_0057bdef:
      iVar3 = -0x7ff8fff2;
      goto LAB_0057bef3;
    }
  }
  iVar3 = -0x7fffbffb;
LAB_0057bef3:
  if (local_8 != (void *)0x0) {
    CDXTexture__Unk_00593526(&local_8,&local_c,(void *)0x0);
  }
  if (local_20 != (void *)0x0) {
    OID__FreeObject_Callback(local_20);
  }
  return iVar3;
}
