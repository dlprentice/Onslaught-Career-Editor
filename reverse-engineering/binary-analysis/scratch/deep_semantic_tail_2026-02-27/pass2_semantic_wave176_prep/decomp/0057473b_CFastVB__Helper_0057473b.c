/* address: 0x0057473b */
/* name: CFastVB__Helper_0057473b */
/* signature: int CFastVB__Helper_0057473b(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CFastVB__Helper_0057473b(void)

{
  int *piVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  int *in_EDX;
  uint uVar5;
  uint uVar6;
  uint *in_stack_00000004;
  uint *in_stack_00000008;
  uint *in_stack_0000000c;
  uint *in_stack_00000010;
  uint in_stack_00000014;
  int *in_stack_00000018;
  int in_stack_0000001c;
  uint in_stack_00000020;
  uint local_108;
  uint local_ec;
  uint local_e8;
  uint local_e4;
  int local_dc;
  uint local_14;
  int local_10;
  uint local_c;
  uint local_8;

  if (in_EDX == (int *)0x0) {
    return -0x7789f794;
  }
  if (in_stack_00000014 == 0xffffffff) {
    in_stack_00000014 = 0;
  }
  if (((in_stack_00000014 & 0xffe039ec) != 0) ||
     ((((in_stack_0000001c != 0 && (in_stack_0000001c != 1)) && (in_stack_0000001c != 2)) &&
      (in_stack_0000001c != 3)))) {
    return -0x7789f794;
  }
  if (in_stack_00000018 == (int *)0x0) {
    local_10 = 0;
  }
  else {
    local_10 = *in_stack_00000018;
  }
  if (in_stack_0000001c == 3) {
    if (local_10 == 0) {
      local_10 = 0x15;
    }
  }
  else {
    piVar1 = CMeshCollisionVolume__Helper_00574270(local_10);
    local_10 = CFastVB__SelectBestFormatHandler(in_EDX,in_stack_00000014,in_stack_00000020,piVar1);
    if (local_10 == 0) {
      return -0x7789f796;
    }
  }
  if (in_stack_00000004 == (uint *)0x0) {
    local_8 = 0xffffffff;
  }
  else {
    local_8 = *in_stack_00000004;
  }
  if (in_stack_00000008 == (uint *)0x0) {
    uVar5 = 0xffffffff;
  }
  else {
    uVar5 = *in_stack_00000008;
  }
  if (in_stack_0000000c == (uint *)0x0) {
    local_c = 0xffffffff;
  }
  else {
    local_c = *in_stack_0000000c;
  }
  if (in_stack_00000010 == (uint *)0x0) {
    local_14 = 0xffffffff;
  }
  else {
    local_14 = *in_stack_00000010;
  }
  if (local_8 == 0xffffffff) {
    local_8 = uVar5;
    if (uVar5 != 0xffffffff) goto LAB_00574839;
    uVar5 = 0x100;
    local_8 = 0x100;
  }
  else {
    if (uVar5 == 0xffffffff) {
      uVar5 = local_8;
    }
LAB_00574839:
    if (local_8 == 0) {
      local_8 = 1;
    }
    if (uVar5 == 0) {
      uVar5 = 1;
    }
  }
  uVar6 = local_8;
  if ((in_stack_00000020 == 5) && (uVar6 = uVar5, uVar5 < local_8)) {
    uVar5 = local_8;
    uVar6 = local_8;
  }
  local_8 = uVar6;
  if ((local_c == 0xffffffff) || (local_c == 0)) {
    local_c = 1;
  }
  if (in_stack_0000001c == 3) goto LAB_00574968;
  (**(code **)(*in_EDX + 0x1c))();
  uVar6 = uVar5;
  if (in_stack_00000020 == 4) {
    if (local_e4 < local_c) {
      local_c = local_e4;
    }
    if (local_e4 < local_8) {
      local_8 = local_e4;
    }
LAB_005748f0:
    if (local_e4 < uVar6) {
      uVar6 = local_e4;
    }
  }
  else {
    if (local_ec < local_8) {
      local_8 = local_ec;
    }
    if (local_e8 < uVar5) {
      uVar6 = local_e8;
    }
    if (in_stack_00000020 == 3) {
      if ((local_108 & 0x20) != 0) {
        local_dc = 1;
      }
      if (local_dc != 0) {
        if (local_dc * uVar6 < local_8) {
          local_8 = local_dc * uVar6;
        }
        local_e4 = local_dc * local_8;
        goto LAB_005748f0;
      }
    }
  }
  uVar4 = local_8;
  uVar3 = local_c;
  if (in_stack_00000020 == 3) {
    uVar2 = 2;
  }
  else if (in_stack_00000020 == 4) {
    uVar2 = 0x40000;
  }
  else {
    uVar2 = in_stack_00000020;
    if (in_stack_00000020 == 5) {
      uVar2 = 0x20000;
    }
  }
  if ((local_14 == 1) && ((local_108 & 0x100) != 0)) {
    uVar2 = 0;
  }
  uVar5 = uVar6;
  if ((local_108 & uVar2) != 0) {
    uVar5 = 1;
    local_8 = 1;
    if (1 < uVar4) {
      do {
        local_8 = local_8 << 1;
      } while (local_8 < uVar4);
    }
    if (1 < uVar6) {
      do {
        uVar5 = uVar5 << 1;
      } while (uVar5 < uVar6);
    }
    local_c = 1;
    if (1 < uVar3) {
      do {
        local_c = local_c << 1;
      } while (local_c < uVar3);
    }
  }
LAB_00574968:
  if ((((local_10 == 0x31545844) || (local_10 == 0x32545844)) || (local_10 == 0x33545844)) ||
     ((local_10 == 0x34545844 || (local_10 == 0x35545844)))) {
    local_8 = local_8 + 3 & 0xfffffffc;
    uVar5 = uVar5 + 3 & 0xfffffffc;
  }
  if (in_stack_00000020 == 3) {
    uVar6 = 0x4000;
  }
  else if (in_stack_00000020 == 4) {
    uVar6 = 0x8000;
  }
  else {
    uVar6 = in_stack_00000020;
    if (in_stack_00000020 == 5) {
      uVar6 = 0x10000;
    }
  }
  if ((in_stack_0000001c == 3) ||
     (((local_108 & uVar6) != 0 &&
      (((local_108 & 0x100) == 0 ||
       ((((local_8 & local_8 - 1) == 0 && ((uVar5 & uVar5 - 1) == 0)) &&
        ((local_c & local_c - 1) == 0)))))))) {
    uVar6 = 0;
    for (uVar3 = local_8; uVar3 != 0; uVar3 = uVar3 >> 1) {
      uVar6 = uVar6 + 1;
    }
    uVar3 = 0;
    for (uVar4 = uVar5; uVar4 != 0; uVar4 = uVar4 >> 1) {
      uVar3 = uVar3 + 1;
    }
    uVar4 = 0;
    for (uVar2 = local_c; uVar2 != 0; uVar2 = uVar2 >> 1) {
      uVar4 = uVar4 + 1;
    }
    if (uVar6 <= uVar3) {
      uVar6 = uVar3;
    }
    if ((in_stack_00000020 == 4) && (uVar6 < uVar4)) {
      uVar6 = uVar4;
    }
    if ((uVar6 < local_14) || (local_14 == 0)) {
      local_14 = uVar6;
    }
    if ((local_14 != 1) && ((in_stack_00000014 & 0x400) != 0)) {
      local_14 = 0;
    }
  }
  else {
    local_14 = 1;
  }
  if (in_stack_00000004 != (uint *)0x0) {
    *in_stack_00000004 = local_8;
  }
  if (in_stack_00000008 != (uint *)0x0) {
    *in_stack_00000008 = uVar5;
  }
  if (in_stack_0000000c != (uint *)0x0) {
    *in_stack_0000000c = local_c;
  }
  if (in_stack_00000010 != (uint *)0x0) {
    *in_stack_00000010 = local_14;
  }
  if (in_stack_00000018 != (int *)0x0) {
    *in_stack_00000018 = local_10;
  }
  return 0;
}
