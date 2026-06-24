/* address: 0x00580a05 */
/* name: CDXTexture__UploadSurfaceRegionWithFallback */
/* signature: int CDXTexture__UploadSurfaceRegionWithFallback(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CDXTexture__UploadSurfaceRegionWithFallback(void)

{
  uint *puVar1;
  int *piVar2;
  int iVar3;
  uint *in_ECX;
  uint uVar4;
  uint *puVar5;
  uint *puVar6;
  undefined4 *in_stack_00000004;
  int *in_stack_00000008;
  undefined4 in_stack_0000000c;
  uint *in_stack_00000010;
  undefined4 in_stack_00000014;
  uint in_stack_00000018;
  int local_74 [2];
  byte local_6b;
  int local_68;
  uint local_5c;
  uint local_58;
  uint local_54;
  uint local_50;
  uint local_4c;
  uint local_48;
  uint local_44;
  uint local_40;
  uint local_3c;
  uint local_38;
  undefined4 local_34;
  undefined4 local_30;
  uint local_2c;
  uint local_28;
  uint local_24;
  int *local_20;
  uint local_1c;
  uint *local_18;
  int *local_14;
  int local_10;
  int local_c;
  int local_8;

  local_18 = in_ECX;
  CDXTexture__FinalizeTextureUploadAndReleaseTemp(in_ECX);
  (**(code **)(*in_stack_00000008 + 0x30))(in_stack_00000008,local_74);
  puVar5 = local_18;
  if (in_stack_00000010 == (uint *)0x0) {
    local_3c = local_5c;
    local_38 = local_58;
    local_44 = 0;
    local_40 = 0;
    local_8 = 0;
    local_1c = ~in_stack_00000018 & 1;
  }
  else {
    local_44 = *in_stack_00000010;
    local_40 = in_stack_00000010[1];
    local_3c = in_stack_00000010[2];
    local_38 = in_stack_00000010[3];
    if (((((int)local_44 < 0) || (local_5c < local_3c)) || ((int)local_3c < (int)local_44)) ||
       ((((int)local_40 < 0 || (local_58 < local_38)) || ((int)local_38 < (int)local_40)))) {
      return -0x7789f794;
    }
    local_1c = 1;
    if (((local_44 != 0) || (local_3c != local_5c)) ||
       ((local_40 != 0 || (local_8 = 0, local_38 != local_58)))) {
      local_8 = 1;
    }
    if (((in_stack_00000018 & 1) != 0) || (local_8 != 0)) {
      local_1c = 0;
    }
  }
  local_2c = in_stack_00000018 & 0x10000;
  if (local_2c != 0) {
    local_28 = local_5c;
    local_24 = local_58;
    local_10 = 0;
    if ((((local_74[0] == 0x31545844) || (local_74[0] == 0x32545844)) || (local_74[0] == 0x33545844)
        ) || ((local_74[0] == 0x34545844 || (local_74[0] == 0x35545844)))) {
      uVar4 = local_58 | local_5c;
      while ((uVar4 & 3) != 0) {
        local_10 = local_10 + 1;
        uVar4 = (local_58 | local_5c) << ((byte)local_10 & 0x1f);
      }
    }
    puVar1 = local_18 + 4;
    (**(code **)(*in_stack_00000008 + 0xc))(in_stack_00000008,puVar1);
    puVar5 = puVar5 + 3;
    local_c = (**(code **)(*(int *)*puVar1 + 0x5c))
                        ((int *)*puVar1,local_28 << ((byte)local_10 & 0x1f),
                         local_24 << ((byte)local_10 & 0x1f),local_10 + 1,0,local_74[0],
                         (local_68 == 3) + '\x02',puVar5,0);
    if (-1 < local_c) {
      puVar6 = local_18 + 2;
      local_c = (**(code **)(*(int *)*puVar5 + 0x48))((int *)*puVar5,local_10,puVar6);
      if (-1 < local_c) {
        if (local_1c == 0) {
          local_14 = (int *)0x0;
          CFastVB__Helper_00579bd5(1);
          local_c = CDXTexture__CopyLockedRectPitchAware(in_stack_00000008,(void *)*puVar6);
          CFastVB__Helper_00579bd5(0);
          if (local_c < 0) {
            if ((local_10 == 0) &&
               (local_c = (**(code **)(*(int *)*puVar1 + 0x70))
                                    ((int *)*puVar1,local_28,local_24,local_74[0],0,0,1,&local_14,0)
               , -1 < local_c)) {
              local_c = (**(code **)(*(int *)*puVar1 + 0x88))
                                  ((int *)*puVar1,in_stack_00000008,0,local_14,0,0);
              if (local_c < 0) {
                (**(code **)(*local_14 + 8))(local_14);
              }
              else {
                local_c = CDXTexture__CopyLockedRectPitchAware(local_14,(void *)*puVar6);
                (**(code **)(*local_14 + 8))(local_14);
                if (-1 < local_c) goto LAB_00580c4b;
              }
            }
            piVar2 = (int *)*puVar6;
            if (piVar2 != (int *)0x0) {
              (**(code **)(*piVar2 + 8))(piVar2);
              *puVar6 = 0;
            }
            goto LAB_00580c25;
          }
        }
LAB_00580c4b:
        local_14 = (int *)*puVar6;
        goto LAB_00580c6b;
      }
    }
    piVar2 = (int *)local_18[2];
    if (piVar2 != (int *)0x0) {
      (**(code **)(*piVar2 + 8))(piVar2);
      local_18[2] = 0;
    }
LAB_00580c25:
    piVar2 = (int *)*puVar5;
    if (piVar2 != (int *)0x0) {
      (**(code **)(*piVar2 + 8))(piVar2);
      *puVar5 = 0;
    }
    piVar2 = (int *)*puVar1;
    if (piVar2 == (int *)0x0) {
      return local_c;
    }
    (**(code **)(*piVar2 + 8))(piVar2);
    *puVar1 = 0;
    return local_c;
  }
  local_14 = in_stack_00000008;
LAB_00580c6b:
  uVar4 = (in_stack_00000018 & 1 | 0x80) << 4;
  if (((local_1c == 0) || (local_2c != 0)) || ((local_6b & 2) == 0)) {
LAB_00580cee:
    if (local_8 != 0) {
      if (local_74[0] < 0x34545845) {
        if (((local_74[0] == 0x34545844) || (local_74[0] == 0x31545844)) ||
           (local_74[0] == 0x32545844)) {
LAB_00580d26:
          local_4c = local_3c + 3 & 0xfffffffc;
          local_54 = local_44 & 0xfffffffc;
          local_50 = local_40 & 0xfffffffc;
          local_48 = local_38 + 3 & 0xfffffffc;
          if (local_5c < local_4c) {
            local_4c = local_5c;
          }
          if (local_58 < local_48) {
            local_48 = local_58;
          }
        }
        else {
          if (local_74[0] != 0x32595559) {
            if (local_74[0] != 0x33545844) goto LAB_00580d99;
            goto LAB_00580d26;
          }
LAB_00580da5:
          local_54 = local_44 & 0xfffffffe;
          local_4c = local_3c + 1 & 0xfffffffe;
          local_50 = local_40;
          local_48 = local_38;
          if (local_5c < local_4c) {
            local_4c = local_5c;
          }
        }
        if ((((local_54 == 0) && (local_4c == local_5c)) && (local_50 == 0)) &&
           (local_48 == local_58)) {
          local_8 = 0;
        }
        else {
          local_8 = 1;
        }
      }
      else {
        if (local_74[0] == 0x35545844) goto LAB_00580d26;
        if (((local_74[0] == 0x42475247) || (local_74[0] == 0x47424752)) ||
           (local_74[0] == 0x59565955)) goto LAB_00580da5;
LAB_00580d99:
        local_54 = local_44;
        local_50 = local_40;
        local_4c = local_3c;
        local_48 = local_38;
      }
    }
    if (local_2c != 0) {
      iVar3 = (**(code **)(*local_14 + 0x34))
                        (local_14,&local_34,-(uint)(local_8 != 0) & (uint)&local_54,uVar4);
      if (iVar3 < 0) {
        return iVar3;
      }
      goto LAB_00580e65;
    }
  }
  else {
    if ((in_stack_00000018 & 0x20000) == 0) {
      CFastVB__Helper_00579bd5(1);
      iVar3 = (**(code **)(*in_stack_00000008 + 0x2c))(in_stack_00000008,&DAT_005eefac,&local_20);
      if (-1 < iVar3) {
        iVar3 = (**(code **)(*local_20 + 0x34))(local_20);
        if (iVar3 == 1) {
          uVar4 = uVar4 | 0x2000;
          local_8 = 0;
        }
        if (local_20 != (int *)0x0) {
          (**(code **)(*local_20 + 8))(local_20);
          local_20 = (int *)0x0;
        }
      }
      CFastVB__Helper_00579bd5(0);
      goto LAB_00580cee;
    }
    uVar4 = uVar4 | 0x2000;
    local_8 = 0;
  }
  CFastVB__Helper_00579bd5(1);
  iVar3 = (**(code **)(*local_14 + 0x34))
                    (local_14,&local_34,-(uint)(local_8 != 0) & (uint)&local_54,uVar4);
  CFastVB__Helper_00579bd5(0);
  if (iVar3 < 0) {
    iVar3 = CDXTexture__UploadSurfaceRegionWithFallback();
    return iVar3;
  }
LAB_00580e65:
  if (local_8 != 0) {
    local_44 = local_44 - local_54;
    local_3c = local_3c - local_54;
    local_40 = local_40 - local_50;
    local_38 = local_38 - local_50;
  }
  *in_stack_00000004 = local_30;
  in_stack_00000004[1] = local_74[0];
  in_stack_00000004[2] = local_34;
  in_stack_00000004[6] = local_5c;
  in_stack_00000004[7] = local_58;
  in_stack_00000004[10] = local_44;
  in_stack_00000004[9] = 1;
  in_stack_00000004[0xb] = local_40;
  in_stack_00000004[0xf] = 1;
  in_stack_00000004[0x10] = 1;
  in_stack_00000004[0x12] = in_stack_00000014;
  in_stack_00000004[0xc] = local_3c;
  in_stack_00000004[3] = 0;
  in_stack_00000004[4] = 0;
  in_stack_00000004[5] = 0;
  in_stack_00000004[8] = 0;
  in_stack_00000004[0xe] = 0;
  in_stack_00000004[0x11] = 0;
  in_stack_00000004[0x13] = in_stack_0000000c;
  in_stack_00000004[0xd] = local_38;
  local_18[1] = (uint)in_stack_00000008;
  *local_18 = in_stack_00000018;
  (**(code **)(*in_stack_00000008 + 4))(in_stack_00000008);
  return 0;
}
