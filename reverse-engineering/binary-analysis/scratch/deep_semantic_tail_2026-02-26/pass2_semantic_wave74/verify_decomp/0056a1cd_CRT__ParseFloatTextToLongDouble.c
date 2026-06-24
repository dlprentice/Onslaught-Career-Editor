/* address: 0x0056a1cd */
/* name: CRT__ParseFloatTextToLongDouble */
/* signature: int CRT__ParseFloatTextToLongDouble(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CRT__ParseFloatTextToLongDouble(void)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  char *pcVar4;
  byte *in_ECX;
  int iVar5;
  byte bVar6;
  byte *pbVar7;
  uint unaff_EDI;
  byte *pbVar8;
  ushort *in_stack_00000004;
  int *in_stack_00000008;
  byte *in_stack_0000000c;
  int in_stack_00000010;
  int in_stack_00000014;
  int in_stack_00000018;
  int in_stack_0000001c;
  int iVar9;
  byte *pbVar10;
  char local_60 [23];
  char local_49;
  ushort local_44;
  undefined2 uStack_42;
  undefined2 uStack_40;
  byte *local_3e;
  ushort local_3a;
  int local_34;
  int local_30;
  undefined4 local_2c;
  int local_28;
  int local_24;
  byte *local_20;
  int local_1c;
  int local_18;
  int local_14;
  char *local_10;
  int local_c;
  uint local_8;

  local_10 = local_60;
  local_2c = 0;
  local_1c = 1;
  local_8 = 0;
  local_14 = 0;
  local_28 = 0;
  local_24 = 0;
  local_30 = 0;
  local_34 = 0;
  local_20 = (byte *)0x0;
  local_c = 0;
  local_18 = 0;
  pbVar8 = in_stack_0000000c;
  while( true ) {
    bVar6 = *pbVar8;
    in_ECX = (byte *)CONCAT31((int3)((uint)in_ECX >> 8),bVar6);
    if ((((bVar6 != 0x20) && (bVar6 != 9)) && (bVar6 != 10)) && (bVar6 != 0xd)) break;
    pbVar8 = pbVar8 + 1;
  }
  iVar1 = 4;
  iVar9 = 0;
  iVar5 = local_14;
LAB_0056a224:
  local_14 = iVar5;
  pbVar7 = pbVar8;
  iVar5 = 1;
  bVar6 = *pbVar7;
  pbVar8 = pbVar7 + 1;
  iVar2 = local_14;
  switch(iVar9) {
  case 0:
    if (('0' < (char)bVar6) && ((char)bVar6 < ':')) {
LAB_0056a241:
      local_14 = iVar2;
      iVar9 = 3;
      goto LAB_0056a466;
    }
    if (bVar6 == DAT_00653aa0) goto LAB_0056a250;
    if (bVar6 == 0x2b) {
      local_2c = 0;
      iVar9 = 2;
      iVar5 = local_14;
    }
    else if (bVar6 == 0x2d) {
      local_2c = 0x8000;
      iVar9 = 2;
      iVar5 = local_14;
    }
    else {
      iVar9 = iVar5;
      iVar5 = local_14;
      if (bVar6 != 0x30) goto LAB_0056a540;
    }
    goto LAB_0056a224;
  case 1:
    local_14 = 1;
    if (('0' < (char)bVar6) && (iVar2 = iVar5, (char)bVar6 < ':')) goto LAB_0056a241;
    iVar9 = iVar1;
    if (bVar6 != DAT_00653aa0) {
      iVar9 = iVar5;
      if ((bVar6 == 0x2b) || (iVar9 = local_14, bVar6 == 0x2d)) goto LAB_0056a2d5;
      iVar9 = iVar5;
      local_14 = iVar5;
      if (bVar6 != 0x30) goto LAB_0056a2ae;
    }
    goto LAB_0056a224;
  case 2:
    if (('0' < (char)bVar6) && ((char)bVar6 < ':')) goto LAB_0056a241;
    if (bVar6 == DAT_00653aa0) {
LAB_0056a250:
      iVar9 = 5;
      iVar5 = local_14;
    }
    else {
      iVar9 = iVar5;
      pbVar7 = in_stack_0000000c;
      iVar5 = local_14;
      if (bVar6 != 0x30) goto LAB_0056a545;
    }
    goto LAB_0056a224;
  case 3:
    local_14 = iVar5;
    while( true ) {
      if (DAT_00653a9c < 2) {
        uVar3 = (byte)PTR_DAT_00653890[(uint)bVar6 * 2] & 4;
        in_ECX = PTR_DAT_00653890;
      }
      else {
        pbVar7 = (byte *)0x4;
        uVar3 = CTexture__Helper_00563951(in_ECX,(uint)bVar6,4,unaff_EDI);
        in_ECX = pbVar7;
      }
      if (uVar3 == 0) break;
      if (local_8 < 0x19) {
        local_8 = local_8 + 1;
        pcVar4 = local_10 + 1;
        *local_10 = bVar6 - 0x30;
        local_10 = pcVar4;
      }
      else {
        local_c = local_c + 1;
      }
      bVar6 = *pbVar8;
      pbVar8 = pbVar8 + 1;
    }
    iVar9 = iVar1;
    iVar5 = local_14;
    if (bVar6 != DAT_00653aa0) goto LAB_0056a3c2;
    goto LAB_0056a224;
  case 4:
    local_14 = 1;
    local_28 = 1;
    iVar9 = iVar5;
    if (local_8 == 0) {
      while (iVar5 = local_28, iVar9 = local_14, bVar6 == 0x30) {
        local_c = local_c + -1;
        bVar6 = *pbVar8;
        pbVar8 = pbVar8 + 1;
      }
    }
    while( true ) {
      local_14 = iVar9;
      local_28 = iVar5;
      if (DAT_00653a9c < 2) {
        uVar3 = (byte)PTR_DAT_00653890[(uint)bVar6 * 2] & 4;
        in_ECX = PTR_DAT_00653890;
      }
      else {
        pbVar7 = (byte *)0x4;
        uVar3 = CTexture__Helper_00563951(in_ECX,(uint)bVar6,4,unaff_EDI);
        in_ECX = pbVar7;
      }
      if (uVar3 == 0) break;
      if (local_8 < 0x19) {
        local_8 = local_8 + 1;
        local_c = local_c + -1;
        pcVar4 = local_10 + 1;
        *local_10 = bVar6 - 0x30;
        local_10 = pcVar4;
      }
      bVar6 = *pbVar8;
      pbVar8 = pbVar8 + 1;
      iVar5 = local_28;
      iVar9 = local_14;
    }
LAB_0056a3c2:
    iVar9 = local_14;
    if ((bVar6 == 0x2b) || (bVar6 == 0x2d)) {
LAB_0056a2d5:
      local_14 = iVar9;
      iVar9 = 0xb;
      pbVar8 = pbVar8 + -1;
      iVar5 = local_14;
    }
    else {
LAB_0056a2ae:
      if (((char)bVar6 < 'D') ||
         (('E' < (char)bVar6 && (((char)bVar6 < 'd' || ('e' < (char)bVar6)))))) goto LAB_0056a540;
      iVar9 = 6;
      iVar5 = local_14;
    }
    goto LAB_0056a224;
  case 5:
    local_28 = iVar5;
    if (DAT_00653a9c < 2) {
      uVar3 = (byte)PTR_DAT_00653890[(uint)bVar6 * 2] & 4;
      in_ECX = PTR_DAT_00653890;
    }
    else {
      pbVar7 = (byte *)0x4;
      uVar3 = CTexture__Helper_00563951(in_ECX,(uint)bVar6,4,unaff_EDI);
      in_ECX = pbVar7;
    }
    iVar9 = iVar1;
    pbVar7 = in_stack_0000000c;
    if (uVar3 != 0) goto LAB_0056a466;
    goto LAB_0056a545;
  case 6:
    pbVar7 = pbVar7 + -1;
    in_ECX = pbVar7;
    in_stack_0000000c = pbVar7;
    if (((char)bVar6 < '1') || ('9' < (char)bVar6)) {
      if (bVar6 == 0x2b) goto LAB_0056a49b;
      if (bVar6 == 0x2d) goto LAB_0056a48f;
      if (bVar6 != 0x30) goto LAB_0056a545;
LAB_0056a434:
      iVar9 = 8;
      iVar5 = local_14;
      goto LAB_0056a224;
    }
    break;
  case 7:
    if (((char)bVar6 < '1') || ('9' < (char)bVar6)) {
      pbVar7 = in_stack_0000000c;
      if (bVar6 == 0x30) goto LAB_0056a434;
      goto LAB_0056a545;
    }
    break;
  case 8:
    local_24 = 1;
    while (bVar6 == 0x30) {
      bVar6 = *pbVar8;
      pbVar8 = pbVar8 + 1;
    }
    if (((char)bVar6 < '1') || ('9' < (char)bVar6)) goto LAB_0056a540;
    break;
  case 9:
    local_24 = 1;
    pbVar7 = (byte *)0x0;
    goto LAB_0056a4c6;
  default:
    goto switchD_0056a230_caseD_a;
  case 0xb:
    if (in_stack_0000001c != 0) {
      if (bVar6 == 0x2b) {
LAB_0056a49b:
        iVar9 = 7;
        in_ECX = pbVar7;
        in_stack_0000000c = pbVar7;
        iVar5 = local_14;
      }
      else {
        in_stack_0000000c = pbVar7;
        if (bVar6 != 0x2d) goto LAB_0056a545;
LAB_0056a48f:
        local_1c = -1;
        iVar9 = 7;
        in_ECX = pbVar7;
        in_stack_0000000c = pbVar7;
        iVar5 = local_14;
      }
      goto LAB_0056a224;
    }
    iVar9 = 10;
    pbVar8 = pbVar7;
switchD_0056a230_caseD_a:
    pbVar7 = pbVar8;
    iVar5 = local_14;
    if (iVar9 != 10) goto LAB_0056a224;
    goto LAB_0056a545;
  }
  iVar9 = 9;
LAB_0056a466:
  pbVar8 = pbVar8 + -1;
  iVar5 = local_14;
  goto LAB_0056a224;
LAB_0056a4c6:
  if (DAT_00653a9c < 2) {
    uVar3 = (byte)PTR_DAT_00653890[(uint)bVar6 * 2] & 4;
    in_ECX = PTR_DAT_00653890;
  }
  else {
    pbVar10 = (byte *)0x4;
    uVar3 = CTexture__Helper_00563951(in_ECX,(uint)bVar6,4,unaff_EDI);
    in_ECX = pbVar10;
  }
  if (uVar3 == 0) goto LAB_0056a510;
  in_ECX = (byte *)(int)(char)bVar6;
  pbVar7 = in_ECX + (int)pbVar7 * 10 + -0x30;
  if (0x1450 < (int)pbVar7) goto LAB_0056a508;
  bVar6 = *pbVar8;
  pbVar8 = pbVar8 + 1;
  goto LAB_0056a4c6;
LAB_0056a508:
  pbVar7 = (byte *)0x1451;
LAB_0056a510:
  while( true ) {
    local_20 = pbVar7;
    if (DAT_00653a9c < 2) {
      uVar3 = (byte)PTR_DAT_00653890[(uint)bVar6 * 2] & 4;
      in_ECX = PTR_DAT_00653890;
    }
    else {
      pbVar7 = (byte *)0x4;
      uVar3 = CTexture__Helper_00563951(in_ECX,(uint)bVar6,4,unaff_EDI);
      in_ECX = pbVar7;
    }
    if (uVar3 == 0) break;
    bVar6 = *pbVar8;
    pbVar8 = pbVar8 + 1;
    pbVar7 = local_20;
  }
LAB_0056a540:
  pbVar7 = pbVar8 + -1;
LAB_0056a545:
  *in_stack_00000008 = (int)pbVar7;
  if (local_14 == 0) {
    local_44 = 0;
    local_3a = 0;
    local_3e = (byte *)0x0;
    in_stack_0000000c = (byte *)0x0;
    local_18 = 4;
    goto LAB_0056a653;
  }
  pcVar4 = local_10;
  if (0x18 < local_8) {
    if ('\x04' < local_49) {
      local_49 = local_49 + '\x01';
    }
    local_8 = 0x18;
    local_c = local_c + 1;
    pcVar4 = local_10 + -1;
  }
  if (local_8 == 0) {
    local_44 = 0;
    local_3a = 0;
    local_3e = (byte *)0x0;
    in_stack_0000000c = (byte *)0x0;
  }
  else {
    while (pcVar4 = pcVar4 + -1, *pcVar4 == '\0') {
      local_8 = local_8 - 1;
      local_c = local_c + 1;
    }
    CTexture__Helper_0056d580(local_60,local_8,&local_44);
    pbVar8 = local_20;
    if (local_1c < 0) {
      pbVar8 = (byte *)-(int)local_20;
    }
    pbVar8 = pbVar8 + local_c;
    if (local_24 == 0) {
      pbVar8 = pbVar8 + in_stack_00000014;
    }
    if (local_28 == 0) {
      pbVar8 = pbVar8 + -in_stack_00000018;
    }
    if ((int)pbVar8 < 0x1451) {
      if (-0x1451 < (int)pbVar8) {
        CRT__LongDoubleScaleByPowerOf10(&local_44,(uint)pbVar8,in_stack_00000010);
        in_stack_0000000c = (byte *)CONCAT22(uStack_40,uStack_42);
        goto LAB_0056a5d8;
      }
      local_34 = 1;
    }
    else {
      local_30 = 1;
    }
    local_3a = (ushort)in_stack_0000000c;
    local_3e = in_stack_0000000c;
    local_44 = local_3a;
  }
LAB_0056a5d8:
  if (local_30 == 0) {
    if (local_34 != 0) {
      local_44 = 0;
      local_3a = 0;
      local_3e = (byte *)0x0;
      in_stack_0000000c = (byte *)0x0;
      local_18 = 1;
    }
  }
  else {
    in_stack_0000000c = (byte *)0x0;
    local_3a = 0x7fff;
    local_3e = (byte *)0x80000000;
    local_44 = 0;
    local_18 = 2;
  }
LAB_0056a653:
  *(byte **)(in_stack_00000004 + 3) = local_3e;
  *(byte **)(in_stack_00000004 + 1) = in_stack_0000000c;
  in_stack_00000004[5] = local_3a | (ushort)local_2c;
  *in_stack_00000004 = local_44;
  return local_18;
}
