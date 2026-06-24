/* address: 0x00580ef4 */
/* name: CDXTexture__CreateTexelCodecProfileFromSurfaceDesc */
/* signature: int CDXTexture__CreateTexelCodecProfileFromSurfaceDesc(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CDXTexture__CreateTexelCodecProfileFromSurfaceDesc(void)

{
  bool bVar1;
  uint uVar2;
  uint uVar3;
  int *in_ECX;
  int iVar4;
  uint uVar5;
  uint *puVar6;
  uint *puVar7;
  undefined4 *in_stack_00000004;
  int *in_stack_00000008;
  undefined4 in_stack_0000000c;
  uint *in_stack_00000010;
  undefined4 in_stack_00000014;
  uint in_stack_00000018;
  int local_68 [2];
  uint local_60;
  int local_5c;
  uint local_58;
  uint local_54;
  uint local_50;
  uint local_4c [4];
  uint local_3c;
  uint local_38;
  uint local_34 [4];
  uint local_24;
  uint local_20;
  undefined4 local_1c;
  undefined4 local_18;
  undefined4 local_14;
  int *local_10;
  uint local_c;
  int *local_8;

  local_10 = in_ECX;
  if (*in_ECX != 0) {
    CFastVB__ShutdownActiveProfile(in_ECX);
  }
  (**(code **)(*in_stack_00000008 + 0x20))(in_stack_00000008,local_68);
  if (in_stack_00000010 == (uint *)0x0) {
    bVar1 = false;
    local_34[2] = local_58;
    local_34[3] = local_54;
    uVar3 = ~in_stack_00000018 & 1;
    local_34[0] = 0;
    local_34[1] = 0;
    local_24 = 0;
    local_20 = local_50;
  }
  else {
    puVar6 = local_34;
    for (iVar4 = 6; iVar4 != 0; iVar4 = iVar4 + -1) {
      *puVar6 = *in_stack_00000010;
      in_stack_00000010 = in_stack_00000010 + 1;
      puVar6 = puVar6 + 1;
    }
    if (local_58 < local_34[2]) {
      return -0x7789f794;
    }
    if (local_34[2] < local_34[0]) {
      return -0x7789f794;
    }
    if (local_54 < local_34[3]) {
      return -0x7789f794;
    }
    if (local_34[3] < local_34[1]) {
      return -0x7789f794;
    }
    if (local_50 < local_20) {
      return -0x7789f794;
    }
    if (local_20 < local_24) {
      return -0x7789f794;
    }
    if (((((local_34[0] != 0) || (local_34[2] != local_58)) || (local_34[1] != 0)) ||
        ((local_34[3] != local_54 || (local_24 != 0)))) || (bVar1 = false, local_20 != local_50)) {
      bVar1 = true;
    }
    if (((in_stack_00000018 & 1) != 0) || (bVar1)) {
      uVar3 = 0;
    }
    else {
      uVar3 = 1;
    }
  }
  uVar2 = local_20;
  if ((local_5c == 0) && ((local_60 & 0x200) == 0)) {
    return -0x7789f794;
  }
  uVar5 = (in_stack_00000018 & 1 | 0x80) << 4;
  local_c = uVar5;
  if ((uVar3 == 0) || ((local_60 & 0x200) == 0)) {
LAB_0058105a:
    if (bVar1) {
      if (local_68[0] < 0x34545845) {
        if (((local_68[0] != 0x34545844) && (local_68[0] != 0x31545844)) &&
           (local_68[0] != 0x32545844)) {
          if (local_68[0] == 0x32595559) {
LAB_00581162:
            local_4c[3] = local_34[3];
            local_4c[1] = local_34[1];
            local_4c[0] = local_34[0] & 0xfffffffe;
            local_4c[2] = local_34[2] + 1 & 0xfffffffe;
            local_3c = local_24;
            if (local_58 < local_4c[2]) {
              local_4c[2] = local_58;
            }
            local_38 = uVar2;
            if (((local_4c[0] != 0) || (local_4c[2] != local_58)) ||
               ((local_34[1] != 0 ||
                (((local_34[3] != local_54 || (local_24 != 0)) || (uVar2 != local_50))))))
            goto LAB_005811bc;
            goto LAB_00581114;
          }
          if (local_68[0] != 0x33545844) goto LAB_00581155;
        }
LAB_0058109d:
        local_4c[0] = local_34[0] & 0xfffffffc;
        local_4c[2] = local_34[2] + 3 & 0xfffffffc;
        local_4c[1] = local_34[1] & 0xfffffffc;
        local_4c[3] = local_34[3] + 3 & 0xfffffffc;
        local_3c = local_24;
        if (local_58 < local_4c[2]) {
          local_4c[2] = local_58;
        }
        if (local_54 < local_4c[3]) {
          local_4c[3] = local_54;
        }
        uVar5 = local_c;
        local_38 = uVar2;
        if (((local_4c[0] == 0) && (local_4c[2] == local_58)) &&
           (((local_4c[1] == 0 && ((local_4c[3] == local_54 && (local_24 == 0)))) &&
            (uVar2 == local_50)))) goto LAB_00581114;
      }
      else {
        if (local_68[0] == 0x35545844) goto LAB_0058109d;
        if (((local_68[0] == 0x42475247) || (local_68[0] == 0x47424752)) ||
           (local_68[0] == 0x59565955)) goto LAB_00581162;
LAB_00581155:
        puVar6 = local_34;
        puVar7 = local_4c;
        for (iVar4 = 6; uVar5 = local_c, iVar4 != 0; iVar4 = iVar4 + -1) {
          *puVar7 = *puVar6;
          puVar6 = puVar6 + 1;
          puVar7 = puVar7 + 1;
        }
      }
LAB_005811bc:
      iVar4 = (**(code **)(*in_stack_00000008 + 0x24))(in_stack_00000008,&local_1c,local_4c,uVar5);
      if (iVar4 < 0) {
        return iVar4;
      }
      local_34[0] = local_34[0] - local_4c[0];
      local_34[2] = local_34[2] - local_4c[0];
      local_34[1] = local_34[1] - local_4c[1];
      local_34[3] = local_34[3] - local_4c[1];
      local_24 = local_24 - local_3c;
      local_20 = uVar2 - local_3c;
      goto LAB_005811f3;
    }
  }
  else {
    if ((in_stack_00000018 & 0x20000) == 0) {
      CDXTexture__SetD3D9DebugMute(1);
      iVar4 = (**(code **)(*in_stack_00000008 + 0x1c))(in_stack_00000008,&DAT_005eef9c,&local_8);
      if (-1 < iVar4) {
        iVar4 = (**(code **)(*local_8 + 0x34))(local_8);
        if (iVar4 == 1) {
          uVar5 = uVar5 | 0x2000;
          bVar1 = false;
          local_c = uVar5;
        }
        if (local_8 != (int *)0x0) {
          (**(code **)(*local_8 + 8))(local_8);
          local_8 = (int *)0x0;
        }
      }
      CDXTexture__SetD3D9DebugMute(0);
      goto LAB_0058105a;
    }
    uVar5 = uVar5 | 0x2000;
  }
LAB_00581114:
  iVar4 = (**(code **)(*in_stack_00000008 + 0x24))(in_stack_00000008,&local_1c,0,uVar5);
  if (iVar4 < 0) {
    return iVar4;
  }
LAB_005811f3:
  *in_stack_00000004 = local_14;
  in_stack_00000004[0x11] = 0;
  in_stack_00000004[1] = local_68[0];
  in_stack_00000004[2] = local_1c;
  in_stack_00000004[3] = local_18;
  in_stack_00000004[4] = 0;
  in_stack_00000004[5] = 0;
  in_stack_00000004[8] = 0;
  in_stack_00000004[9] = local_50;
  puVar6 = local_34;
  puVar7 = in_stack_00000004 + 10;
  for (iVar4 = 6; iVar4 != 0; iVar4 = iVar4 + -1) {
    *puVar7 = *puVar6;
    puVar6 = puVar6 + 1;
    puVar7 = puVar7 + 1;
  }
  in_stack_00000004[0x12] = in_stack_00000014;
  in_stack_00000004[6] = local_58;
  in_stack_00000004[0x13] = in_stack_0000000c;
  in_stack_00000004[7] = local_54;
  in_stack_00000004[0x10] = 1;
  *local_10 = (int)in_stack_00000008;
  (**(code **)(*in_stack_00000008 + 4))(in_stack_00000008);
  return 0;
}
